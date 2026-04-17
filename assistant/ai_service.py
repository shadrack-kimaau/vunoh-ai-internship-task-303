import json
import os
from typing import Any, Dict, List, Optional, Tuple

from .ai_client import chat_completion_json_only, get_ai_config
from .heuristics import detect_intent, extract_entities


ALLOWED_INTENTS = [
    "send_money",
    "get_airport_transfer",
    "hire_service",
    "verify_document",
    "check_status",
]

EXPECTED_ENTITY_KEYS = [
    "amount_kes",
    "recipient_name",
    "recipient_location",
    "recipient_bank_or_method",
    "urgency",
    "pickup_location",
    "arrival_time",
    "passenger_name",
    "vehicle_type",
    "service_type",
    "location",
    "scheduled_date",
    "scheduled_time",
    "document_type",
    "document_reference",
    "task_code",
    "reference",
]


def _normalize_entities(intent: str, entities: Dict[str, Any]) -> Dict[str, Any]:
    e = dict(entities or {})

    # Ensure all expected keys exist for downstream stability.
    for k in EXPECTED_ENTITY_KEYS:
        e.setdefault(k, None)

    # Normalize amount_kes -> int | None.
    amount = e.get("amount_kes")
    if isinstance(amount, str):
        # remove commas like "15,000"
        cleaned = amount.replace(",", "").strip()
        if cleaned.isdigit():
            e["amount_kes"] = int(cleaned)
        else:
            e["amount_kes"] = None
    elif isinstance(amount, float):
        e["amount_kes"] = int(amount)
    elif not isinstance(amount, (int, type(None))):
        e["amount_kes"] = None

    # Normalize urgency -> "urgent" | None
    urgency = e.get("urgency")
    if isinstance(urgency, str):
        u = urgency.lower().strip()
        e["urgency"] = "urgent" if u in {"urgent", "asap", "immediately"} else (None if u else None)
    else:
        e["urgency"] = None

    # For check_status, allow task_code in entities.
    if intent == "check_status":
        tc = e.get("task_code")
        e["task_code"] = str(tc).strip() if tc else None

    return e


def build_extraction_prompts() -> Tuple[str, str]:
    system_prompt = """
You are a structured intent extraction engine for a Kenyan diaspora assistant.
Return ONLY valid JSON (no markdown, no extra keys, no commentary).

Allowed intents:
- send_money
- get_airport_transfer
- hire_service
- verify_document
- check_status

You must output an object with:
{
  "intent": one of the allowed intents,
  "entities": {
    // include ALL keys below with value null when unknown
    "amount_kes": number|null,
    "recipient_name": string|null,
    "recipient_location": string|null,
    "recipient_bank_or_method": string|null,
    "urgency": string|null,

    "pickup_location": string|null,
    "arrival_time": string|null,
    "passenger_name": string|null,
    "vehicle_type": string|null,

    "service_type": string|null,
    "location": string|null,
    "scheduled_date": string|null,
    "scheduled_time": string|null,

    "document_type": string|null,
    "document_reference": string|null,

    "task_code": string|null,
    "reference": string|null
  }
}

Rules:
- amount_kes must be numeric (no commas).
- urgency should be one of: "urgent" only when user indicates urgent/asap/immediately; otherwise null.
- If the user mentions a task code like VG-YYYYMMDD-xxxxx, set entities.task_code.
""".strip()

    user_prompt = """
Extract intent and entities from this customer request:
\"\"\"{customer_request}\"\"\"
""".strip()

    return system_prompt, user_prompt


def build_steps_prompts() -> Tuple[str, str]:
    system_prompt = """
You are generating a logical step plan for fulfilling a diaspora assistant task.
Return ONLY valid JSON (no markdown).

Output format:
{
  "steps": [
    {"step_order": 1, "step_text": "..." },
    {"step_order": 2, "step_text": "..." }
  ]
}

Rules:
- steps must be ordered and actionable
- steps should be specific enough to show in a dashboard
- generate 4 to 7 steps depending on intent
""".strip()

    user_prompt = """
Task:
Intent: {intent}
Entities: {entities_json}
Task code: {task_code}

Generate the step plan.
""".strip()

    return system_prompt, user_prompt


