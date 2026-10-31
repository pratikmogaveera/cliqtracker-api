import io
import os
import tarfile
import urllib.request

from arq import func
from arq.connections import RedisSettings
from geoip2 import database

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models import click_event, link, user  # noqa: F401
from app.tasks import process_click, send_email_job

REDIS_SETTINGS = RedisSettings.from_dsn(dsn=settings.REDIS_URL.get_secret_value())


def _download_mmdb() -> None:
  if not settings.MAXMIND_LICENSE_KEY:
    print(
      "[Worker] MAXMIND_LICENSE_KEY not set — skipping mmdb download. Geo lookups will be unavailable."
    )
    return

  print(f"[Worker] {settings.MMDB_PATH} not found — downloading from MaxMind...")
  url = (
    f"https://download.maxmind.com/app/geoip_download"
    f"?edition_id=GeoLite2-City&license_key={settings.MAXMIND_LICENSE_KEY}&suffix=tar.gz"
  )

  with urllib.request.urlopen(url) as response:
    data = response.read()

  with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
    for member in tar.getmembers():
      if member.name.endswith("GeoLite2-City.mmdb"):
        f = tar.extractfile(member)
        dir_path = os.path.dirname(settings.MMDB_PATH)
        if dir_path:
          os.makedirs(dir_path, exist_ok=True)
        with open(settings.MMDB_PATH, "wb") as out:
          out.write(f.read())  # type: ignore
        print("[Worker] GeoLite2-City.mmdb downloaded successfully.")
        return

  print("[Worker] Failed to find GeoLite2-City.mmdb in the downloaded archive.")


async def startup(ctx):
  print("[Worker] Server started.")

  if not os.path.exists(settings.MMDB_PATH):
    _download_mmdb()

  ctx["session_factory"] = AsyncSessionLocal
  ctx["geo_reader"] = (
    database.Reader(settings.MMDB_PATH) if os.path.exists(settings.MMDB_PATH) else None
  )


async def shutdown(ctx):
  if ctx.get("geo_reader"):
    ctx["geo_reader"].close()
  print("[Worker] Server shutting down.")


class WorkerSettings:
  functions = [func(process_click, max_tries=3), func(send_email_job, max_tries=3)]
  on_startup = startup
  on_shutdown = shutdown
  redis_settings = REDIS_SETTINGS
