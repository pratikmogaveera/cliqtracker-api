from arq import ArqRedis
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis import get_arq_pool, get_redis
from app.schemas.common import ApiResponse
from app.schemas.redirect import UnlockRedirectUrlRequest, UnlockRedirectUrlResponse
from app.services.redirect import get_redirect_url, get_unlock_redirect_url

router = APIRouter(prefix="/go", tags=["Redirect"])


@router.get("/{short_code}")
async def redirect_url_route(
  request: Request,
  short_code: str,
  db: AsyncSession = Depends(get_db),
  redis: Redis = Depends(get_redis),
  arq_pool: ArqRedis = Depends(get_arq_pool),
) -> RedirectResponse:
  redirect_url = await get_redirect_url(
    short_code=short_code, request=request, db=db, redis=redis, arq_pool=arq_pool
  )
  return RedirectResponse(status_code=302, url=str(redirect_url))


@router.post("/unlock/{short_code}", response_model=ApiResponse[UnlockRedirectUrlResponse])
async def unlock_redirect_url_route(
  short_code: str,
  request: Request,
  payload: UnlockRedirectUrlRequest,
  db: AsyncSession = Depends(get_db),
  redis: Redis = Depends(get_redis),
  arq_pool: ArqRedis = Depends(get_arq_pool),
) -> ApiResponse[UnlockRedirectUrlResponse]:
  data = await get_unlock_redirect_url(
    short_code=short_code, data=payload, request=request, db=db, redis=redis, arq_pool=arq_pool
  )
  return ApiResponse(success=True, data=data, message="Link unlocked successfully")
