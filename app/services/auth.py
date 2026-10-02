from hashlib import sha256

from fastapi import HTTPException
from nanoid import generate
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_jwt_token, verify_password
from app.models.user import User
from app.schemas.user import LoginUserRequest, UserResponse


async def create_session(user_id: str, redis: Redis) -> tuple[str, str]:
  access_token = create_jwt_token(user_id)
  refresh_token = generate(size=32)
  hashed = sha256(refresh_token.encode()).hexdigest()
  await redis.setex(
    name=f"refresh:{hashed}", value=user_id, time=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
  )
  return access_token, refresh_token


async def authenticate_user(
  data: LoginUserRequest, db: AsyncSession, redis: Redis
) -> tuple[UserResponse, str, str]:
  query = select(User).where(User.email == data.email)
  result = await db.execute(query)
  user = result.scalar_one_or_none()

  if user is None:
    raise HTTPException(401, "Invalid email or password.")

  if verify_password(raw_password=data.raw_password, hashed_password=user.hashed_password):
    access_token, refresh_token = await create_session(user_id=user.id, redis=redis)
    return UserResponse.model_validate(user), access_token, refresh_token
  else:
    raise HTTPException(401, "Invalid email or password.")


async def logout_user(refresh_token: str, redis: Redis) -> None:
  hashed_existing_refresh_token = sha256(refresh_token.encode("utf-8")).hexdigest()
  await redis.delete(f"refresh:{hashed_existing_refresh_token}")


async def refresh_access_token(refresh_token: str, redis: Redis) -> tuple[str, str]:
  hashed_existing_refresh_token = sha256(refresh_token.encode("utf-8")).hexdigest()
  user_id: str = await redis.get(f"refresh:{hashed_existing_refresh_token}")

  if user_id is not None:
    await redis.delete(f"refresh:{hashed_existing_refresh_token}")
    access_token, refresh_token = await create_session(user_id=user_id, redis=redis)
    return access_token, refresh_token

  raise HTTPException(401, "Your session has expired. Please log in again.")
