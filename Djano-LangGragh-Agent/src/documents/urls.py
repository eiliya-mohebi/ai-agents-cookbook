from django.urls import path
from . import views

urlpatterns = [
    path("agent/chat/", views.chat_with_agent, name="agent-chat"),
]
