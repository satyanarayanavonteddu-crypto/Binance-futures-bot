import pandas as pd
import numpy as np

def tema(series, length):
    ema1 = series.ewm(span=length, adjust=False).mean()
    ema2 = ema1.ewm(span=length, adjust=False).mean()
    ema3 = ema2.ewm(span=length, adjust=False).mean()
    return 3 * (ema1 - ema2) + ema3

def vervoort_hacolt(df, length=55, ema_length=60, candle_factor=1.1):
    o = df['open']
    h = df['high']
    l = df['low']
    c = df['close']

    ohlc4 = (o + h + l + c) / 4
    hl2 = (h + l) / 2

    # Heiken-Ashi calculations
    ha_open = pd.Series(index=df.index, dtype=float)
    ha_open.iloc[0] = ohlc4.iloc[0]
    for i in range(1, len(df)):
        ha_open.iloc[i] = (ha_open.iloc[i-1] + ohlc4.iloc[i]) / 2

    ha_close = (ha_open + np.maximum(h, ha_open) + np.minimum(l, ha_open) + ohlc4) / 4

    # TEMA smoothing
    tha_close = tema(ha_close, length)
    thl2 = tema(hl2, length)
    ha_close_smooth = 2 * tha_close - tema(tha_close, length)
    hl2_smooth = 2 * thl2 - tema(thl2, length)

    short_candle = abs(c - o) < ((h - l) * candle_factor)

    keepn1 = ((ha_close >= ha_open) & (ha_close.shift(1) >= ha_open.shift(1))) | \
             (c >= ha_close) | (h > h.shift(1)) | (l > l.shift(1)) | \
             (hl2_smooth >= ha_close_smooth)

    keepall1 = keepn1 | ((keepn1.shift(1)) & ((c >= o) | (c >= c.shift(1))))
    keep13 = short_candle & (h >= l.shift(1))
    utr = keepall1 | ((keepall1.shift(1)) & keep13)

    keepn2 = ((ha_close < ha_open) & (ha_close.shift(1) < ha_open.shift(1))) | \
             (hl2_smooth < ha_close_smooth)

    keep23 = short_candle & (l <= h.shift(1))
    keepall2 = keepn2 | ((keepn2.shift(1)) & ((c < o) | (c < c.shift(1))))
    dtr = keepall2 | ((keepall2.shift(1)) & keep23)

    upw = (dtr == 0) & (dtr.shift(1)) & utr
    dnw = (utr == 0) & (utr.shift(1)) & dtr

    # Uptrend offset logic
    upw_offset = upw.copy()
    for i in range(1, len(df)):
        if upw.iloc[i] == dnw.iloc[i]:
            upw_offset.iloc[i] = upw_offset.iloc[i-1]

    buy_sig = upw | (~dnw & upw_offset.fillna(0).astype(bool))
    lt_sell = c < c.ewm(span=ema_length, adjust=False).mean()
    neutral = buy_sig | ((~lt_sell) & (lambda x: x.shift(1) if isinstance(x,pd.Series) else 0)(buy_sig))

    hacolt = np.where(buy_sig, 1, np.where(neutral, 0, -1))

    df['HACOLT'] = hacolt
    df['HACOLT_signal'] = np.where(df['HACOLT'] > 0, "BUY",
                           np.where(df['HACOLT'] < 0, "SELL", "NEUTRAL"))

    return df
