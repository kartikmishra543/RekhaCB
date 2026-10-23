import json
import re
import secrets
import sqlite3
import time
from pathlib import Path
import httpx
from .model import complete


def store():
    Path("storage").mkdir(exist_ok=True)
    c = sqlite3.connect("storage/copilot.db")
    c.execute(
        "CREATE TABLE IF NOT EXISTS pending(id TEXT PRIMARY KEY, user_id INTEGER, plan TEXT, expires REAL, used INTEGER DEFAULT 0)"
    )
    c.execute(
        "CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY,user_id INTEGER,role TEXT,intent TEXT,status TEXT,tool TEXT,message TEXT,records TEXT,created REAL)"
    )
    return c


def audit(user, intent, result, message):
    safe = (
        "[sensitive request redacted]"
        if re.search(
            r"password|bank|salary|salaries|pan|token|secret|bearer", message, re.I
        )
        else re.sub(r"\S+@\S+|\b\d{6,}\b", "[redacted]", message)
    )
    record = result.get("result")
    ids = (
        [record["id"]]
        if isinstance(record, dict) and isinstance(record.get("id"), int)
        else []
    )
    with store() as c:
        c.execute(
            "INSERT INTO audit(user_id,role,intent,status,tool,message,records,created) VALUES(?,?,?,?,?,?,?,?)",
            (
                user.id,
                user.role.value,
                intent,
                result.get("status", "ok"),
                result.get("tool"),
                safe,
                json.dumps(ids),
                time.time(),
            ),
        )


