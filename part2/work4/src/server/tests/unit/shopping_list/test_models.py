import pytest

from .helpers import create_product_from_db


class TestProduct:
    @pytest.mark.parametrize("quantity", [-1, -10, -1000])
    def test_raises_error_when_quantity_less_than_zero(self, quantity):
        with pytest.raises(ValueError) as exc_info:
            create_product_from_db(id=1, text="text", quantity=quantity)

        assert exc_info.value.args == ("Quantity must be a positive number",)

    @pytest.mark.parametrize("quantity", [0, 1, 10])
    def test_creates_without_error_when_quantity_is_valid(self, quantity):
        create_product_from_db(id=1, text="text", quantity=quantity)

    def test_converts_to_json(self):
        product = create_product_from_db(id=1, text="Text", quantity=10, completed=True)

        json = product.to_json()

        assert json == '{"id":1,"text":"Text","quantity":10,"created_at":"2000-01-01T00:00:00","completed":true}'
