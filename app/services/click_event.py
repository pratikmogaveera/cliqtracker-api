from hashlib import sha256
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.click_event import ClickEvent


async def create_click_event(
  link_id: str,
  continent: str | None,
  country: str | None,
  state: str | None,
  browser: str | None,
  device_type: str | None,
  os: str | None,
  referrer: str | None,
  ip: str | None,
  db: AsyncSession,
  params: dict[str, Any] | None,
) -> None:
  db.add(
    ClickEvent(
      link_id=link_id,
      continent=continent,
      country=country,
      state=state,
      browser=browser,
      device_type=device_type,
      os=os,
      referrer=referrer,
      hashed_ip=sha256(ip.encode()).hexdigest() if ip is not None else None,
      params=params,
    )
  )
  await db.commit()
