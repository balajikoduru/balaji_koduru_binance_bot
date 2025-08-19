from typing import Dict, Any
from .logger import get_logger

log = get_logger("validators")

class SymbolRules:
    def __init__(self, info: Dict[str, Any]):
        self.symbol = info["symbol"]
        self.pricePrecision = info.get("pricePrecision", 2)
        self.quantityPrecision = info.get("quantityPrecision", 3)
        self.filters = {f["filterType"]: f for f in info.get("filters", [])}

    def round_price(self, price: float) -> float:
        tick = float(self.filters.get("PRICE_FILTER", {}).get("tickSize", 0.01))
        # Floor to tick grid
        return round((price // tick) * tick, 10)

    def round_qty(self, qty: float) -> float:
        step = float(self.filters.get("LOT_SIZE", {}).get("stepSize", 0.001))
        # Floor to step grid
        return round((qty // step) * step, 10)

    def ensure_price(self, price: float) -> float:
        p = self.round_price(price)
        if p <= 0:
            raise ValueError("Price must be > 0")
        min_price = float(self.filters.get("PRICE_FILTER", {}).get("minPrice", 0.0))
        if p < min_price:
            raise ValueError(f"Price {p} < minPrice {min_price}")
        return p

    def ensure_qty(self, qty: float) -> float:
        q = self.round_qty(qty)
        lot = self.filters.get("LOT_SIZE", {})
        min_qty = float(lot.get("minQty", 0.0))
        if q < min_qty:
            raise ValueError(f"Quantity {q} < minQty {min_qty}")
        return q
