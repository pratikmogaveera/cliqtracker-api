import json
from datetime import UTC, datetime

from arq import ArqRedis
from fastapi import HTTPException, Request
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import verify_password
from app.helper import extract_client_details
from app.models.link import Link
from app.schemas.link import CachedLinkData
from app.schemas.redirect import UnlockRedirectUrlRequest, UnlockRedirectUrlResponse


async def get_redirect_url(
  short_code: str, request: Request, db: AsyncSession, redis: Redis, arq_pool: ArqRedis
) -> str:
  redirect_data: CachedLinkData
  ip, user_agent, referrer = extract_client_details(request)
  cached_data_string: str | None = await redis.get(f"short:{short_code}")

  if cached_data_string is None:
    query = select(Link).where(Link.short_code == short_code)
    raw_response = await db.execute(query)
    response = raw_response.scalar_one_or_none()
    if response is None:
      raise HTTPException(404, "Link not found.")

    redirect_data = CachedLinkData(
      link_id=response.id,
      full_url=response.full_url,
      expiry_at=response.expiry_at,
      is_protected=response.hashed_password is not None,
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

  if redirect_data.is_protected:
    return f"{settings.FRONTEND_URL}/unlock/{short_code}"

  await arq_pool.enqueue_job("process_click", redirect_data.link_id, ip, user_agent, referrer)
  return redirect_data.full_url


async def get_unlock_redirect_url(
  short_code: str,
  data: UnlockRedirectUrlRequest,
  request: Request,
  db: AsyncSession,
  redis: Redis,
  arq_pool: ArqRedis,
) -> UnlockRedirectUrlResponse:
  query = select(Link).where(Link.short_code == short_code)
  raw_response = await db.execute(query)
  response = raw_response.scalar_one_or_none()
  if response is None:
    raise HTTPException(404, "Link not found.")

  if response.expiry_at is not None:
    now = datetime.now(UTC)
    if now > response.expiry_at:
      raise HTTPException(status_code=410, detail="The link has expired.")

  if response.hashed_password is None:
    raise HTTPException(400, "This link is not password protected.")

  if not verify_password(raw_password=data.password, hashed_password=response.hashed_password):
    raise HTTPException(401, "Incorrect password.")

  redirect_data = CachedLinkData(
    link_id=response.id,
    full_url=response.full_url,
    expiry_at=response.expiry_at,
    is_protected=response.hashed_password is not None,
  )
  await redis.setex(
    name=f"short:{short_code}",
    value=json.dumps(redirect_data.model_dump(mode="json")),
    time=settings.REDIS_LINK_CACHE_EXPIRY,
  )

  ip, user_agent, referrer = extract_client_details(request)

  await arq_pool.enqueue_job("process_click", redirect_data.link_id, ip, user_agent, referrer)

  return UnlockRedirectUrlResponse(full_url=response.full_url)
