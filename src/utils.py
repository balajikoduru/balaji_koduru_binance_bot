from typing import Dict
from .http_client import BinanceFuturesClient
from .validators import SymbolRules
from .logger import get_logger

log = get_logger("utils")

_symbol_cache: Dict[str, SymbolRules] = {}

def get_symbol_rules(client: BinanceFuturesClient, symbol: str) -> SymbolRules:
    sym = symbol.upper()
    if sym in _symbol_cache:
        return _symbol_cache[sym]
    info = client.exchange_info()
    for s in info.get("symbols", []):
        if s.get("symbol") == sym:
            rules = SymbolRules(s)
            _symbol_cache[sym] = rules
            log.info(f"Loaded rules for {sym}")
            return rules
    raise ValueError(f"Symbol {sym} not found in exchangeInfo")

def side_from_str(s: str) -> str:
    u = s.upper()
    if u not in ("BUY", "SELL"):
        raise ValueError("Side must be BUY or SELL")
    return u

def order_response_brief(r):
    if r and isinstance(r, dict) and "dryRun" in r:
        return f"DRY_RUN: {r}"
    if not r:
        return "<no response>"
    oid = r.get("orderId")
    status = r.get("status")
    p = r.get("price")
    q = r.get("origQty")
    t = r.get("type")
    return f"orderId={oid} status={status} type={t} price={p} qty={q}"
