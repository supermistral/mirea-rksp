from pydantic import BaseConfig


class Config(BaseConfig):
    HOST: str = "localhost"
    PORT: int = 6565
    DATABASE_URL: str = "sqlite+aiosqlite:///database.db"


def get_config() -> Config:
    config = Config()

    return config


config = get_config()
