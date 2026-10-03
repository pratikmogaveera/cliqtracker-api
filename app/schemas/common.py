from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
  success: bool
  message: str
  data: T | None = None


class PaginatedResponse(BaseModel, Generic[T]):
  items: list[T]
  has_next_page: bool
  page: int
  limit: int
