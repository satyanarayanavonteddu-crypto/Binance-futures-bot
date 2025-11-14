import pandas as pd
from binance.client import Client
from config import API_KEY, API_SECRET, USE_TESTNET

# ✅ Connect to Binance (Testnet or Real)
if USE_TESTNET:
    client = Client(API_KEY, API_SECRET, testnet=True)
    print("✅ Connected to Binance TESTNET")
else:
    client = Client(API_KEY, API_SECRET)
    print("✅ Connected to Binance REAL account")

# ✅ Function to get candle data
def get_klines(symbol, interval, limit):
    try:
        klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
        df = pd.DataFrame(klines, columns=[
            'open_time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'trades', 'taker_base_vol',
            'taker_quote_vol', 'ignore'
        ])
        df['open'] = df['open'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['close'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(float)
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None
