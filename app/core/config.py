from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  DATABASE_URL: str
  FRONTEND_URL: str
  REDIS_URL: str
  JWT_SECRET: str
  JWT_ALGORITHM: str = "HS256"
  ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
  REFRESH_TOKEN_EXPIRE_DAYS: int = 7
  ENVIRONMENT: str = "dev"
  PAGE_SIZE: int = 25
  REDIS_LINK_CACHE_EXPIRY: int = 1 * 60 * 60  # 1hr

  model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()  # type: ignore
