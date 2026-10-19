import json

from fastapi import HTTPException
from nanoid import generate
from redis.asyncio import Redis
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import hash_password
from app.models.click_event import ClickEvent
from app.models.link import Link
from app.schemas.common import PaginatedResponse
from app.schemas.link import CachedLinkData, CreateLinkRequest, LinkResponse, UpdateLinkRequest


async def create_link(data: CreateLinkRequest, user_id: str, db: AsyncSession) -> LinkResponse:
  try:
    if data.short_code is None:
      short_code = generate(
        alphabet="_-0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", size=6
      )
    else:
      short_code = data.short_code

    new_link = Link(
      title=data.title,
      full_url=str(data.full_url),
      short_code=short_code,
      owner_id=user_id,
      is_custom_slug=data.short_code is not None,
      expiry_at=data.expiry_at,
      hashed_password=hash_password(data.raw_password) if data.raw_password is not None else None,
    )

    db.add(new_link)

    await db.commit()
    await db.refresh(new_link)

    return LinkResponse.model_validate(new_link).model_copy(
      update={"is_protected": new_link.hashed_password is not None}
    )
  except IntegrityError:
    await db.rollback()
    raise HTTPException(409, "A link with this short code already exists.")


async def _get_link_or_raise(link_id: str, user_id: str, db: AsyncSession) -> Link:
  link = await db.get(Link, link_id)
  if link is None:
    raise HTTPException(404, "No link found.")
  if link.owner_id != user_id:
    raise HTTPException(403, "Not authorised.")
  return link


async def get_link(user_id: str, link_id: str, db: AsyncSession) -> LinkResponse:
  link = await _get_link_or_raise(link_id=link_id, user_id=user_id, db=db)

  count_result = await db.execute(
    select(func.count(ClickEvent.id)).where(ClickEvent.link_id == link_id)
  )
  count = count_result.scalar() or 0

  return LinkResponse.model_validate(link).model_copy(
    update={"click_count": count, "is_protected": link.hashed_password is not None}
  )


async def get_links(
  user_id: str, db: AsyncSession, page: int = 1, limit: int = settings.PAGE_SIZE
) -> PaginatedResponse[LinkResponse]:
  query = (
    select(Link, func.count(ClickEvent.id).label("click_count"))
    .outerjoin(target=ClickEvent, onclause=Link.id == ClickEvent.link_id)
    .where(Link.owner_id == user_id)
    .group_by(Link.id)
    .order_by(Link.created_on.desc())
    .limit(limit + 1)
    .offset((page - 1) * limit)
  )

  raw_response = await db.execute(query)
  response = raw_response.all()
  items_to_return = response[:limit]

  items: list[LinkResponse] = []

  for link, count in items_to_return:
    items.append(
      LinkResponse.model_validate(link).model_copy(
        update={"click_count": count, "is_protected": link.hashed_password is not None}
      )
    )

  return PaginatedResponse(items=items, page=page, limit=limit, has_next_page=len(response) > limit)


async def update_link(
  link_id: str, user_id: str, data: UpdateLinkRequest, db: AsyncSession, redis: Redis
) -> LinkResponse:
  link = await _get_link_or_raise(link_id=link_id, user_id=user_id, db=db)

  if data.title is not None:
    link.title = data.title
  if data.full_url is not None:
    link.full_url = str(data.full_url)
  if data.is_active is not None:
    link.is_active = data.is_active
  if data.expiry_at is not None:
    link.expiry_at = data.expiry_at
  elif data.clear_expiry:
    link.expiry_at = None
  if data.raw_password is not None:
    link.hashed_password = hash_password(data.raw_password)
  elif data.clear_password:
    link.hashed_password = None

  await db.commit()
  await db.refresh(link)

  redirect_data = CachedLinkData(
    link_id=link.id,
    full_url=link.full_url,
    expiry_at=link.expiry_at,
    is_protected=link.hashed_password is not None,
  )

  await redis.setex(
    name=f"short:{link.short_code}",
    value=json.dumps(redirect_data.model_dump(mode="json")),
    time=settings.REDIS_LINK_CACHE_EXPIRY,
  )

  return LinkResponse.model_validate(link).model_copy(
    update={"is_protected": link.hashed_password is not None}
  )


async def delete_link(link_id: str, user_id: str, db: AsyncSession, redis: Redis) -> None:
  link = await _get_link_or_raise(link_id=link_id, user_id=user_id, db=db)
  await db.delete(link)
  await db.commit()

  await redis.delete(f"short:{link.short_code}")
