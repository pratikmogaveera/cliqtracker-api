from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ClickEventResponse(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: str
  link_id: str
  continent: str | None = None
  country: str | None = None
  state: str | None = None
  browser: str | None = None
  device_type: str | None = None
  os: str | None = None
  referrer: str | None = None
  clicked_at: datetime
