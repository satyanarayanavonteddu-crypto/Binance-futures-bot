import time

import pandas as pd from data_fetcher import get_klines from trading_engine import run_bot

symbol = "BTCUSDT"

interval = "5m" # You can change later

limit 200 # Number of candles

def main():

print(" Bot Started... Fetching data & applying strategy")

while True:

try:

df = get_klines (symbol, interval, limit)

if df is not None and len (df) > 0:

run_bot(df)

else:

print("No data received... Skipping cycle")

except Exception as e: print(f"Error: {e}")

time.sleep(15) # Wait 15 seconds before next cycle

if name == "main":

main()
