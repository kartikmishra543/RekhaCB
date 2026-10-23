"""Explicitly labelled sample policy additions for reproducible capstone evaluation."""

import asyncio
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models.hr_policy import HRPolicy

TEXT = """# RekhaCB demonstration policy — fictional training company
## Leave
The sample annual allocation is 10 sick days, 12 casual days and 15 earned days. Available balances are authoritative and may differ after usage. A half-day request uses 0.5 days and must specify first or second half. Leave requires manager approval; admin self-service follows the existing auto-approval rule.
## Work from home
Work from home requires manager approval. Ask your manager before changing your work location.
## Attendance
Clock in before 9:30 AM on working days. A late clock-in is recorded as late. This document does not define salary deductions for lateness.
## Document uploads
Use My Documents for your own documents. Employees may delete only their OTHER document uploads. HR manages appointment, tax and payslip documents.
"""


async def main():
    async with SessionLocal() as db:
        title = "RekhaCB sample employee handbook"
        if not (
            await db.execute(select(HRPolicy).where(HRPolicy.title == title))
        ).scalar_one_or_none():
            db.add(
                HRPolicy(
                    title=title,
                    category="DEMO_HANDBOOK",
                    content=TEXT,
                    original_filename="rekhacb_sample_handbook.md",
                )
            )
            await db.commit()


if __name__ == "__main__":
    asyncio.run(main())
