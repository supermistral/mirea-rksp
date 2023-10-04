import json
from typing import Any
from typing import Union
from typing import Callable
from typing import Awaitable
from functools import wraps

from db import get_session


def load_data(data: Union[str, bytes]) -> Any:
    return json.loads(data)


def dump_data(data: Any) -> bytes:
    return json.dumps(data).encode("utf-8")


def with_repository(repository_creator: type) -> Callable[[Callable[..., Awaitable]], Callable]:
    def wrapper(method: Callable[..., Awaitable]):
        @wraps(method)
        async def inner(*args, **kwargs):
            async with get_session() as session:
                repo = repository_creator(db_session=session)
                kwargs.update({"repo": repo})

                result = await method(*args, **kwargs)

            return result

        return inner

    return wrapper
