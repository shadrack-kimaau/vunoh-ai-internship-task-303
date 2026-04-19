from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("api/tasks", views.tasks_list, name="tasks_list"),
    path("api/tasks/<str:task_code>", views.task_detail, name="task_detail"),
    path("api/assistant", views.assistant_placeholder, name="assistant_placeholder"),
    path(
        "api/tasks/<str:task_code>/status",
        views.task_status_update_placeholder,
        name="task_status_update_placeholder",
    ),
]

