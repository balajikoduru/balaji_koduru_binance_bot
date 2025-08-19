from dotenv import load_dotenv
import os
import argparse
import time
from ..http_client import BinanceFuturesClient
from ..utils import get_symbol_rules, order_response_brief
from ..logger import get_logger

# Load environment variables
load_dotenv(override=True)

log = get_logger("oco")

'''
Binance spot offers native OCO. Futures doesn't expose classic OCO; we emulate it:
- Place both a STOP_MARKET (stop-loss) and a TAKE_PROFIT_MARKET (take-profit) as reduce-only.
- Poll for fills; when one is FILLED, cancel the other.
- Intended for closing an existing position (reduceOnly=true or closePosition=true).
'''

def main():
    # Argument parsing
    p = argparse.ArgumentParser(description="Pseudo-OCO: simultaneous TP and SL for an existing position")
    p.add_argument("symbol")
    p.add_argument("positionSide", choices=["BOTH", "LONG", "SHORT"], default="BOTH")
    p.add_argument("tpPrice", type=float, help="take profit trigger price")
    p.add_argument("slPrice", type=float, help="stop loss trigger price")
    p.add_argument("quantity", type=float, help="qty to close (ignored if closePosition)")
    p.add_argument("--closePosition", action="store_true", help="close entire position")
    p.add_argument("--poll", type=float, default=1.5, help="poll seconds")
    args = p.parse_args()

    # Client and symbol rules
    client = BinanceFuturesClient()
    rules = get_symbol_rules(client, args.symbol)
    qty = rules.ensure_qty(args.quantity)

    # Base order parameters
    base = dict(symbol=args.symbol.upper(), positionSide=args.positionSide)
    if args.closePosition:
        base["closePosition"] = "true"  # remove reduceOnly if closing full position
    else:
        base["reduceOnly"] = "true"     # only reduce-only if not closing full position

    # Place Take Profit order
    tp = client.place_order(
        **base,
        side="SELL" if args.positionSide in ("BOTH", "LONG") else "BUY",
        type="TAKE_PROFIT_MARKET",
        stopPrice=rules.ensure_price(args.tpPrice),
        workingType="CONTRACT_PRICE",
    )

    # Place Stop Loss order
    sl = client.place_order(
        **base,
        side="BUY" if args.positionSide == "SHORT" else "SELL",
        type="STOP_MARKET",
        stopPrice=rules.ensure_price(args.slPrice),
        workingType="CONTRACT_PRICE",
    )

    log.info(f"TP: {order_response_brief(tp)} | SL: {order_response_brief(sl)}")
    tp_id, sl_id = tp.get("orderId"), sl.get("orderId")

    # Polling loop to emulate OCO
    def status(oid):
        return client.get_order(args.symbol.upper(), oid).get("status")

    while True:
        tps, sls = status(tp_id), status(sl_id)
        log.info(f"tp={tps} sl={sls}")

        if tps == "FILLED":
            client.cancel_order(args.symbol.upper(), sl_id)
            log.info("TP filled; SL cancelled")
            print("TP filled; SL cancelled")
