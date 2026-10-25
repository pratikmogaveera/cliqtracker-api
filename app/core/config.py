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
  MMDB_PATH: str = "GeoLite2-City.mmdb"
  MAXMIND_LICENSE_KEY: str = ""
  PAGE_SIZE: int = 25
  REDIS_LINK_CACHE_EXPIRY: int = 1 * 60 * 60  # 1hr
  LIMIT_COOKIE: int = 30
  LIMIT_API_KEY: int = 60
  LIMIT_UNAUTH: int = 10
  REFILL_COOKIE: float = 0.5  # per sec
  REFILL_API_KEY: float = 1.0  # per sec
  REFILL_UNAUTH: float = 0.1  # per sec

  model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()  # type: ignore
