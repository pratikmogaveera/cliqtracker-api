from datetime import UTC, datetime
from hashlib import sha256
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, Request, Security
from fastapi.security import APIKeyHeader
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import authenticate_jwt
from app.models.service_token import ServiceToken

Token = Annotated[str | None, Cookie()]
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_user_id(
  request: Request,
  access_token: Token = None,
  api_key: str = Security(api_key_header),
  db: AsyncSession = Depends(get_db),
) -> str:
  print(f"access_token: {access_token} | api_key: {api_key}")
  if access_token is None and api_key is None:
    raise HTTPException(401, "Invalid/missing access token.")

  try:
    if access_token is None:
      query = select(ServiceToken).where(
        ServiceToken.hashed_token == sha256(api_key.encode()).hexdigest()
      )
      response = await db.execute(query)
      service_token = response.scalars().first()

      if service_token is None:
        raise HTTPException(401, "Invalid/missing access token.")

      if service_token.revoked_on is not None or service_token.expiry_at < datetime.now(UTC):
        raise HTTPException(401, "Expired access token.")

      request.state.auth_via = "api_key"
      request.state.scopes = service_token.scopes
      user_id = service_token.owner_id

    else:
      user_id = authenticate_jwt(token=access_token)

      request.state.auth_via = "cookie"
    return user_id
  except JWTError:
    raise HTTPException(401, "Invalid/missing access token.")


def require_scope(required_scopes: str):
  async def check_scope(request: Request, _: str = Depends(get_user_id)) -> None:
    if request.state.auth_via == "api_key":
      required_scopes_list = required_scopes.split(" ")
      token_scopes = request.state.scopes.split(" ")

      result = all(scope in token_scopes for scope in required_scopes_list)
      if not result:
        raise HTTPException(403, "You don't have sufficient access.")

  return check_scope
