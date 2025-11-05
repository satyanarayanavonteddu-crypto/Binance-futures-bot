import pandas as pd
from binance.client import Client
from Config import API_KEY, API_SECRET
from strategy import generate_signal
from apply_indicators import apply_all_indicators

# Binance Futures Testnet
client = Client(API_KEY, API_SECRET, testnet=True)

symbol = "BTCUSDT"
leverage = 5

client.futures_change_leverage(symbol=symbol, leverage=leverage)

def get_latest_position():
    positions = client.futures_account()['positions']
    for p in positions:
        if p['symbol'] == symbol:
            return float(p['positionAmt'])
    return 0

def place_order(side, quantity):
    client.futures_create_order(
        symbol=symbol,
        type="MARKET",
        side=side,
        quantity=quantity
    )
    print(f"{side} order placed for {quantity} {symbol}")

def run_bot(df):
    df = apply_all_indicators(df)
    signal = generate_signal(df)

    position = get_latest_position()
    qty = 0.001  # small safety qty for testing

    if signal == "BUY" and position == 0:
        place_order("BUY", qty)

    elif signal == "SELL" and position > 0:
        place_order("SELL", qty)

    else:
        print("No trade — waiting...")
