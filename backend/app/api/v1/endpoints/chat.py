from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.auth import get_current_user, oauth2_scheme
from app.models.employee import Employee
from app.services.ai.policy_rag import answer_policy
from app.services.ai.sql_agent import query_hr
from app.services.ai.actions import action, audit, store

router = APIRouter()


class ChatInput(BaseModel):
    message: str = Field(default="Confirm", min_length=1, max_length=4000)
    confirmation_id: str | None = Field(default=None, max_length=100)


def route(message):
    q = message.lower()
    if any(
        x in q
        for x in (
            "apply",
            "create",
            "approve",
            "reject",
            "balance",
            "assign employee",
            "assign ticket",
            "update ticket",
        )
    ):
        return "actions"
    if any(
        x in q
        for x in ("policy", "entitled", "how many sick", "half-day", "work from home")
    ):
        return "policy"
    if any(
        x in q
        for x in ("project", "employee", "skill", "team", "salary", "salaries", "bank")
    ):
        return "sql"
    return "policy"


async def run(kind, payload, user, db, token):
    try:
        if kind == "policy":
            result = await answer_policy(db, payload.message)
        elif kind == "sql":
            result = await query_hr(db, user, payload.message)
        else:
            result = await action(
                user, payload.message, payload.confirmation_id, token, db=db
            )
    except Exception:
        result = {
            "answer": "The copilot could not complete this request. Check server configuration or try again.",
            "status": "error",
        }
    result["route"] = kind
    audit(user, kind, result, payload.message)
    return {"success": result.get("status") != "error", "data": result, "error": None}


@router.post("/{kind}")
async def chat(
    kind: str,
    payload: ChatInput,
    user: Employee = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    if kind not in {"policy", "sql", "actions", "router"}:
        from fastapi import HTTPException

        raise HTTPException(404, "Unknown copilot endpoint")
    return await run(
        (
            route(payload.message)
            if kind == "router" and not payload.confirmation_id
            else "actions" if payload.confirmation_id else kind
        ),
        payload,
        user,
        db,
        token,
    )


@router.get("/audit/recent")
async def recent(user: Employee = Depends(get_current_user)):
    with store() as c:
        rows = c.execute(
            "SELECT intent,status,tool,created FROM audit WHERE user_id=? ORDER BY id DESC LIMIT 20",
            (user.id,),
        ).fetchall()
    return {
        "success": True,
        "data": [dict(zip(["intent", "status", "tool", "created"], r)) for r in rows],
        "error": None,
    }
