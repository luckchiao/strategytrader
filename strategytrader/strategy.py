from dataclasses import dataclass, fields
from typing import Dict, List, Optional, Union
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
from .util import quantity_from_amount


@dataclass
class TFTOrder:
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


class Strategy:
    def __init__(self, contract: Contract, amount: int = 5000000):
        self.contract = contract
        self.amount = amount
        self.bidask_chg_pct = 0.88
        self.first_ask_vol = 0
        self.snapshot: Optional[QuoteSTKv1] = None

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
        tftorder = TFTOrder(**raw_order)
        if tftorder.op_code not in ["00", "31", "51"]:
            return None
        if self.snapshot is None:
            return None
        if tftorder.order_type == TFTOrderType.IOC:
            undeal_qty = tftorder.quantity - tftorder.order_quantity
            logger.info(
                f"{self.contract.code} {self.contract.name} IOC order Order: {tftorder.quantity} Deal: {tftorder.order_quantity}"
            )
            if undeal_qty == 0:
                return None
            ord_arg = {
                "quantity": undeal_qty,
                "price": self.snapshot.ask_price[0],
                "price_type": TFTStockPriceType.LMT,
                "action": Action.Buy,
                "order_type": TFTOrderType.ROD,
            }

            return ord_arg
        return None

    def apply_deal(self, tftdeal: Dict):
        pass
