import pytest
import mock

from server.tooling.api import load_data, dump_data, with_repository


class TestLoadData:
    @pytest.mark.parametrize(
        "data",
        [
            '{"key": "value", "int_key": 3, "arr_key": [1, 2, 3]}',
            b'{"key": "value", "int_key": 3, "arr_key": [1, 2, 3]}',
        ]
    )
    def test_converts_json_to_python(self, data):
        obj = load_data(data)

        assert obj == {"key": "value", "int_key": 3, "arr_key": [1, 2, 3]}


class TestDumpData:
    def test_converts_python_to_json(self):
        data = {"key": "value", "int_key": 3, "arr_key": [1, 2, 3]}

        bytes_string = dump_data(data)

        assert bytes_string == b'{"key": "value", "int_key": 3, "arr_key": [1, 2, 3]}'


@pytest.mark.asyncio
class TestWithRepository:
    async def test_calls_wrapped_method(self):
        method = mock.AsyncMock(return_value="Some value")
        repository_creator = mock.Mock()
        wrapped = with_repository(repository_creator=repository_creator)(method)

        result = await wrapped(1, "abc", a=[1, 2])

        assert result == "Some value"
        method.assert_awaited_once_with(1, "abc", a=[1, 2], repo=repository_creator.return_value)

    async def test_calls_repository_with_session(self, mock_session):
        method = mock.AsyncMock()
        repository_creator = mock.Mock()
        wrapped = with_repository(repository_creator=repository_creator)(method)

        await wrapped()

        repository_creator.assert_called_once_with(db_session=mock_session)
