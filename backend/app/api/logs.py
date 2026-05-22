from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.ingestion.handler import ingest_log
from app.models.schemas import InferenceLogPayload

router = APIRouter(prefix="/logs", tags=["ingestion"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def receive_log(payload: InferenceLogPayload, db: AsyncSession = Depends(get_db)):
    """Ingestion endpoint: validates payload and persists inference metadata."""
    record = await ingest_log(db, payload)
    return {"id": str(record.id), "status": "stored"}
