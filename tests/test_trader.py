from loguru import logger
from decimal import Decimal
import datetime
import pytest
import shioaji as sj
from shioaji.constant import OrderState
from strategytrader.trader import StrategyTrader
from strategytrader.strategy import Strategy
from shioaji.order import Trade, Order, Account, OrderStatus
from shioaji.contracts import Stock


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
                "custom_field": "st",
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
                "custom_field": "st",
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
    tftdeal_data,
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
        mocker_fuc = mocker.patch(
            "strategytrader.strategy.Strategy.apply_deal_qty"
        )
        trader.order_handler(order_state=OrderState.TFTDeal, msg=tftdeal_data)
        mocker_fuc.assert_called_once()


def test_run_after_update_order(
    trader: StrategyTrader,
    strategy: Strategy,
    sj_api: sj.Shioaji,
    mocker,
):

    strategy.trade = Trade(
        contract=Stock(
            exchange="TSE",
            code="1795",
            symbol="TSE1795",
            name="美時",
            category="22",
            unit=1000,
            limit_up=271.0,
            limit_down=222.0,
            reference=246.5,
            update_date="2022/11/29",
            margin_trading_balance=264,
            short_selling_balance=1,
        ),
        order=Order(
            action="Buy",
            price=222,
            quantity=2,
            id="af9eb35e",
            seqno="797667",
            ordno="IK695",
            account=Account(
                account_type="S",
                person_id="",
                broker_id="9A95",
                account_id="",
                signed=True,
            ),
            price_type="LMT",
            order_type="ROD",
        ),
        status=OrderStatus(
            id="af9eb35e",
            status="PendingSubmit",
            status_code="0",
            order_datetime=datetime.datetime(2022, 11, 29, 9, 47, 4),
            msg="委託成功",
            deals=[],
        ),
    )
    mocker_fuc = mocker.patch(
        "strategytrader.strategy.Strategy.update_trade_price"
    )
    mocker_fuc.return_value = 223
    mocker_update_status = mocker.patch.object(sj_api, "update_status")
    mocker_update_order = mocker.patch.object(sj_api, "update_order")
    mocker_update_order.return_value = Trade(
        contract=Stock(
            exchange="TSE",
            code="1795",
            symbol="TSE1795",
            name="美時",
            category="22",
            unit=1000,
            limit_up=271.0,
            limit_down=222.0,
            reference=246.5,
            update_date="2022/11/29",
            margin_trading_balance=264,
            short_selling_balance=1,
        ),
        order=Order(
            action="Buy",
            price=223,
            quantity=2,
            id="af9eb35e",
            seqno="797667",
            ordno="IK695",
            account=Account(
                account_type="S",
                person_id="",
                broker_id="9A95",
                account_id="",
                signed=True,
            ),
            price_type="LMT",
            order_type="ROD",
        ),
        status=OrderStatus(
            id="af9eb35e",
            status="PendingSubmit",
            status_code="0",
            order_datetime=datetime.datetime(2022, 11, 29, 9, 47, 4),
            msg="委託成功",
            deals=[],
        ),
    )

    trader.run_after_update_order(5, strategy)
    mocker_update_status.assert_called_once()
    mocker_update_order.assert_called_once()
    assert (
        mocker_update_order.return_value.order.price == mocker_fuc.return_value
    )
