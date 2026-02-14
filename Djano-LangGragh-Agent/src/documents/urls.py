from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"docs", views.DocumentViewSet, basename="document")

urlpatterns = [
    path("", include(router.urls)),
    path("agent/chat/", views.chat_with_agent, name="agent-chat"),
]
