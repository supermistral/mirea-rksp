import pytest
from unittest import mock


class AsyncContextManager:
    async def __aenter__(self): ...
    async def __aexit__(self, exc_type, exc, traceback): ...


@pytest.fixture(autouse=True)
def mock_session():
    with mock.patch("server.db.session.async_session") as mocked_session:
        mocked_session.return_value.__aenter__.return_value.begin = mock.MagicMock((AsyncContextManager))
        yield mocked_session.return_value.__aenter__.return_value


@pytest.fixture(autouse=True)
def mock_sleep():
    with mock.patch("asyncio.sleep") as mocked:
        yield mocked
