from pathlib import Path

from fastapi_mail import ConnectionConfig, FastMail

from app.core.config import settings

connection_config = ConnectionConfig(
  MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
  MAIL_FROM=settings.MAIL_FROM,
  MAIL_USERNAME=settings.MAIL_USERNAME,
  MAIL_PASSWORD=settings.MAIL_PASSWORD,
  MAIL_PORT=settings.MAIL_PORT,
  MAIL_SERVER=settings.MAIL_SERVER,
  MAIL_SSL_TLS=False,
  MAIL_STARTTLS=True,
  USE_CREDENTIALS=True,
  VALIDATE_CERTS=True,
  TEMPLATE_FOLDER=Path(__file__).parent.parent / "templates" / "email",
)

client = FastMail(config=connection_config)
