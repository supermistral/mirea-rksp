import random
import time
import queue
import uuid
import logging
import concurrent.futures
from functools import wraps
from typing import Optional
from typing import Callable
from dataclasses import dataclass
from enum import Enum

import utils
from constants import MILLISECONDS

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

THREAD_POOL = concurrent.futures.ThreadPoolExecutor(max_workers=8)

MIN_FILE_SIZE = 10
MAX_FILE_SIZE = 100
FILE_QUEUE_SIZE = 5


def threaded_method(target: Callable) -> Callable:
    @wraps(target)
    def wrapper(*args, **kwargs):
        return THREAD_POOL.submit(target, *args, **kwargs)

    return wrapper


class FileType(Enum):
    XML = 1
    JSON = 2
    XLS = 3


@dataclass
class File:
    type: FileType
    size: int


class FileQueue(queue.Queue):
    ...


class FileGenerator:
    def __init__(self, queue: FileQueue):
        self.queue = queue

    @threaded_method
    def generate(
        self,
        min_file_size: int = MIN_FILE_SIZE,
        max_file_size: int = MAX_FILE_SIZE,
    ):
        LOG.info(f"Generator is starting to generate")

        while True:
            seconds = random.randint(100, 1000)
            time.sleep(seconds * MILLISECONDS)

            file = File(
                type=random.choice(list(FileType)),
                size=random.randint(min_file_size, max_file_size),
            )

            LOG.info(f"Generator generated {file}")

            self.queue.put(file)


class FileHandler:
    HANDLE_SLEEP_SECONDS = 2

    def __init__(self, file_type: FileType, queue: FileQueue):
        self.queue = queue
        self.file_type = file_type
        self._id = uuid.uuid4().hex

    def _get_file_from_queue(self) -> Optional[File]:
        file: File = self.queue.get()

        if file.type == self.file_type:
            self.queue.task_done()
            return file

        self.queue.put(file)
        return None

    @threaded_method
    def handle(self):
        while True:
            time.sleep(self.HANDLE_SLEEP_SECONDS)
            file = self._get_file_from_queue()

            LOG.info(f"Handler [{self._id}] got {file}")

            if file is None:
                continue

            time.sleep(7 * file.size * MILLISECONDS)
            # Some heavy work ...

            LOG.info(f"Handler [{self._id}] completed handling")


def main():
    file_queue = FileQueue(maxsize=FILE_QUEUE_SIZE)

    generator = FileGenerator(queue=file_queue)
    handlers = [
        FileHandler(
            file_type=file_type,
            queue=file_queue,
        )
        for file_type in list(FileType)
    ]

    for _ in range(0):
        handlers.append(
            FileHandler(
                file_type=random.choice(list(FileType)),
                queue=file_queue,
            )
        )

    generator.generate()

    for handler in handlers:
        handler.handle()

    file_queue.join()


if __name__ == "__main__":
    main()
