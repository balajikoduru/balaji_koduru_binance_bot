import argparse
from .http_client import BinanceFuturesClient
from .utils import get_symbol_rules, side_from_str, order_response_brief
from .logger import get_logger

log = get_logger("market")

def main():
    p = argparse.ArgumentParser(description="Place a MARKET order on Binance USDT-M Futures")
    p.add_argument("symbol", help="e.g., BTCUSDT")
    p.add_argument("side", help="BUY or SELL")
    p.add_argument("quantity", type=float, help="order quantity")
    args = p.parse_args()

    client = BinanceFuturesClient()
    rules = get_symbol_rules(client, args.symbol)
    side = side_from_str(args.side)
    qty = rules.ensure_qty(args.quantity)

    log.info(f"Placing MARKET {side} {args.symbol} qty={qty}")
    resp = client.place_order(
        symbol=args.symbol.upper(),
        side=side,
        type="MARKET",
        quantity=qty,
    )
    log.info("Response: %s", order_response_brief(resp))
    print(order_response_brief(resp))

if __name__ == "__main__":
    main()
