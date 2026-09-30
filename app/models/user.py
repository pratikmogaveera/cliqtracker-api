from datetime import datetime
from uuid import uuid4

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
  __tablename__ = "users"

  id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))
  first_name: Mapped[str]
  last_name: Mapped[str]
  email: Mapped[str] = mapped_column(unique=True, index=True)
  hashed_password: Mapped[str]
  created_on: Mapped[datetime] = mapped_column(server_default=func.now())
  updated_on: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
