import argparse
from ..http_client import BinanceFuturesClient
from ..utils import get_symbol_rules, order_response_brief
from ..logger import get_logger

log = get_logger("grid")

'''
Simple static grid:
- Build N price levels between lower and upper bounds.
- Place BUY limits below mid price and SELL limits above.
- Demonstration; robust implementations re-place opposite orders on fills.
'''

def linspace(a, b, n):
    if n < 2:
        return [a]
    step = (b - a) / (n - 1)
    return [a + i * step for i in range(n)]

def main():
    p = argparse.ArgumentParser(description="Grid strategy: place layered limit orders")
    p.add_argument("symbol")
    p.add_argument("lower", type=float)
    p.add_argument("upper", type=float)
    p.add_argument("levels", type=int)
    p.add_argument("quantity", type=float, help="per-level qty")
    args = p.parse_args()

    if args.lower >= args.upper:
        raise ValueError("lower must be < upper")

    client = BinanceFuturesClient()
    rules = get_symbol_rules(client, args.symbol)

    qty = rules.ensure_qty(args.quantity)
    prices = [rules.ensure_price(p) for p in linspace(args.lower, args.upper, args.levels)]

    placed = []
    mid = (args.lower + args.upper) / 2

    for pz in prices:
        side = "BUY" if pz < mid else "SELL"
        r = client.place_order(symbol=args.symbol.upper(), side=side, type="LIMIT", price=pz, quantity=qty, timeInForce="GTC")
        placed.append(r)
        log.info(f"Grid {side} at {pz}: {order_response_brief(r)}")
        print(f"Grid {side} at {pz}: {order_response_brief(r)}")

    log.info(f"Placed {len(placed)} grid orders")

if __name__ == "__main__":
    main()
