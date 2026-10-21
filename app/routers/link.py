from fastapi import APIRouter

from app.core.config import settings
from app.deps import DB, CurrentUserId, RedisClient, RequiredScope
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.link import CreateLinkRequest, LinkResponse, QRCodeImageResponse, UpdateLinkRequest
from app.services.link import (
  create_link,
  delete_link,
  generate_link_qr_code,
  get_link,
  get_links,
  update_link,
)

router = APIRouter(prefix="/links", tags=["Link"])


@router.get(
  "/",
  response_model=ApiResponse[PaginatedResponse[LinkResponse]],
  dependencies=[RequiredScope("links:read")],
)
async def get_links_route(
  user_id: CurrentUserId,
  db: DB,
  page: int = 1,
  limit: int = settings.PAGE_SIZE,
) -> ApiResponse[PaginatedResponse[LinkResponse]]:
  paginated_links = await get_links(user_id=user_id, db=db, page=page, limit=limit)
  return ApiResponse(
    success=True, message="Link details fetched successfully.", data=paginated_links
  )


@router.get(
  "/{link_id}",
  response_model=ApiResponse[LinkResponse],
  dependencies=[RequiredScope("links:read")],
)
async def get_link_route(link_id: str, user_id: CurrentUserId, db: DB) -> ApiResponse[LinkResponse]:
  link = await get_link(link_id=link_id, user_id=user_id, db=db)
  return ApiResponse(success=True, message="Link details fetched successfully.", data=link)


@router.post(
  "/",
  response_model=ApiResponse[LinkResponse],
  dependencies=[RequiredScope("links:write")],
)
async def create_link_route(
  payload: CreateLinkRequest,
  user_id: CurrentUserId,
  db: DB,
) -> ApiResponse[LinkResponse]:
  link = await create_link(user_id=user_id, data=payload, db=db)
  return ApiResponse(success=True, message="Link created successfully.", data=link)


@router.delete(
  "/{link_id}",
  response_model=ApiResponse[None],
  dependencies=[RequiredScope("links:delete")],
)
async def delete_link_route(
  link_id: str,
  user_id: CurrentUserId,
  db: DB,
  redis: RedisClient,
) -> ApiResponse[None]:
  await delete_link(link_id=link_id, user_id=user_id, db=db, redis=redis)
  return ApiResponse(success=True, message="Link deleted successfully.")


@router.patch(
  "/{link_id}",
  response_model=ApiResponse[LinkResponse],
  dependencies=[RequiredScope("links:write")],
)
async def update_link_route(
  link_id: str,
  data: UpdateLinkRequest,
  user_id: CurrentUserId,
  db: DB,
  redis: RedisClient,
) -> ApiResponse[LinkResponse]:
  link = await update_link(link_id=link_id, data=data, user_id=user_id, db=db, redis=redis)
  return ApiResponse(success=True, message="Link updated successfully.", data=link)


@router.get(
  "/{link_id}/qr",
  response_model=ApiResponse[QRCodeImageResponse],
  dependencies=[RequiredScope("links:read")],
)
async def generate_link_qr_code_route(
  link_id: str, user_id: CurrentUserId, db: DB
) -> ApiResponse[QRCodeImageResponse]:
  data = await generate_link_qr_code(link_id=link_id, user_id=user_id, db=db)
  return ApiResponse(success=True, data=data, message="QR Code generated successfully.")
