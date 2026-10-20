from time import time

from redis.asyncio import Redis


async def check_rate_limit(
  redis: Redis, bucket_id: str, max_tokens: int, refill_rate: float
) -> bool:
  value: str | None = await redis.get(f"rate:{bucket_id}")
  now = time()

  if value is not None:
    last_call, last_tokens = value.split("|")
    last_call = float(last_call)
    last_tokens = float(last_tokens)
    refill_amount = (now - last_call) * refill_rate

    if last_tokens + refill_amount >= 1:
      await redis.setex(
        name=f"rate:{bucket_id}",
        value=f"{now}|{min(max_tokens, last_tokens + refill_amount) - 1}",
        time=int(max_tokens / refill_rate),
      )
      return True
    else:
      return False

  else:
    await redis.setex(
      name=f"rate:{bucket_id}",
      value=f"{now}|{max_tokens - 1}",
      time=int(max_tokens / refill_rate),
    )
    return True
