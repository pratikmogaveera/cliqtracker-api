from datetime import UTC, datetime, timedelta
from typing import Literal

from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.click_event import ClickEvent
from app.models.link import Link
from app.schemas.dashboard import DashboardSummaryResponse

DashboardPeriod = Literal["1d", "7d", "30d", "90d"]


async def get_dashboard_summary(
  period: DashboardPeriod, user_id: str, db: AsyncSession
) -> DashboardSummaryResponse:
  period_int = int(period[:-1])

  now = datetime.now(UTC)
  current_start = now - timedelta(days=period_int)
  prev_start = now - timedelta(days=period_int * 2)

  def _window_query(start, end=None):
    q = (
      select(
        func.count(ClickEvent.id).label("total_clicks"),
        func.count(distinct(ClickEvent.hashed_ip)).label("unique_clicks"),
        func.count(distinct(ClickEvent.country)).label("countries_reached"),
      )
      .join(target=Link, onclause=Link.id == ClickEvent.link_id)
      .where(Link.owner_id == user_id)
      .filter(ClickEvent.clicked_at >= start)
    )
    if end is not None:
      q = q.filter(ClickEvent.clicked_at < end)
    return q

  def _delta(current: int, previous: int) -> float:
    if previous == 0 and current == 0:
      return 0.0
    if previous == 0:
      return 100.0
    if current == 0:
      return -100.0
    return ((current - previous) / previous) * 100

  curr = (await db.execute(_window_query(current_start))).first()
  total_clicks, unique_clicks, countries_reached = curr if curr is not None else (0, 0, 0)
  avg_clicks_per_day = total_clicks // period_int

  prev = (await db.execute(_window_query(prev_start, end=current_start))).first()
  prev_total_clicks, prev_unique_clicks, prev_countries_reached = (
    prev if prev is not None else (0, 0, 0)
  )
  prev_avg_clicks_per_day = prev_total_clicks // period_int

  return DashboardSummaryResponse(
    total_clicks=total_clicks,
    total_clicks_delta=_delta(total_clicks, prev_total_clicks),
    unique_clicks=unique_clicks,
    unique_clicks_delta=_delta(unique_clicks, prev_unique_clicks),
    countries_reached=countries_reached,
    countries_reached_delta=_delta(countries_reached, prev_countries_reached),
    avg_clicks_per_day=avg_clicks_per_day,
    avg_clicks_per_day_delta=_delta(avg_clicks_per_day, prev_avg_clicks_per_day),
  )
