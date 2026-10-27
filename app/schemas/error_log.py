from pydantic import BaseModel


class CreateErrorLog(BaseModel):
  method: str
  path: str
  user_id: str | None = None
  error_type: str
  error_message: str
  traceback: str
