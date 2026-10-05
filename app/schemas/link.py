from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel, ConfigDict


class CreateLinkRequest(BaseModel):
  title: str
  full_url: AnyHttpUrl
  short_code: str | None = None


class UpdateLinkRequest(BaseModel):
  title: str | None = None
  full_url: AnyHttpUrl | None = None
  is_active: bool | None = None


class LinkResponse(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: str
  title: str
  full_url: str
  short_code: str
  owner_id: str | None
  is_active: bool
  is_custom_slug: bool
  click_count: int | None = None
  created_on: datetime
  updated_on: datetime


class CachedLinkData(BaseModel):
  link_id: str
  full_url: str
