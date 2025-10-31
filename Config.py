API_KEY = "YOUR_BINANCE_API_KEY"
API_SECRET = "YOUR_BINANCE_SECRET_KEY"

# Trading Settings
USE_TESTNET = False  # True if you want testnet, False for real futures
TRADE_SYMBOLS = ["BTCUSDT", "ETHUSDT"]  # Bot will scan many later
TIMEFRAME = "5m"

CAPITAL_PERCENT = 0.10  # Use 10% of capital
MAX_LEVERAGE = 50

# Whales tracking sources
WHALE_WATCH_URLS = [
    "https://api.whale-alert.io/v1/transactions",
]

# Orderbook depth levels to monitor
ORDERBOOK_DEPTH = 50

# Profit system
TRAILING_STOP = True
SCALPING_MODE = True
