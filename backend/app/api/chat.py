import json
import uuid
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.auth.deps import get_current_user
from app.config import settings
from app.db.database import AsyncSessionLocal
from app.db.models import User
from app.models.schemas import ChatRequest, ChatResponse, ChatMessageSchema, MessageRole
from app.providers.base import LLMMessage
from app.services import chat_service

router = APIRouter(tags=["chat"])


@router.post("/chat")
async def chat_endpoint(
    body: ChatRequest,
    request: Request,
    user: User = Depends(get_current_user),
):
    if not body.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    async with AsyncSessionLocal() as db:
        try:
            conversation_id = await chat_service.ensure_conversation_access(
                db, body.conversation_id, user.id
            )
            await chat_service.add_message(db, conversation_id, "user", body.message)
            history = await chat_service.get_recent_messages(
                db, conversation_id, settings.context_message_limit
            )
            await db.commit()
        except HTTPException:
            await db.rollback()
            raise
        except Exception:
            await db.rollback()
            raise

    client, model = chat_service.build_llm_client(body.provider, body.model, user)
    request_id = uuid.uuid4()
    history_msgs = list(history)

    if body.stream:
        return StreamingResponse(
            _stream_events(
                client=client,
                model=model,
                messages=history_msgs,
                conversation_id=conversation_id,
                request_id=request_id,
                http_request=request,
            ),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    try:
        result = await client.generate(
            model=model,
            messages=history_msgs,
            conversation_id=conversation_id,
            request_id=request_id,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e)) from e

    async with AsyncSessionLocal() as db:
        assistant_msg = await chat_service.add_message(
            db, conversation_id, "assistant", result.content
        )
        await db.commit()

    return ChatResponse(
        conversation_id=conversation_id,
        message=ChatMessageSchema(role=MessageRole.assistant, content=assistant_msg.content),
        request_id=request_id,
    )


async def _stream_events(
    *,
    client,
    model: str,
    messages: list[LLMMessage],
    conversation_id: UUID,
    request_id: uuid.UUID,
    http_request: Request,
):
    collected: list[str] = []
    meta = {
        "type": "meta",
        "conversation_id": str(conversation_id),
        "request_id": str(request_id),
    }
    yield f"data: {json.dumps(meta)}\n\n"

    try:
        async for chunk in client.generate_stream(
            model=model,
            messages=messages,
            conversation_id=conversation_id,
            request_id=request_id,
        ):
            if await http_request.is_disconnected():
                yield f"data: {json.dumps({'type': 'cancelled'})}\n\n"
                return

            if chunk.done:
                continue

            collected.append(chunk.content)
            yield f"data: {json.dumps({'type': 'token', 'content': chunk.content})}\n\n"

        full_text = "".join(collected)
        async with AsyncSessionLocal() as db:
            await chat_service.add_message(db, conversation_id, "assistant", full_text)
            await db.commit()
        yield f"data: {json.dumps({'type': 'done', 'content': full_text})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
