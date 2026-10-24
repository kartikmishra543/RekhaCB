"""Privacy boundary for copilot text; never use this to authorize HR API access."""
from contextvars import ContextVar
from functools import lru_cache
import re
from sqlalchemy import select
from app.models.employee import Employee
from app.models.payroll_record import PayrollRecord

private_values = ContextVar("copilot_private_values", default=())


async def load_private_values(db):
    # Include nonstandard identifiers too: regex format checks alone miss them.
    values = set()
    rows = (await db.execute(select(
        Employee.hashed_password, Employee.bank_account_number, Employee.bank_ifsc,
        Employee.pan_number, Employee.phone, Employee.date_of_birth, Employee.pan_dob,
        Employee.current_salary_usd,
    ))).all()
    for row in rows:
        for value in row:
            if value is not None:
                values.add(str(value))
                if hasattr(value, "strftime"):
                    values.add(value.strftime("%d-%m-%Y"))
                if hasattr(value, "as_tuple"):
                    values.add(format(value.normalize(), "f"))
    for row in (await db.execute(select(PayrollRecord.pf_uan, PayrollRecord.esi_no))).all():
        values.update(str(value) for value in row if value)
    return tuple(sorted((v for v in values if len(v) >= 4), key=len, reverse=True))


@lru_cache(maxsize=8)
def _private_pattern(values):
    if not values:
        return None
    return re.compile(r"(?<!\w)(?:" + "|".join(re.escape(v) for v in values) + r")(?!\w)", re.I)


def redact_text(text, values=None):
    if not isinstance(text, str):
        return text
    pattern = _private_pattern(tuple(private_values.get() if values is None else values))
    if pattern:
        text = pattern.sub("[private]", text)
    text = re.sub(r"(?im)^.*\b(?:password|temporary password|api[_ ]?key|secret|bank account(?: number)?|pan(?: number)?|pf[_ ]?uan|esi(?: number|_no)?|ifsc)\s*[:=].*$", "[private]", text)
    patterns = [
        r"\bsk-[A-Za-z0-9_-]{12,}", r"\bgh[pousr]_[A-Za-z0-9]{12,}",
        r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+",
        r"\b[A-Z]{5}\d{4}[A-Z]\b", r"\b[A-Z]{4}0[A-Z0-9]{6}\b",
        r"\b\d{6,}\b", r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",
        r"(?<!\S)(?=\S*[A-Za-z])(?=\S*\d)(?=\S*[@#$%^&*!])\S{8,}",
        r"-----BEGIN .*?PRIVATE KEY-----[\s\S]*?-----END .*?PRIVATE KEY-----",
    ]
    for pattern in patterns:
        text = re.sub(pattern, "[private]", text, flags=re.I)
    return text


def redact_object(value, values=None):
    if isinstance(value, str):
        return redact_text(value, values)
    if isinstance(value, list):
        return [redact_object(v, values) for v in value]
    if isinstance(value, dict):
        return {k: redact_object(v, values) for k, v in value.items()}
    return value
