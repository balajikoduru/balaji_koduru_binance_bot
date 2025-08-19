import argparse
import time
from ..http_client import BinanceFuturesClient
from ..utils import get_symbol_rules, side_from_str, order_response_brief
from ..logger import get_logger

log = get_logger("twap")

def main():
    p = argparse.ArgumentParser(description="TWAP: split a large order into equal slices over time")
    p.add_argument("symbol")
    p.add_argument("side")
    p.add_argument("totalQty", type=float)
    p.add_argument("slices", type=int)
    p.add_argument("interval", type=float, help="seconds between slices")
    args = p.parse_args()

    client = BinanceFuturesClient()
    rules = get_symbol_rules(client, args.symbol)
    side = side_from_str(args.side)

    per = rules.ensure_qty(args.totalQty / args.slices)
    log.info(f"TWAP {side} {args.symbol} total={args.totalQty} slices={args.slices} perSlice={per}")

    for i in range(args.slices):
        resp = client.place_order(symbol=args.symbol.upper(), side=side, type="MARKET", quantity=per)
        log.info(f"Slice {i+1}/{args.slices}: {order_response_brief(resp)}")
        print(f"Slice {i+1}/{args.slices}: {order_response_brief(resp)}")
        if i < args.slices - 1:
            time.sleep(args.interval)

if __name__ == "__main__":
    main()
