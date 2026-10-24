"""Deterministic checks around untrusted requests and model output.

These are defense in depth. Backend API authorization and the scoped SQL
projection remain the security boundary; regex checks do not prove grounding.
"""
import re
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field
from datetime import date
from pydantic import model_validator

PositiveID = Annotated[int, Field(strict=True, gt=0)]


class Payload(BaseModel):
    model_config = ConfigDict(extra="forbid")


class LeavePayload(Payload):
    leave_type: Literal["SICK", "CASUAL", "EARNED"]
    start_date: date
    end_date: date
    reason: str = Field(min_length=3, max_length=500)
    is_half_day: bool = False
    half_day_period: Literal["FIRST_HALF", "SECOND_HALF"] | None = None

    @model_validator(mode="after")
    def valid_dates(self):
        from .readiness import LeavePlan
        LeavePlan(**self.model_dump())
        return self


class TicketPayload(Payload):
    title: str = Field(min_length=3, max_length=180)
    description: str = Field(min_length=5, max_length=5000)
    category: Literal["IT", "HR", "ONBOARDING"]
    priority: Literal["LOW", "MEDIUM", "HIGH"]


class AnnouncementPayload(Payload):
    title: str = Field(min_length=3, max_length=180)
    body: str = Field(min_length=3, max_length=10000)


class DecisionPayload(Payload):
    request_id: PositiveID


class AssignmentPayload(Payload):
    employee_id: PositiveID
    project_id: PositiveID
    role_on_project: str | None = Field(default=None, min_length=2, max_length=120)


class ProjectPayload(Payload):
    name: str = Field(min_length=3, max_length=180)
    description: str | None = Field(default=None, max_length=1000)
    status: Literal["ONGOING", "COMPLETED", "ON_HOLD", "PLANNED"] = "ONGOING"


class TicketAssignmentPayload(Payload):
    ticket_id: PositiveID
    assignee_id: PositiveID


class TicketStatusPayload(Payload):
    ticket_id: PositiveID
    status: Literal["OPEN", "IN_PROGRESS", "RESOLVED"]


TOOLS = {
    "balance": Payload, "leave": LeavePayload, "ticket": TicketPayload,
    "announcement": AnnouncementPayload, "approve": DecisionPayload,
    "reject": DecisionPayload, "assign_project": AssignmentPayload,
    "create_project": ProjectPayload, "assign_ticket": TicketAssignmentPayload,
    "ticket_status": TicketStatusPayload,
}


def validate_action(plan, stored=False):
    if not isinstance(plan, dict) or not isinstance(plan.get("tool"), str):
        raise ValueError("An action object with a supported tool is required")
    allowed = {"tool", "payload"} | ({"requires_readiness"} if stored else set())
    if set(plan) - allowed or plan["tool"] not in TOOLS:
        raise ValueError("Unsupported tool or action fields")
    payload = TOOLS[plan["tool"]].model_validate(plan.get("payload", {}))
    result = {"tool": plan["tool"], "payload": payload.model_dump(mode="json")}
    if stored and plan.get("requires_readiness") is True:
        result["requires_readiness"] = True
    return result


def blocked_instruction(message):
    return bool(re.search(
        r"ignore\s+(?:(?:all|the|your|previous|above|prior)\s+)*instructions|"
        r"(?:reveal|print|show|expose)\s+(?:the\s+)?(?:system prompt|api key|jwt secret|access token)|"
        r"bypass\s+(?:the\s+)?(?:permissions|authorization|guardrails)|"
        r"(?:act|pretend)\s+as\s+(?:an?\s+)?admin",
        message, re.I,
    ))


def acceptable_policy_answer(answer, source_count):
    if not isinstance(answer, str) or not answer.strip() or len(answer) > 12000:
        return False
    citations = re.findall(r"\[(\d+)\]", answer)
    if not citations or any(not 1 <= int(n) <= source_count for n in citations):
        return False
    return not re.search(
        r"\bsk-[A-Za-z0-9_-]{20,}|\bgh[pousr]_[A-Za-z0-9]{20,}|"
        r"\b[A-Z]{5}[0-9]{4}[A-Z]\b|-----BEGIN .*PRIVATE KEY-----",
        answer,
    )
