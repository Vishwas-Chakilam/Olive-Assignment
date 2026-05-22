from fastapi import APIRouter

from app.config import settings
from app.db.database import check_db_connection
from app.providers.registry import PROVIDERS, DEFAULT_MODELS

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    db_ok = await check_db_connection()
    return {
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
        "database_url_scheme": settings.database_url.split("://")[0],
        "hint": None
        if db_ok
        else "Database unreachable or pool busy. Retry in a moment; if persistent, check DATABASE_URL and MySQL service.",
    }


@router.get("/providers")
async def list_providers():
    return {
        "providers": [
            {"name": name, "default_model": DEFAULT_MODELS.get(name)}
            for name in PROVIDERS
        ]
    }
