from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.deps import get_user_id
from app.schemas.analytics import (
  AnalyticsByBrowserAndDevice,
  AnalyticsByGeolocation,
  AnalyticsByReferrer,
  AnalyticsByTimeseries,
  AnalyticsSummaryResponse,
)
from app.schemas.common import ApiResponse
from app.services.analytics import (
  Granularity,
  get_link_devices,
  get_link_geo,
  get_link_referrers,
  get_link_summary,
  get_link_timeseries,
)

router = APIRouter(prefix="/links/{link_id}/analytics", tags=["Analytics"])


@router.get("/summary", response_model=ApiResponse[AnalyticsSummaryResponse])
async def get_link_summary_router(
  link_id: str,
  user_id: str = Depends(get_user_id),
  db: AsyncSession = Depends(get_db),
) -> ApiResponse[AnalyticsSummaryResponse]:
  data = await get_link_summary(link_id=link_id, user_id=user_id, db=db)
  return ApiResponse(
    success=True, data=data, message="Link's analytics' summary fetched successfully"
  )


@router.get("/timeseries", response_model=ApiResponse[AnalyticsByTimeseries])
async def get_link_timeseries_router(
  link_id: str,
  granularity: Granularity = Granularity.DAILY,
  user_id: str = Depends(get_user_id),
  db: AsyncSession = Depends(get_db),
) -> ApiResponse[AnalyticsByTimeseries]:
  data = await get_link_timeseries(link_id=link_id, user_id=user_id, granularity=granularity, db=db)
  return ApiResponse(
    success=True, data=data, message="Link's timeseries analytics fetched successfully"
  )


@router.get("/geo", response_model=ApiResponse[AnalyticsByGeolocation])
async def get_link_geo_route(
  link_id: str, user_id: str = Depends(get_user_id), db: AsyncSession = Depends(get_db)
) -> ApiResponse[AnalyticsByGeolocation]:
  data = await get_link_geo(link_id=link_id, user_id=user_id, db=db)
  return ApiResponse(
    success=True, data=data, message="Link's geolocation analytics fetched successfully"
  )


@router.get("/devices", response_model=ApiResponse[AnalyticsByBrowserAndDevice])
async def get_link_devices_route(
  link_id: str, user_id: str = Depends(get_user_id), db: AsyncSession = Depends(get_db)
) -> ApiResponse[AnalyticsByBrowserAndDevice]:
  data = await get_link_devices(link_id=link_id, user_id=user_id, db=db)
  return ApiResponse(
    success=True, data=data, message="Link's browser and device analytics fetched successfully"
  )


@router.get("/referrers", response_model=ApiResponse[AnalyticsByReferrer])
async def get_link_referrers_route(
  link_id: str, user_id: str = Depends(get_user_id), db: AsyncSession = Depends(get_db)
) -> ApiResponse[AnalyticsByReferrer]:
  data = await get_link_referrers(link_id=link_id, user_id=user_id, db=db)
  return ApiResponse(
    success=True, data=data, message="Link's referrer analytics fetched successfully"
  )
