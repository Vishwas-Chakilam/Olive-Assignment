from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class MessageRole(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"


class ChatMessageSchema(BaseModel):
    role: MessageRole
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_id: UUID | None = None
    provider: str | None = None
    model: str | None = None
    stream: bool = True


class ChatResponse(BaseModel):
    conversation_id: UUID
    message: ChatMessageSchema
    request_id: UUID


class ConversationSummary(BaseModel):
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0


class ConversationDetail(BaseModel):
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[ChatMessageSchema]


class InferenceLogPayload(BaseModel):
    request_id: UUID
    conversation_id: UUID | None = None
    provider: str
    model: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    latency_ms: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str
    error_message: str | None = None
    input_preview: str | None = None
    output_preview: str | None = None


class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=128)
    display_name: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserProfile(BaseModel):
    id: UUID
    email: str
    username: str
    display_name: str
    bio: str | None = None
    avatar_url: str | None = None
    theme: str = "dark"
    default_provider: str = "mock"
    default_model: str = "mock-gpt"
    created_at: datetime


class UserProfileUpdate(BaseModel):
    display_name: str | None = None
    bio: str | None = None
    avatar_url: str | None = None
    theme: str | None = None
    default_provider: str | None = None
    default_model: str | None = None


class AuthToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile


class MetricsSummary(BaseModel):
    total_requests: int
    success_count: int
    error_count: int
    error_rate: float
    avg_latency_ms: float
    requests_per_minute: float
    total_tokens: int
    by_provider: dict[str, int]
    by_model: dict[str, int]
    latency_series: list[dict[str, float | str]]
    throughput_series: list[dict[str, float | str]]
    error_series: list[dict[str, float | str]]
