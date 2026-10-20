from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.rate_limit import check_rate_limit
from app.schemas.common import ApiResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
  async def dispatch(self, request: Request, call_next):
    bucket_id: str
    max_tokens: int
    refill_rate: float

    access_token = request.cookies.get("access_token")
    api_key = request.headers.get("X-API-Key")
    if access_token is not None:
      bucket_id = access_token
    elif api_key is not None:
      bucket_id = api_key
    else:
      forwarded_for = request.headers.get("x-forwarded-for")
      if forwarded_for:
        bucket_id = forwarded_for.split(",")[0].strip()
      elif request.client:
        bucket_id = request.client.host
      else:
        bucket_id = "unknown"

    if access_token is not None:
      max_tokens = settings.LIMIT_COOKIE
      refill_rate = settings.REFILL_COOKIE
    elif api_key is not None:
      max_tokens = settings.LIMIT_API_KEY
      refill_rate = settings.REFILL_API_KEY
    else:
      max_tokens = settings.LIMIT_UNAUTH
      refill_rate = settings.REFILL_UNAUTH

    if not await check_rate_limit(
      redis=request.app.state.redis,
      bucket_id=bucket_id,
      max_tokens=max_tokens,
      refill_rate=refill_rate,
    ):
      return JSONResponse(
        status_code=429,
        content=ApiResponse(
          success=False, data=None, message="Too many requests. Please try again later."
        ).model_dump(),
      )

    response: Response = await call_next(request)
    return response
