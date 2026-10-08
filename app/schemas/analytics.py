from pydantic import BaseModel


class TimeseriesItem(BaseModel):
  date: str
  hour: str | None = None
  count: int


class AnalyticsSummaryResponse(BaseModel):
  total_clicks: int
  top_country: str | None
  top_browser: str | None
  top_referrer: str | None


class AnalyticsByTimeseries(BaseModel):
  data: list[TimeseriesItem]


class AnalyticsByGeolocation(BaseModel):
  data: dict[str, int]


class AnalyticsByBrowserAndDevice(BaseModel):
  browsers: dict[str, int]
  device_types: dict[str, int]
  os: dict[str, int]


class AnalyticsByReferrer(BaseModel):
  data: dict[str, int]
