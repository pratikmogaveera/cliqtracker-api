from datetime import UTC, datetime
from hashlib import sha256

from fastapi import HTTPException
from nanoid import generate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.service_token import ServiceToken
from app.schemas.service_token import (
  CreateServiceTokenRequest,
  CreateServiceTokenResponse,
  ServiceTokenResponse,
  UpdateServiceTokenRequest,
)


async def create_service_token(
  data: CreateServiceTokenRequest, user_id: str, db: AsyncSession
) -> CreateServiceTokenResponse:
  token = generate(size=32).encode()
  new_service_token = ServiceToken(
    owner_id=user_id,
    title=data.title,
    hashed_token=sha256(token).hexdigest(),
    scopes=data.scopes,
    expiry_at=data.expiry_at,
    revoked_on=None,
  )

  db.add(new_service_token)
  await db.commit()
  await db.refresh(new_service_token)

  return CreateServiceTokenResponse.model_validate(new_service_token).model_copy(
    update={"token": token.decode()}
  )


async def _get_service_token_or_raise(
  token_id: str, user_id: str, db: AsyncSession
) -> ServiceToken:
  service_token = await db.get(ServiceToken, token_id)
  if service_token is None:
    raise HTTPException(404, "No token found.")
  if service_token.owner_id != user_id:
    raise HTTPException(403, "Not authorised.")
  return service_token


async def get_service_tokens(user_id: str, db: AsyncSession) -> list[ServiceTokenResponse]:
  query = select(ServiceToken).where(ServiceToken.owner_id == user_id)
  response = await db.execute(query)
  result = response.scalars().all()

  data = []
  for row in result:
    row: ServiceToken
    data.append(ServiceTokenResponse.model_validate(row))

  return data


async def get_service_token(token_id: str, user_id: str, db: AsyncSession) -> ServiceTokenResponse:
  service_token = await _get_service_token_or_raise(token_id=token_id, user_id=user_id, db=db)

  return ServiceTokenResponse.model_validate(service_token)


async def update_service_token(
  token_id: str, user_id: str, data: UpdateServiceTokenRequest, db: AsyncSession
) -> ServiceTokenResponse:
  service_token = await _get_service_token_or_raise(token_id=token_id, user_id=user_id, db=db)

  if data.title is not None:
    service_token.title = data.title
  if data.revoke_token:
    service_token.revoked_on = datetime.now(UTC)

  await db.commit()
  await db.refresh(service_token)

  return ServiceTokenResponse.model_validate(service_token)


async def rotate_service_token(
  token_id: str, user_id: str, db: AsyncSession
) -> CreateServiceTokenResponse:
  existing_token = await _get_service_token_or_raise(token_id=token_id, user_id=user_id, db=db)

  if existing_token.revoked_on is not None:
    raise HTTPException(status_code=403, detail="Cannot rotate a revoked token.")

  token = generate(size=32).encode()
  rotated_token = ServiceToken(
    owner_id=user_id,
    title=existing_token.title,
    hashed_token=sha256(token).hexdigest(),
    scopes=existing_token.scopes,
    expiry_at=existing_token.expiry_at,
    revoked_on=None,
  )

  existing_token.revoked_on = datetime.now(UTC)
  db.add(rotated_token)
  await db.commit()
  await db.refresh(existing_token)
  await db.refresh(rotated_token)

  return CreateServiceTokenResponse.model_validate(rotated_token).model_copy(
    update={"token": token.decode()}
  )


async def delete_service_token(token_id: str, user_id: str, db: AsyncSession) -> None:
  existing_token = await _get_service_token_or_raise(token_id=token_id, user_id=user_id, db=db)

  await db.delete(existing_token)
  await db.commit()
