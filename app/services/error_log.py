from sqlalchemy.ext.asyncio import AsyncSession

from app.models.error_log import ErrorLog
from app.schemas.error_log import CreateErrorLog


async def create_error_log(data: CreateErrorLog, db: AsyncSession) -> None:
  log = ErrorLog(
    method=data.method,
    path=data.path,
    user_id=data.user_id,
    error_type=data.error_type,
    error_message=data.error_message,
    traceback=data.traceback,
  )

  db.add(log)
  await db.commit()
