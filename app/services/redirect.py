from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.link import Link


async def get_redirect_url(short_code: str, db: AsyncSession) -> tuple[str, str]:
  query = select(Link).where(Link.short_code == short_code)
  raw_response = await db.execute(query)
  response = raw_response.scalar_one_or_none()

  if response is None:
    raise HTTPException(404, "No link found.")

  return response.id, response.full_url
