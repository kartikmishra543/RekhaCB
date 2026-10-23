"""Model SQL runs only against a disposable, permission-scoped projection."""

import re
import sqlite3
from sqlalchemy import select
from app.models.employee import Employee
from app.models.project import Project
from app.models.employee_project import EmployeeProject
from app.models.employee_skill import EmployeeSkill
from app.models.skill import Skill
from .model import complete

SCHEMA = "employees(id, name, department_id, manager_id); projects(id, name, status); employee_projects(employee_id, project_id, role_on_project); skills(employee_id, name)"


def execute_safe(conn, sql):
    if (
        not re.match(r"^\s*SELECT\b", sql, re.I)
        or ";" in sql.rstrip().rstrip(";")
        or re.search(
            r"--|/\*|\b(pragma|attach|detach|insert|update|delete|drop|alter|create|replace|truncate)\b",
            sql,
            re.I,
        )
    ):
        raise ValueError("Only a single read-only SELECT is allowed.")
    allowed = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION}
    conn.set_authorizer(
        lambda action, a, b, c, d: (
            sqlite3.SQLITE_OK
            if action in allowed
            and (
                action != sqlite3.SQLITE_READ
                or a in {"employees", "projects", "employee_projects", "skills"}
            )
            and (
                action != sqlite3.SQLITE_FUNCTION
                or (b or "").lower()
                in {"count", "lower", "upper", "sum", "avg", "min", "max", "coalesce"}
            )
            else sqlite3.SQLITE_DENY
        )
    )
    ticks = [0]

    def budget():
        ticks[0] += 1
        return int(ticks[0] > 1000)

    conn.set_progress_handler(budget, 1000)
    cursor = conn.execute("SELECT * FROM (" + sql.strip().rstrip(";") + ") LIMIT 100")
    return [
        dict(zip([c[0] for c in cursor.description], row)) for row in cursor.fetchall()
    ]


async def query_hr(db, user, message):
    if re.search(
        r"\b(drop|delete|truncate|insert|update|alter|pragma|attach|detach)\b",
        message,
        re.I,
    ):
        return {
            "answer": "The data assistant supports read-only questions only.",
            "rows": [],
            "status": "refused",
        }
    if re.search(
        r"salary|salaries|payroll|bank|password|pan_number|date_of_birth|system prompt",
        message,
        re.I,
    ):
        return {
            "answer": "That information is not available through the copilot.",
            "rows": [],
            "status": "refused",
        }
    role = user.role.value
    scope = select(Employee)
    if role == "EMPLOYEE":
        scope = scope.where(Employee.id == user.id)
    elif role == "MANAGER":
        scope = scope.where((Employee.id == user.id) | (Employee.manager_id == user.id))
    people = (await db.execute(scope)).scalars().all()
    ids = [p.id for p in people]
    conn = sqlite3.connect(":memory:")
    try:
        conn.executescript(
            "CREATE TABLE employees(id INTEGER,name TEXT,department_id INTEGER,manager_id INTEGER); CREATE TABLE projects(id INTEGER,name TEXT,status TEXT); CREATE TABLE employee_projects(employee_id INTEGER,project_id INTEGER,role_on_project TEXT); CREATE TABLE skills(employee_id INTEGER,name TEXT);"
        )
        conn.executemany(
            "INSERT INTO employees VALUES(?,?,?,?)",
            [(p.id, p.name, p.department_id, p.manager_id) for p in people],
        )
        projects = (await db.execute(select(Project))).scalars().all()
        conn.executemany(
            "INSERT INTO projects VALUES(?,?,?)",
            [(p.id, p.name, p.status.value) for p in projects],
        )
        assignments = (
            (
                await db.execute(
                    select(EmployeeProject).where(EmployeeProject.employee_id.in_(ids))
                )
            )
            .scalars()
            .all()
        )
        conn.executemany(
            "INSERT INTO employee_projects VALUES(?,?,?)",
            [(p.employee_id, p.project_id, p.role_on_project) for p in assignments],
        )
        skills = (
            await db.execute(
                select(EmployeeSkill.employee_id, Skill.name)
                .join(Skill, Skill.id == EmployeeSkill.skill_id)
                .where(EmployeeSkill.employee_id.in_(ids))
            )
        ).all()
        conn.executemany("INSERT INTO skills VALUES(?,?)", [tuple(s) for s in skills])
        sql = await complete(
            "Return ONLY one SQLite SELECT, no markdown. Schema: "
            + SCHEMA
            + ". Data is already role scoped. Never query any other tables. Limit results to 100.",
            message,
        )
        if not sql:
            q = message.lower()
            if "skill" in q or any(s in q for s in ("python", "fastapi", "langchain")):
                terms = [s[1] for s in skills if s[1].lower() in q]
                sql = "SELECT e.name, s.name AS skill FROM employees e JOIN skills s ON e.id=s.employee_id"
                if terms:
                    sql += (
                        " WHERE lower(s.name) IN ("
                        + ",".join(
                            "'" + t.lower().replace("'", "''") + "'"
                            for t in sorted(set(terms))
                        )
                        + ")"
                    )
            elif "assign" in q or "my project" in q:
                sql = "SELECT e.name, p.name AS project, ep.role_on_project FROM employee_projects ep JOIN employees e ON e.id=ep.employee_id JOIN projects p ON p.id=ep.project_id"
            elif "project" in q:
                sql = "SELECT id,name,status FROM projects" + (
                    " WHERE status='ONGOING'" if "ongoing" in q else ""
                )
            elif "employee" in q or "team" in q:
                sql = "SELECT id,name,department_id FROM employees"
            else:
                return {
                    "answer": "Try asking about projects, assignments, employees or skills. Flexible questions require AI_API_KEY.",
                    "rows": [],
                }
        rows = execute_safe(conn, sql)
        return {
            "answer": f"Found {len(rows)} rows within your {role.lower()} access scope (maximum 100).",
            "rows": rows,
            "sql": sql if role != "EMPLOYEE" else None,
        }
    finally:
        conn.close()
