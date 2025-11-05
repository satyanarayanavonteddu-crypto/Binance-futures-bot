import numpy as np
import talib

def hma(series, length):
    half = int(length / 2)
    sqrt_len = int(np.sqrt(length))
    wma1 = talib.WMA(series, timeperiod=length)
    wma2 = talib.WMA(series, timeperiod=half)
    return talib.WMA(2 * wma2 - wma1, timeperiod=sqrt_len)

def ehma(series, length):
    half = int(length / 2)
    sqrt_len = int(np.sqrt(length))
    ema1 = talib.EMA(series, timeperiod=length)
    ema2 = talib.EMA(series, timeperiod=half)
    return talib.EMA(2 * ema2 - ema1, timeperiod=sqrt_len)

def thma(series, length):
    w1 = talib.WMA(series, timeperiod=int(length / 3))
    w2 = talib.WMA(series, timeperiod=int(length / 2))
    w3 = talib.WMA(series, timeperiod=length)
    return talib.WMA(3 * w1 - w2 - w3, timeperiod=length)

def namib_hull(series, mode="Hma", length=60, length_mult=6.0):
    """Returns Hull direction: +1 uptrend, -1 downtrend"""

    length = int(length * length_mult)

    if mode == "Hma":
        hull = hma(series, length)
    elif mode == "Ehma":
        hull = ehma(series, length)
    elif mode == "Thma":
        hull = thma(series, int(length/2))
    else:
        hull = hma(series, length)

    # Hull confirmation logic (trend check)
    hull_current = hull[-1]
    hull_prev = hull[-3]

    if hull_current > hull_prev:
        return 1  # uptrend
    elif hull_current < hull_prev:
        return -1  # downtrend
    else:
        return 0  # neutral
