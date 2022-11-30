import time
from typing import Dict, Union
from loguru import logger
import shioaji as sj
from shioaji.constant import (
    QuoteType,
    QuoteVersion,
)
from shioaji import QuoteSTKv1, Exchange
from shioaji.constant import OrderState
from .strategy import Strategy
from shioaji.contracts import Contract
from concurrent.futures import Future, ThreadPoolExecutor


class StrategyTrader:
    def __init__(self, api: sj.Shioaji):
        self.api: sj.Shioaji = api
        self.api.quote.set_on_quote_stk_v1_callback(self.quote_handler)
        self.api.set_order_callback(self.order_handler)
        self.strategy_collection: Dict[str, Strategy] = {}
        self.executor = ThreadPoolExecutor()
        self.wait_sec: int = 5

    def quote_handler(self, exchange: Exchange, quote: QuoteSTKv1) -> None:
        code = quote.code
        strategy = self.strategy_collection.get(code, None)
        if strategy is None:
            return
        else:
            ord_arg = strategy.apply_quote(quote)
            if ord_arg:
                order = sj.Order(**ord_arg)
                self.api.place_order(strategy.contract, order)

    def order_handler(self, order_state: OrderState, msg: Dict) -> None:
        code = (
            msg["contract"]["code"]
            if order_state == OrderState.TFTOrder
            else msg["code"]
        )
        strategy = self.strategy_collection.get(code, None)
        if strategy is None:
            logger.warning(f" [{code}] Strategy Not Found {msg}")
            return
        if order_state == OrderState.TFTOrder:
            ord_arg = strategy.apply_order(msg)
            logger.info(ord_arg)
            if ord_arg:
                strategy.trade = self.api.place_order(
                    strategy.contract, ord_arg
                )
                self.executor.submit(
                    self.run_after_update_order, self.wait_sec, strategy
                )

        elif order_state == OrderState.TFTDeal:
            strategy.apply_deal_qty(msg)

    def add_strategy(self, contract: Union[Contract, str], amount: int):
        if isinstance(contract, str):
            contract = self.api.Contracts.Stocks[contract]
        strtegy = Strategy(contract=contract, amount=amount)
        self.strategy_collection[contract.code] = strtegy
        self.api.quote.subscribe(
            contract=contract,
            quote_type=QuoteType.Quote,
            version=QuoteVersion.v1,
        )

    def run_after_update_order(
        self, sec: int, strategy: Strategy, *args, **kwargs
    ):
        time.sleep(sec)
        update_price = strategy.update_trade_price()
        self.api.update_status(strategy.trade)
        self.api.update_order(strategy.trade, update_price)
