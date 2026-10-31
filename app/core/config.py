from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  DATABASE_URL: SecretStr
  FRONTEND_URL: str
  REDIS_URL: SecretStr
  JWT_SECRET: SecretStr
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
  MAIL_USERNAME: str
  MAIL_PASSWORD: SecretStr
  MAIL_FROM: str
  MAIL_FROM_NAME: str
  MAIL_SERVER: str
  MAIL_PORT: int

  model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()  # type: ignore


def get_user_readable_validation_error(type: str, ctx) -> str:
  if type == "missing":
    return "Please provide all the required fields."
  if type == "string_too_short" and ctx is not None:
    return f"Must be at least {ctx['min_length']} characters."
  if type == "string_too_long" and ctx is not None:
    return f"Must be at most {ctx['max_length']} characters."
  if type == "string_pattern_mismatch":
    return "Please provide input in correct format."
  if type == "url_parsing":
    return "Please provide a valid URL."
  if type == "value_error" and ctx is not None:
    return ctx["reason"]
  if type == "datetime_parsing":
    return "Please provide a valid date."

  return "Invalid input."
