from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.core.config import settings

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Token(BaseModel):
  sub: str
  exp: datetime


def hash_password(raw_password: str) -> str:
  return password_context.hash(raw_password)


def verify_password(raw_password: str, hashed_password: str) -> bool:
  return password_context.verify(raw_password, hashed_password)


def create_jwt_token(sub: str) -> str:
  return jwt.encode(
    {
      "sub": sub,
      "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    },
    key=settings.JWT_SECRET,
    algorithm=settings.JWT_ALGORITHM,
  )


def authenticate_jwt(token: str) -> str:
  payload = jwt.decode(
    token,
    key=settings.JWT_SECRET,
    algorithms=[settings.JWT_ALGORITHM],
  )
  token_data = Token(**payload)
  return token_data.sub
