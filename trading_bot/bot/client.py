"""
client.py
Low-level Binance Futures Testnet REST client.

- Handles HMAC-SHA256 request signing
- Logs every request and response at DEBUG level
- Raises BinanceAPIError on non-2xx responses
"""

from __future__ import annotations

import hashlib
import hmac
import os
import time
from typing import Any
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

from bot.logging_config import setup_logger

load_dotenv()

logger = setup_logger("trading_bot.client")

TESTNET_BASE_URL = "https://testnet.binancefuture.com"
ORDER_ENDPOINT = "/fapi/v1/order"
PING_ENDPOINT = "/fapi/v1/ping"
TIME_ENDPOINT = "/fapi/v1/time"


class BinanceAPIError(Exception):
    """Raised when Binance returns a non-2xx HTTP response."""

    def __init__(self, status_code: int, code: int, message: str) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(f"[HTTP {status_code}] Binance error {code}: {message}")


class BinanceClient:
    """
    Thin wrapper around the Binance Futures Testnet REST API.

    API key and secret are read from environment variables:
        BINANCE_API_KEY
        BINANCE_API_SECRET
    """

    def __init__(self) -> None:
        self.api_key = os.getenv("BINANCE_API_KEY", "").strip()
        self.api_secret = os.getenv("BINANCE_API_SECRET", "").strip()

        if not self.api_key:
            raise EnvironmentError(
                "BINANCE_API_KEY not set. Add it to your .env file."
            )
        if not self.api_secret:
            raise EnvironmentError(
                "BINANCE_API_SECRET not set. Add it to your .env file."
            )

        self.session = requests.Session()
        self.session.headers.update(
            {
                "X-MBX-APIKEY": self.api_key,
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )
        # Sync with server time to avoid -1021 timestamp errors
        self._time_offset_ms: int = 0
        self._sync_time()
        logger.debug("BinanceClient initialised (testnet: %s)", TESTNET_BASE_URL)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _sync_time(self) -> None:
        """Calculate offset between local clock and Binance server time."""
        try:
            local_before = int(time.time() * 1000)
            server_time = self.get_server_time()
            local_after = int(time.time() * 1000)
            local_mid = (local_before + local_after) // 2
            self._time_offset_ms = server_time - local_mid
            logger.debug("Time offset synced: %d ms", self._time_offset_ms)
        except Exception as exc:
            logger.warning("Could not sync server time: %s — using local time", exc)
            self._time_offset_ms = 0

    def _timestamp(self) -> int:
        """Return current UTC timestamp in milliseconds, adjusted for server offset."""
        return int(time.time() * 1000) + self._time_offset_ms

    def _sign(self, params: dict) -> str:
        """Return HMAC-SHA256 signature for the given params dict."""
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return signature

    def _post(self, endpoint: str, params: dict) -> dict:
        """
        Sign and POST to the given endpoint.
        Returns parsed JSON response dict.
        Raises BinanceAPIError on API-level errors.
        """
        params["timestamp"] = self._timestamp()
        params["signature"] = self._sign(params)

        url = TESTNET_BASE_URL + endpoint

        logger.debug("POST %s | params: %s", url, {k: v for k, v in params.items() if k != "signature"})

        try:
            response = self.session.post(url, data=params, timeout=10)
        except requests.exceptions.ConnectionError as exc:
            logger.error("Network error connecting to Binance: %s", exc)
            raise
        except requests.exceptions.Timeout:
            logger.error("Request to %s timed out.", url)
            raise

        logger.debug("Response [%s]: %s", response.status_code, response.text)

        data = response.json()

        if not response.ok:
            code = data.get("code", -1)
            msg = data.get("msg", "Unknown error")
            logger.error("Binance API error %s: %s", code, msg)
            raise BinanceAPIError(response.status_code, code, msg)

        return data

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def ping(self) -> bool:
        """Check server connectivity. Returns True if reachable."""
        url = TESTNET_BASE_URL + PING_ENDPOINT
        try:
            r = self.session.get(url, timeout=5)
            logger.debug("Ping response: %s", r.status_code)
            return r.ok
        except Exception as exc:
            logger.error("Ping failed: %s", exc)
            return False

    def get_server_time(self) -> int:
        """Return Binance server timestamp in ms."""
        url = TESTNET_BASE_URL + TIME_ENDPOINT
        r = self.session.get(url, timeout=5)
        return r.json().get("serverTime", 0)

    def post_order(self, params: dict[str, Any]) -> dict:
        """
        Place a new order.

        Args:
            params: Order parameters (symbol, side, type, quantity, etc.)
                    Do NOT include timestamp or signature — handled internally.

        Returns:
            Parsed order response from Binance.
        """
        return self._post(ORDER_ENDPOINT, params)
