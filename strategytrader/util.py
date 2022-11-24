from typing import List, Dict
from shioaji import Order
from shioaji.constant import TFTOrderType


def quantity_from_amount(price: float, amount: int) -> int:
    quantity = amount // price // 1000
    return quantity
