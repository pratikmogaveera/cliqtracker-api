from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import CreateUserRequest, UpdateUserRequest, UserResponse


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


async def delete_user(user_id: str, db: AsyncSession) -> None:
  user = await db.get(User, user_id)
  if user is None:
    raise HTTPException(404, "Account not found.")
  await db.delete(user)
  await db.commit()


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
