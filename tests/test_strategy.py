import pytest
from strategytrader.strategy import Strategy
import shioaji as sj
from shioaji import QuoteSTKv1
from decimal import Decimal


@pytest.fixture
def strategy(sj_api: sj.Shioaji, quote_data):
    strategy = Strategy(
        contract=sj_api.Contracts.Stocks["1795"], amount=5000000
    )
    return strategy


testdata_apply_order = [
    [
        {
            "operation": {"op_type": "New", "op_code": "00", "op_msg": ""},
            "order": {
                "id": "0e9161dd",
                "seqno": "433352",
                "ordno": "XA470",
                "account": {
                    "account_type": "S",
                    "person_id": "",
                    "broker_id": "9A9j",
                    "account_id": "0112598",
                    "signed": True,
                },
                "action": "Sell",
                "price": 219.5,
                "quantity": 2,
                "order_type": "ROD",
                "price_type": "LMT",
                "order_cond": "Cash",
                "order_lot": "Common",
                "custom_field": "216.02",
            },
            "status": {
                "id": "0e9161dd",
                "exchange_ts": 1669251663,
                "modified_price": 0.0,
                "cancel_quantity": 0,
                "order_quantity": 2,
                "web_id": "137",
            },
            "contract": {
                "security_type": "STK",
                "exchange": "TSE",
                "code": "1795",
                "symbol": "",
                "name": "",
                "currency": "TWD",
            },
        },
        None,
    ],
    [
        {
            "operation": {"op_type": "New", "op_code": "31", "op_msg": ""},
            "order": {
                "id": "0e9161dd",
                "seqno": "433352",
                "ordno": "XA470",
                "account": {
                    "account_type": "S",
                    "person_id": "",
                    "broker_id": "9A9j",
                    "account_id": "0112598",
                    "signed": True,
                },
                "action": "Sell",
                "price": 219.5,
                "quantity": 4,
                "order_type": "IOC",
                "price_type": "LMT",
                "order_cond": "Cash",
                "order_lot": "Common",
                "custom_field": "216.02",
            },
            "status": {
                "id": "0e9161dd",
                "exchange_ts": 1669251663,
                "modified_price": 0.0,
                "cancel_quantity": 0,
                "order_quantity": 3,
                "web_id": "137",
            },
            "contract": {
                "security_type": "STK",
                "exchange": "TSE",
                "code": "1795",
                "symbol": "",
                "name": "",
                "currency": "TWD",
            },
        },
        {
            "quantity": 1,
            "price": Decimal("461.5"),
            "price_type": "LMT",
            "action": "Buy",
            "order_type": "ROD",
        },
    ],
]


@pytest.mark.parametrize("raw_data, expected", testdata_apply_order)
def test_apply_order(strategy: Strategy, raw_data, expected):
    ord_arg = strategy.apply_order(raw_data)
    assert ord_arg == None


@pytest.mark.parametrize("raw_data, expected", testdata_apply_order)
def test_apply_order_with_quote(
    strategy: Strategy, raw_data, expected, quote_data
):
    _, quote = quote_data
    strategy.apply_quote(quote)
    ord_arg = strategy.apply_order(raw_data)
    assert expected == ord_arg
