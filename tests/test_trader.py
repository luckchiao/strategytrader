from loguru import logger
from decimal import Decimal
import pytest
import shioaji as sj
from shioaji.constant import OrderState
from strategytrader.trader import StrategyTrader


def test_add_strategy(trader: StrategyTrader, sj_api: sj.Shioaji):
    trader.add_strategy(sj_api.Contracts.Stocks["2303"], 4000000)
    trader.add_strategy("2330", 6000000)
    assert len(trader.strategy_collection) == 2
    assert "2330" in trader.strategy_collection.keys()
    assert "2303" in trader.strategy_collection.keys()
    assert "2890" not in trader.strategy_collection.keys()


def test_quote_handler(
    trader: StrategyTrader, sj_api: sj.Shioaji, quote_data, mocker
):
    exchange, quote = quote_data
    trader.add_strategy("1795", 6000000)
    mocker_place_order = mocker.patch.object(sj_api, "place_order")

    quote.ask_volume = [100, 2, 3, 4, 5]
    trader.quote_handler(exchange=exchange, quote=quote)

    quote.ask_volume = [90, 2, 3, 4, 5]
    trader.quote_handler(exchange=exchange, quote=quote)

    quote.ask_volume = [88, 2, 3, 4, 5]
    trader.quote_handler(exchange=exchange, quote=quote)

    mocker_place_order.assert_called_once()


testdata_order_handler = [
    (
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
        0,
    ),
    (
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
        1,
    ),
]


@pytest.mark.parametrize("raw_data, call_times", testdata_order_handler)
def test_order_handler(
    trader: StrategyTrader,
    sj_api: sj.Shioaji,
    raw_data,
    call_times,
    quote_data,
    mocker,
):
    mocker_place_order = mocker.patch.object(sj_api, "place_order")
    trader.order_handler(order_state=OrderState.TFTOrder, msg=raw_data)
    mocker_place_order.assert_not_called()

    trader.add_strategy(trader.api.Contracts.Stocks["1795"], 5000000)
    trader.quote_handler(*quote_data)
    trader.order_handler(order_state=OrderState.TFTOrder, msg=raw_data)
    if call_times == 0:
        mocker_place_order.assert_not_called()
    elif call_times == 1:
        mocker_place_order.assert_called_once()
