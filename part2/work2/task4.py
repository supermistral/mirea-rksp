import time
import logging
import difflib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import utils
from task3 import _get_16bit_checksum

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

DIR_PATH = '.'


class TaskEventHandler(FileSystemEventHandler):
    MAX_FILES_CONTENT_SIZE = 1024 * 1024 * 200  # 200 mb

    def __init__(self):
        self.files: dict[str, str] = {}
        self.files_content_size = 0

    def on_created(self, event):
        if event.is_directory:
            return

        LOG.info(f"File {event.src_path} was created")

        self._add_file(filename=event.src_path)

    def on_modified(self, event):
        if event.is_directory:
            return

        if event.src_path not in self.files:
            LOG.info(f"File {event.src_path} is not stored yet")
        else:
            diff = self._get_diff(filename=event.src_path)
            diff = "\n".join(diff)

            LOG.info(f"File {event.src_path} was modified, diff:\n{diff}")

        self._add_file(filename=event.src_path)

    def on_deleted(self, event):
        if event.is_directory or event.is_synthetic:
            return

        if event.src_path not in self.files:
            LOG.info(f"File {event.src_path} is not stored")
        else:
            content = self.files[event.src_path]
            size = len(content)
            checksum = _get_16bit_checksum(content.encode(encoding="utf-8"))

            LOG.info(f"File {event.src_path} has size = {size} b, checksum = {checksum}")

            self._delete_file(filename=event.src_path)

    def _get_diff(self, filename: str):
        stored_content = self.files[filename].splitlines()
        new_content = self._read_file(filename).splitlines()

        differ = difflib.Differ()
        return differ.compare(stored_content, new_content)

    def _read_file(self, filename: str) -> str:
        with open(filename, 'r') as f:
            content = f.read()
        return content

    def _add_file(self, filename: str):
        content = self._read_file(filename)

        if len(content) + self.files_content_size > self.MAX_FILES_CONTENT_SIZE:
            for stored_filename in self.files.keys():
                self._delete_file(stored_filename)

                if len(content) + self.files_content_size <= self.MAX_FILES_CONTENT_SIZE:
                    break
            else:
                return

        self.files[filename] = content
        self.files_content_size += len(content)

    def _delete_file(self, filename: str):
        self.files_content_size -= len(self.files[filename])
        del self.files[filename]


def main():
    event_handler = TaskEventHandler()
    observer = Observer()

    observer.schedule(event_handler=event_handler, path=DIR_PATH, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    main()
