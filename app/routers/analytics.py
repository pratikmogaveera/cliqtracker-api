from datetime import date

from fastapi import APIRouter

from app.deps import DB, CurrentUserId, RequiredScope
from app.schemas.analytics import (
  AnalyticsByBrowserAndDevice,
  AnalyticsByGeolocation,
  AnalyticsByParams,
  AnalyticsByReferrer,
  AnalyticsByTimeseries,
  AnalyticsSummaryResponse,
)
from app.schemas.common import ApiResponse
from app.services.analytics import (
  Granularity,
  get_link_devices,
  get_link_geo,
  get_link_params,
  get_link_referrers,
  get_link_summary,
  get_link_timeseries,
)

router = APIRouter(prefix="/links/{link_id}/analytics", tags=["Analytics"])


@router.get(
  "/summary",
  response_model=ApiResponse[AnalyticsSummaryResponse],
  dependencies=[RequiredScope("analytics:read")],
)
async def get_link_summary_router(
  link_id: str,
  user_id: CurrentUserId,
  db: DB,
  start_date: date | None = None,
  end_date: date | None = None,
) -> ApiResponse[AnalyticsSummaryResponse]:
  data = await get_link_summary(
    link_id=link_id, start_date=start_date, end_date=end_date, user_id=user_id, db=db
  )
  return ApiResponse(
    success=True, data=data, message="Link analytics summary fetched successfully."
  )


@router.get(
  "/timeseries",
  response_model=ApiResponse[AnalyticsByTimeseries],
  dependencies=[RequiredScope("analytics:read")],
)
async def get_link_timeseries_router(
  link_id: str,
  user_id: CurrentUserId,
  db: DB,
  start_date: date | None = None,
  end_date: date | None = None,
  granularity: Granularity = Granularity.DAILY,
) -> ApiResponse[AnalyticsByTimeseries]:
  data = await get_link_timeseries(
    link_id=link_id,
    start_date=start_date,
    end_date=end_date,
    user_id=user_id,
    granularity=granularity,
    db=db,
  )
  return ApiResponse(
    success=True, data=data, message="Link timeseries analytics fetched successfully."
  )


@router.get(
  "/geo",
  response_model=ApiResponse[AnalyticsByGeolocation],
  dependencies=[RequiredScope("analytics:read")],
)
async def get_link_geo_route(
  link_id: str,
  user_id: CurrentUserId,
  db: DB,
  start_date: date | None = None,
  end_date: date | None = None,
) -> ApiResponse[AnalyticsByGeolocation]:
  data = await get_link_geo(
    link_id=link_id, start_date=start_date, end_date=end_date, user_id=user_id, db=db
  )
  return ApiResponse(
    success=True, data=data, message="Link geolocation analytics fetched successfully."
  )


@router.get(
  "/devices",
  response_model=ApiResponse[AnalyticsByBrowserAndDevice],
  dependencies=[RequiredScope("analytics:read")],
)
async def get_link_devices_route(
  link_id: str,
  user_id: CurrentUserId,
  db: DB,
  start_date: date | None = None,
  end_date: date | None = None,
) -> ApiResponse[AnalyticsByBrowserAndDevice]:
  data = await get_link_devices(
    link_id=link_id, start_date=start_date, end_date=end_date, user_id=user_id, db=db
  )
  return ApiResponse(success=True, data=data, message="Link device analytics fetched successfully.")


@router.get(
  "/referrers",
  response_model=ApiResponse[AnalyticsByReferrer],
  dependencies=[RequiredScope("analytics:read")],
)
async def get_link_referrers_route(
  link_id: str,
  user_id: CurrentUserId,
  db: DB,
  start_date: date | None = None,
  end_date: date | None = None,
) -> ApiResponse[AnalyticsByReferrer]:
  data = await get_link_referrers(
    link_id=link_id, start_date=start_date, end_date=end_date, user_id=user_id, db=db
  )
  return ApiResponse(
    success=True, data=data, message="Link referrer analytics fetched successfully."
  )


@router.get(
  "/params",
  response_model=ApiResponse[AnalyticsByParams],
  dependencies=[RequiredScope("analytics:read")],
)
async def get_link_params_route(
  link_id: str,
  user_id: CurrentUserId,
  db: DB,
  start_date: date | None = None,
  end_date: date | None = None,
) -> ApiResponse[AnalyticsByParams]:
  data = await get_link_params(
    link_id=link_id, start_date=start_date, end_date=end_date, user_id=user_id, db=db
  )
  return ApiResponse(success=True, data=data, message="Link params analytics fetched successfully.")
