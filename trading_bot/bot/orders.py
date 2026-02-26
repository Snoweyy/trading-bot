"""
orders.py
Order placement logic for Binance Futures Testnet.

Provides functions for:
  - Market orders
  - Limit orders
  - Stop-Market orders (bonus)

Each function prints a clean request summary before calling the API
and a formatted response summary after.
"""

from __future__ import annotations

from bot.client import BinanceClient, BinanceAPIError
from bot.logging_config import setup_logger

logger = setup_logger("trading_bot.orders")


# ---------------------------------------------------------------------------
# Pretty-print helpers
# ---------------------------------------------------------------------------

def _print_request_summary(order_type: str, params: dict) -> None:
    """Print a formatted order request summary to stdout."""
    print("\n" + "=" * 55)
    print(f"  📤  ORDER REQUEST — {order_type}")
    print("=" * 55)
    for key, value in params.items():
        print(f"  {key:<18}: {value}")
    print("=" * 55)


def _print_response_summary(response: dict) -> None:
    """Print a formatted order response summary to stdout."""
    print("\n" + "=" * 55)
    print("  📥  ORDER RESPONSE")
    print("=" * 55)
    fields = [
        ("orderId", "Order ID"),
        ("symbol", "Symbol"),
        ("side", "Side"),
        ("type", "Type"),
        ("origQty", "Orig Qty"),
        ("executedQty", "Executed Qty"),
        ("avgPrice", "Avg Price"),
        ("price", "Price"),
        ("stopPrice", "Stop Price"),
        ("status", "Status"),
        ("timeInForce", "Time In Force"),
        ("updateTime", "Update Time"),
    ]
    for api_key, label in fields:
        value = response.get(api_key)
        if value not in (None, "", "0", "0.00000000"):
            print(f"  {label:<18}: {value}")
    print("=" * 55)


def _log_and_print_success(order_type: str, symbol: str, response: dict) -> None:
    order_id = response.get("orderId", "N/A")
    status = response.get("status", "N/A")
    logger.info(
        "✅ %s order placed successfully | symbol=%s | orderId=%s | status=%s",
        order_type, symbol, order_id, status,
    )
    print(f"\n  ✅  SUCCESS — {order_type} order placed!")
    print(f"      orderId : {order_id}")
    print(f"      status  : {status}\n")


# ---------------------------------------------------------------------------
# Order functions
# ---------------------------------------------------------------------------

def place_market_order(
    client: BinanceClient, symbol: str, side: str, quantity: float
) -> dict:
    """
    Place a MARKET order on Binance Futures Testnet.

    Args:
        client:   Authenticated BinanceClient instance.
        symbol:   Trading pair, e.g. 'BTCUSDT'.
        side:     'BUY' or 'SELL'.
        quantity: Order quantity in base asset.

    Returns:
        Binance API response dict.
    """
    params = {
        "symbol": symbol,
        "side": side,
        "type": "MARKET",
        "quantity": quantity,
    }

    _print_request_summary("MARKET", params)
    logger.info("Placing MARKET order | symbol=%s side=%s qty=%s", symbol, side, quantity)

    try:
        response = client.post_order(params)
    except BinanceAPIError as exc:
        logger.error("Failed to place MARKET order: %s", exc)
        print(f"\n  ❌  FAILED — {exc}\n")
        raise

    _print_response_summary(response)
    _log_and_print_success("MARKET", symbol, response)
    return response


def place_limit_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    time_in_force: str = "GTC",
) -> dict:
    """
    Place a LIMIT order on Binance Futures Testnet.

    Args:
        client:        Authenticated BinanceClient instance.
        symbol:        Trading pair, e.g. 'BTCUSDT'.
        side:          'BUY' or 'SELL'.
        quantity:      Order quantity in base asset.
        price:         Limit price.
        time_in_force: 'GTC' (default), 'IOC', or 'FOK'.

    Returns:
        Binance API response dict.
    """
    params = {
        "symbol": symbol,
        "side": side,
        "type": "LIMIT",
        "quantity": quantity,
        "price": price,
        "timeInForce": time_in_force,
    }

    _print_request_summary("LIMIT", params)
    logger.info(
        "Placing LIMIT order | symbol=%s side=%s qty=%s price=%s",
        symbol, side, quantity, price,
    )

    try:
        response = client.post_order(params)
    except BinanceAPIError as exc:
        logger.error("Failed to place LIMIT order: %s", exc)
        print(f"\n  ❌  FAILED — {exc}\n")
        raise

    _print_response_summary(response)
    _log_and_print_success("LIMIT", symbol, response)
    return response


def place_take_profit_market_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    stop_price: float,
) -> dict:
    """
    Place a TAKE_PROFIT_MARKET order on Binance Futures Testnet. (Bonus order type)

    Closes the entire open position at market price when the stop price is reached.
    Uses closePosition=true so no quantity needs to be specified.

    Args:
        client:     Authenticated BinanceClient instance.
        symbol:     Trading pair, e.g. 'BTCUSDT'.
        side:       'BUY' or 'SELL' (opposite of your open position side).
        stop_price: Price at which profit-taking triggers.

    Returns:
        Binance API response dict.
    """
    params = {
        "symbol": symbol,
        "side": side,
        "type": "TAKE_PROFIT_MARKET",
        "stopPrice": stop_price,
        "closePosition": "true",
    }

    _print_request_summary("TAKE_PROFIT_MARKET", params)
    logger.info(
        "Placing TAKE_PROFIT_MARKET order | symbol=%s side=%s stopPrice=%s",
        symbol, side, stop_price,
    )

    try:
        response = client.post_order(params)
    except BinanceAPIError as exc:
        logger.error("Failed to place TAKE_PROFIT_MARKET order: %s", exc)
        print(f"\n  ❌  FAILED — {exc}\n")
        raise

    _print_response_summary(response)
    _log_and_print_success("TAKE_PROFIT_MARKET", symbol, response)
    return response
