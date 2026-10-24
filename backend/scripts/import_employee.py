"""Import one private local employee JSON through the existing admin-only API.

From backend: python scripts/import_employee.py --profile storage/employee_profile.private.json
No server is needed. The configured local database must already be migrated.
"""
import argparse
import asyncio
import getpass
import json
from pathlib import Path
from sqlalchemy import select
import httpx
from app.main import app
from app.db.session import SessionLocal
from app.models.department import Department
from app.schemas.employee import EmployeeCreate


async def import_profile(path, admin_email, admin_password):
    raw = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    department_name = raw.pop("department", None)
    if "password" not in raw:
        raw["password"] = getpass.getpass("New employee temporary password: ")
    if department_name:
        async with SessionLocal() as db:
            department = (await db.execute(select(Department).where(Department.name == department_name))).scalar_one_or_none()
            if department is None:
                raise ValueError("Department not found; create it in the HRMS first.")
            raw["department_id"] = department.id
    payload = EmployeeCreate.model_validate(raw).model_dump(mode="json")
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://internal") as client:
        auth = await client.post("/api/v1/auth/login", json={"email": admin_email, "password": admin_password})
        if auth.status_code != 200:
            raise ValueError("Admin sign-in failed.")
        token = auth.json()["data"]["access_token"]
        response = await client.post("/api/v1/employees", headers={"Authorization": "Bearer " + token}, json=payload)
        if response.status_code == 409:
            raise ValueError("An active employee already uses this email; no changes were made.")
        if response.status_code >= 400:
            raise ValueError("Import rejected by the HR API. Review the profile fields and admin permissions.")
        return response.json()["data"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--admin-email", default="admin@mock-hrms.dev")
    args = parser.parse_args()
    password = getpass.getpass("HRMS admin password: ")
    try:
        employee = asyncio.run(import_profile(args.profile, args.admin_email, password))
        print("Employee imported successfully. Open the Employees screen to review the profile.")
    except Exception:
        print("Import failed. Check the JSON fields, department, admin credentials and migrated database. No private field values are printed.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
