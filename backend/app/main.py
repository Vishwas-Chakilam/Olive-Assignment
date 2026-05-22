from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, chat, conversations, health, logs, metrics
from app.db.database import Base, engine
from app.db.migrate import run_startup_migrations


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await run_startup_migrations(conn)
    yield
    await engine.dispose()


app = FastAPI(
    title="Ollive Inference Platform",
    description="Chat service with inference logging and ingestion pipeline",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(conversations.router)
app.include_router(logs.router)
app.include_router(metrics.router)
