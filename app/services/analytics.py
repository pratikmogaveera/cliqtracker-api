from enum import Enum

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.click_event import ClickEvent
from app.models.link import Link
from app.schemas.analytics import (
  AnalyticsByBrowserAndDevice,
  AnalyticsByGeolocation,
  AnalyticsByReferrer,
  AnalyticsByTimeseries,
  AnalyticsSummaryResponse,
  TimeseriesItem,
)


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
  link_id: str, user_id: str, db: AsyncSession
) -> AnalyticsSummaryResponse:
  await _verify_link_ownership(link_id=link_id, user_id=user_id, db=db)
  query = select(func.count(ClickEvent.id)).where(ClickEvent.link_id == link_id)
  total = (await db.execute(query)).scalar() or 0

  query = (
    select(ClickEvent.browser, func.count(ClickEvent.id))
    .where(ClickEvent.link_id == link_id)
    .where(ClickEvent.browser.is_not(None))
    .group_by(ClickEvent.browser)
    .order_by(func.count(ClickEvent.id).desc())
    .limit(1)
  )
  result = await db.execute(query)
  rows = result.all()

  browser = rows[0][0] if rows else None

  query = (
    select(ClickEvent.country, func.count(ClickEvent.id))
    .where(ClickEvent.link_id == link_id)
    .where(ClickEvent.country.is_not(None))
    .group_by(ClickEvent.country)
    .order_by(func.count(ClickEvent.id).desc())
    .limit(1)
  )
  result = await db.execute(query)
  rows = result.all()

  country = rows[0][0] if rows else None
  query = (
    select(ClickEvent.referrer, func.count(ClickEvent.id))
    .where(ClickEvent.link_id == link_id)
    .where(ClickEvent.referrer.is_not(None))
    .group_by(ClickEvent.referrer)
    .order_by(func.count(ClickEvent.id).desc())
    .limit(1)
  )
  result = await db.execute(query)
  rows = result.all()

  referrer = rows[0][0] if rows else None

  return AnalyticsSummaryResponse(
    total_clicks=total, top_browser=browser, top_country=country, top_referrer=referrer
  )


async def get_link_timeseries(
  link_id: str, user_id: str, db: AsyncSession, granularity: Granularity = Granularity.HOURLY
) -> AnalyticsByTimeseries:
  await _verify_link_ownership(link_id=link_id, user_id=user_id, db=db)
  query = (
    select(
      func.date_trunc(granularity.value, ClickEvent.clicked_at).label("bucket"),
      func.count(ClickEvent.id),
    )
    .where(ClickEvent.link_id == link_id)
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


async def get_link_geo(link_id: str, user_id: str, db: AsyncSession) -> AnalyticsByGeolocation:
  await _verify_link_ownership(link_id=link_id, user_id=user_id, db=db)
  data = dict()
  query = (
    select(ClickEvent.country, func.count(ClickEvent.id))
    .where(ClickEvent.link_id == link_id)
    .group_by(ClickEvent.country)
    .order_by(func.count(ClickEvent.id).desc())
  )
  result = await db.execute(query)
  rows = result.all()

  for country, count in rows:
    if country is not None:
      data[country] = count

  return AnalyticsByGeolocation(data=data)


async def get_link_devices(
  link_id: str, user_id: str, db: AsyncSession
) -> AnalyticsByBrowserAndDevice:
  await _verify_link_ownership(link_id=link_id, user_id=user_id, db=db)
  query = (
    select(ClickEvent.browser, func.count(ClickEvent.id))
    .where(ClickEvent.link_id == link_id)
    .group_by(ClickEvent.browser)
    .order_by(func.count(ClickEvent.id).desc())
  )
  result = await db.execute(query)
  rows = result.all()
  browser = dict()
  for key, value in rows:
    if key is not None:
      browser[key] = value

  query = (
    select(ClickEvent.device_type, func.count(ClickEvent.id))
    .where(ClickEvent.link_id == link_id)
    .group_by(ClickEvent.device_type)
    .order_by(func.count(ClickEvent.id).desc())
  )
  result = await db.execute(query)
  rows = result.all()
  device_type = dict()
  for key, value in rows:
    if key is not None:
      device_type[key] = value

  query = (
    select(ClickEvent.os, func.count(ClickEvent.id))
    .where(ClickEvent.link_id == link_id)
    .group_by(ClickEvent.os)
    .order_by(func.count(ClickEvent.id).desc())
  )
  result = await db.execute(query)
  rows = result.all()
  os = dict()
  for key, value in rows:
    if key is not None:
      os[key] = value

  return AnalyticsByBrowserAndDevice(browsers=browser, device_types=device_type, os=os)


async def get_link_referrers(link_id: str, user_id: str, db: AsyncSession) -> AnalyticsByReferrer:
  await _verify_link_ownership(link_id=link_id, user_id=user_id, db=db)
  query = (
    select(ClickEvent.referrer, func.count(ClickEvent.id))
    .where(ClickEvent.link_id == link_id)
    .group_by(ClickEvent.referrer)
    .order_by(func.count(ClickEvent.id).desc())
  )
  result = await db.execute(query)
  rows = result.all()
  referrer = dict()
  for key, value in rows:
    if key is not None:
      referrer[key] = value

  return AnalyticsByReferrer(data=referrer)