def build_messages_prompts() -> Tuple[str, str]:
    system_prompt = """
You are generating confirmation messages for three different channels.
Return ONLY valid JSON (no markdown).

Output format:
{
  "whatsapp": "string",
  "email": {"subject": "string", "body": "string"},
  "sms": "string"
}

Rules:
- WhatsApp message should be conversational and concise, with natural line breaks.
- Email should be formal and structured, and must include the task code and key details.
- SMS must be <=160 characters. It must include the task code and the key next action only.
""".strip()

    user_prompt = """
Create messages for this task.
Intent: {intent}
Entities: {entities_json}
Task code: {task_code}

Generate messages.
""".strip()

    return system_prompt, user_prompt


def _has_ai_key() -> bool:
    api_key, _, _ = get_ai_config()
    return bool(api_key)


def extract_intent_entities(customer_request: str) -> Dict[str, Any]:
    if not _has_ai_key():
        intent = detect_intent(customer_request)
        entities = extract_entities(intent, customer_request)
        return {"intent": intent, "entities": _normalize_entities(intent, entities)}

    system_prompt, user_prompt_tpl = build_extraction_prompts()
    user_prompt = user_prompt_tpl.format(customer_request=customer_request)

    # Retry once if JSON parsing fails.
    for attempt in range(2):
        try:
            parsed = chat_completion_json_only(system_prompt, user_prompt)
            intent = parsed.get("intent")
            entities = parsed.get("entities") or {}
            if intent not in ALLOWED_INTENTS:
                raise ValueError("Invalid intent from AI")
            return {"intent": intent, "entities": _normalize_entities(intent, entities)}
        except Exception:
            if attempt == 1:
                # Fallback to heuristics
                intent = detect_intent(customer_request)
                entities = extract_entities(intent, customer_request)
                return {"intent": intent, "entities": _normalize_entities(intent, entities)}
            # On retry, tell it to output JSON only.
            user_prompt = user_prompt + "\nReturn ONLY valid JSON; no other text."

    raise RuntimeError("Unreachable")


