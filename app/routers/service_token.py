from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.deps import get_user_id
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
  token_id: str, user_id: str = Depends(get_user_id), db: AsyncSession = Depends(get_db)
) -> ApiResponse[ServiceTokenResponse]:
  data = await get_service_token(token_id=token_id, user_id=user_id, db=db)
  return ApiResponse(success=True, data=data, message="Service token details fetched successfully.")


@router.get("/", response_model=ApiResponse[list[ServiceTokenResponse]])
async def get_service_tokens_route(
  user_id: str = Depends(get_user_id), db: AsyncSession = Depends(get_db)
) -> ApiResponse[list[ServiceTokenResponse]]:
  data = await get_service_tokens(user_id=user_id, db=db)
  return ApiResponse(
    success=True, data=data, message="Service tokens details fetched successfully."
  )


@router.post("/", response_model=ApiResponse[CreateServiceTokenResponse])
async def create_service_token_route(
  payload: CreateServiceTokenRequest,
  user_id: str = Depends(get_user_id),
  db: AsyncSession = Depends(get_db),
) -> ApiResponse[CreateServiceTokenResponse]:
  data = await create_service_token(data=payload, user_id=user_id, db=db)
  return ApiResponse(success=True, data=data, message="Service token created successfully.")


@router.patch("/{token_id}", response_model=ApiResponse[ServiceTokenResponse])
async def update_service_token_route(
  token_id: str,
  payload: UpdateServiceTokenRequest,
  user_id: str = Depends(get_user_id),
  db: AsyncSession = Depends(get_db),
) -> ApiResponse[ServiceTokenResponse]:
  data = await update_service_token(token_id=token_id, data=payload, user_id=user_id, db=db)
  return ApiResponse(success=True, data=data, message="Service token updated successfully.")


@router.patch("/{token_id}/rotate", response_model=ApiResponse[CreateServiceTokenResponse])
async def rotate_service_token_route(
  token_id: str,
  user_id: str = Depends(get_user_id),
  db: AsyncSession = Depends(get_db),
) -> ApiResponse[CreateServiceTokenResponse]:
  data = await rotate_service_token(token_id=token_id, user_id=user_id, db=db)
  return ApiResponse(success=True, data=data, message="Service token rotated successfully.")


@router.delete("/{token_id}", response_model=ApiResponse[None])
async def delete_service_token_route(
  token_id: str,
  user_id: str = Depends(get_user_id),
  db: AsyncSession = Depends(get_db),
) -> ApiResponse[None]:
  data = await delete_service_token(token_id=token_id, user_id=user_id, db=db)
  return ApiResponse(success=True, data=data, message="Service token deleted successfully.")
