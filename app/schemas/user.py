from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CreateUserRequest(BaseModel):
  first_name: str = Field(min_length=1, max_length=25)
  last_name: str = Field(min_length=1, max_length=25)
  email: EmailStr
  raw_password: str = Field(min_length=8, max_length=25)


class UpdateUserRequest(BaseModel):
  first_name: str | None = Field(default=None, min_length=1, max_length=25)
  last_name: str | None = Field(default=None, min_length=1, max_length=25)
  email: EmailStr | None = None
  raw_password: str | None = Field(default=None, min_length=8, max_length=25)


class LoginUserRequest(BaseModel):
  email: EmailStr
  raw_password: str = Field(min_length=8, max_length=25)


class UserResponse(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: str
  first_name: str
  last_name: str
  email: str
  created_on: datetime
  updated_on: datetime
