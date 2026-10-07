from geoip2.errors import AddressNotFoundError
from geoip2.models import City
from user_agents import parse
from user_agents.parsers import UserAgent

from app.services.click_event import create_click_event


def get_device_type(ua: UserAgent) -> str | None:
  if ua.is_mobile:
    return "Mobile"
  elif ua.is_tablet:
    return "Tablet"
  elif ua.is_pc:
    return "PC"

  return None


async def process_click(
  ctx, link_id: str, ip: str | None, user_agent: str | None, referrer: str | None
) -> None:
  async with ctx["session_factory"]() as session:
    continent = country = state = browser = device_type = None

    if user_agent:
      ua = parse(user_agent)
      browser = ua.browser.family
      device_type = get_device_type(ua)

    if ip:
      try:
        response: City = ctx["geo_reader"].city(ip)
        continent = response.continent.name
        country = response.country.name
        state = response.subdivisions.most_specific.name
      except AddressNotFoundError:
        pass  # geo stays None

    await create_click_event(
      link_id=link_id,
      db=session,
      continent=continent,
      country=country,
      state=state,
      browser=browser,
      device_type=device_type,
      referrer=referrer,
    )
