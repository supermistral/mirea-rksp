import json
from typing import Any
from typing import Union


def load_data(data: Union[str, bytes]) -> Any:
    return json.loads(data)


def dump_data(data: Any) -> bytes:
    return json.dumps(data).encode("utf-8")
