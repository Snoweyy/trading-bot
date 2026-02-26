"""
logging_config.py
Configure a rotating file logger + colored console logger.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
LOG_FILE = os.path.join(LOG_DIR, "trading_bot.log")

# Simple color codes for console output
COLORS = {
    "DEBUG": "\033[36m",    # Cyan
    "INFO": "\033[32m",     # Green
    "WARNING": "\033[33m",  # Yellow
    "ERROR": "\033[31m",    # Red
    "CRITICAL": "\033[35m", # Magenta
    "RESET": "\033[0m",
}


class ColoredFormatter(logging.Formatter):
    """Formatter that adds color codes to console output."""

    def format(self, record: logging.LogRecord) -> str:
        color = COLORS.get(record.levelname, COLORS["RESET"])
        reset = COLORS["RESET"]
        record.levelname = f"{color}{record.levelname}{reset}"
        return super().format(record)


def setup_logger(name: str = "trading_bot") -> logging.Logger:
    """
    Create and return a configured logger.

    Handlers:
    - RotatingFileHandler  → logs/trading_bot.log  (plain text, max 5 MB × 3 backups)
    - StreamHandler        → stdout  (colored)
    """
    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger(name)
    if logger.handlers:
        # Avoid adding duplicate handlers on re-import
        return logger

    logger.setLevel(logging.DEBUG)

    fmt_file = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    fmt_console = "%(asctime)s | %(levelname)-8s | %(message)s"
    date_fmt = "%Y-%m-%d %H:%M:%S"

    # --- File handler (plain) ---
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(fmt_file, datefmt=date_fmt))

    # --- Console handler (colored) ---
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(ColoredFormatter(fmt_console, datefmt=date_fmt))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
