from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.deps import get_user_id
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.link import CreateLinkRequest, LinkResponse, UpdateLinkRequest
from app.services.link import create_link, delete_link, get_link, get_links, update_link

router = APIRouter(prefix="/links", tags=["Link"])


@router.get("/", response_model=ApiResponse[PaginatedResponse[LinkResponse]])
async def get_links_route(
  page: int = 1,
  limit: int = settings.PAGE_SIZE,
  user_id: str = Depends(get_user_id),
  db: AsyncSession = Depends(get_db),
) -> ApiResponse[PaginatedResponse[LinkResponse]]:
  paginated_links = await get_links(user_id=user_id, db=db, page=page, limit=limit)
  return ApiResponse(
    success=True, message="Link details fetched successfully.", data=paginated_links
  )


@router.get("/{link_id}", response_model=ApiResponse[LinkResponse])
async def get_link_route(
  link_id: str, user_id: str = Depends(get_user_id), db: AsyncSession = Depends(get_db)
) -> ApiResponse[LinkResponse]:
  link = await get_link(link_id=link_id, user_id=user_id, db=db)
  return ApiResponse(success=True, message="Link details fetched successfully.", data=link)


@router.post("/", response_model=ApiResponse[LinkResponse])
async def create_link_route(
  payload: CreateLinkRequest,
  user_id: str = Depends(get_user_id),
  db: AsyncSession = Depends(get_db),
) -> ApiResponse[LinkResponse]:
  link = await create_link(user_id=user_id, data=payload, db=db)
  return ApiResponse(success=True, message="Link created successfully.", data=link)


@router.delete("/{link_id}", response_model=ApiResponse[None])
async def delete_link_route(
  link_id: str, user_id: str = Depends(get_user_id), db: AsyncSession = Depends(get_db)
) -> ApiResponse[None]:
  await delete_link(link_id=link_id, user_id=user_id, db=db)
  return ApiResponse(success=True, message="Link deleted successfully")


@router.patch("/{link_id}", response_model=ApiResponse[LinkResponse])
async def update_link_route(
  link_id: str,
  data: UpdateLinkRequest,
  user_id: str = Depends(get_user_id),
  db: AsyncSession = Depends(get_db),
) -> ApiResponse[LinkResponse]:
  link = await update_link(link_id=link_id, data=data, user_id=user_id, db=db)
  return ApiResponse(success=True, message="Link updated successfully.", data=link)
