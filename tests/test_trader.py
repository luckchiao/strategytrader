import datetime
from decimal import Decimal
import pytest
from pytest_mock import mocker
import shioaji as sj
from shioaji import Exchange
from strategytrader.trader import StrategyTrader
from .quote import QuoteSTKv1


@pytest.fixture
def trader(sj_api):
    return StrategyTrader(api=sj_api)


quote: QuoteSTKv1 = QuoteSTKv1(
    code="2330",
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
exchange: Exchange = Exchange("TSE")


def test_add_strategy(trader: StrategyTrader, sj_api: sj.Shioaji):
    trader.add_strategy(sj_api.Contracts.Stocks["2303"], 4000000)
    trader.add_strategy("2330", 6000000)
    assert len(trader.strategy_collection) == 2
    assert "2330" in trader.strategy_collection.keys()
    assert "2303" in trader.strategy_collection.keys()
    assert "2890" not in trader.strategy_collection.keys()


def test_quote_handler(trader: StrategyTrader, sj_api: sj.Shioaji, mocker):
    trader.add_strategy("2330", 6000000)
    strategy = trader.strategy_collection.get("2330")
    assert strategy.first_ask_vol == 0
    trader.quote_handler(exchange=exchange, quote=quote)
    assert strategy.first_ask_vol == 123
    quote.ask_volume = [88, 2, 3, 4, 5]

    mocker_place_order = mocker.patch.object(trader, "place_order")

    # mock_method = mocker.patch(
    #     "strategytrader.trader.StrategyTrader.place_order"
    # )

    trader.quote_handler(exchange=exchange, quote=quote)
    trader.quote_handler(exchange=exchange, quote=quote)
    mocker_place_order.assert_called_once()
    # assert trader.place_order.assert_called_once()
