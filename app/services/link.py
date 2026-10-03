from fastapi import HTTPException
from nanoid import generate
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.click_event import ClickEvent
from app.models.link import Link
from app.schemas.common import PaginatedResponse
from app.schemas.link import CreateLinkRequest, LinkResponse, UpdateLinkRequest


async def create_link(payload: CreateLinkRequest, user_id: str, db: AsyncSession) -> LinkResponse:
  try:
    if payload.short_code is None:
      short_code = generate(
        alphabet="_-0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", size=6
      )
    else:
      short_code = payload.short_code

    new_link = Link(
      title=payload.title,
      full_url=str(payload.full_url),
      short_code=short_code,
      owner_id=user_id,
      is_custom_slug=payload.short_code is not None,
    )

    db.add(new_link)

    await db.commit()
    await db.refresh(new_link)

    return LinkResponse.model_validate(new_link)
  except IntegrityError:
    await db.rollback()
    raise HTTPException(409, "A link with this short code already exists.")


async def get_link(user_id: str, link_id: str, db: AsyncSession) -> LinkResponse:
  query = (
    select(Link, func.count(ClickEvent.id).label("click_count"))
    .outerjoin(target=ClickEvent, onclause=Link.id == ClickEvent.link_id)
    .where(Link.id == link_id)
    .where(Link.owner_id == user_id)
    .group_by(Link.id)
  )

  raw_response = await db.execute(query)
  response = raw_response.first()

  if response is None:
    raise HTTPException(404, "No link found.")

  link, count = response
  result = LinkResponse.model_validate(link).model_copy(update={"click_count": count})
  return result


async def get_links(
  user_id: str, db: AsyncSession, page: int, limit: int = settings.PAGE_SIZE
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
    items.append(LinkResponse.model_validate(link).model_copy(update={"click_count": count}))

  return PaginatedResponse(items=items, page=page, limit=limit, has_next_page=len(response) > limit)


async def update_link(link_id: str, user_id: str, payload: UpdateLinkRequest, db: AsyncSession):
  link = await db.get(Link, link_id)

  if link is None:
    raise HTTPException(404, "Link not found.")

  if link.owner_id != user_id:
    raise HTTPException(403, "Not authorised.")

  if payload.title is not None:
    link.title = payload.title
  if payload.full_url is not None:
    link.full_url = str(payload.full_url)
  if payload.is_active is not None:
    link.is_active = payload.is_active

  await db.commit()
  await db.refresh(link)

  return LinkResponse.model_validate(link)


async def delete_link(link_id: str, user_id: str, db: AsyncSession):
  link = await db.get(Link, link_id)

  if link is None:
    raise HTTPException(404, "Link not found.")

  if link.owner_id != user_id:
    raise HTTPException(403, "Not authorised.")
  await db.delete(link)
  await db.commit()
