import numpy as np
import talib

def qqe2_zero_cross(close, RSI_Period2=6, SF2=5, QQE2=1.61, threshold=50):
    close = np.array(close, dtype=float)

    # RSI & smoothed RSI
    rsi = talib.RSI(close, timeperiod=RSI_Period2)
    rsi_ma = talib.EMA(rsi, timeperiod=SF2)

    # Wilder ATR RSI
    Wilders_Period2 = RSI_Period2 * 2 - 1
    atr_rsi = np.abs(np.roll(rsi_ma, 1) - rsi_ma)
    ma_atr = talib.EMA(atr_rsi, timeperiod=Wilders_Period2)
    dar2 = talib.EMA(ma_atr, timeperiod=Wilders_Period2) * QQE2

    RSIndex2 = rsi_ma
    new_shortband = RSIndex2 + dar2
    new_longband = RSIndex2 - dar2

    longband = np.zeros_like(close)
    shortband = np.zeros_like(close)
    trend2 = np.zeros_like(close)

    for i in range(1, len(close)):
        longband[i] = max(longband[i-1], new_longband[i]) if (RSIndex2[i-1] > longband[i-1] and RSIndex2[i] > longband[i-1]) else new_longband[i]
        shortband[i] = min(shortband[i-1], new_shortband[i]) if (RSIndex2[i-1] < shortband[i-1] and RSIndex2[i] < shortband[i-1]) else new_shortband[i]

        bull_cross = RSIndex2[i] > shortband[i-1]
        bear_cross = longband[i-1] > RSIndex2[i]

        if bull_cross:
            trend2[i] = 1
        elif bear_cross:
            trend2[i] = -1
        else:
            trend2[i] = trend2[i-1]

    # Zero-cross counting
    above = RSIndex2 >= threshold
    below = RSIndex2 < threshold

    QQEzlong = 0
    QQEzshort = 0

    for i in range(len(close)):
        if above[i]:
            QQEzlong += 1
            QQEzshort = 0
        elif below[i]:
            QQEzshort += 1
            QQEzlong = 0

    # Final bullish/bearish signal
    if trend2[-2] == -1 and trend2[-1] == 1:
        return 1  # Bullish
    elif trend2[-2] == 1 and trend2[-1] == -1:
        return -1  # Bearish
    else:
        return 0
