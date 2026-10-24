import json
import secrets
import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.employee import Employee
from app.services.auth import get_current_user
from app.services.ai.readiness import LeavePlan, analyze_leave
from app.services.ai.actions import audit
from app.services.ai import actions

from app.services.ai.privacy import load_private_values, redact_text


async def check_private_reason(plan, db):
    if redact_text(plan.reason, await load_private_values(db)) != plan.reason:
        raise HTTPException(400, "Remove private identifiers or credentials from the leave reason.")


router = APIRouter()


@router.post("/analyze")
async def analyze(
    plan: LeavePlan,
    user: Employee = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_private_reason(plan, db)
    result = await analyze_leave(db, user, plan)
    audit(
        user,
        "readiness",
        {"status": result["status"], "tool": "leave_readiness"},
        "Leave readiness review",
    )
    return {"success": True, "data": result, "error": None}


@router.post("/prepare")
async def prepare(
    plan: LeavePlan,
    user: Employee = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_private_reason(plan, db)
    result = await analyze_leave(db, user, plan)
    if not result["can_prepare"]:
        audit(
            user,
            "readiness",
            {"status": "blocked", "tool": "leave_readiness"},
            "Blocked leave preparation",
        )
        return {
            "success": False,
            "data": result,
            "error": {
                "code": "READINESS_BLOCKED",
                "message": "Resolve blocking checks first.",
            },
        }
    proposal = {
        "tool": "leave",
        "payload": plan.model_dump(mode="json"),
        "requires_readiness": True,
    }
    key = secrets.token_urlsafe(24)
    with actions.store() as c:
        c.execute(
            "INSERT INTO pending(id,user_id,plan,expires) VALUES(?,?,?,?)",
            (key, user.id, json.dumps(proposal), time.time() + 300),
        )
    audit(
        user,
        "readiness",
        {"status": "confirmation_required", "tool": "leave"},
        "Prepared leave after readiness review",
    )
    return {
        "success": True,
        "data": {
            "answer": "Your checked request is prepared. Review and confirm to submit it.",
            "status": "confirmation_required",
            "confirmation_id": key,
            "preview": proposal,
            "readiness": result,
        },
        "error": None,
    }
