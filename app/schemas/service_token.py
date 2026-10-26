from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CreateServiceTokenRequest(BaseModel):
  title: str = Field(min_length=1, max_length=50)
  scopes: str = Field(min_length=1, pattern=r"^([a-z]+:[a-z]+)( [a-z]+:[a-z]+)*$")
  expiry_at: datetime

  @field_validator("expiry_at")
  @classmethod
  def ensure_timezone(cls, v):
    if v is not None and v.tzinfo is None:
      return v.replace(tzinfo=UTC)
    return v


class UpdateServiceTokenRequest(BaseModel):
  title: str | None = Field(default=None, min_length=1, max_length=50)
  revoke_token: bool = False


class CreateServiceTokenResponse(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: str
  owner_id: str
  title: str
  token: str = ""
  scopes: str
  expiry_at: datetime
  revoked_on: datetime | None
  created_on: datetime
  updated_on: datetime


class ServiceTokenResponse(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: str
  owner_id: str
  title: str
  scopes: str
  expiry_at: datetime
  revoked_on: datetime | None
  created_on: datetime
  updated_on: datetime