def generate_steps(intent: str, entities: Dict[str, Any], task_code: str) -> List[Dict[str, Any]]:
    def fallback() -> List[Dict[str, Any]]:
        base = 1
        if intent == "send_money":
            steps = [
                {"step_order": base, "step_text": "Confirm recipient details (name/location)."},
                {"step_order": base + 1, "step_text": "Verify urgency and amount for the transfer."},
                {"step_order": base + 2, "step_text": "Run identity checks for the requester and recipient."},
                {"step_order": base + 3, "step_text": "Initiate the transfer and share confirmation."},
                {"step_order": base + 4, "step_text": "Provide final status update to you."},
            ]
        elif intent == "hire_service":
            steps = [
                {"step_order": base, "step_text": "Confirm service type and location details."},
                {"step_order": base + 1, "step_text": "Match with available local service providers."},
                {"step_order": base + 2, "step_text": "Schedule at your requested date/time."},
                {"step_order": base + 3, "step_text": "Share provider confirmation and instructions."},
                {"step_order": base + 4, "step_text": "Collect sign-off when service is complete."},
            ]
        elif intent == "verify_document":
            steps = [
                {"step_order": base, "step_text": "Confirm the document type and reference you provided."},
                {"step_order": base + 1, "step_text": "Validate ownership/format requirements for verification."},
                {"step_order": base + 2, "step_text": "Perform verification checks and validate relevant records."},
                {"step_order": base + 3, "step_text": "Return results with next actions (if any)."},
            ]
        elif intent == "get_airport_transfer":
            steps = [
                {"step_order": base, "step_text": "Confirm pickup location and arrival details."},
                {"step_order": base + 1, "step_text": "Assign an available driver/partner for the trip."},
                {"step_order": base + 2, "step_text": "Share confirmation and pickup instructions."},
                {"step_order": base + 3, "step_text": "Confirm completion of the transfer."},
            ]
        else:
            steps = [
                {"step_order": base, "step_text": "Locate your task using the task code."},
                {"step_order": base + 1, "step_text": "Confirm your provided reference matches the task code."},
                {"step_order": base + 2, "step_text": "Retrieve the latest saved status from the system."},
                {"step_order": base + 3, "step_text": "Send you the latest update and next recommended action."},
            ]

        for i, s in enumerate(steps, start=1):
            s["step_order"] = i
        return steps

    if not _has_ai_key():
        return fallback()

    system_prompt, user_prompt_tpl = build_steps_prompts()
    user_prompt = user_prompt_tpl.format(
        intent=intent, entities_json=json.dumps(entities or {}), task_code=task_code
    )

    for attempt in range(2):
        try:
            parsed = chat_completion_json_only(system_prompt, user_prompt)
            steps = parsed.get("steps") or []
            normalized: List[Dict[str, Any]] = []
            for s in steps:
                if not isinstance(s, dict):
                    continue
                normalized.append(
                    {
                        "step_order": int(s.get("step_order")),
                        "step_text": str(s.get("step_text") or "").strip(),
                    }
                )
            normalized.sort(key=lambda x: x["step_order"])
            # ensure between 4 and 7
            if not normalized:
                raise ValueError("AI returned no steps")
            return normalized
        except Exception:
            if attempt == 1:
                return fallback()
            user_prompt = user_prompt + "\nReturn ONLY valid JSON; no other text."

    return fallback()


def generate_messages(intent: str, entities: Dict[str, Any], task_code: str) -> Dict[str, Any]:
    def fallback() -> Dict[str, Any]:
        whatsapp = (
            f"Hi! We received your request.\nTask code: {task_code}\n"
            f"We will handle it shortly. ✅"
        )
        subject = f"Vunoh Global - Task {task_code} created"
        body = (
            "Hello,\n\n"
            "Your request has been received and a task has been created.\n"
            f"Task code: {task_code}\nIntent: {intent}\n\n"
            "We’ll update you as the steps progress.\n"
        )
        sms = (
            f"{task_code}: we started your {intent.replace('_', ' ')} request. "
            "Reply for updates."
        )
        if len(sms) > 160:
            sms = sms[:157] + "..."
        return {
            "whatsapp": whatsapp,
            "email": {"subject": subject, "body": body},
            "sms": sms,
        }

    if not _has_ai_key():
        return fallback()

    system_prompt, user_prompt_tpl = build_messages_prompts()
    user_prompt = user_prompt_tpl.format(
        intent=intent, entities_json=json.dumps(entities or {}), task_code=task_code
    )

    for attempt in range(2):
        try:
            parsed = chat_completion_json_only(system_prompt, user_prompt)
            whatsapp = str(parsed.get("whatsapp") or "").strip()
            email = parsed.get("email") or {}
            sms = str(parsed.get("sms") or "").strip()
            subject = str(email.get("subject") or "").strip() or f"Vunoh Global - Task {task_code}"
            body = str(email.get("body") or "").strip() or whatsapp

            # Enforce SMS length.
            if len(sms) > 160:
                # Keep task code and truncate.
                sms_prefix = sms
                if len(sms_prefix) > 160:
                    sms = sms_prefix[:157] + "..."

            if not whatsapp or not sms:
                raise ValueError("AI returned empty fields")
            return {"whatsapp": whatsapp, "email": {"subject": subject, "body": body}, "sms": sms}
        except Exception:
            if attempt == 1:
                return fallback()
            user_prompt = user_prompt + "\nReturn ONLY valid JSON; no other text."

    return fallback()

