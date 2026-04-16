from django.db import models


class Task(models.Model):
    INTENT_SEND_MONEY = "send_money"
    INTENT_GET_AIRPORT_TRANSFER = "get_airport_transfer"
    INTENT_HIRE_SERVICE = "hire_service"
    INTENT_VERIFY_DOCUMENT = "verify_document"
    INTENT_CHECK_STATUS = "check_status"

    INTENT_CHOICES = [
        (INTENT_SEND_MONEY, "Send money"),
        (INTENT_GET_AIRPORT_TRANSFER, "Airport transfer"),
        (INTENT_HIRE_SERVICE, "Hire service"),
        (INTENT_VERIFY_DOCUMENT, "Verify document"),
        (INTENT_CHECK_STATUS, "Check status"),
    ]

    STATUS_PENDING = "PENDING"
    STATUS_IN_PROGRESS = "IN_PROGRESS"
    STATUS_COMPLETED = "COMPLETED"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_COMPLETED, "Completed"),
    ]

    TEAM_FINANCE = "FINANCE"
    TEAM_OPERATIONS = "OPERATIONS"
    TEAM_LEGAL = "LEGAL"
    TEAM_SUPPORT = "SUPPORT"

    ASSIGNED_TEAM_CHOICES = [
        (TEAM_FINANCE, "Finance"),
        (TEAM_OPERATIONS, "Operations"),
        (TEAM_LEGAL, "Legal"),
        (TEAM_SUPPORT, "Support"),
    ]

    task_code = models.CharField(max_length=64, unique=True)
    client_id = models.CharField(max_length=64, blank=True)
    customer_request = models.TextField()

    intent = models.CharField(max_length=32, choices=INTENT_CHOICES)
    entities = models.JSONField(default=dict, blank=True)

    risk_score = models.IntegerField(default=0)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING)
    assigned_team = models.CharField(
        max_length=16, choices=ASSIGNED_TEAM_CHOICES, default=TEAM_SUPPORT
    )

    # Stored for explainability in the README.
    ai_model = models.CharField(max_length=128, blank=True)
    prompt_version = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Optional reference for check_status tasks.
    reference_task_code = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.task_code} ({self.intent})"


class TaskStep(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="steps")
    step_order = models.PositiveIntegerField()
    step_text = models.TextField()

    class Meta:
        unique_together = [("task", "step_order")]
        ordering = ["step_order"]

    def __str__(self) -> str:
        return f"{self.task.task_code} - step {self.step_order}"


class TaskMessage(models.Model):
    CHANNEL_WHATSAPP = "WHATSAPP"
    CHANNEL_EMAIL = "EMAIL"
    CHANNEL_SMS = "SMS"

    CHANNEL_CHOICES = [
        (CHANNEL_WHATSAPP, "WhatsApp"),
        (CHANNEL_EMAIL, "Email"),
        (CHANNEL_SMS, "SMS"),
    ]

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="messages")
    channel = models.CharField(max_length=16, choices=CHANNEL_CHOICES)
    subject = models.CharField(max_length=200, blank=True)
    message_text = models.TextField()

    class Meta:
        unique_together = [("task", "channel")]

    def __str__(self) -> str:
        return f"{self.task.task_code} - {self.channel}"


class StatusHistory(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="status_history")
    old_status = models.CharField(max_length=16, blank=True)
    new_status = models.CharField(max_length=16)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.CharField(max_length=64, default="system")

    class Meta:
        ordering = ["changed_at"]

    def __str__(self) -> str:
        return f"{self.task.task_code}: {self.old_status} -> {self.new_status}"
