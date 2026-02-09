import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ai.agents import get_document_agent


@csrf_exempt
def chat_with_agent(request):

    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed. Use POST."}, status=405)

    try:
        # 1. Parse the request body
        data = json.loads(request.body)
        prompt = data.get("prompt")

        if not prompt:
            return JsonResponse({"error": "No 'prompt' field provided."}, status=400)

        # 2. Determine the User ID
        user_id = request.user.id if request.user.is_authenticated else 1

        # 3. Initialize the Agent
        agent = get_document_agent()

        # 4. Prepare inputs and config for LangGraph
        inputs = {"messages": [{"role": "user", "content": prompt}]}

        # Pass user_id in configurable, which your tools read from
        config = {"configurable": {"user_id": user_id}}

        # 5. Invoke the Agent
        result = agent.invoke(inputs, config=config)

        # 6. Extract the final response
        # The result is a state dict; the last message is the agent's final answer.
        last_message = result["messages"][-1]
        response_text = last_message.content

        return JsonResponse({"response": response_text})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body."}, status=400)
    except Exception as e:
        # Log the error in a real app
        return JsonResponse({"error": str(e)}, status=500)
