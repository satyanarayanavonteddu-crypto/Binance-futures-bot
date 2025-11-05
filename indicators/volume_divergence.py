import pandas as pd
import numpy as np

def pivot_low(series, lbL, lbR):
    return (series.shift(lbL) == series.rolling(lbL + lbR + 1).min())

def pivot_high(series, lbL, lbR):
    return (series.shift(lbL) == series.rolling(lbL + lbR + 1).max())

def barssince(condition):
    idx = np.where(condition, np.arange(len(condition)), np.nan)
    last = pd.Series(idx).fillna(method="ffill")
    return (np.arange(len(condition)) - last).astype(int)

def volume_divergence(df, vl1=5, vl2=8, lbL=5, lbR=5, rangeLower=5, rangeUpper=60):
    # Pine WMA replacement
    def pine_wma(x, length):
        weight_sum = sum((length - i) * length for i in range(length))
        wma = []
        for i in range(len(x)):
            if i < length: 
                wma.append(0)
            else:
                total = 0
                for j in range(length):
                    weight = (length - j) * length
                    factor = 1 if df["close"].iloc[i-j] >= df["open"].iloc[i-j] else -1
                    total += x.iloc[i-j] * weight * factor
                wma.append(total / weight_sum)
        return pd.Series(wma, index=x.index)

    v1 = pine_wma(df['volume'], vl1)
    v2 = pine_wma(v1, vl2)
    v3 = pine_wma(v2, vl1+vl2)
    v4 = pine_wma(v3, vl1+vl2+vl1+vl2) 
    vol = pine_wma(v4, vl1+vl2 + (vl1+vl2) + (vl1+vl2+vl1+vl2))

    df["vol"] = vol

    pl = pivot_low(df["vol"], lbL, lbR)
    ph = pivot_high(df["vol"], lbL, lbR)

    pl_price = pivot_low(df["low"], lbL, lbR)
    ph_price = pivot_high(df["high"], lbL, lbR)

    in_range_pl = (barssince(pl) >= rangeLower) & (barssince(pl) <= rangeUpper)
    in_range_ph = (barssince(ph) >= rangeLower) & (barssince(ph) <= rangeUpper)

    prev_vol_pl = df["vol"].shift(lbR).where(pl).ffill()
    prev_vol_ph = df["vol"].shift(lbR).where(ph).ffill()

    prev_low = df["low"].shift(lbR).where(pl_price).ffill()
    prev_high = df["high"].shift(lbR).where(ph_price).ffill()

    # Divergence Logic
    df["regular_bull"] = (df["low"].shift(lbR) < prev_low) & (df["vol"].shift(lbR) > prev_vol_pl) & pl & in_range_pl
    df["hidden_bull"] = (df["low"].shift(lbR) > prev_low) & (df["vol"].shift(lbR) < prev_vol_pl) & pl & in_range_pl

    df["regular_bear"] = (df["high"].shift(lbR) > prev_high) & (df["vol"].shift(lbR) < prev_vol_ph) & ph & in_range_ph
    df["hidden_bear"] = (df["high"].shift(lbR) < prev_high) & (df["vol"].shift(lbR) > prev_vol_ph) & ph & in_range_ph

    # Signal Column
    df["div_signal"] = 0
    df.loc[df["regular_bull"] | df["hidden_bull"], "div_signal"] = 1
    df.loc[df["regular_bear"] | df["hidden_bear"], "div_signal"] = -1

    # Text Labels
    df["div_label"] = ""
    df.loc[df["regular_bull"], "div_label"] = "Bullish Divergence"
    df.loc[df["hidden_bull"], "div_label"] = "Hidden Bullish Divergence"
    df.loc[df["regular_bear"], "div_label"] = "Bearish Divergence"
    df.loc[df["hidden_bear"], "div_label"] = "Hidden Bearish Divergence"

    return df
