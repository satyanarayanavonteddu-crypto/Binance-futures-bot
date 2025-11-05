import numpy as np
import talib

def qqe_mod(close, RSI_Period=6, SF=5, QQE=3, ThreshHold=3, bb_length=50, bb_mult=0.35):
    close = np.array(close, dtype=float)

    # RSI & smoothed RSI
    rsi = talib.RSI(close, timeperiod=RSI_Period)
    rsi_ma = talib.EMA(rsi, timeperiod=SF)

    # Wilder ATR on RSI
    AtrRsi = np.abs(np.roll(rsi_ma, 1) - rsi_ma)
    Wilders_Period = RSI_Period * 2 - 1
    ma_atr_rsi = talib.EMA(AtrRsi, timeperiod=Wilders_Period)
    dar = talib.EMA(ma_atr_rsi, timeperiod=Wilders_Period) * QQE

    # Bands
    RSIndex = rsi_ma
    new_short_band = RSIndex + dar
    new_long_band = RSIndex - dar

    longband = np.zeros_like(close)
    shortband = np.zeros_like(close)
    trend = np.zeros_like(close)

    for i in range(1, len(close)):
        longband[i] = max(longband[i-1], new_long_band[i]) if (RSIndex[i-1] > longband[i-1] and RSIndex[i] > longband[i-1]) else new_long_band[i]
        shortband[i] = min(shortband[i-1], new_short_band[i]) if (RSIndex[i-1] < shortband[i-1] and RSIndex[i] < shortband[i-1]) else new_short_band[i]

        bull_cross = RSIndex[i] > shortband[i-1]
        bear_cross = longband[i-1] > RSIndex[i]

        if bull_cross:
            trend[i] = 1
        elif bear_cross:
            trend[i] = -1
        else:
            trend[i] = trend[i-1]

    FastAtrRsiTL = np.where(trend == 1, longband, shortband)

    # Bollinger filter on QQE line
    basis = talib.SMA(FastAtrRsiTL - 50, timeperiod=bb_length)
    dev = talib.STDDEV(FastAtrRsiTL - 50, timeperiod=bb_length) * bb_mult
    upper = basis + dev
    lower = basis - dev

    # Signal Conditions
    prev = trend[-2]
    curr = trend[-1]

    if prev == -1 and curr == 1:
        return 1   # Bullish cross
    elif prev == 1 and curr == -1:
        return -1  # Bearish cross
    else:
        return 0   # No signal
