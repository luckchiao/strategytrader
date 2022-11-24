import pytest
from strategytrader.util import quantity_from_amount

testdata_quantity_from_amount = [[230, 5000000, 21], [1000, 500, 0]]


@pytest.mark.parametrize(
    "quote_price, amount, expected", testdata_quantity_from_amount
)
def test_quantity_from_amount(quote_price, amount, expected):
    sut = quantity_from_amount(quote_price, amount)
    assert expected == sut
