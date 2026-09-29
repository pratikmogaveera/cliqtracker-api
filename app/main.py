from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import Redis

from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
  redis = Redis.from_url(url=settings.REDIS_URL, decode_responses=True)
  app.state.redis = redis

  yield

  await redis.close()


app = FastAPI(lifespan=lifespan)
