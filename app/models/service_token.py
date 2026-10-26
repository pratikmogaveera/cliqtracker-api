from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ServiceToken(Base):
  __tablename__ = "service_tokens"

  id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))
  owner_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
  title: Mapped[str]
  hashed_token: Mapped[str] = mapped_column(index=True)
  scopes: Mapped[str]
  expiry_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
  revoked_on: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
  created_on: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
  updated_on: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
