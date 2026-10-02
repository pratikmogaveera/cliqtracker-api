from fastapi import APIRouter, Depends, HTTPException, Request, Response
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis import get_redis
from app.schemas.common import ApiResponse
from app.schemas.user import LoginUserRequest, UserResponse
from app.services.auth import authenticate_user, logout_user, refresh_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=ApiResponse[UserResponse])
async def authenticate_user_route(
  payload: LoginUserRequest,
  response: Response,
  db: AsyncSession = Depends(get_db),
  redis: Redis = Depends(get_redis),
) -> ApiResponse[UserResponse]:
  user_details, access_token, refresh_token = await authenticate_user(
    data=payload, db=db, redis=redis
  )
  response.set_cookie(key="access_token", value=access_token, httponly=True, samesite="lax")
  response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, samesite="lax")

  return ApiResponse(success=True, data=user_details, message="Logged in successfully!")


@router.post("/logout", response_model=ApiResponse[None])
async def logout_user_route(
  request: Request, response: Response, redis: Redis = Depends(get_redis)
) -> ApiResponse[None]:
  refresh_token = request.cookies.get("refresh_token")

  response.delete_cookie("access_token")
  response.delete_cookie("refresh_token")

  if refresh_token is not None:
    await logout_user(refresh_token, redis)

  return ApiResponse(success=True, message="Logged out successfully.")


@router.post("/refresh", response_model=ApiResponse[None])
async def refresh_access_token_route(
  request: Request, response: Response, redis: Redis = Depends(get_redis)
) -> ApiResponse[None]:
  refresh_token = request.cookies.get("refresh_token")
  response.delete_cookie("access_token")
  response.delete_cookie("refresh_token")

  if refresh_token is None:
    raise HTTPException(401, "Your session has expired. Please log in again.")

  new_access_token, new_refresh_token = await refresh_access_token(
    refresh_token=refresh_token, redis=redis
  )

  response.set_cookie(key="access_token", value=new_access_token, httponly=True, samesite="lax")
  response.set_cookie(key="refresh_token", value=new_refresh_token, httponly=True, samesite="lax")

  return ApiResponse(success=True, message="Session refreshed successfully.")
