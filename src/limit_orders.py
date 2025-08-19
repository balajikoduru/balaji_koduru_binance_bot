import argparse
from .http_client import BinanceFuturesClient
from .utils import get_symbol_rules, side_from_str, order_response_brief
from .logger import get_logger

log = get_logger("limit")

def main():
    p = argparse.ArgumentParser(description="Place a LIMIT order on Binance USDT-M Futures")
    p.add_argument("symbol")
    p.add_argument("side")
    p.add_argument("quantity", type=float)
    p.add_argument("price", type=float)
    p.add_argument("--timeInForce", default="GTC", choices=["GTC", "IOC", "FOK"])
    args = p.parse_args()

    client = BinanceFuturesClient()
    rules = get_symbol_rules(client, args.symbol)
    side = side_from_str(args.side)
    qty = rules.ensure_qty(args.quantity)
    price = rules.ensure_price(args.price)

    log.info(f"Placing LIMIT {side} {args.symbol} qty={qty} price={price}")
    resp = client.place_order(
        symbol=args.symbol.upper(),
        side=side,
        type="LIMIT",
        quantity=qty,
        price=price,
        timeInForce=args.timeInForce,
    )
    log.info("Response: %s", order_response_brief(resp))
    print(order_response_brief(resp))

if __name__ == "__main__":
    main()
