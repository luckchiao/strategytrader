from dataclasses import dataclass, Field
from typing import Dict, List, Optional, Union
from loguru import logger
import shioaji as sj
from shioaji.constant import QuoteType, QuoteVersion
from shioaji import QuoteSTKv1, Exchange


@dataclass
class Strategy:
    contract: sj.contracts.Contract
    amount: int = 5000000
    first_ask_vol: int = 0


class StrategyTrader:
    def __init__(self, api: sj.Shioaji):
        self.api: sj.Shioaji = api
        self.api.quote.set_on_quote_stk_v1_callback(self.quote_handler)
        self.strategy_collection: Dict[str, Strategy] = {}

    def quote_handler(self, exchange: Exchange, quote: QuoteSTKv1) -> None:
        code = quote.code
        strategy = self.strategy_collection.get(code, None)
        if strategy is None:
            return
        ask_vol = quote.ask_volume[0]
        if strategy.first_ask_vol == 0:
            strategy.first_ask_vol = ask_vol
        else:
            if ask_vol <= strategy.first_ask_vol * 0.88:
                self.place_order(strategy)
            else:
                return

    def place_order(self, strategy):
        pass

    def add_strategy(
        self, contract: Union[sj.contracts.Contract, str], amount: int
    ):
        if isinstance(contract, str):
            contract = self.api.Contracts.Stocks[contract]
        elif isinstance(contract, sj.contracts.Contract):
            pass
        strtegy = Strategy(contract=contract, amount=amount)
        self.strategy_collection[contract.code] = strtegy
        self.api.quote.subscribe(
            contract=contract,
            quote_type=QuoteType.Quote,
            version=QuoteVersion.v1,
        )
