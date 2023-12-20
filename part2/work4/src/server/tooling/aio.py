import asyncio
import functools
from typing import Callable
from typing import Awaitable


def async_to_sync(f: Callable[..., Awaitable]) -> Callable:
    @functools.wraps(f)
    def wrapper(self, *args, **kwargs):
        return asyncio.ensure_future(f(self, *args, **kwargs))

    return wrapper
