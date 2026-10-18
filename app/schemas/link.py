from datetime import UTC, datetime

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, field_validator


class CreateLinkRequest(BaseModel):
  title: str
  full_url: AnyHttpUrl
  short_code: str | None = None
  expiry_at: datetime | None = None
  raw_password: str | None = None

  @field_validator("expiry_at")
  @classmethod
  def ensure_timezone(cls, v):
    if v is not None and v.tzinfo is None:
      return v.replace(tzinfo=UTC)
    return v


class UpdateLinkRequest(BaseModel):
  title: str | None = None
  full_url: AnyHttpUrl | None = None
  is_active: bool | None = None
  expiry_at: datetime | None = None
  clear_expiry: bool = False
  raw_password: str | None = None
  clear_password: bool = False

  @field_validator("expiry_at")
  @classmethod
  def ensure_timezone(cls, v):
    if v is not None and v.tzinfo is None:
      return v.replace(tzinfo=UTC)
    return v


class LinkResponse(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: str
  title: str
  full_url: str
  short_code: str
  owner_id: str | None
  is_active: bool
  is_custom_slug: bool
  expiry_at: datetime | None = None
  is_protected: bool = False
  click_count: int | None = None
  created_on: datetime
  updated_on: datetime


class CachedLinkData(BaseModel):
  link_id: str
  full_url: str
  expiry_at: datetime | None = None
  is_protected: bool = False
