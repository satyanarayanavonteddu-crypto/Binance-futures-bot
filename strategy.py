from indicators.rsi import rsi_signal
from indicators.macd import macd_signal
from indicators.supertrend import supertrend_signal
from indicators.support_resistance import sr_signal
from indicators.ema import ema_signal

ENTRY_THRESHOLD = 4  # example: need 4 points to trade
EXIT_THRESHOLD = -3  # example: exit if -3 score

def get_trade_signal(df):
    score = 0

    # RSI
    if rsi_signal(df) == "buy": score += 1
    elif rsi_signal(df) == "sell": score -= 1

    # MACD
    if macd_signal(df) == "buy": score += 1
    elif macd_signal(df) == "sell": score -= 1

    # EMA Cross
    if ema_signal(df) == "buy": score += 2
    elif ema_signal(df) == "sell": score -= 2

    # Supertrend
    if supertrend_signal(df) == "buy": score += 1
    elif supertrend_signal(df) == "sell": score -= 1

    # Support / Resistance
    if sr_signal(df) == "buy": score += 1
    elif sr_signal(df) == "sell": score -= 1

    # Decision
    if score >= ENTRY_THRESHOLD:
        return "BUY"
    elif score <= EXIT_THRESHOLD:
        return "SELL"
    else:
        return "WAIT"
