import pytest
from unittest import mock

from rsocket.streams.exceptions import FinishedIterator
from rsocket.payload import Payload

from server.shopping_list.streams import product_creating_stream, product_getting_stream, ProductCreatingSubscriber
from server.shopping_list.schemas import ProductCreate as ProductCreateSchema
from .helpers import create_product_from_db


@pytest.fixture(autouse=True)
def mocked_repository():
    with mock.patch("server.shopping_list.streams.ProductRepository", autospec=True) as mocked:
        yield mocked


@pytest.mark.asyncio
class TestProductCreatingStream:
    async def test_calls_method_of_repository_exactly_max_ttl_times(self, mocked_repository):
        mocked_repository.return_value.get_first_added_after_time = mock.AsyncMock(return_value=None)

        publisher = product_creating_stream(limit=1)
        await publisher._start_generator()

        async for payload, is_complete in publisher._generate_next_n(1):
            ...

        mocked_repository.return_value.get_first_added_after_time.mock_calls == [mock.call() for _ in range(101)]

    async def test_generates_payload_with_actual_data(self, mocked_repository):
        product = create_product_from_db(id=1, text="Text")
        mocked_repository.return_value.get_first_added_after_time = mock.AsyncMock(side_effect=[None, product])
        counter = 0

        publisher = product_creating_stream(limit=1)
        await publisher._start_generator()

        async for payload, is_complete in publisher._generate_next_n(2):
            counter += 1

        encoded_product = '{"id":1,"text":"Text","quantity":1,"created_at":"2000-01-01T00:00:00","completed":false}'

        assert counter == 1
        assert payload.data == encoded_product.encode("utf-8")

    async def test_saves_order_of_generation(self, mocked_repository):
        products = [
            create_product_from_db(id=1, text="text1"),
            create_product_from_db(id=2, text="text2"),
            create_product_from_db(id=3, text="text3"),
        ]
        repo_return_values = [None, *products, None]
        counter = 0
        mocked_repository.return_value.get_first_added_after_time = mock.AsyncMock(side_effect=repo_return_values)

        publisher = product_creating_stream(limit=3)
        await publisher._start_generator()

        payloads = []
        is_completes = []

        async for payload, is_complete in publisher._generate_next_n(4):
            payloads.append(payload)
            is_completes.append(is_complete)
            counter += 1

        encoded_products = [
            '{"id":1,"text":"text1","quantity":1,"created_at":"2000-01-01T00:00:00","completed":false}',
            '{"id":2,"text":"text2","quantity":1,"created_at":"2000-01-01T00:00:00","completed":false}',
            '{"id":3,"text":"text3","quantity":1,"created_at":"2000-01-01T00:00:00","completed":false}',
        ]

        assert counter == 3

        for payload, encoded_product in zip(payloads, encoded_products):
            assert payload.data == encoded_product.encode("utf-8")

        assert not all(is_completes[:-1])
        assert is_completes[-1]


@pytest.mark.asyncio
class TestProductGettingStream:
    async def test_calls_method_of_repository(self, mocked_repository):
        mocked_repository.return_value.all_uncompleted = mock.AsyncMock(return_value=[])
        counter = 0

        publisher = product_getting_stream(limit=1)
        await publisher._start_generator()

        with pytest.raises(FinishedIterator):
            async for payload, is_complete in publisher._generate_next_n(1):
                counter += 1

            assert payload.data is None
            assert is_complete

        assert counter == 0
        mocked_repository.return_value.all_uncompleted.assert_called_once_with(limit=1)

    async def test_generates_payload_with_actual_data(self, mocked_repository):
        product = create_product_from_db(id=1, text="text")
        mocked_repository.return_value.all_uncompleted = mock.AsyncMock(return_value=[product])
        counter = 0
        payloads = []
        is_completes = []

        publisher = product_getting_stream(limit=1)
        await publisher._start_generator()

        async for payload, is_complete in publisher._generate_next_n(1):
            payloads.append(payload)
            is_completes.append(is_complete)
            counter += 1

        encoded_product = '{"id":1,"text":"text","quantity":1,"created_at":"2000-01-01T00:00:00","completed":false}'

        assert counter == 1
        assert len(payloads) == 1
        assert payloads[0].data == encoded_product.encode("utf-8")
        assert is_completes == [True]

    async def test_saves_order_of_generation(self, mocked_repository):
        products = [
            create_product_from_db(id=1, text="text1"),
            create_product_from_db(id=2, text="text2"),
            create_product_from_db(id=3, text="text3"),
        ]
        counter = 0
        mocked_repository.return_value.all_uncompleted = mock.AsyncMock(return_value=products)

        publisher = product_getting_stream(limit=3)
        await publisher._start_generator()

        payloads = []
        is_completes = []

        async for payload, is_complete in publisher._generate_next_n(3):
            payloads.append(payload)
            is_completes.append(is_complete)
            counter += 1

        encoded_products = [
            '{"id":1,"text":"text1","quantity":1,"created_at":"2000-01-01T00:00:00","completed":false}',
            '{"id":2,"text":"text2","quantity":1,"created_at":"2000-01-01T00:00:00","completed":false}',
            '{"id":3,"text":"text3","quantity":1,"created_at":"2000-01-01T00:00:00","completed":false}',
        ]

        assert counter == 3

        for payload, encoded_product in zip(payloads, encoded_products):
            assert payload.data == encoded_product.encode("utf-8")

        assert not all(is_completes[:-1])
        assert is_completes[-1]


@pytest.mark.skip
class TestProductCreatingSubscriber:
    def test_calls_subscription_request_on_subscribe(self):
        subscription = mock.MagicMock()
        subscriber = ProductCreatingSubscriber(limit=10)

        subscriber.on_subscribe(subscription=subscription)

        subscription.request.assert_called_once_with(limit=10)

    def test_calls_repository_method_on_next(self, mocked_repository):
        subscriber = ProductCreatingSubscriber(limit=10)
        encoded_product = b'{"id":1,"text":"text","quantity":1,"created_at":"2000-01-01T00:00:00","completed":false}'

        subscriber.on_next(Payload(encoded_product), False)

        create_schema = ProductCreateSchema(
            text="text",
            quantity=1,
            completed=False,
        )

        mocked_repository.return_value.create.assert_called_once_with(create_schema)
