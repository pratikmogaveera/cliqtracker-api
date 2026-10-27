from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ErrorLog(Base):
  __tablename__ = "error_logs"

  id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))
  method: Mapped[str]
  path: Mapped[str]
  user_id: Mapped[str | None] = mapped_column(default=None)
  error_type: Mapped[str]
  error_message: Mapped[str]
  traceback: Mapped[str]
  created_on: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
