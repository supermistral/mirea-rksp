from pydantic import BaseConfig


class Config(BaseConfig):
    SERVER_HOST: str = "localhost"
    SERVER_PORT: int = 6565


def get_config() -> Config:
    config = Config()

    return config


config = get_config()
