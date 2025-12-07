import time
import pandas as pd
from config import API_KEY, API_SECRET, USE_TESTNET, SYMBOL, TIMEFRAME
import ccxt
from strategy import generate_signal

exchange = ccxt.binance({
    "apiKey": API_KEY,
    "secret": API_SECRET,
})
exchange.set_sandbox_mode(True)

def fetch_ohlcv():
    try:
        candles = exchange.fetch_ohlcv(SYMBOL, TIMEFRAME, limit=200)
        df = pd.DataFrame(candles, columns=[
            "timestamp", "open", "high", "low", "close", "volume"
        ])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df
    except Exception as e:
        print("Error:", e)
        return None

print("Starting Test Bot...\n")

while True:
    df = fetch_ohlcv()
    if df is not None:
        signal = generate_signal(df)
        print("Signal:", signal)
    time.sleep(5)
