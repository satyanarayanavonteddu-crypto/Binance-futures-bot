import pandas as pd
from data_fetcher import get_klines

# === Import indicator functions === #
# Example (we will add more below)
from indicators.rvi import rvi_indicator  # ✅ example

# TODO: Add all your indicators here later


def apply_indicators(df):
    """
    Apply all indicators to dataframe & return signals
    """
    
    # Example RVI (replace col names correctly later)
    try:
        df["RVI"] = rvi_indicator(df)
    except Exception as e:
        print("RVI error:", e)

    # TODO: Add other indicators after RVI is working
    

    return df


# === Test run === #
if __name__ == "__main__":
    df = get_klines("BTCUSDT","1m",500)
    df = apply_indicators(df)
    print(df.tail())
