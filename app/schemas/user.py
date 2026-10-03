from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class CreateUserRequest(BaseModel):
  first_name: str
  last_name: str
  email: EmailStr
  raw_password: str


class UpdateUserRequest(BaseModel):
  first_name: str | None = None
  last_name: str | None = None
  email: EmailStr | None = None
  raw_password: str | None = None


class LoginUserRequest(BaseModel):
  email: EmailStr
  raw_password: str


class UserResponse(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: str
  first_name: str
  last_name: str
  email: str
  created_on: datetime
  updated_on: datetime
