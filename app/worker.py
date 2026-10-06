from arq import func
from arq.connections import RedisSettings

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models import click_event, link, user  # noqa: F401
from app.tasks import process_click

REDIS_SETTINGS = RedisSettings.from_dsn(dsn=settings.REDIS_URL)


async def startup(ctx):
  print("[Worker] Server started.")
  ctx["session_factory"] = AsyncSessionLocal


async def shutdown(ctx):
  print("[Worker] Server shutting down.")


class WorkerSettings:
  functions = [func(process_click, max_tries=3)]
  on_startup = startup
  on_shutdown = shutdown
  redis_settings = REDIS_SETTINGS
