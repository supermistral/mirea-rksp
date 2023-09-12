import time
import logging
import psutil
import os
from inspect import iscoroutine
from functools import wraps
from typing import Callable

logging.basicConfig(format="%(asctime)s:%(threadName)s: %(message)s")

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


def print_result(target: Callable) -> Callable:
    @wraps(target)
    async def wrapper(*args, **kwargs):
        start_time = time.monotonic_ns()
        LOG.info(f"Starting execution of the function '{target.__qualname__}'")

        process = psutil.Process(os.getpid())
        start_memory_usage = process.memory_info().rss

        if iscoroutine(target):
            result = await target(*args, **kwargs)
        else:
            result = target(*args, **kwargs)

        memory_usage = process.memory_info().rss - start_memory_usage

        execution_time = time.monotonic_ns() - start_time
        LOG.info(
            f"The function '{target.__qualname__}' was executed with result: "
            f"{result}, time = {execution_time / 10**6} ms, "
            f"memory_usage = {memory_usage / 1024} Kb"
        )

        return result

    return wrapper
