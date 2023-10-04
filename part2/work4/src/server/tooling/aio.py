import asyncio
from typing import Callable
from typing import Awaitable
from functools import wraps


def async_to_sync(f: Callable[..., Awaitable]) -> Callable:
    @wraps(f)
    def wrapper(*args, **kwargs):
        asyncio.run(f(*args, **kwargs))

    return wrapper
