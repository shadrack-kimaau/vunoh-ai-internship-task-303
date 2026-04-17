import json
import random
from datetime import datetime
from zoneinfo import ZoneInfo

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods

from .ai_service import extract_intent_entities, generate_messages, generate_steps
from .assignment import assigned_team_for_intent
from .models import StatusHistory, Task, TaskMessage, TaskStep


def index(request):
    return render(request, "assistant/index.html")


@require_GET
def tasks_list(request):
    limit = int(request.GET.get("limit", "50"))
    limit = max(1, min(limit, 200))
    tasks = Task.objects.all().order_by("-created_at")[:limit]

    data = [
        {
            "task_code": t.task_code,
            "intent": t.intent,
            "status": t.status,
            "risk_score": t.risk_score,
            "assigned_team": t.assigned_team,
            "created_at": t.created_at.isoformat(),
        }
        for t in tasks
    ]
    return JsonResponse({"tasks": data})


@csrf_exempt
@require_http_methods(["POST"])
def assistant_placeholder(request):
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    customer_request = (payload.get("customer_request") or "").strip()
    client_id = (payload.get("client_id") or "").strip()

    if not customer_request:
        return JsonResponse({"error": "customer_request is required"}, status=400)
    if not client_id:
        return JsonResponse({"error": "client_id is required"}, status=400)

    # 1) AI intent extraction
    extracted = extract_intent_entities(customer_request)
    intent = extracted["intent"]
    entities = extracted.get("entities") or {}

    # 2) Risk scoring + history stats
    from .risk import RiskContext, score_risk

    history_qs = Task.objects.filter(client_id=client_id, status="COMPLETED")
    total_qs = Task.objects.filter(client_id=client_id)
    total_count = total_qs.count()
    completed_count = history_qs.count()
    completion_ratio = (completed_count / total_count) if total_count else 0.0

    risk_score = score_risk(RiskContext(intent=intent, entities=entities, completion_ratio=completion_ratio))

    # 3) Generate task code
    tz = ZoneInfo("Africa/Nairobi")
    now = datetime.now(tz)
    for _ in range(10):
        task_code = f"VG-{now.strftime('%Y%m%d')}-{random.randint(0, 99999):05d}"
        if not Task.objects.filter(task_code=task_code).exists():
            break
    else:
        return JsonResponse({"error": "Could not generate a unique task code"}, status=500)

    assigned_team = assigned_team_for_intent(intent)
    # 4) Create task + persist steps/messages
    with transaction.atomic():
        task = Task.objects.create(
            task_code=task_code,
            client_id=client_id,
            customer_request=customer_request,
            intent=intent,
            entities=entities,
            risk_score=risk_score,
            status=Task.STATUS_PENDING,
            assigned_team=assigned_team,
            # Explainability fields (AI model/prompt version can be expanded in Day 3).
            ai_model="",
            prompt_version="day2_v1",
            reference_task_code=None,
        )

        # steps
        steps = generate_steps(intent=intent, entities=entities, task_code=task_code)
        for s in steps:
            TaskStep.objects.create(
                task=task, step_order=int(s["step_order"]), step_text=str(s["step_text"])
            )

        # messages
        messages = generate_messages(intent=intent, entities=entities, task_code=task_code)
        whatsapp_text = str(messages.get("whatsapp") or "").strip()
        email = messages.get("email") or {}
        sms_text = str(messages.get("sms") or "").strip()

        TaskMessage.objects.create(
            task=task,
            channel=TaskMessage.CHANNEL_WHATSAPP,
            message_text=whatsapp_text,
        )
        TaskMessage.objects.create(
            task=task,
            channel=TaskMessage.CHANNEL_EMAIL,
            subject=str(email.get("subject") or f"Task {task_code}"),
            message_text=str(email.get("body") or whatsapp_text),
        )
        TaskMessage.objects.create(
            task=task,
            channel=TaskMessage.CHANNEL_SMS,
            message_text=sms_text[:160],
        )

        StatusHistory.objects.create(
            task=task,
            old_status="",
            new_status=Task.STATUS_PENDING,
            changed_by="system",
        )

    return JsonResponse(
        {
            "task": {
                "task_code": task.task_code,
                "intent": task.intent,
                "status": task.status,
                "risk_score": task.risk_score,
                "assigned_team": task.assigned_team,
                "created_at": task.created_at.isoformat(),
                "entities": task.entities,
            },
            "steps": [{"step_order": s.step_order, "step_text": s.step_text} for s in task.steps.all()],
            "messages": {
                "whatsapp": task.messages.filter(channel=TaskMessage.CHANNEL_WHATSAPP)
                .first()
                .message_text,
                "email": {
                    "subject": task.messages.filter(channel=TaskMessage.CHANNEL_EMAIL)
                    .first()
                    .subject,
                    "body": task.messages.filter(channel=TaskMessage.CHANNEL_EMAIL)
                    .first()
                    .message_text,
                },
                "sms": task.messages.filter(channel=TaskMessage.CHANNEL_SMS).first().message_text,
            },
        }
    )


@csrf_exempt
@require_http_methods(["PATCH"])
def task_status_update_placeholder(request, task_code: str):
    task = get_object_or_404(Task, task_code=task_code)
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    new_status = payload.get("status") or ""
    new_status = str(new_status).strip()
    if new_status not in {Task.STATUS_PENDING, Task.STATUS_IN_PROGRESS, Task.STATUS_COMPLETED}:
        return JsonResponse({"error": "Invalid status"}, status=400)

    with transaction.atomic():
        old_status = task.status
        if old_status != new_status:
            task.status = new_status
            task.save(update_fields=["status"])
            StatusHistory.objects.create(
                task=task,
                old_status=old_status,
                new_status=new_status,
                changed_by="customer",
            )

    return JsonResponse(
        {
            "task": {
                "task_code": task.task_code,
                "intent": task.intent,
                "status": task.status,
                "risk_score": task.risk_score,
                "assigned_team": task.assigned_team,
                "created_at": task.created_at.isoformat(),
            }
        }
    )
