from sqlalchemy.ext.asyncio import AsyncSession

from app.models.click_event import ClickEvent


async def create_click_event(link_id: str, db: AsyncSession) -> None:
  db.add(ClickEvent(link_id=link_id))
  await db.commit()
