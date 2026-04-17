import re
from typing import Any, Dict, Optional, Tuple


def _extract_amount_kes(text: str) -> Optional[int]:
    # Examples: "KES 15,000", "KSh15000"
    # If commas are present, require at least one comma group so we don't stop at 1-3 digits.
    m = re.search(
        r"(?:KES|KSh|KSH)\s*([0-9]{1,3}(?:,[0-9]{3})+|[0-9]+)",
        text,
        re.I,
    )
    if not m:
        return None
    raw = m.group(1).replace(",", "")
    try:
        return int(raw)
    except ValueError:
        return None


def _extract_location_after_in_or_at(text: str) -> Optional[str]:
    # Very lightweight: "in Kisumu", "at Westlands"
    m = re.search(r"\b(?:in|at)\s+([A-Za-z][A-Za-z\s-]{1,40})", text, re.I)
    if not m:
        return None
    loc = m.group(1).strip()
    # Avoid capturing common filler
    loc = re.sub(r"\s+(urgently|asap|immediately|please)\b", "", loc, flags=re.I).strip()
    return loc or None


def _extract_urgency(text: str) -> Optional[str]:
    if re.search(r"\burgent|urgently|asap|immediately|right now|tonight\b", text, re.I):
        return "urgent"
    if re.search(r"\bsoon\b", text, re.I):
        return "soon"
    return None


def _extract_document_type(text: str) -> Optional[str]:
    t = text.lower()
    if "land title" in t or "land title deed" in t or "title deed" in t:
        return "land_title_deed"
    if "id" in t:
        return "id"
    if "certificate" in t:
        return "certificate"
    return None


def _extract_scheduled_date_time(text: str) -> Tuple[Optional[str], Optional[str]]:
    # date: "Friday", "Saturday", "Monday"
    day_match = re.search(
        r"\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b", text, re.I
    )
    # time: "10am", "9:30pm", "14:00"
    time_match = re.search(r"\b([0-1]?\d(?::[0-5]\d)?\s?(?:am|pm)?)\b", text, re.I)
    date = day_match.group(1) if day_match else None
    time = time_match.group(1) if time_match else None
    return date, time


def detect_intent(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ["send", "transfer", "money", "kes", "ksh"]):
        return "send_money"
    if any(k in t for k in ["airport", "pickup", "dropoff", "drop", "arrival"]):
        return "get_airport_transfer"
    if any(
        k in t
        for k in ["clean", "cleaner", "lawyer", "errand", "errand runner", "hire", "runner"]
    ):
        return "hire_service"
    if any(k in t for k in ["verify", "verification", "land title", "title deed", "id ", "certificate"]):
        return "verify_document"
    if any(k in t for k in ["status", "track", "follow up", "task code", "check status"]):
        return "check_status"
    # Default
    return "hire_service"


def extract_entities(intent: str, text: str) -> Dict[str, Any]:
    amount = _extract_amount_kes(text)
    urgency = _extract_urgency(text)
    location = _extract_location_after_in_or_at(text)
    doc_type = _extract_document_type(text)
    scheduled_date, scheduled_time = _extract_scheduled_date_time(text)

    # Task code reference (for check_status)
    task_code = None
    m = re.search(r"\b(VG-[0-9]{8}-[0-9]{5}|[A-Z]{2,3}-[0-9]{6,})\b", text)
    if m:
        task_code = m.group(1)

    entities: Dict[str, Any] = {
        "amount_kes": None,
        "recipient_name": None,
        "recipient_location": None,
        "recipient_bank_or_method": None,
        "urgency": None,
        "pickup_location": None,
        "arrival_time": None,
        "passenger_name": None,
        "vehicle_type": None,
        "service_type": None,
        "location": None,
        "scheduled_date": None,
        "scheduled_time": None,
        "document_type": None,
        "document_reference": None,
        "task_code": task_code,
        "reference": None,
    }

    if intent == "send_money":
        entities["amount_kes"] = amount
        entities["recipient_location"] = location
        entities["urgency"] = urgency
    elif intent == "get_airport_transfer":
        entities["pickup_location"] = location
        # arrival time is too hard to reliably parse; keep null unless present
        entities["arrival_time"] = None
        entities["urgency"] = urgency
    elif intent == "hire_service":
        entities["service_type"] = (
            "cleaner" if "clean" in text.lower() or "cleaner" in text.lower() else None
        )
        entities["location"] = location
        entities["scheduled_date"] = scheduled_date
        entities["scheduled_time"] = scheduled_time
        entities["urgency"] = urgency
    elif intent == "verify_document":
        entities["document_type"] = doc_type
        entities["location"] = location
        entities["urgency"] = urgency
    elif intent == "check_status":
        entities["task_code"] = task_code
        entities["reference"] = None

    # Convert "soon" into a normalized label.
    if entities.get("urgency") == "soon":
        entities["urgency"] = "urgent"

    return entities

