from fastapi import APIRouter

from app.deps import DB, CurrentUserId, RequiredScope
from app.schemas.common import ApiResponse
from app.schemas.dashboard import DashboardSummaryResponse
from app.services.dashboard import DashboardPeriod, get_dashboard_summary

router = APIRouter(prefix="/analytics", tags=["Dashboard"])


@router.get(
  "/dashboard-summary",
  response_model=ApiResponse[DashboardSummaryResponse],
  dependencies=[RequiredScope("analytics:read")],
)
async def get_dashboard_summary_route(
  user_id: CurrentUserId,
  db: DB,
  period: DashboardPeriod = "7d",
) -> ApiResponse[DashboardSummaryResponse]:
  data = await get_dashboard_summary(period=period, user_id=user_id, db=db)
  return ApiResponse(success=True, data=data, message="Dashboard summary fetched successfully.")
