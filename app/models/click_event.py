from datetime import datetime
from uuid import uuid4

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ClickEvent(Base):
  __tablename__ = "click_events"

  id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))
  link_id: Mapped[str] = mapped_column(ForeignKey("links.id"), index=True)
  continent: Mapped[str | None]
  country: Mapped[str | None]
  state: Mapped[str | None]
  browser: Mapped[str | None]
  device_type: Mapped[str | None]
  os: Mapped[str | None]
  referrer: Mapped[str | None]
  clicked_at: Mapped[datetime] = mapped_column(server_default=func.now())
