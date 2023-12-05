from pathlib import Path
from typing import Optional
import mimetypes
import shutil

from fastapi import UploadFile

from ..config import settings


class FileService:
    MIME_TYPES = mimetypes.MimeTypes()

    def __init__(self, user_directory: Path = settings.USER_FILES_DIRECTORY):
        self._user_directory = user_directory

    @staticmethod
    def get_media_type_by_name(name: str) -> Optional[str]:
        return FileService.MIME_TYPES.guess_type(name)[0]

    @property
    def file_directory(self) -> str:
        return self._user_directory

    def get_all_names(self) -> list[str]:
        path = self._user_directory.glob("**/*")
        return [x.name for x in path if x.is_file()]

    def get_by_name(self, name: str):
        with open(self._get_file_path(name), mode="rb") as f:
            yield from f

    def upload_files(self, files: list[UploadFile]):
        for file in files:
            self.upload_file(file)

    def upload_file(self, file: UploadFile):
        new_filename = self._get_file_path(file.filename)

        try:
            with open(new_filename, mode="wb") as f:
                shutil.copyfileobj(file.file, f)
        finally:
            file.file.close()

    def _get_file_path(self, name: str):
        return self._user_directory / name
