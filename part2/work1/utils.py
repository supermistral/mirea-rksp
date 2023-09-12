import time
import logging
from functools import wraps
from typing import Callable

logging.basicConfig(format="%(asctime)s:%(threadName)s: %(message)s")

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


def print_result(target: Callable) -> Callable:
    @wraps(target)
    def wrapper(*args, **kwargs):
        start_time = time.monotonic_ns()
        LOG.info(f"Starting execution of the function '{target.__qualname__}'")

        result = target(*args, **kwargs)

        execution_time = time.monotonic_ns() - start_time
        LOG.info(
            f"The function '{target.__qualname__}' was executed with result: "
            f"{result}, time = {execution_time / 10**6} ms"
        )

        return result

    return wrapper
