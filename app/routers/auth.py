from fastapi import APIRouter, HTTPException, Request, Response

from app.core.config import settings
from app.deps import DB, CookieOnly, RedisClient
from app.schemas.common import ApiResponse
from app.schemas.user import LoginUserRequest, UserResponse
from app.services.auth import authenticate_user, logout_user, refresh_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=ApiResponse[UserResponse])
async def authenticate_user_route(
  payload: LoginUserRequest,
  response: Response,
  db: DB,
  redis: RedisClient,
) -> ApiResponse[UserResponse]:
  user_details, access_token, refresh_token = await authenticate_user(
    data=payload, db=db, redis=redis
  )
  response.set_cookie(
    key="access_token",
    value=access_token,
    httponly=True,
    samesite="lax",
    secure=settings.ENVIRONMENT == "prod",
  )
  response.set_cookie(
    key="refresh_token",
    value=refresh_token,
    httponly=True,
    samesite="lax",
    secure=settings.ENVIRONMENT == "prod",
  )

  return ApiResponse(success=True, data=user_details, message="Logged in successfully!")


@router.post("/logout", response_model=ApiResponse[None], dependencies=[CookieOnly])
async def logout_user_route(
  request: Request, response: Response, redis: RedisClient
) -> ApiResponse[None]:
  refresh_token = request.cookies.get("refresh_token")

  response.delete_cookie("access_token")
  response.delete_cookie("refresh_token")

  if refresh_token is not None:
    await logout_user(refresh_token, redis)

  return ApiResponse(success=True, message="Logged out successfully.")


@router.post("/refresh", response_model=ApiResponse[None], dependencies=[CookieOnly])
async def refresh_access_token_route(
  request: Request, response: Response, redis: RedisClient
) -> ApiResponse[None]:
  refresh_token = request.cookies.get("refresh_token")
  response.delete_cookie("access_token")
  response.delete_cookie("refresh_token")

  if refresh_token is None:
    raise HTTPException(401, "Your session has expired. Please log in again.")

  new_access_token, new_refresh_token = await refresh_access_token(
    refresh_token=refresh_token, redis=redis
  )

  response.set_cookie(
    key="access_token",
    value=new_access_token,
    httponly=True,
    samesite="lax",
    secure=settings.ENVIRONMENT == "prod",
  )
  response.set_cookie(
    key="refresh_token",
    value=new_refresh_token,
    httponly=True,
    samesite="lax",
    secure=settings.ENVIRONMENT == "prod",
  )

  return ApiResponse(success=True, message="Session refreshed successfully.")
