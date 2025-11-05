import numpy as np
import pandas as pd

def supertrend(df, atr_period=10, multiplier=3.0, change_atr=True):
    """
    Convert TradingView SuperTrend PineScript to Python.
    df must contain: ['open','high','low','close']
    Returns: trend, up_line, dn_line, buy, sell
    """

    hl2 = (df['high'] + df['low']) / 2

    # ATR calculation
    tr1 = df['high'] - df['low']
    tr2 = abs(df['high'] - df['close'].shift(1))
    tr3 = abs(df['low'] - df['close'].shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    if change_atr:
        atr = tr.ewm(alpha=1/atr_period).mean()   # ATR() TradingView version
    else:
        atr = tr.rolling(atr_period).mean()       # SMA(TR)

    up = hl2 - multiplier * atr
    dn = hl2 + multiplier * atr

    # replicate nz() & recursion logic
    up1 = up.copy()
    dn1 = dn.copy()

    for i in range(1, len(df)):
        up1.iloc[i] = max(up.iloc[i], up1.iloc[i-1]) if df['close'].iloc[i-1] > up1.iloc[i-1] else up.iloc[i]
        dn1.iloc[i] = min(dn.iloc[i], dn1.iloc[i-1]) if df['close'].iloc[i-1] < dn1.iloc[i-1] else dn.iloc[i]

    trend = np.ones(len(df))
    for i in range(1, len(df)):
        prev = trend[i-1]
        if prev == -1 and df['close'].iloc[i] > dn1.iloc[i-1]:
            trend[i] = 1
        elif prev == 1 and df['close'].iloc[i] < up1.iloc[i-1]:
            trend[i] = -1
        else:
            trend[i] = prev

    buy_signal = (trend == 1) & (np.roll(trend, 1) == -1)
    sell_signal = (trend == -1) & (np.roll(trend, 1) == 1)

    result = pd.DataFrame({
        'trend': trend,
        'up': up1,
        'dn': dn1,
        'buy': buy_signal,
        'sell': sell_signal
    })

    return result
