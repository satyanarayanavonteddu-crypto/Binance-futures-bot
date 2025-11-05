import pandas as pd
from binance.client import Client
from config import BINANCE_API_KEY, BINANCE_SECRET_KEY

client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)

def get_klines(symbol="BTCUSDT", interval="1m", limit=500):
    """
    Fetch OHLCV from Binance Futures
    """
    try:
        data = client.futures_klines(symbol=symbol, interval=interval, limit=limit)

        df = pd.DataFrame(data, columns=[
            "open_time","open","high","low","close","volume",
            "close_time","qav","trades","taker_base","taker_quote","ignore"
        ])

        df["open"] = df["open"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        df["close"] = df["close"].astype(float)
        df["volume"] = df["volume"].astype(float)
        df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")

        return df

    except Exception as e:
        print("Error fetching data:", e)
        return None


# Test run (remove when integrating bot)
if __name__ == "__main__":
    df = get_klines()
    print(df.tail())
