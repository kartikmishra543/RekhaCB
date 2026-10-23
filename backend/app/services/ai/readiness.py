"""Evidence-backed leave planning. Facts and checks, never an AI approval score."""

from datetime import date, datetime
from hashlib import sha256
from typing import Literal
import json
from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import select
from app.models.leave_balance import LeaveBalance
from app.models.leave_request import LeaveRequest
from app.models.enums import LeaveType, LeaveRequestStatus
from app.api.v1.endpoints.leaves import DEFAULT_LEAVE_TOTALS
from .policy_rag import answer_policy


class LeavePlan(BaseModel):
    leave_type: Literal["SICK", "CASUAL", "EARNED"] = "CASUAL"
    start_date: date
    end_date: date
    reason: str = Field(min_length=3, max_length=500)
    is_half_day: bool = False
    half_day_period: Literal["FIRST_HALF", "SECOND_HALF"] | None = None

    @model_validator(mode="after")
    def valid_range(self):
        if self.end_date < self.start_date:
            raise ValueError("End date must be on or after start date.")
        if (self.end_date - self.start_date).days > 365:
            raise ValueError("Please plan no more than one year at a time.")
        if self.is_half_day and (
            self.start_date != self.end_date or not self.half_day_period
        ):
            raise ValueError("Half-day leave needs one date and a first/second half.")
        if not self.is_half_day and self.half_day_period:
            raise ValueError("A half-day period is only valid for half-day leave.")
        return self


async def analyze_leave(db, user, plan: LeavePlan):
    requested = (
        0.5 if plan.is_half_day else float((plan.end_date - plan.start_date).days + 1)
    )
    balances = (
        (
            await db.execute(
                select(LeaveBalance)
                .where(
                    LeaveBalance.employee_id == user.id,
                    LeaveBalance.leave_type == LeaveType(plan.leave_type),
                )
                .order_by(LeaveBalance.id)
            )
        )
        .scalars()
        .all()
    )
    # Match the inherited balance API's duplicate repair semantics without writing.
    total = (
        max(float(b.total or 0) for b in balances)
        if balances
        else DEFAULT_LEAVE_TOTALS[LeaveType(plan.leave_type)]
    )
    used = max(float(b.used or 0) for b in balances) if balances else 0.0
    remaining = max(0.0, total - used)
    overlaps = (
        (
            await db.execute(
                select(LeaveRequest).where(
                    LeaveRequest.employee_id == user.id,
                    LeaveRequest.status.in_(
                        [LeaveRequestStatus.PENDING, LeaveRequestStatus.APPROVED]
                    ),
                    LeaveRequest.start_date <= plan.end_date,
                    LeaveRequest.end_date >= plan.start_date,
                )
            )
        )
        .scalars()
        .all()
    )
    pending = (
        (
            await db.execute(
                select(LeaveRequest).where(
                    LeaveRequest.employee_id == user.id,
                    LeaveRequest.leave_type == LeaveType(plan.leave_type),
                    LeaveRequest.status == LeaveRequestStatus.PENDING,
                )
            )
        )
        .scalars()
        .all()
    )
    pending_units = sum(
        0.5 if p.is_half_day else (p.end_date - p.start_date).days + 1 for p in pending
    )
    checks = []

    def add(key, state, title, detail):
        checks.append(dict(key=key, state=state, title=title, detail=detail))

    add(
        "balance",
        "pass" if requested <= remaining else "block",
        "Available balance",
        f"{requested:g} days requested; {remaining:g} days available. Days use the existing calendar-day rule, including weekends.",
    )
    add(
        "overlap",
        "block" if overlaps else "pass",
        "Existing requests",
        (
            f"{len(overlaps)} pending or approved requests overlap these dates."
            if overlaps
            else "No pending or approved request overlaps these dates."
        ),
    )
    today = datetime.now(ZoneInfo("Asia/Kolkata")).date()
    add(
        "past_dates",
        "warn" if plan.start_date < today else "pass",
        "Date review",
        (
            "These dates include past days. Confirm retrospective leave with HR."
            if plan.start_date < today
            else "The request starts today or later."
        ),
    )
    add(
        "pending",
        "warn" if requested + pending_units > remaining else "pass",
        "Pending commitments",
        f"{pending_units:g} days are already pending for this leave type. Pending requests do not reserve balance in the starter HRMS.",
    )
    approver = (
        "Automatically approved by the existing admin self-service API."
        if user.role.value == "ADMIN"
        else "A manager/admin must approve this request. Readiness is not approval."
    )
    add("approval", "info", "Approval path", approver)
    try:
        evidence = await answer_policy(
            db,
            "What is the leave policy for "
            + plan.leave_type.lower()
            + " leave and half-day leave?",
        )
    except Exception:
        evidence = {
            "answer": "Policy retrieval is temporarily unavailable. Verify entitlement with HR.",
            "sources": [],
        }
    add(
        "evidence",
        "pass" if evidence.get("sources") else "warn",
        "Policy evidence",
        (
            "Policy references are attached for review; eligibility still depends on HR rules."
            if evidence.get("sources")
            else "No supporting policy references were retrieved. Ask HR before relying on this plan."
        ),
    )
    blockers = sum(c["state"] == "block" for c in checks)
    warnings = sum(c["state"] == "warn" for c in checks)
    payload = plan.model_dump(mode="json")
    snapshot = {
        "employee_id": user.id,
        "plan": payload,
        "remaining": remaining,
        "pending_units": pending_units,
        "overlap_ids": [p.id for p in overlaps],
        "checks": checks,
        "evidence": evidence,
    }
    fingerprint = sha256(
        json.dumps(snapshot, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return {
        "status": "blocked" if blockers else "review" if warnings else "ready",
        "headline": (
            "Resolve the blocking checks first"
            if blockers
            else (
                "Review the warnings before continuing"
                if warnings
                else "Ready to prepare your request"
            )
        ),
        "plan": payload,
        "checks": checks,
        "impact": {
            "requested_days": requested,
            "available_days": remaining,
            "projected_days": remaining - requested,
            "pending_days": pending_units,
            "counting_rule": "calendar_days",
        },
        "evidence": evidence,
        "approval_path": approver,
        "receipt": {
            "fingerprint": fingerprint,
            "generated_at": datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),
            "scope": "Your leave only",
            "meaning": "Snapshot fingerprint for comparing reviews; not a signature or approval.",
        },
        "can_prepare": blockers == 0,
    }
