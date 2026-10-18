from pydantic import BaseModel


class UnlockRedirectUrlRequest(BaseModel):
  password: str


class UnlockRedirectUrlResponse(BaseModel):
  full_url: str
