"""
validators.py
Input validation helpers for CLI arguments.
"""

from __future__ import annotations

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "TAKE_PROFIT"}


class ValidationError(ValueError):
    """Raised when user-supplied CLI input is invalid."""


def validate_symbol(symbol: str) -> str:
    """Return uppercased symbol or raise ValidationError."""
    symbol = symbol.strip().upper()
    if not symbol:
        raise ValidationError("Symbol cannot be empty.")
    if not symbol.isalnum():
        raise ValidationError(
            f"Symbol '{symbol}' must contain only letters and numbers (e.g. BTCUSDT)."
        )
    return symbol


def validate_side(side: str) -> str:
    """Return uppercased side (BUY/SELL) or raise ValidationError."""
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValidationError(
            f"Invalid side '{side}'. Must be one of: {', '.join(sorted(VALID_SIDES))}."
        )
    return side


def validate_order_type(order_type: str) -> str:
    """Return uppercased order type or raise ValidationError."""
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type '{order_type}'. Must be one of: "
            f"{', '.join(sorted(VALID_ORDER_TYPES))}."
        )
    return order_type


def validate_quantity(quantity: str | float) -> float:
    """Return positive float quantity or raise ValidationError."""
    try:
        qty = float(quantity)
    except (TypeError, ValueError):
        raise ValidationError(f"Quantity '{quantity}' is not a valid number.")
    if qty <= 0:
        raise ValidationError(f"Quantity must be greater than 0. Got: {qty}")
    return qty


def validate_price(price: str | float | None) -> float:
    """Return positive float price or raise ValidationError."""
    if price is None:
        raise ValidationError("Price is required for LIMIT orders.")
    try:
        p = float(price)
    except (TypeError, ValueError):
        raise ValidationError(f"Price '{price}' is not a valid number.")
    if p <= 0:
        raise ValidationError(f"Price must be greater than 0. Got: {p}")
    return p


def validate_stop_price(stop_price: str | float | None) -> float:
    """Return positive float stop price or raise ValidationError."""
    if stop_price is None:
        raise ValidationError("Stop price (--stop-price) is required for STOP_MARKET orders.")
    try:
        sp = float(stop_price)
    except (TypeError, ValueError):
        raise ValidationError(f"Stop price '{stop_price}' is not a valid number.")
    if sp <= 0:
        raise ValidationError(f"Stop price must be greater than 0. Got: {sp}")
    return sp


def validate_all(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str | float | None = None,
    price: str | float | None = None,
    stop_price: str | float | None = None,
) -> dict:
    """
    Run all relevant validators based on order type.
    Returns a dict of validated values.
    """
    order_type_validated = validate_order_type(order_type)
    validated = {
        "symbol": validate_symbol(symbol),
        "side": validate_side(side),
        "order_type": order_type_validated,
    }

    # Quantity required for MARKET and LIMIT; not needed for TAKE_PROFIT (uses closePosition)
    if order_type_validated in ("MARKET", "LIMIT"):
        if quantity is None:
            raise ValidationError(f"--qty is required for {order_type_validated} orders.")
        validated["quantity"] = validate_quantity(quantity)

    if order_type_validated == "LIMIT":
        validated["price"] = validate_price(price)

    if order_type_validated == "TAKE_PROFIT":
        validated["stop_price"] = validate_stop_price(stop_price)

    return validated
