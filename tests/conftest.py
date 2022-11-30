import pytest
import pathlib
import pickle
import shioaji as sj
from decimal import Decimal
import datetime
from shioaji import Exchange
from .quote import QuoteSTKv1
from strategytrader.trader import StrategyTrader
from strategytrader.strategy import Strategy


@pytest.fixture
def trader(sj_api):
    return StrategyTrader(api=sj_api)


def read_contracts_pkl():
    data_path = pathlib.Path(__file__).parent.absolute()
    with open(f"{data_path}/data/contracts.pkl", "rb") as f:
        contracts = pickle.load(f)
    return contracts


@pytest.fixture
def sj_api():
    api = sj.Shioaji()
    api.Contracts = read_contracts_pkl()
    return api


@pytest.fixture
def strategy(sj_api: sj.Shioaji, quote_data):
    strategy = Strategy(
        contract=sj_api.Contracts.Stocks["1795"], amount=5000000
    )
    return strategy


@pytest.fixture
def quote_data():
    quote = QuoteSTKv1(
        code="1795",
        datetime=datetime.datetime(2022, 7, 1, 10, 43, 15, 840092),
        open=Decimal("471.5"),
        avg_price=Decimal("467.9"),
        close=Decimal("461"),
        high=Decimal("474"),
        low=Decimal("461"),
        amount=Decimal("9220000"),
        total_amount=Decimal("11843696000"),
        volume=0,
        total_volume=25312,
        tick_type=2,
        chg_type=4,
        price_chg=Decimal("-15"),
        pct_chg=Decimal("-3.15"),
        bid_side_total_vol=9350,
        ask_side_total_vol=15962,
        bid_side_total_cnt=2730,
        ask_side_total_cnt=2848,
        closing_oddlot_shares=0,
        closing_oddlot_close=Decimal("0.0"),
        closing_oddlot_amount=Decimal("0"),
        closing_oddlot_bid_price=Decimal("0.0"),
        closing_oddlot_ask_price=Decimal("0.0"),
        fixed_trade_vol=0,
        fixed_trade_amount=Decimal("0"),
        bid_price=[
            Decimal("461"),
            Decimal("460.5"),
            Decimal("460"),
            Decimal("459.5"),
            Decimal("459"),
        ],
        bid_volume=[201, 141, 994, 63, 132],
        diff_bid_vol=[0, 1, 0, 0, 0],
        ask_price=[
            Decimal("461.5"),
            Decimal("462"),
            Decimal("462.5"),
            Decimal("463"),
            Decimal("463.5"),
        ],
        ask_volume=[123, 101, 103, 139, 95],
        diff_ask_vol=[0, 0, 0, 0, 0],
        avail_borrowing=9579699,
        suspend=0,
        simtrade=0,
    )
    exchange = Exchange("TSE")
    return exchange, quote


@pytest.fixture
def tftorder_data():
    tftorder = {
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
    }
    return tftorder


@pytest.fixture
def tftdeal_data():
    tftdeal = {
        "trade_id": "c8864e05",
        "seqno": "422258",
        "ordno": "IA129",
        "exchange_seq": "186586",
        "broker_id": "9A9g",
        "account_id": "0173750",
        "action": "Sell",
        "code": "1795",
        "order_cond": "ShortSelling",
        "order_lot": "Common",
        "price": 219,
        "quantity": 1,
        "web_id": "137",
        "custom_field": "",
        "ts": 1669254154,
    }
    return tftdeal
