from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.schemas import MetricsSummary
from app.services.metrics_service import compute_metrics

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("", response_model=MetricsSummary)
async def get_metrics(db: AsyncSession = Depends(get_db)):
    return await compute_metrics(db)
