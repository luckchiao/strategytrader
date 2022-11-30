import pytest
import datetime
from strategytrader.strategy import Strategy
from strategytrader.trader import StrategyTrader
import shioaji as sj
from shioaji import QuoteSTKv1
from decimal import Decimal
from shioaji.order import Trade, Order, Account, OrderStatus
from shioaji.contracts import Stock

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
        {
            "quantity": 1,
            "price": Decimal("461.5"),
            "price_type": "LMT",
            "action": "Buy",
            "order_type": "ROD",
            "custom_field": "st",
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


testdata_apply_deal_qty = [
    [
        {
            "trade_id": "c8864e05",
            "seqno": "422258",
            "ordno": "IA129",
            "exchange_seq": "186586",
            "broker_id": "9A9g",
            "account_id": "0173750",
            "action": "Sell",
            "code": "6156",
            "order_cond": "ShortSelling",
            "order_lot": "Common",
            "price": 21.05,
            "quantity": 1,
            "web_id": "137",
            "custom_field": "st",
            "ts": 1669254154,
        },
        -1,
    ],
    [
        {
            "trade_id": "c8864e05",
            "seqno": "422258",
            "ordno": "IA129",
            "exchange_seq": "186586",
            "broker_id": "9A9g",
            "account_id": "0173750",
            "action": "Buy",
            "code": "6156",
            "order_cond": "ShortSelling",
            "order_lot": "Common",
            "price": 21.05,
            "quantity": 2,
            "web_id": "137",
            "custom_field": "st",
            "ts": 1669254154,
        },
        2,
    ],
]


@pytest.mark.parametrize("raw_data, expected", testdata_apply_deal_qty)
def test_apply_deal_qty(strategy: Strategy, raw_data, expected):
    strategy.apply_deal_qty(raw_data)
    assert strategy.deal_qty == expected


testdata_update_trade_price = [
    (
        Trade(
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
        ),
        1,
        462,
    ),
    (
        Trade(
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
        ),
        2,
        None,
    ),
    (None, 1, None),
]


@pytest.mark.parametrize(
    "trade, deal_qty, expected", testdata_update_trade_price
)
def test_update_trade_price(
    trader: StrategyTrader,
    sj_api: sj.Shioaji,
    strategy: Strategy,
    quote_data: QuoteSTKv1,
    trade,
    deal_qty,
    expected,
):
    trader.add_strategy(sj_api.Contracts.Stocks["1795"], 4000000)
    strategy.apply_quote(quote_data[1])
    strategy.trade = trade
    strategy.deal_qty = deal_qty
    assert strategy.update_trade_price() == expected
