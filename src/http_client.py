import time
import hmac
import hashlib
import requests
from urllib.parse import urlencode
from typing import Dict, Any, Optional
import os

from .config import BINANCE_FAPI_BASE, API_KEY, API_SECRET, RECV_WINDOW, TIMEOUT, DRY_RUN
from .logger import get_logger

log = get_logger("http")

class BinanceFuturesClient:
    def __init__(self, key: str = API_KEY, secret: str = API_SECRET, base: str = BINANCE_FAPI_BASE):
        if not key or not secret:
            log.warning("API key/secret not set. Set BINANCE_API_KEY and BINANCE_API_SECRET.")
        self.key = key
        self.secret = secret.encode()
        self.base = base.rstrip('/')
        self.session = requests.Session()
        if key:
            self.session.headers.update({"X-MBX-APIKEY": key})

        # Check if Futures access works, else switch to Testnet
        if not self._has_futures_access():
            testnet_base = os.environ.get("BINANCE_FAPI_TESTNET", "https://testnet.binancefuture.com")
            log.warning(f"Live API cannot access Futures. Switching to TESTNET: {testnet_base}")
            self.base = testnet_base.rstrip('/')

    # ✅ Use server time for signed requests
    def _ts(self) -> int:
        try:
            return self.server_time()["serverTime"]
        except Exception as e:
            log.warning(f"Failed to fetch server time, falling back to local time: {e}")
            return int(time.time() * 1000)

    def _sign(self, params: Dict[str, Any]) -> str:
        query = urlencode(params, doseq=True)
        return hmac.new(self.secret, query.encode(), hashlib.sha256).hexdigest()

    def _req(self, method: str, path: str, params: Optional[Dict[str, Any]] = None, signed: bool = False):
        url = f"{self.base}{path}"
        params = params or {}
        if signed:
            params.setdefault("timestamp", self._ts())
            params.setdefault("recvWindow", RECV_WINDOW)
            params["signature"] = self._sign(params)

        try:
            if method == 'GET':
                r = self.session.get(url, params=params, timeout=TIMEOUT)
            elif method == 'POST':
                r = self.session.post(url, params=params, timeout=TIMEOUT)
            elif method == 'DELETE':
                r = self.session.delete(url, params=params, timeout=TIMEOUT)
            else:
                raise ValueError(f"Unsupported method {method}")
        except requests.RequestException as e:
            log.error(f"HTTP error: {e}")
            raise

        if r.status_code >= 400:
            log.error(f"{method} {path} {r.status_code}: {r.text}")
            r.raise_for_status()

        return r.json()

    # 🔎 Check futures access properly
    def _has_futures_access(self) -> bool:
        try:
            params = {"timestamp": int(time.time() * 1000), "recvWindow": RECV_WINDOW}
            params["signature"] = self._sign(params)
            r = self.session.get(self.base + "/fapi/v1/account", params=params, timeout=TIMEOUT)
            return r.status_code == 200
        except Exception:
            return False

    # Public
    def exchange_info(self):
        return self._req('GET', '/fapi/v1/exchangeInfo')

    def server_time(self):
        return self._req('GET', '/fapi/v1/time')

    def mark_price(self, symbol: str):
        return self._req('GET', '/fapi/v1/premiumIndex', {"symbol": symbol})

    # Trading
    def place_order(self, **params):
        if DRY_RUN:
            log.info(f"[DRY_RUN] Would place order: {params}")
            return {"dryRun": True, **params}
        return self._req('POST', '/fapi/v1/order', params, signed=True)

    def get_order(self, symbol: str, orderId: int):
        return self._req('GET', '/fapi/v1/order', {"symbol": symbol, "orderId": orderId}, signed=True)

    def cancel_order(self, symbol: str, orderId: int):
        return self._req('DELETE', '/fapi/v1/order', {"symbol": symbol, "orderId": orderId}, signed=True)

    def open_orders(self, symbol: str = None):
        params = {"symbol": symbol} if symbol else {}
        return self._req('GET', '/fapi/v1/openOrders', params, signed=True)
