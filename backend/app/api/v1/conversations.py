from typing import List, Optional
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from app.db.base import get_db
from app.core.security import get_current_active_user
from app.core.audit import log_audit_event
from app.schemas.conversation import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    ConversationMessageResponse,
    ChatRequest,
    ChatResponse,
)
from app.models.conversation import Conversation, ConversationMessage
from app.models.user import User
from app.services.orchestration import create_orchestration_service
from app.services.llm import ChatMessage

router = APIRouter()


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    data: ConversationCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    conversation = Conversation(user_id=current_user.id, title=data.title)
    db.add(conversation)
    await db.flush()
    await log_audit_event(db, "create", "conversation", conversation.id, current_user.id, f"Created conversation: {conversation.title}")
    return conversation


@router.get("", response_model=List[ConversationResponse])
async def list_conversations(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(desc(Conversation.updated_at))
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.id == conversation_id, Conversation.user_id == current_user.id)
        .options(selectinload(Conversation.messages))
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.patch("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: int,
    data: ConversationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == current_user.id)
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if data.title is not None:
        conversation.title = data.title
    await db.flush()
    return conversation


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == current_user.id)
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    await db.delete(conversation)
    await log_audit_event(db, "delete", "conversation", conversation_id, current_user.id, f"Deleted conversation")
    return None


@router.post("/{conversation_id}/messages", response_model=ChatResponse)
async def send_message(
    conversation_id: int,
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.id == conversation_id, Conversation.user_id == current_user.id)
        .options(selectinload(Conversation.messages))
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    user_message = ConversationMessage(
        conversation_id=conversation_id,
        role="user",
        content=request.message,
    )
    db.add(user_message)
    await db.flush()
    
    orchestration = await create_orchestration_service(db, current_user.id)
    
    history = [
        ChatMessage(role=msg.role, content=msg.content)
        for msg in conversation.messages[-10:]
    ]
    
    orch_result = await orchestration.process_question(request.message, history)
    
    assistant_message = ConversationMessage(
        conversation_id=conversation_id,
        role="assistant",
        content=orch_result["answer"],
        tool_calls=json.dumps(orch_result["tool_calls"]) if orch_result["tool_calls"] else None,
        citations=json.dumps(orch_result["citations"]) if orch_result["citations"] else None,
    )
    db.add(assistant_message)
    
    conversation.updated_at = datetime.utcnow()
    await db.flush()
    await log_audit_event(db, "chat", "conversation", conversation_id, current_user.id, f"Chat message")
    
    return ChatResponse(message=assistant_message, conversation=conversation)