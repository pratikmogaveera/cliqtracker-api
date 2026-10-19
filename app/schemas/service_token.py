from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, field_validator


class CreateServiceTokenRequest(BaseModel):
  title: str
  scopes: str
  expiry_at: datetime

  @field_validator("expiry_at")
  @classmethod
  def ensure_timezone(cls, v):
    if v is not None and v.tzinfo is None:
      return v.replace(tzinfo=UTC)
    return v


class UpdateServiceTokenRequest(BaseModel):
  title: str | None = None
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
