from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BASE_DIR: Path = Path(__file__).parent
    TEMPLATES_DIR: Path = BASE_DIR / "templates"

    USER_FILES_PATH: str = "/content"
    USER_FILES_DIRECTORY: Path = BASE_DIR.parent.parent / "user-files"


settings = Settings()
