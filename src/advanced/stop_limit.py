import argparse
from ..http_client import BinanceFuturesClient
from ..utils import get_symbol_rules, side_from_str, order_response_brief
from ..logger import get_logger

log = get_logger("stop_limit")

def main():
    p = argparse.ArgumentParser(description="Place a STOP-LIMIT order (trigger limit when stop hits)")
    p.add_argument("symbol")
    p.add_argument("side")
    p.add_argument("quantity", type=float)
    p.add_argument("price", type=float, help="limit price after trigger")
    p.add_argument("stopPrice", type=float, help="stop trigger price")
    p.add_argument("--timeInForce", default="GTC")
    args = p.parse_args()

    client = BinanceFuturesClient()
    rules = get_symbol_rules(client, args.symbol)
    side = side_from_str(args.side)
    qty = rules.ensure_qty(args.quantity)
    limit_price = rules.ensure_price(args.price)
    stop_price = rules.ensure_price(args.stopPrice)

    params = dict(
        symbol=args.symbol.upper(),
        side=side,
        type="STOP",
        quantity=qty,
        price=limit_price,
        stopPrice=stop_price,
        timeInForce=args.timeInForce,
        workingType="CONTRACT_PRICE",
        priceProtect="TRUE",
    )
    log.info(f"Placing STOP-LIMIT: {params}")
    resp = client.place_order(**params)
    log.info("Response: %s", order_response_brief(resp))
    print(order_response_brief(resp))

if __name__ == "__main__":
    main()
