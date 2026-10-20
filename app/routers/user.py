from fastapi import APIRouter, Response

from app.deps import DB, CurrentUserId, RedisClient
from app.schemas.common import ApiResponse
from app.schemas.user import CreateUserRequest, UpdateUserRequest, UserResponse
from app.services.auth import create_session
from app.services.user import create_user, delete_user, get_user, update_user

router = APIRouter(prefix="/users", tags=["User"])


@router.get("/me", response_model=ApiResponse[UserResponse])
async def get_user_route(user_id: CurrentUserId, db: DB) -> ApiResponse[UserResponse]:
  user = await get_user(user_id=user_id, db=db)
  return ApiResponse(success=True, message="Account details fetched successfully.", data=user)


@router.post("/register", response_model=ApiResponse[UserResponse])
async def create_user_route(
  payload: CreateUserRequest,
  response: Response,
  db: DB,
  redis: RedisClient,
) -> ApiResponse[UserResponse]:
  new_user = await create_user(data=payload, db=db)

  access_token, refresh_token = await create_session(user_id=new_user.id, redis=redis)
  response.set_cookie(key="access_token", value=access_token, httponly=True, samesite="lax")
  response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, samesite="lax")

  return ApiResponse(success=True, message="User created successfully.", data=new_user)


@router.delete("/me", response_model=ApiResponse[None])
async def delete_user_route(
  response: Response, user_id: CurrentUserId, db: DB
) -> ApiResponse[None]:
  await delete_user(user_id=user_id, db=db)
  response.delete_cookie("access_token")
  response.delete_cookie("refresh_token")
  return ApiResponse(success=True, message="User deleted successfully")


@router.patch("/me", response_model=ApiResponse[UserResponse])
async def update_user_route(
  payload: UpdateUserRequest,
  user_id: CurrentUserId,
  db: DB,
) -> ApiResponse[UserResponse]:
  updated_user = await update_user(data=payload, user_id=user_id, db=db)
  return ApiResponse(success=True, message="User updated successfully.", data=updated_user)
