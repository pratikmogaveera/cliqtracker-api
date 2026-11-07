from pydantic import BaseModel


class DashboardSummaryResponse(BaseModel):
  total_clicks: int
  total_clicks_delta: float
  unique_clicks: int
  unique_clicks_delta: float
  countries_reached: int
  countries_reached_delta: float
  avg_clicks_per_day: int
  avg_clicks_per_day_delta: float