async def action(user, message, confirmation, token, db=None):
    if confirmation:
        with store() as c:
            row = c.execute(
                "SELECT plan FROM pending WHERE id=? AND user_id=? AND expires>? AND used=0",
                (confirmation, user.id, time.time()),
            ).fetchone()
            if not row:
                return {
                    "answer": "This confirmation expired or was already used. Please prepare the action again.",
                    "status": "refused",
                }
            changed = c.execute(
                "UPDATE pending SET used=1 WHERE id=? AND used=0", (confirmation,)
            ).rowcount
            if not changed:
                return {"answer": "Action already submitted.", "status": "refused"}
        plan = json.loads(row[0])
    else:
        if "balance" in message.lower():
            plan = {"tool": "balance", "payload": {}}
        else:
            raw = await complete(
                'Extract an HR action as JSON {"tool":"leave|ticket|announcement|approve|reject|assign_project|create_project|assign_ticket|ticket_status","payload":{}}. Leave payload: leave_type SICK/CASUAL/EARNED, start_date and end_date YYYY-MM-DD, reason. Ticket: title,description,category IT/HR/ONBOARDING,priority LOW/MEDIUM/HIGH. Announcement: title,body. Approve/reject: request_id integer. assign_project: employee_id,project_id,role_on_project. create_project: name,description,status. assign_ticket: ticket_id,assignee_id. ticket_status: ticket_id,status OPEN/IN_PROGRESS/RESOLVED. Do not invent missing dates or IDs; return {"tool":"clarify"} if missing.',
                message,
            )
            if raw:
                try:
                    plan = json.loads(raw)
                except (ValueError, TypeError):
                    return {
                        "answer": "I could not extract a valid action. Please rephrase.",
                        "status": "clarify",
                    }
            else:
                dates = re.findall(r"\d{4}-\d{2}-\d{2}", message)
                q = message.lower()
                if "leave" in q and ("apply" in q or "request" in q) and dates:
                    leave_types = set(re.findall(r"\b(sick|casual|earned)\s+leave\b", q))
                    if len(leave_types) != 1:
                        return {
                            "answer": "Please specify one leave type: sick, casual or earned leave.",
                            "status": "clarify",
                        }
                    plan = {
                        "tool": "leave",
                        "payload": {
                            "leave_type": leave_types.pop().upper(),
                            "start_date": dates[0],
                            "end_date": dates[-1],
                            "reason": message,
                        },
                    }
                elif "ticket" in q and "create" in q:
                    plan = {
                        "tool": "ticket",
                        "payload": {
                            "title": message[:180],
                            "description": message,
                            "category": "IT",
                            "priority": "MEDIUM",
                        },
                    }
                elif "announcement" in q and "create" in q:
                    plan = {
                        "tool": "announcement",
                        "payload": {"title": message[:180], "body": message},
                    }
                elif (
                    "assign" in q and "project" in q and len(re.findall(r"\d+", q)) >= 2
                ):
                    numbers = re.findall(r"\d+", q)
                    plan = {
                        "tool": "assign_project",
                        "payload": {
                            "employee_id": int(numbers[0]),
                            "project_id": int(numbers[1]),
                            "role_on_project": "Contributor",
                        },
                    }
                elif re.search(r"(approve|reject).*\d+", q):
                    plan = {
                        "tool": "approve" if "approve" in q else "reject",
                        "payload": {"request_id": int(re.search(r"\d+", q)[0])},
                    }
                else:
                    return {
                        "answer": "Please include the task details. Example: Apply sick leave from 2026-10-22 to 2026-10-23 because of fever.",
                        "status": "clarify",
                    }
    if confirmation and plan.get("requires_readiness"):
        from .readiness import LeavePlan, analyze_leave

        current = await analyze_leave(db, user, LeavePlan(**plan["payload"]))
        if not current["can_prepare"]:
            return {
                "answer": "Your leave facts changed. Reopen Request Readiness and resolve the blocking checks.",
                "status": "rejected",
                "tool": "leave",
            }
    tool = plan.get("tool")
    if tool not in {
        "balance",
        "leave",
        "ticket",
        "announcement",
        "approve",
        "reject",
        "assign_project",
        "create_project",
        "assign_ticket",
        "ticket_status",
    }:
        return {
            "answer": "I need more details, or this action is not supported. Use the regular HRMS screen for other tasks.",
            "status": "clarify",
        }
    if (
        tool
        in {
            "announcement",
            "approve",
            "reject",
            "assign_project",
            "create_project",
            "assign_ticket",
            "ticket_status",
        }
        and user.role.value == "EMPLOYEE"
    ):
        return {"answer": "Your role cannot perform this action.", "status": "refused"}
    if tool == "create_project" and user.role.value != "ADMIN":
        return {
            "answer": "Only an admin can create projects through the copilot.",
            "status": "refused",
        }
    if not confirmation and tool != "balance":
        key = secrets.token_urlsafe(24)
        with store() as c:
            c.execute(
                "INSERT INTO pending(id,user_id,plan,expires) VALUES(?,?,?,?)",
                (key, user.id, json.dumps(plan), time.time() + 300),
            )
        return {
            "answer": "Review these details before submitting. This confirmation is valid for five minutes.",
            "status": "confirmation_required",
            "confirmation_id": key,
            "preview": plan,
            "tool": tool,
        }
    paths = {
        "balance": ("GET", "/leaves/balances/me"),
        "leave": ("POST", "/leaves/requests"),
        "ticket": ("POST", "/tickets"),
        "announcement": ("POST", "/announcements"),
    }
    payload = plan.get("payload", {})
    if tool == "assign_project":
        payload = dict(payload)
        employee_id = int(payload.pop("employee_id", 0))
        method, path = "POST", f"/employees/{employee_id}/projects"
    elif tool == "create_project":
        method, path = "POST", "/employees/projects/catalog"
    elif tool in {"assign_ticket", "ticket_status"}:
        payload = dict(payload)
        ticket_id = int(payload.pop("ticket_id", 0))
        method, path = (
            "POST",
            f"/tickets/{ticket_id}/{'assign' if tool == 'assign_ticket' else 'status'}",
        )
    elif tool in {"approve", "reject"}:
        request_id = int(payload.get("request_id", 0))
        method, path = "POST", f"/leaves/requests/{request_id}/{tool}"
        payload = {}
    else:
        method, path = paths[tool]
    # ASGI transport uses the real authenticated route and service validation.
    from app.main import app

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://internal"
    ) as client:
        response = await client.request(
            method,
            "/api/v1" + path,
            headers={"Authorization": "Bearer " + token},
            json=payload if method != "GET" else None,
        )
    if response.status_code >= 400:
        return {
            "answer": "The HR API rejected the request. Check dates, balance, ownership and required fields in the HRMS screen.",
            "status": "rejected",
            "tool": tool,
        }
    return {
        "answer": (
            "Leave balance retrieved."
            if tool == "balance"
            else "The HR API completed your request."
        ),
        "result": response.json().get("data"),
        "tool": tool,
        "status": "completed",
    }
