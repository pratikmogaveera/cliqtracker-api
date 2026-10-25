from hashlib import sha256

from fastapi import Request


def extract_client_details(request: Request) -> tuple[str | None, str | None, str | None]:
  forwarded_for = request.headers.get("x-forwarded-for")
  ip = (
    forwarded_for.split(",")[0].strip()
    if forwarded_for
    else (request.client.host if request.client else None)
  )
  hashed_ip = sha256(ip.encode()).hexdigest() if ip is not None else None
  user_agent = request.headers.get("user-agent")
  referrer = request.headers.get("referer")

  return hashed_ip, user_agent, referrer
