import numpy as np

def namib_final(
        close, open_price,
        hull, hull_prev2,
        iTrend,
        rsi_ma, rsi_ma2,
        upper, lower,
        ThreshHold2=3
    ):
    # Hull trend
    hull_green = hull > hull_prev2
    hull_red = hull < hull_prev2

    # Follow line trend
    follow_green = iTrend > 0
    follow_red = not follow_green

    # QQE conditions
    Greenbar1 = (rsi_ma2 - 50) > ThreshHold2
    Greenbar2 = (rsi_ma - 50) > upper

    Redbar1 = (rsi_ma2 - 50) < -ThreshHold2
    Redbar2 = (rsi_ma - 50) < lower

    QQE_green = Greenbar1 and Greenbar2
    QQE_red = Redbar1 and Redbar2

    # Candle momentum
    bar_green = close > open_price
    bar_red = close < open_price

    # Full combined condition like TradingView script
    full_condition_long = hull_green and follow_green and QQE_green and bar_green
    full_condition_short = hull_red and follow_red and QQE_red and bar_red

    # We need previous values, so we return raw, and handle counters in strategy.py
    return full_condition_long, full_condition_short
