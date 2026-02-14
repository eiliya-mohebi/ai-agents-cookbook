from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, viewsets, filters
from django.shortcuts import get_object_or_404
from ai.agents import get_document_agent
from .models import Document
from .serializers import (
    DocumentSerializer,
    ChatRequestSerializer,
)  # Assuming ChatRequestSerializer exists from previous step


class DocumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows documents to be viewed or edited.
    Supports filtering by user_id and searching by title/content.
    """

    serializer_class = DocumentSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "content"]

    def get_queryset(self):
        queryset = Document.objects.filter(active=True).order_by("-created_at")
        user_id = self.request.query_params.get("user_id") or self.request.data.get(
            "user_id"
        )

        if user_id:
            queryset = queryset.filter(owner_id=user_id)
        return queryset

    def perform_create(self, serializer):
        user_id = self.request.data.get("user_id")

        serializer.save(owner_id=user_id, active=True)

    def perform_destroy(self, instance):
        instance.active = False
        instance.save()


@api_view(["GET", "POST"])
def chat_with_agent(request):

    if request.method == "GET":
        return Response({"message": "Send a POST request with {'prompt': '...'}"})

    # 1. Validate Input using Serializer
    serializer = ChatRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    prompt = serializer.validated_data["prompt"]

    try:
        # 2. Determine User ID
        user_id = request.user.id if request.user.is_authenticated else 1

        # 3. Initialize the Agent
        agent = get_document_agent()

        # 4. Prepare inputs and config for LangGraph
        inputs = {"messages": [{"role": "user", "content": prompt}]}
        config = {"configurable": {"user_id": user_id}}

        # 5. Invoke the Agent
        result = agent.invoke(inputs, config=config)

        # 6. Extract the final response
        last_message = result["messages"][-1]
        response_text = last_message.content

        return Response({"response": response_text}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
