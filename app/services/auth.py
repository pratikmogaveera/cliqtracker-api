from hashlib import sha256

from fastapi import HTTPException
from nanoid import generate
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_jwt_token, hash_password, verify_password
from app.models.user import User
from app.schemas.user import CreateUserRequest, LoginUserRequest, UpdateUserRequest, UserResponse


async def create_user(data: CreateUserRequest, db: AsyncSession) -> UserResponse:
  try:
    new_user = User(
      first_name=data.first_name,
      last_name=data.last_name,
      email=data.email,
      hashed_password=hash_password(data.raw_password),
    )

    db.add(new_user)

    await db.commit()
    await db.refresh(new_user)

    return UserResponse.model_validate(new_user)

  except IntegrityError:
    await db.rollback()
    raise HTTPException(409, "An account with this email already exists.")


async def update_user(data: UpdateUserRequest, user_id: str, db: AsyncSession) -> UserResponse:
  user_to_update = await db.get(User, user_id)

  if user_to_update is None:
    raise HTTPException(404, "Account not found.")
  try:
    if data.email is not None:
      user_to_update.email = data.email
    if data.first_name is not None:
      user_to_update.first_name = data.first_name
    if data.last_name is not None:
      user_to_update.last_name = data.last_name
    if data.raw_password is not None:
      user_to_update.hashed_password = hash_password(data.raw_password)

    await db.commit()
    await db.refresh(user_to_update)

    return UserResponse.model_validate(user_to_update)
  except IntegrityError:
    await db.rollback()
    raise HTTPException(409, "This email is already in use.")


async def get_user(user_id: str, db: AsyncSession) -> UserResponse:
  user = await db.get(User, user_id)

  if user is None:
    raise HTTPException(404, "Account not found.")

  return UserResponse.model_validate(user)


async def authenticate_user(
  data: LoginUserRequest, db: AsyncSession, redis: Redis
) -> tuple[UserResponse, str, str]:
  query = select(User).where(User.email == data.email)
  result = await db.execute(query)
  user = result.scalar_one_or_none()

  if user is None:
    raise HTTPException(401, "Invalid email or password.")

  if verify_password(raw_password=data.raw_password, hashed_password=user.hashed_password):
    access_token = create_jwt_token(user.id)
    refresh_token = generate(size=32)
    hashed_new_refresh_token = sha256(refresh_token.encode("utf-8")).hexdigest()

    await redis.setex(
      name=f"refresh:{hashed_new_refresh_token}",
      value=user.id,
      time=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return UserResponse.model_validate(user), access_token, refresh_token
  else:
    raise HTTPException(401, "Invalid email or password.")


async def logout_user(refresh_token: str, redis: Redis):
  hashed_existing_refresh_token = sha256(refresh_token.encode("utf-8")).hexdigest()
  await redis.delete(f"refresh:{hashed_existing_refresh_token}")


async def refresh_access_token(refresh_token: str, redis: Redis) -> tuple[str, str]:
  hashed_existing_refresh_token = sha256(refresh_token.encode("utf-8")).hexdigest()
  user_id: str = await redis.get(f"refresh:{hashed_existing_refresh_token}")

  if user_id is not None:
    access_token = create_jwt_token(user_id)
    refresh_token = generate(size=32)
    hashed_new_refresh_token = sha256(refresh_token.encode("utf-8")).hexdigest()

    await redis.delete(f"refresh:{hashed_existing_refresh_token}")
    await redis.setex(
      name=f"refresh:{hashed_new_refresh_token}",
      value=user_id,
      time=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return access_token, refresh_token

  raise HTTPException(401, "Your session has expired. Please log in again.")
