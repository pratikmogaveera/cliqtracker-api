from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ClickEvent(Base):
  __tablename__ = "click_events"
  __table_args__ = (
    Index("ix_click_events_link_id_clicked_at", "link_id", "clicked_at"),
    Index("ix_click_events_link_id_country", "link_id", "country"),
    Index("ix_click_events_link_id_browser", "link_id", "browser"),
    Index("ix_click_events_link_id_device_type", "link_id", "device_type"),
    Index("ix_click_events_link_id_referrer", "link_id", "referrer"),
    Index("ix_click_events_link_id_os", "link_id", "os"),
  )
  id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))
  link_id: Mapped[str] = mapped_column(ForeignKey("links.id"), index=True)
  continent: Mapped[str | None]
  country: Mapped[str | None]
  state: Mapped[str | None]
  browser: Mapped[str | None]
  device_type: Mapped[str | None]
  os: Mapped[str | None]
  referrer: Mapped[str | None]
  hashed_ip: Mapped[str | None]
  clicked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
