import numpy as np
import talib

def follow_line(close, high, low, BBperiod=6, BBdev=1.0, ATRperiod=5, useATR=True):
    """
    Returns:
      +1 bullish trend flip
      -1 bearish trend flip
       0 no change
    """

    close = np.array(close, dtype=float)
    high = np.array(high, dtype=float)
    low = np.array(low, dtype=float)

    # Bollinger mid & bands
    sma = talib.SMA(close, timeperiod=BBperiod)
    std = talib.STDDEV(close, timeperiod=BBperiod)
    BBupper = sma + (std * BBdev)
    BBlower = sma - (std * BBdev)

    # ATR
    atr = talib.ATR(high, low, close, timeperiod=ATRperiod)

    TrendLine = np.zeros_like(close)
    iTrend = np.zeros_like(close)

    for i in range(1, len(close)):

        # BB Signal
        if close[i] > BBupper[i]:
            BBSignal = 1
        elif close[i] < BBlower[i]:
            BBSignal = -1
        else:
            BBSignal = 0

        # TrendLine Logic
        if BBSignal == 1:
            TL = low[i] - atr[i] if useATR else low[i]
            if TL < TrendLine[i-1]:
                TL = TrendLine[i-1]
        elif BBSignal == -1:
            TL = high[i] + atr[i] if useATR else high[i]
            if TL > TrendLine[i-1]:
                TL = TrendLine[i-1]
        else:
            TL = TrendLine[i-1]

        TrendLine[i] = TL

        # Trend Direction
        if TrendLine[i] > TrendLine[i-1]:
            iTrend[i] = 1
        elif TrendLine[i] < TrendLine[i-1]:
            iTrend[i] = -1
        else:
            iTrend[i] = iTrend[i-1]

    # Detect signal on latest bar
    if iTrend[-2] == -1 and iTrend[-1] == 1:
        return 1    # Bullish Flip
    elif iTrend[-2] == 1 and iTrend[-1] == -1:
        return -1   # Bearish Flip
    else:
        return 0    # No signal
