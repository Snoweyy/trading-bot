"""
cli.py
Command-line entry point for the Binance Futures Testnet Trading Bot.

Usage examples:
  python cli.py --symbol BTCUSDT --side BUY  --type MARKET     --qty 0.001
  python cli.py --symbol BTCUSDT --side SELL --type LIMIT       --qty 0.001 --price 80000
  python cli.py --symbol BTCUSDT --side BUY  --type STOP_MARKET --qty 0.001 --stop-price 90000
"""

from __future__ import annotations

import argparse
import sys

from bot.client import BinanceClient, BinanceAPIError
from bot.logging_config import setup_logger
from bot.orders import place_limit_order, place_market_order, place_take_profit_market_order
from bot.validators import ValidationError, validate_all

logger = setup_logger("trading_bot.cli")


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description=(
            "Binance Futures Testnet Trading Bot\n"
            "Place MARKET, LIMIT, or STOP_MARKET orders via the CLI.\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python cli.py --symbol BTCUSDT --side BUY  --type MARKET     --qty 0.001\n"
            "  python cli.py --symbol BTCUSDT --side SELL --type LIMIT       --qty 0.001 --price 80000\n"
            "  python cli.py --symbol BTCUSDT --side BUY  --type STOP_MARKET --qty 0.001 --stop-price 90000\n"
        ),
    )

    parser.add_argument(
        "--symbol", "-s",
        required=True,
        metavar="SYMBOL",
        help="Trading pair symbol, e.g. BTCUSDT",
    )
    parser.add_argument(
        "--side",
        required=True,
        metavar="SIDE",
        help="Order side: BUY or SELL",
    )
    parser.add_argument(
        "--type", "-t",
        required=True,
        dest="order_type",
        metavar="TYPE",
        help="Order type: MARKET | LIMIT | STOP_MARKET",
    )
    parser.add_argument(
        "--qty", "-q",
        required=False,
        default=None,
        metavar="QUANTITY",
        help="Order quantity in base asset (e.g. 0.001 for BTC). Not required for TAKE_PROFIT.",
    )
    parser.add_argument(
        "--price", "-p",
        default=None,
        metavar="PRICE",
        help="Limit price — required for LIMIT orders",
    )
    parser.add_argument(
        "--stop-price",
        default=None,
        metavar="STOP_PRICE",
        help="Stop trigger price — required for STOP_MARKET orders",
    )

    return parser


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    logger.info(
        "CLI invoked | symbol=%s side=%s type=%s qty=%s price=%s stop_price=%s",
        args.symbol, args.side, args.order_type, args.qty, args.price, args.stop_price,
    )

    # --- Validate all inputs ---
    try:
        validated = validate_all(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.qty,
            price=args.price,
            stop_price=args.stop_price,
        )
    except ValidationError as exc:
        logger.error("Validation failed: %s", exc)
        print(f"\n  ❌  VALIDATION ERROR: {exc}\n")
        sys.exit(1)

    symbol = validated["symbol"]
    side = validated["side"]
    order_type = validated["order_type"]
    quantity = validated.get("quantity")  # None for TAKE_PROFIT (uses closePosition)

    # --- Initialise client ---
    try:
        client = BinanceClient()
    except EnvironmentError as exc:
        logger.error("Client init failed: %s", exc)
        print(f"\n  ❌  CONFIG ERROR: {exc}\n")
        sys.exit(1)

    # --- Connectivity check ---
    if not client.ping():
        logger.error("Cannot reach Binance Testnet. Check your network.")
        print("\n  ❌  ERROR: Cannot reach Binance Testnet. Check your network.\n")
        sys.exit(1)

    # --- Dispatch to correct order function ---
    try:
        if order_type == "MARKET":
            place_market_order(client, symbol, side, quantity)

        elif order_type == "LIMIT":
            price = validated["price"]
            place_limit_order(client, symbol, side, quantity, price)

        elif order_type == "TAKE_PROFIT":
            stop_price = validated["stop_price"]
            place_take_profit_market_order(client, symbol, side, stop_price)

    except BinanceAPIError:
        # Already logged inside the order functions
        sys.exit(1)
    except Exception as exc:
        logger.exception("Unexpected error: %s", exc)
        print(f"\n  ❌  UNEXPECTED ERROR: {exc}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
