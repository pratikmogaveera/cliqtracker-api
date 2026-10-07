from sqlalchemy.ext.asyncio import AsyncSession

from app.models.click_event import ClickEvent


async def create_click_event(
  link_id: str,
  continent: str | None,
  country: str | None,
  state: str | None,
  browser: str | None,
  device_type: str | None,
  referrer: str | None,
  db: AsyncSession,
) -> None:
  db.add(
    ClickEvent(
      link_id=link_id,
      continent=continent,
      country=country,
      state=state,
      browser=browser,
      device_type=device_type,
      referrer=referrer,
    )
  )
  await db.commit()
