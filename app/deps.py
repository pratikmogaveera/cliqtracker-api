from typing import Annotated

from fastapi import Cookie, HTTPException
from jose import JWTError

from app.core.security import authenticate_jwt

Token = Annotated[str | None, Cookie()]


def get_user_id(access_token: Token = None) -> str:
  if access_token is None:
    raise HTTPException(401, "Invalid/missing access token.")
  try:
    user_id = authenticate_jwt(token=access_token)
    return user_id
  except JWTError:
    raise HTTPException(401, "Invalid/missing access token.")
