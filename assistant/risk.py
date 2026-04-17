from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class RiskContext:
    intent: str
    entities: Dict[str, Any]
    completion_ratio: float


def clamp_int(x: int, lo: int = 0, hi: int = 100) -> int:
    return max(lo, min(hi, x))


def score_risk(ctx: RiskContext) -> int:
    """
    Deterministic risk score based on diaspora context factors.

    Output:
      Integer score in range [0..100].
    """

    intent = ctx.intent
    e = ctx.entities or {}

    score = 10  # baseline uncertainty

    urgency = (e.get("urgency") or "").lower()
    if urgency in {"urgent", "asap", "immediately"}:
        score += 20

    # Returning / clean history: reduce uncertainty.
    # completion_ratio is computed on customer_id history.
    if ctx.completion_ratio > 0.7:
        score -= 15
    elif ctx.completion_ratio < 0.3 and ctx.completion_ratio != 0:
        score += 10
    # completion_ratio == 0 => neutral

    if intent == "send_money":
        amount = e.get("amount_kes")
        if isinstance(amount, int):
            if amount >= 100_000:
                score += 30
            elif amount >= 50_000:
                score += 20
            elif amount >= 20_000:
                score += 10
        else:
            score += 10

        if not e.get("recipient_name"):
            score += 15
        if not e.get("recipient_location") and not e.get("recipient_bank_or_method"):
            score += 10
        if not e.get("recipient_bank_or_method") and e.get("recipient_location"):
            # location alone still leaves recipient method unclear
            score += 10

    elif intent == "get_airport_transfer":
        if not e.get("pickup_location"):
            score += 15
        if not e.get("arrival_time"):
            score += 15
        if e.get("pickup_location") and e.get("arrival_time"):
            score += 0

    elif intent == "hire_service":
        if not e.get("service_type"):
            score += 10
        if not e.get("location"):
            score += 10
        if not e.get("scheduled_date"):
            score += 20

    elif intent == "verify_document":
        doc_type = (e.get("document_type") or "").lower()
        if not e.get("document_type"):
            score += 15
        elif "land_title" in doc_type or "title" in doc_type:
            score += 40
        else:
            score += 25

        if e.get("location") is None:
            score += 10
        if not e.get("document_reference"):
            # unknown doc reference increases uncertainty
            score += 10

    elif intent == "check_status":
        if not e.get("task_code"):
            score += 20
        # status checks are usually low risk by nature
        score += 5

    return clamp_int(int(score))

