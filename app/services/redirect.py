import json
from datetime import UTC, datetime

from arq import ArqRedis
from fastapi import HTTPException, Request
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.link import Link
from app.schemas.link import CachedLinkData


async def get_redirect_url(
  short_code: str, request: Request, db: AsyncSession, redis: Redis, arq_pool: ArqRedis
) -> str:
  redirect_data: CachedLinkData
  forwarded_for = request.headers.get("x-forwarded-for")
  ip = (
    forwarded_for.split(",")[0].strip()
    if forwarded_for
    else (request.client.host if request.client else None)
  )
  user_agent = request.headers.get("user-agent")
  referrer = request.headers.get("referer")
  cached_data_string: str | None = await redis.get(f"short:{short_code}")

  if cached_data_string is None:
    query = select(Link).where(Link.short_code == short_code)
    raw_response = await db.execute(query)
    response = raw_response.scalar_one_or_none()
    if response is None:
      raise HTTPException(404, "No link found.")

    redirect_data = CachedLinkData(
      link_id=response.id, full_url=response.full_url, expiry_at=response.expiry_at
    )
    await redis.setex(
      name=f"short:{short_code}",
      value=json.dumps(redirect_data.model_dump(mode="json")),
      time=settings.REDIS_LINK_CACHE_EXPIRY,
    )
  else:
    redirect_data = CachedLinkData.model_validate_json(cached_data_string)

  if redirect_data.expiry_at is not None:
    now = datetime.now(UTC)
    if now > redirect_data.expiry_at:
      raise HTTPException(status_code=410, detail="The link has expired.")

  await arq_pool.enqueue_job("process_click", redirect_data.link_id, ip, user_agent, referrer)
  return redirect_data.full_url
