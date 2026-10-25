from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Link(Base):
  __tablename__ = "links"

  id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))
  title: Mapped[str]
  full_url: Mapped[str]
  short_code: Mapped[str] = mapped_column(unique=True, index=True)
  owner_id: Mapped[str | None] = mapped_column(
    ForeignKey("users.id", ondelete="SET NULL"), index=True
  )
  is_active: Mapped[bool] = mapped_column(default=True)
  is_custom_slug: Mapped[bool] = mapped_column(default=False)
  expiry_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
  hashed_password: Mapped[str | None] = mapped_column(default=None)
  created_on: Mapped[datetime] = mapped_column(server_default=func.now())
  updated_on: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
