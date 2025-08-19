import os
from dotenv import load_dotenv

load_dotenv()
BINANCE_FAPI_BASE = os.environ.get("BINANCE_FAPI_BASE", "https://fapi.binance.com")
API_KEY = os.environ.get("BINANCE_API_KEY", "")
API_SECRET = os.environ.get("BINANCE_API_SECRET", "")

# Default recvWindow for signed endpoints (ms)
RECV_WINDOW = int(os.environ.get("BINANCE_RECV_WINDOW", "5000"))

# Safety toggles
DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"
TIMEOUT = float(os.environ.get("HTTP_TIMEOUT", "10"))
