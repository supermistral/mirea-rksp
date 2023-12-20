from pydantic import ConfigDict, BaseModel


class Config(BaseModel):
    model_config = ConfigDict(validate_default=False)

    HOST: str = "localhost"
    PORT: int = 6565
    DATABASE_URL: str = "sqlite+aiosqlite:///database.db"


def get_config() -> Config:
    config = Config()

    return config


config = get_config()
