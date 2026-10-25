from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict


class ConversationBase(BaseModel):
    title: str = Field(min_length=1, max_length=500)


class ConversationCreate(ConversationBase):
    pass


class ConversationUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=500)


class ConversationResponse(ConversationBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class ConversationMessageBase(BaseModel):
    role: str
    content: str


class ConversationMessageCreate(ConversationMessageBase):
    conversation_id: int
    tool_calls: Optional[str] = None
    tool_results: Optional[str] = None
    citations: Optional[str] = None


class ConversationMessageResponse(ConversationMessageBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    conversation_id: int
    tool_calls: Optional[str] = None
    tool_results: Optional[str] = None
    citations: Optional[str] = None
    created_at: datetime


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    conversation_id: Optional[int] = None


class ChatResponse(BaseModel):
    message: ConversationMessageResponse
    conversation: ConversationResponse