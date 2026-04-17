from __future__ import annotations


def assigned_team_for_intent(intent: str) -> str:
    """
    Deterministic mapping from intent to employee team.
    """

    if intent in {"send_money", "get_airport_transfer"}:
        return "FINANCE"
    if intent == "hire_service":
        return "OPERATIONS"
    if intent == "verify_document":
        return "LEGAL"
    if intent == "check_status":
        return "SUPPORT"
    # Safe default
    return "SUPPORT"

