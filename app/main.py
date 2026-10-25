from contextlib import asynccontextmanager

from arq import create_pool
from arq.connections import RedisSettings
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from redis.asyncio import Redis

from app.core.config import settings
from app.middleware import RateLimitMiddleware
from app.routers.analytics import router as analytics_router
from app.routers.auth import router as auth_router
from app.routers.link import router as link_router
from app.routers.redirect import router as redirect_router
from app.routers.service_token import router as service_token_router
from app.routers.user import router as user_router

REDIS_SETTINGS = RedisSettings.from_dsn(settings.REDIS_URL)

origins = [settings.FRONTEND_URL]
if settings.ENVIRONMENT == "dev":
  origins.append("http://localhost:3000")


@asynccontextmanager
async def lifespan(app: FastAPI):
  redis = Redis.from_url(url=settings.REDIS_URL, decode_responses=True)
  arq_pool = await create_pool(REDIS_SETTINGS)

  app.state.redis = redis
  app.state.arq_pool = arq_pool

  yield

  await redis.close()
  await arq_pool.aclose()


app = FastAPI(lifespan=lifespan, redirect_slashes=False)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
  return JSONResponse(
    status_code=exc.status_code,
    content={"success": False, "message": exc.detail, "data": None},
  )


app.add_middleware(RateLimitMiddleware)
app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,  # List of allowed origins
  allow_credentials=True,  # Support cookies/auth headers
  allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
  allow_headers=["*"],  # Allow all request headers
)


app.include_router(analytics_router)
app.include_router(auth_router)
app.include_router(link_router)
app.include_router(redirect_router)
app.include_router(service_token_router)
app.include_router(user_router)
