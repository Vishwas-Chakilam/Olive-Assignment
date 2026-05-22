from collections import defaultdict
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.ingestion.handler import get_recent_logs
from app.models.schemas import MetricsSummary


def _bucket_key(ts: datetime, minutes: int = 5) -> str:
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    floored = ts.replace(second=0, microsecond=0)
    floored = floored.replace(minute=(floored.minute // minutes) * minutes)
    return floored.isoformat()


async def compute_metrics(db: AsyncSession) -> MetricsSummary:
    logs = await get_recent_logs(db, limit=1000)
    if not logs:
        return MetricsSummary(
            total_requests=0,
            success_count=0,
            error_count=0,
            error_rate=0.0,
            avg_latency_ms=0.0,
            requests_per_minute=0.0,
            total_tokens=0,
            by_provider={},
            by_model={},
            latency_series=[],
            throughput_series=[],
            error_series=[],
        )

    success = [l for l in logs if l.status == "success"]
    errors = [l for l in logs if l.status != "success"]
    total = len(logs)
    avg_latency = sum(l.latency_ms for l in logs) / total

    now = datetime.now(timezone.utc)
    window_start = now - timedelta(hours=1)
    recent = [l for l in logs if l.created_at and l.created_at >= window_start.replace(tzinfo=None)]
    rpm = len(recent) / 60.0 if recent else len(logs) / 60.0

    by_provider: dict[str, int] = defaultdict(int)
    by_model: dict[str, int] = defaultdict(int)
    latency_buckets: dict[str, list[int]] = defaultdict(list)
    throughput_buckets: dict[str, int] = defaultdict(int)
    error_buckets: dict[str, int] = defaultdict(int)

    for log in logs:
        by_provider[log.provider] += 1
        by_model[log.model] += 1
        key = _bucket_key(log.created_at)
        latency_buckets[key].append(log.latency_ms)
        throughput_buckets[key] += 1
        if log.status != "success":
            error_buckets[key] += 1

    latency_series = [
        {"time": k, "avg_latency_ms": sum(v) / len(v)}
        for k, v in sorted(latency_buckets.items())
    ]
    throughput_series = [{"time": k, "requests": v} for k, v in sorted(throughput_buckets.items())]
    error_series = [
        {
            "time": k,
            "errors": error_buckets.get(k, 0),
            "error_rate": error_buckets.get(k, 0) / throughput_buckets[k] if throughput_buckets[k] else 0,
        }
        for k in sorted(throughput_buckets.keys())
    ]

    total_tokens = sum(l.total_tokens or 0 for l in logs)

    return MetricsSummary(
        total_requests=total,
        success_count=len(success),
        error_count=len(errors),
        error_rate=len(errors) / total if total else 0.0,
        avg_latency_ms=round(avg_latency, 2),
        requests_per_minute=round(rpm, 2),
        total_tokens=total_tokens,
        by_provider=dict(by_provider),
        by_model=dict(by_model),
        latency_series=latency_series[-24:],
        throughput_series=throughput_series[-24:],
        error_series=error_series[-24:],
    )
