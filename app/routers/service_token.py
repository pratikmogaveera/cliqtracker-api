from fastapi import APIRouter

from app.deps import DB, CurrentUserId
from app.schemas.common import ApiResponse
from app.schemas.service_token import (
  CreateServiceTokenRequest,
  CreateServiceTokenResponse,
  ServiceTokenResponse,
  UpdateServiceTokenRequest,
)
from app.services.service_token import (
  create_service_token,
  delete_service_token,
  get_service_token,
  get_service_tokens,
  rotate_service_token,
  update_service_token,
)

router = APIRouter(prefix="/service-token", tags=["ServiceToken"])


@router.get("/{token_id}", response_model=ApiResponse[ServiceTokenResponse])
async def get_service_token_route(
  token_id: str, user_id: CurrentUserId, db: DB
) -> ApiResponse[ServiceTokenResponse]:
  data = await get_service_token(token_id=token_id, user_id=user_id, db=db)
  return ApiResponse(success=True, data=data, message="Service token details fetched successfully.")


@router.get("/", response_model=ApiResponse[list[ServiceTokenResponse]])
async def get_service_tokens_route(
  user_id: CurrentUserId, db: DB
) -> ApiResponse[list[ServiceTokenResponse]]:
  data = await get_service_tokens(user_id=user_id, db=db)
  return ApiResponse(
    success=True, data=data, message="Service token list fetched successfully."
  )


@router.post("/", response_model=ApiResponse[CreateServiceTokenResponse])
async def create_service_token_route(
  payload: CreateServiceTokenRequest,
  user_id: CurrentUserId,
  db: DB,
) -> ApiResponse[CreateServiceTokenResponse]:
  data = await create_service_token(data=payload, user_id=user_id, db=db)
  return ApiResponse(success=True, data=data, message="Service token created successfully.")


@router.patch("/{token_id}", response_model=ApiResponse[ServiceTokenResponse])
async def update_service_token_route(
  token_id: str,
  payload: UpdateServiceTokenRequest,
  user_id: CurrentUserId,
  db: DB,
) -> ApiResponse[ServiceTokenResponse]:
  data = await update_service_token(token_id=token_id, data=payload, user_id=user_id, db=db)
  return ApiResponse(success=True, data=data, message="Service token updated successfully.")


@router.patch("/{token_id}/rotate", response_model=ApiResponse[CreateServiceTokenResponse])
async def rotate_service_token_route(
  token_id: str,
  user_id: CurrentUserId,
  db: DB,
) -> ApiResponse[CreateServiceTokenResponse]:
  data = await rotate_service_token(token_id=token_id, user_id=user_id, db=db)
  return ApiResponse(success=True, data=data, message="Service token rotated successfully.")


@router.delete("/{token_id}", response_model=ApiResponse[None])
async def delete_service_token_route(
  token_id: str,
  user_id: CurrentUserId,
  db: DB,
) -> ApiResponse[None]:
  data = await delete_service_token(token_id=token_id, user_id=user_id, db=db)
  return ApiResponse(success=True, data=data, message="Service token deleted successfully.")
