from dataclasses import dataclass, fields
from typing import Dict, Optional
from loguru import logger
from shioaji.constant import (
    TFTOrderType,
    Action,
    TFTStockPriceType,
    StockOrderCond,
    TFTStockOrderLot,
)
from shioaji import QuoteSTKv1, Exchange
from shioaji.contracts import Contract
from shioaji.order import Trade
from .util import quantity_from_amount


@dataclass
class TFTOrder:
    id: str
    op_type: str
    op_code: str
    seqno: str
    ordno: str
    action: Action
    price: float
    quantity: int
    order_type: TFTOrderType
    price_type: TFTStockPriceType
    order_cond: StockOrderCond
    order_lot: TFTStockOrderLot
    custom_field: str
    broker_id: str
    account_id: str
    code: str
    exchange_ts: float
    order_quantity: int
    cancel_quantity: int

    def __init__(self, **kwargs):
        def set_value_nestd_dict(dt):
            for k, v in dt.items():
                if isinstance(v, dict):
                    set_value_nestd_dict(v)
                if k in names:
                    setattr(self, k, v)

        names = set([f.name for f in fields(self)])
        set_value_nestd_dict(kwargs)


@dataclass
class TFTDeal:
    trade_id: str
    seqno: str
    ordno: str
    exchange_seq: str
    broker_id: str
    account_id: str
    action: Action
    code: str
    order_cond: StockOrderCond
    order_lot: TFTStockOrderLot
    price: float
    quantity: int
    web_id: str
    custom_field: str
    ts: float

    def __init__(self, **kwargs):
        names = set([f.name for f in fields(self)])
        for k, v in kwargs.items():
            if k in names:
                setattr(self, k, v)


class Strategy:
    def __init__(self, contract: Contract, amount: int = 5000000):
        self.contract = contract
        self.amount = amount
        self.bidask_chg_pct = 0.88
        self.first_ask_vol = 0
        self.snapshot: Optional[QuoteSTKv1] = None
        self.name: str = "st"
        self.deal_qty: int = 0
        self.trade: Trade = None

    def apply_quote(self, quote: QuoteSTKv1):
        if quote.simtrade == 1:
            return
        self.snapshot = quote
        if self.first_ask_vol == 0:
            self.first_ask_vol = float(quote.ask_volume[0])
        else:
            if float(quote.ask_volume[0]) <= (
                self.first_ask_vol * self.bidask_chg_pct
            ):
                ord_arg = {
                    "quantity": quantity_from_amount(quote.close, self.amount),
                    "price": quote.close,
                    "price_type": TFTStockPriceType.LMT,
                    "action": Action.Buy,
                    "order_type": TFTOrderType.IOC,
                }
                return ord_arg
        return None

    def apply_order(self, raw_order: Dict) -> Optional[Dict]:
        tft_order = TFTOrder(**raw_order)
        if tft_order.custom_field != self.name:
            return None
        if tft_order.op_code not in ["00", "31", "51"]:
            return None
        if self.snapshot is None:
            return None
        if tft_order.order_type == TFTOrderType.IOC:
            undeal_qty = tft_order.quantity - tft_order.order_quantity
            logger.info(
                f"{self.contract.code} {self.contract.name} IOC order Order: {tft_order.quantity} Deal: {tft_order.order_quantity}"
            )
            if undeal_qty == 0:
                return None
            ord_arg = {
                "quantity": undeal_qty,
                "price": self.snapshot.ask_price[0],
                "price_type": TFTStockPriceType.LMT,
                "action": Action.Buy,
                "order_type": TFTOrderType.ROD,
                "custom_field": self.name,
            }

            return ord_arg
        return None

    def update_trade_price(self):
        if self.trade is None:
            return None
        undeal_qty = self.trade.order.quantity - self.deal_qty
        if undeal_qty > 0:
            return self.snapshot.ask_price[1]
        return None

    def apply_deal_qty(self, raw_deal: Dict):
        tftdeal = TFTDeal(**raw_deal)
        if tftdeal.action == Action.Buy:
            self.deal_qty += tftdeal.quantity
        elif tftdeal.action == Action.Sell:
            self.deal_qty -= tftdeal.quantity
