from app.services.click_event import create_click_event


async def process_click(ctx, link_id: str) -> None:
  async with ctx["session_factory"]() as session:
    await create_click_event(link_id=link_id, db=session)
