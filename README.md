# Binance USDT-M Futures Order Bot (CLI)

**Features**
- Core: Market, Limit orders
- Advanced: Stop-Limit, pseudo-OCO (TP/SL), TWAP, Grid
- Live validation from `exchangeInfo`
- Structured logs in `bot.log`
- Pure REST via HMAC (no external Binance SDK)

## Setup
1. Python 3.10+
2. Install deps:
   ```bash
   pip install -r requirements.txt
   ```
3. Export credentials (NEVER commit keys):
   ```bash
   export BINANCE_API_KEY=your_key
   export BINANCE_API_SECRET=your_secret
   # Optional safety
   export DRY_RUN=true  # simulate without sending real orders
   ```

## Usage (run from project root)
### Market
```bash
python -m src.market_orders BTCUSDT BUY 0.001
```

### Limit
```bash
python -m src.limit_orders BTCUSDT SELL 0.001 70000 --timeInForce GTC
```

### Stop-Limit
```bash
python -m src.advanced.stop_limit BTCUSDT SELL 0.001 68000 68500
```

### Pseudo-OCO (TP/SL for existing position)
```bash
python -m src.advanced.oco BTCUSDT BOTH 72000 66000 0.001 --closePosition
```

### TWAP
```bash
python -m src.advanced.twap BTCUSDT BUY 0.01 5 10
```

### Grid
```bash
python -m src.advanced.grid_strategy BTCUSDT 65000 75000 6 0.001
```


## Notes
- Ensure your Binance Futures account is enabled and has margin.
- Use `DRY_RUN=true` to test without placing real orders.
- For realtime fills, consider user data streams (websocket).
- Automated trading carries risk. Trade responsibly.
