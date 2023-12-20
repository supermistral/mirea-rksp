from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    def to_json(self) -> str:
        raise NotImplementedError()
