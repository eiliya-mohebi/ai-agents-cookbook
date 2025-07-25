from fastapi import APIRouter, Depends, HTTPException
from api.chat.models import ChatMessage, ChatMessagePayload, ChatMessageListItem
from api.db import get_session
from sqlmodel import Session, select
from typing import List
from api.ai.services import generate_email_message
from api.ai.schemas import (
    EmailMessageSchema,
    SupervisorMessageSchema,
    ChatResponseSchema,
)
from api.ai.agents import get_supervisor

router = APIRouter()


# /api/chats/
@router.get("/")
def chat_health():
    return {"status": "ok"}


@router.get("/recent/", response_model=List[ChatMessageListItem])
def chat_list_messages(session: Session = Depends(get_session)):
    query = select(ChatMessage)
    result = session.exec(query).fetchall()[:10]
    return result


@router.post("/", response_model=ChatResponseSchema)
def chat_create_message(
    payload: ChatMessagePayload, session: Session = Depends(get_session)
):
    data = payload.model_dump()  # pydantic -> dict
    obj = ChatMessage.model_validate(data)
    session.add(obj)
    session.commit()
    supe = get_supervisor()
    msg_data = {
        "messages": [
            {"role": "user", "content": f"{payload.message}"},
        ]
    }
    result = supe.invoke(msg_data)
    if not result:
        raise HTTPException(status_code=400, detail="Error with supervisor")
    messages = result.get("messages")
    if not messages:
        raise HTTPException(status_code=400, detail="Error with supervisor")
    final_message_content = messages[-1].content

    email_content_str = None
    for message in reversed(messages):
        if message.name == "research_agent":
            if message.content and not message.tool_calls:
                email_content_str = message.content
                break

    return ChatResponseSchema(
        final_message=final_message_content, email_content=email_content_str
    )
