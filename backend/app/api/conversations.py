from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import get_current_user
from app.db.database import get_db
from app.db.models import User
from app.models.schemas import ChatMessageSchema, ConversationDetail, ConversationSummary
from app.services import chat_service

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("", response_model=list[ConversationSummary])
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rows = await chat_service.list_conversations(db, user.id)
    return [
        ConversationSummary(
            id=c.id,
            title=c.title,
            created_at=c.created_at,
            updated_at=c.updated_at,
            message_count=count,
        )
        for c, count in rows
    ]


@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    conv = await chat_service.get_conversation(db, conversation_id, user.id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return ConversationDetail(
        id=conv.id,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=[
            ChatMessageSchema(role=m.role, content=m.content)
            for m in sorted(conv.messages, key=lambda x: x.timestamp)
        ],
    )


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    deleted = await chat_service.delete_conversation(db, conversation_id, user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"deleted": True}
