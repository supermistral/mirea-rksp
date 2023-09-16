import random
import time
import uuid
import multiprocessing
from dataclasses import dataclass
from enum import Enum

import reactivex
from reactivex import operators as ops
from reactivex.scheduler import ThreadPoolScheduler

MIN_FILE_SIZE = 10
MAX_FILE_SIZE = 100

MILLISECONDS = 10**(-3)


class FileType(Enum):
    XML = 1
    JSON = 2
    XLS = 3


@dataclass
class File:
    type: FileType
    size: int


class FileGenerator:
    def __init__(
        self,
        subject: reactivex.Subject,
        min_file_size: int = MIN_FILE_SIZE,
        max_file_size: int = MAX_FILE_SIZE,
    ):
        self.subject = subject
        self.min_file_size = min_file_size
        self.max_file_size = max_file_size

    def generate(self):
        print(f"Generator is starting to generate")

        while True:
            seconds = random.randint(100, 1000)
            time.sleep(seconds * MILLISECONDS)

            file = File(
                type=random.choice(list(FileType)),
                size=random.randint(self.min_file_size, self.max_file_size),
            )

            print(f"Generator generated {file}")

            self.subject.on_next(file)


class FileHandler:
    HANDLE_SLEEP_SECONDS = 2

    def __init__(self, file_type: FileType):
        self.file_type = file_type
        self._id = uuid.uuid4().hex

    def handle(self, file: File):
        if file.type != self.file_type:
            return

        print(f"Handler [{self._id}] got {file}")

        time.sleep(7 * file.size * MILLISECONDS)
        # Some heavy work ...

        print(f"Handler [{self._id}] completed handling")


def create_threadpool() -> ThreadPoolScheduler:
    optimal_thread_count = multiprocessing.cpu_count()
    return ThreadPoolScheduler(optimal_thread_count)


def main():
    threadpool = create_threadpool()
    subject = reactivex.Subject()

    generator = FileGenerator(subject=subject)
    handlers = [
        FileHandler(file_type=file_type)
        for file_type in list(FileType)
    ]

    subject.pipe(
        ops.subscribe_on(threadpool)
    )

    for handler in handlers:
        subject.subscribe(on_next=handler.handle)

    generator.generate()


if __name__ == "__main__":
    main()
