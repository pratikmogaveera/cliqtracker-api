from typing import Any

from fastapi_mail import MessageSchema, MessageType
from pydantic import NameEmail

from app.core.email import client


async def send_email(
  to: str,
  first_name: str,
  subject: str,
  template_name: str,
  template_body: dict[str, Any] | None = None,
):
  message = MessageSchema(
    recipients=[NameEmail(email=to, name=first_name)],
    subject=subject,
    subtype=MessageType.html,
    template_body=template_body,
  )

  await client.send_message(message, template_name=template_name)
