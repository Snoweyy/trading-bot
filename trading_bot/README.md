# Binance Futures Testnet Trading Bot

A clean, structured Python CLI application to place **MARKET**, **LIMIT**, and **STOP_MARKET** orders on the [Binance Futures Testnet](https://testnet.binancefuture.com) (USDT-M).

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # HMAC-signed Binance REST client
│   ├── orders.py          # Order placement logic
│   ├── validators.py      # CLI input validation
│   └── logging_config.py  # Rotating file + colored console logger
├── cli.py                 # CLI entry point (argparse)
├── logs/                  # Auto-created; contains trading_bot.log
├── .env                   # API credentials (not committed to git)
├── .env.example           # Template for credentials
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Get Testnet API Keys

1. Go to [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Log in / register
3. Generate API key + secret

### 2. Configure Credentials

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

Edit `.env`:
```
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## How to Run

All commands are run from the `trading_bot/` directory.

### Place a MARKET order

```bash
# BUY 0.001 BTC at market price
python cli.py --symbol BTCUSDT --side BUY --type MARKET --qty 0.001

# SELL 0.001 BTC at market price
python cli.py --symbol BTCUSDT --side SELL --type MARKET --qty 0.001
```

### Place a LIMIT order

```bash
# BUY 0.001 BTC at $80,000 limit  
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --qty 0.001 --price 80000

# SELL 0.001 BTC at $100,000 limit
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --qty 0.001 --price 100000
```

### Place a STOP_MARKET order *(Bonus)*

```bash
# Trigger a market BUY when price hits $90,000
python cli.py --symbol BTCUSDT --side BUY --type STOP_MARKET --qty 0.001 --stop-price 90000
```

### Show help

```bash
python cli.py --help
```

---

## CLI Arguments

| Argument | Required | Description |
|---|---|---|
| `--symbol` / `-s` | ✅ | Trading pair (e.g. `BTCUSDT`) |
| `--side` | ✅ | `BUY` or `SELL` |
| `--type` / `-t` | ✅ | `MARKET`, `LIMIT`, or `STOP_MARKET` |
| `--qty` / `-q` | ✅ | Quantity in base asset |
| `--price` / `-p` | ⚠️ | Required for `LIMIT` orders |
| `--stop-price` | ⚠️ | Required for `STOP_MARKET` orders |

---

## Sample Output

```
=======================================================
  📤  ORDER REQUEST — MARKET
=======================================================
  symbol            : BTCUSDT
  side              : BUY
  type              : MARKET
  quantity          : 0.001
=======================================================

=======================================================
  📥  ORDER RESPONSE
=======================================================
  Order ID          : 3294128763
  Symbol            : BTCUSDT
  Side              : BUY
  Type              : MARKET
  Orig Qty          : 0.001
  Executed Qty      : 0.001
  Avg Price         : 84523.50
  Status            : FILLED
=======================================================

  ✅  SUCCESS — MARKET order placed!
      orderId : 3294128763
      status  : FILLED
```

---

## Logging

All API requests, responses, and errors are logged to `logs/trading_bot.log`.

- **DEBUG** level: full request params + raw API response
- **INFO** level: order placement events, success/failure
- **ERROR** level: API errors, network failures, validation errors

Log file rotates at 5 MB (keeps 3 backups).

---

## Error Handling

| Scenario | Behaviour |
|---|---|
| Invalid side/type | Validation error printed, exits with code 1 |
| Missing price for LIMIT | Validation error, no API call made |
| Missing API keys in .env | Config error message, exits |
| Binance API error (e.g. -2019 margin) | Error message + logged |
| Network timeout / connection error | Error message + logged |

---

## Assumptions

- Testnet base URL: `https://testnet.binancefuture.com`
- Default `timeInForce` for LIMIT orders: `GTC` (Good Till Cancelled)
- Quantity precision follows Binance Futures rules — use at least 3 decimal places for BTC
- No third-party Binance SDK used — raw REST calls with `requests` for full transparency

---

## Requirements

```
requests==2.31.0
python-dotenv==1.0.1
```

Python 3.8+ required.
