import os

from pydantic import BaseModel, Field
from typing import Optional


class EmailMessageSchema(BaseModel):
    subject: str
    contents: str
    invalid_request: bool | None = Field(default=False)


class SupervisorMessageSchema(BaseModel):
    content: str


class ChatResponseSchema(BaseModel):
    final_message: str
    email_content: Optional[str] = None
