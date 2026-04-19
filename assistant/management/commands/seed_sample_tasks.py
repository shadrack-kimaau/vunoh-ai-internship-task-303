import random
from datetime import datetime
from zoneinfo import ZoneInfo

from django.core.management.base import BaseCommand
from django.db import transaction

from assistant.ai_service import extract_intent_entities, generate_messages, generate_steps
from assistant.assignment import assigned_team_for_intent
from assistant.models import StatusHistory, Task, TaskMessage, TaskStep
from assistant.risk import RiskContext, score_risk


SAMPLE_REQUESTS = [
    "I need to send KES 15,000 to my mother in Kisumu urgently.",
    "Please verify my land title deed for the plot in Karen.",
    "Can someone clean my apartment in Westlands on Friday at 10am?",
    "I need an airport pickup in Nairobi for arrival at 7pm tonight.",
    "What is the status of task VG-20260416-00001?",
]


def _unique_task_code() -> str:
    tz = ZoneInfo("Africa/Nairobi")
    now = datetime.now(tz)
    for _ in range(50):
        task_code = f"VG-{now.strftime('%Y%m%d')}-{random.randint(0, 99999):05d}"
        if not Task.objects.filter(task_code=task_code).exists():
            return task_code
    raise RuntimeError("Could not generate unique task code")


class Command(BaseCommand):
    help = "Seed at least five sample tasks with full data (entities/steps/messages/history)."

    def add_arguments(self, parser):
        parser.add_argument("--client-id", default="sample_client_001")
        parser.add_argument("--min", type=int, default=5)

    def handle(self, *args, **options):
        client_id = str(options["client_id"])
        min_count = int(options["min"])

        existing = Task.objects.count()
        to_create = max(0, min_count - existing)
        if to_create <= 0:
            self.stdout.write(self.style.SUCCESS(f"Already have {existing} tasks (>= {min_count})."))
            return

        created = 0
        for text in SAMPLE_REQUESTS:
            if created >= to_create:
                break

            extracted = extract_intent_entities(text)
            intent = extracted["intent"]
            entities = extracted.get("entities") or {}

            completion_ratio = 1.0 if Task.objects.filter(client_id=client_id, status="COMPLETED").exists() else 0.0
            risk_score = score_risk(RiskContext(intent=intent, entities=entities, completion_ratio=completion_ratio))

            task_code = _unique_task_code()
            assigned_team = assigned_team_for_intent(intent)

            reference_task_code = None
            if intent == Task.INTENT_CHECK_STATUS:
                # If there is no referenced task code in the sample text, point to the latest task.
                reference_task_code = (entities.get("task_code") or "").strip() or None
                if not reference_task_code:
                    last = Task.objects.exclude(intent=Task.INTENT_CHECK_STATUS).order_by("-created_at").first()
                    if last:
                        reference_task_code = last.task_code
                        entities = dict(entities)
                        entities["task_code"] = reference_task_code

                if reference_task_code:
                    ref = Task.objects.filter(task_code=reference_task_code).first()
                    if ref:
                        entities = dict(entities)
                        entities["reference_task"] = {
                            "task_code": ref.task_code,
                            "intent": ref.intent,
                            "status": ref.status,
                            "risk_score": ref.risk_score,
                            "assigned_team": ref.assigned_team,
                            "created_at": ref.created_at.isoformat(),
                        }

            with transaction.atomic():
                task = Task.objects.create(
                    task_code=task_code,
                    client_id=client_id,
                    customer_request=text,
                    intent=intent,
                    entities=entities,
                    risk_score=risk_score,
                    status=Task.STATUS_PENDING,
                    assigned_team=assigned_team,
                    ai_model="",
                    prompt_version="seed_v1",
                    reference_task_code=reference_task_code,
                )

                steps = generate_steps(intent=intent, entities=entities, task_code=task_code)
                for s in steps:
                    TaskStep.objects.create(
                        task=task, step_order=int(s["step_order"]), step_text=str(s["step_text"])
                    )

                messages = generate_messages(intent=intent, entities=entities, task_code=task_code)
                whatsapp_text = str(messages.get("whatsapp") or "").strip()
                email = messages.get("email") or {}
                sms_text = str(messages.get("sms") or "").strip()

                TaskMessage.objects.create(
                    task=task, channel=TaskMessage.CHANNEL_WHATSAPP, message_text=whatsapp_text
                )
                TaskMessage.objects.create(
                    task=task,
                    channel=TaskMessage.CHANNEL_EMAIL,
                    subject=str(email.get("subject") or f"Task {task_code}"),
                    message_text=str(email.get("body") or whatsapp_text),
                )
                TaskMessage.objects.create(
                    task=task, channel=TaskMessage.CHANNEL_SMS, message_text=sms_text[:160]
                )

                StatusHistory.objects.create(
                    task=task, old_status="", new_status=Task.STATUS_PENDING, changed_by="system"
                )

            created += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {created} task(s). Total tasks now: {Task.objects.count()}"))

