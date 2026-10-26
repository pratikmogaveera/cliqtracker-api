from datetime import UTC, date, datetime, time
from enum import Enum

from fastapi import HTTPException
from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.click_event import ClickEvent
from app.models.link import Link
from app.schemas.analytics import (
  AnalyticsByBrowserAndDevice,
  AnalyticsByGeolocation,
  AnalyticsByReferrer,
  AnalyticsByTimeseries,
  AnalyticsSummaryResponse,
  ReferrerItem,
  TimeseriesItem,
)


def _date_filters(start_date: date | None, end_date: date | None) -> list:
  filters = []
  if start_date:
    filters.append(
      ClickEvent.clicked_at >= datetime.combine(start_date, time.min).replace(tzinfo=UTC)
    )
  if end_date:
    filters.append(
      ClickEvent.clicked_at <= datetime.combine(end_date, time.max).replace(tzinfo=UTC)
    )
  return filters


async def _verify_link_ownership(link_id: str, user_id: str, db: AsyncSession) -> None:
  link = await db.get(Link, link_id)
  if link is None:
    raise HTTPException(404, "Link not found.")

  if link.owner_id != user_id:
    raise HTTPException(403, "Not authorised.")


class Granularity(Enum):
  HOURLY = "hour"
  DAILY = "day"


async def get_link_summary(
  link_id: str, user_id: str, start_date: date | None, end_date: date | None, db: AsyncSession
) -> AnalyticsSummaryResponse:
  await _verify_link_ownership(link_id=link_id, user_id=user_id, db=db)

  query = select(
    func.count(ClickEvent.id),
    func.count(distinct(ClickEvent.hashed_ip)),
    func.count(distinct(ClickEvent.country)),
    func.min(ClickEvent.clicked_at),
    func.max(ClickEvent.clicked_at),
  ).where(ClickEvent.link_id == link_id, *_date_filters(start_date, end_date))

  response = (await db.execute(query)).first()

  total_clicks, unique_clicks, countries_reached, min_date, max_date = (
    response if response else (0, 0, 0, None, None)
  )

  if not total_clicks or min_date is None or max_date is None:
    return AnalyticsSummaryResponse(
      total_clicks=0, unique_clicks=0, countries_reached=0, avg_clicks_per_day=0
    )

  first_click = min_date.replace(tzinfo=UTC)
  last_click = max_date.replace(tzinfo=UTC)

  days = (last_click - first_click).days or 1
  avg_clicks_per_day = total_clicks // days

  return AnalyticsSummaryResponse(
    total_clicks=total_clicks,
    unique_clicks=unique_clicks,
    countries_reached=countries_reached,
    avg_clicks_per_day=avg_clicks_per_day,
  )


async def get_link_timeseries(
  link_id: str,
  user_id: str,
  start_date: date | None,
  end_date: date | None,
  db: AsyncSession,
  granularity: Granularity = Granularity.HOURLY,
) -> AnalyticsByTimeseries:
  await _verify_link_ownership(link_id=link_id, user_id=user_id, db=db)

  query = (
    select(
      func.date_trunc(granularity.value, ClickEvent.clicked_at).label("bucket"),
      func.count(ClickEvent.id),
    )
    .where(ClickEvent.link_id == link_id, *_date_filters(start_date, end_date))
    .group_by("bucket")
    .order_by("bucket")
  )

  response = await db.execute(query)
  result = []

  for bucket, count in response.all():
    item = TimeseriesItem(
      date=bucket.strftime("%Y-%m-%d"),
      hour=str(bucket.hour) if granularity == Granularity.HOURLY else None,
      count=count,
    )
    result.append(item)

  return AnalyticsByTimeseries(data=result)


async def get_link_geo(
  link_id: str, user_id: str, start_date: date | None, end_date: date | None, db: AsyncSession
) -> AnalyticsByGeolocation:
  await _verify_link_ownership(link_id=link_id, user_id=user_id, db=db)

  continents = {}
  countries = {}

  query = (
    select(ClickEvent.country, ClickEvent.continent, func.count(ClickEvent.id))
    .where(ClickEvent.link_id == link_id, *_date_filters(start_date, end_date))
    .group_by(ClickEvent.country, ClickEvent.continent)
    .order_by(func.count(ClickEvent.id).desc())
  )

  rows = (await db.execute(query)).all()

  for country, continent, count in rows:
    if country:
      countries[country] = count
    if continent:
      continents[continent] = continents.get(continent, 0) + count

  return AnalyticsByGeolocation(countries=countries, continents=continents)


async def get_link_devices(
  link_id: str, user_id: str, start_date: date | None, end_date: date | None, db: AsyncSession
) -> AnalyticsByBrowserAndDevice:
  await _verify_link_ownership(link_id=link_id, user_id=user_id, db=db)

  query = (
    select(ClickEvent.browser, ClickEvent.device_type, ClickEvent.os, func.count(ClickEvent.id))
    .where(ClickEvent.link_id == link_id, *_date_filters(start_date, end_date))
    .group_by(ClickEvent.browser, ClickEvent.device_type, ClickEvent.os)
    .order_by(func.count(ClickEvent.id).desc())
  )

  rows = (await db.execute(query)).all()

  browsers: dict[str, int] = {}
  device_types: dict[str, int] = {}
  os_dict: dict[str, int] = {}

  for browser, device_type, os, count in rows:
    if browser:
      browsers[browser] = browsers.get(browser, 0) + count
    if device_type:
      device_types[device_type] = device_types.get(device_type, 0) + count
    if os:
      os_dict[os] = os_dict.get(os, 0) + count

  return AnalyticsByBrowserAndDevice(browsers=browsers, device_types=device_types, os=os_dict)


async def get_link_referrers(
  link_id: str, user_id: str, start_date: date | None, end_date: date | None, db: AsyncSession
) -> AnalyticsByReferrer:
  await _verify_link_ownership(link_id=link_id, user_id=user_id, db=db)

  query = (
    select(
      ClickEvent.referrer, func.count(ClickEvent.id), func.count(distinct(ClickEvent.hashed_ip))
    )
    .where(ClickEvent.link_id == link_id, *_date_filters(start_date, end_date))
    .group_by(ClickEvent.referrer)
    .order_by(func.count(ClickEvent.id).desc())
  )

  rows = (await db.execute(query)).all()

  result = []
  for key, count, unique_count in rows:
    result.append(
      ReferrerItem(
        referrer=key if key else "Direct", total_clicks=count, unique_clicks=unique_count
      )
    )

  return AnalyticsByReferrer(data=result)
