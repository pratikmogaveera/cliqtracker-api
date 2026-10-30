from pydantic import BaseModel


class TimeseriesItem(BaseModel):
  date: str
  hour: str | None = None
  count: int


class ReferrerItem(BaseModel):
  referrer: str
  total_clicks: int
  unique_clicks: int


class ParamItem(BaseModel):
  param: str
  value: str
  count: int


class AnalyticsSummaryResponse(BaseModel):
  total_clicks: int
  unique_clicks: int
  countries_reached: int
  avg_clicks_per_day: int


class AnalyticsByTimeseries(BaseModel):
  data: list[TimeseriesItem]


class AnalyticsByGeolocation(BaseModel):
  continents: dict[str, int]
  countries: dict[str, int]


class AnalyticsByBrowserAndDevice(BaseModel):
  browsers: dict[str, int]
  device_types: dict[str, int]
  os: dict[str, int]


class AnalyticsByReferrer(BaseModel):
  data: list[ReferrerItem]


class AnalyticsByParams(BaseModel):
  data: list[ParamItem]
