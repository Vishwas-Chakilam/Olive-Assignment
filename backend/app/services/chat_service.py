import uuid

from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.db.models import ChatMessage, Conversation, User
from app.providers.base import LLMMessage
from app.providers.registry import DEFAULT_MODELS, _default_provider, get_provider
from app.sdk.llm_client import InstrumentedLLMClient
from app.utils.model_names import normalize_model_name


async def list_conversations(db: AsyncSession, user_id: uuid.UUID) -> list[tuple[Conversation, int]]:
    stmt = (
        select(Conversation, func.count(ChatMessage.id).label("message_count"))
        .where(Conversation.user_id == user_id)
        .outerjoin(ChatMessage)
        .group_by(Conversation.id)
        .order_by(Conversation.updated_at.desc())
    )
    rows = await db.execute(stmt)
    return [(row[0], row[1]) for row in rows.all()]


async def get_conversation(
    db: AsyncSession, conversation_id: uuid.UUID, user_id: uuid.UUID
) -> Conversation | None:
    result = await db.execute(
        select(Conversation)
        .where(Conversation.id == conversation_id, Conversation.user_id == user_id)
        .options(selectinload(Conversation.messages))
    )
    return result.scalar_one_or_none()


async def delete_conversation(db: AsyncSession, conversation_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    result = await db.execute(
        delete(Conversation).where(
            Conversation.id == conversation_id, Conversation.user_id == user_id
        )
    )
    return result.rowcount > 0


async def create_conversation(db: AsyncSession, user_id: uuid.UUID, title: str = "New conversation") -> Conversation:
    conv = Conversation(title=title, user_id=user_id)
    db.add(conv)
    await db.flush()
    await db.refresh(conv)
    return conv


async def add_message(
    db: AsyncSession, conversation_id: uuid.UUID, role: str, content: str
) -> ChatMessage:
    msg = ChatMessage(conversation_id=conversation_id, role=role, content=content)
    db.add(msg)
    conv = await db.get(Conversation, conversation_id)
    if conv and conv.title == "New conversation" and role == "user":
        conv.title = content[:60] + ("..." if len(content) > 60 else "")
    await db.flush()
    await db.refresh(msg)
    return msg


async def get_recent_messages(db: AsyncSession, conversation_id: uuid.UUID, limit: int) -> list[LLMMessage]:
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.timestamp.desc())
        .limit(limit)
    )
    rows = list(reversed(result.scalars().all()))
    return [LLMMessage(role=m.role, content=m.content) for m in rows]


def build_llm_client(
    provider_name: str | None, model: str | None, user: User | None = None
) -> tuple[InstrumentedLLMClient, str]:
    pname = (provider_name or (user.default_provider if user else None) or _default_provider()).lower()
    provider = get_provider(pname)
    default = user.default_model if user else settings.default_model
    raw_model = model or DEFAULT_MODELS.get(pname, default)
    resolved_model = normalize_model_name(raw_model)
    return InstrumentedLLMClient(provider), resolved_model


async def ensure_conversation_access(
    db: AsyncSession, conversation_id: uuid.UUID | None, user_id: uuid.UUID
) -> uuid.UUID:
    if conversation_id:
        conv = await get_conversation(db, conversation_id, user_id)
        if not conv:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
        return conv.id
    conv = await create_conversation(db, user_id)
    return conv.id
