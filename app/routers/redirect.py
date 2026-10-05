import json

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis import get_redis
from app.schemas.link import CachedLinkData
from app.services.click_event import create_click_event
from app.services.redirect import get_redirect_url

router = APIRouter(prefix="/go", tags=["Redirect"])


@router.get("/{short_code}")
async def redirect_url_route(
  short_code: str, db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)
) -> RedirectResponse:
  redirect_data: CachedLinkData
  cached_data_string: str | None = await redis.get(f"short:{short_code}")

  if cached_data_string is None:
    link_id, redirect_url = await get_redirect_url(short_code=short_code, db=db)
    redirect_data = CachedLinkData(link_id=link_id, full_url=redirect_url)
    await redis.set(name=f"short:{short_code}", value=json.dumps(redirect_data.model_dump()))
  else:
    parsed_data = json.loads(s=cached_data_string)
    redirect_data = CachedLinkData(**parsed_data)

  await create_click_event(link_id=redirect_data.link_id, db=db)
  return RedirectResponse(status_code=302, url=str(redirect_data.full_url))
