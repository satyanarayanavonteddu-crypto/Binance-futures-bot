# indicators/dynamic_sr.py
import numpy as np
import pandas as pd

def find_pivots(df, prd=10, source='high_low', maxnumpp=20):
    """
    Find pivot highs/lows similar to ta.pivothigh/pivotlow behavior.
    Returns pivotvals list (most recent first).
    """
    highs = df['high'].values
    lows = df['low'].values
    n = len(df)
    pivotvals = []

    # iterate bars, exclude edges
    for i in range(prd, n - prd):
        # If source "High/Low" use highs/lows pair
        left_high = highs[i-prd:i+prd+1]
        left_low  = lows[i-prd:i+prd+1]
        is_ph = highs[i] == left_high.max()
        is_pl = lows[i] == left_low.min()
        if is_ph:
            pivotvals.insert(0, float(highs[i]))   # most recent at index 0
        elif is_pl:
            pivotvals.insert(0, float(lows[i]))

        if len(pivotvals) >= maxnumpp:
            break

    return pivotvals


def get_sr_vals_for_pivot(pivotvals, ind, cwidth):
    """
    Equivalent of get_sr_vals in Pine.
    Given pivotvals list (most recent first) compute hi, lo and count (strength).
    """
    if ind >= len(pivotvals):
        return None, None, 0
    lo = pivotvals[ind]
    hi = lo
    numpp = 0
    for cpp in pivotvals:
        wdth = (hi - cpp) if cpp <= lo else (cpp - lo)  # width relative
        if wdth <= cwidth:
            if cpp <= hi:
                lo = min(lo, cpp)
            else:
                hi = max(hi, cpp)
            numpp += 1
    return float(hi), float(lo), int(numpp)


def dynamic_sr(df,
               prd=10,
               maxnumpp=20,
               channelW_percent=10,
               maxnumsr=5,
               min_strength=2):
    """
    Compute Dynamic Support/Resistance similar to SRv2.
    Returns dict:
      - levels: list of midpoints (sorted by strength desc)
      - up_levels, dn_levels: lists of hi/lo
      - strength: list of strength
      - crossed_over: bool (price crossed above any midpoint this bar)
      - crossed_under: bool (price crossed below any midpoint this bar)
    """
    if not {'high','low','close'}.issubset(df.columns):
        raise ValueError("df must contain 'high','low','close'")

    # Channel width absolute value: use recent high/low range
    recent_high = df['high'].rolling(window=300, min_periods=1).max().iloc[-1]
    recent_low  = df['low'].rolling(window=300, min_periods=1).min().iloc[-1]
    cwidth = (recent_high - recent_low) * (channelW_percent / 100.0)
    if cwidth <= 0:
        cwidth = (df['high'].max() - df['low'].min()) * (channelW_percent / 100.0)

    # 1) get pivot values (most-recent-first)
    pivotvals = find_pivots(df, prd=prd, maxnumpp=maxnumpp)

    # 2) build sr candidates
    sr_up_level = []
    sr_dn_level = []
    sr_strength = []

    def check_sr(hi, lo, strength):
        # ensure new zone doesn't collide with existing zones of >= strength
        for i in range(len(sr_up_level)):
            existing_hi = sr_up_level[i]
            existing_lo = sr_dn_level[i]
            if (existing_hi >= lo and existing_hi <= hi) or (existing_lo >= lo and existing_lo <= hi):
                # overlap found
                if strength >= sr_strength[i]:
                    # replace weaker zone
                    sr_up_level.pop(i)
                    sr_dn_level.pop(i)
                    sr_strength.pop(i)
                    return True
                else:
                    return False
        return True

    # iterate pivots and create zones
    for idx in range(len(pivotvals)):
        hi, lo, strength = get_sr_vals_for_pivot(pivotvals, idx, cwidth)
        if hi is None:
            continue
        if strength >= min_strength and check_sr(hi, lo, strength):
            # insert maintaining descending strength order up to maxnumsr
            insert_at = len(sr_strength)
            for i in range(len(sr_strength)-1, -1, -1):
                if strength > sr_strength[i]:
                    insert_at = i
            sr_strength.insert(insert_at, strength)
            sr_up_level.insert(insert_at, hi)
            sr_dn_level.insert(insert_at, lo)
            # limit size
            if len(sr_strength) > maxnumsr:
                sr_strength = sr_strength[:maxnumsr]
                sr_up_level = sr_up_level[:maxnumsr]
                sr_dn_level = sr_dn_level[:maxnumsr]

    # 3) compute midpoints and detect crosses
    midpoints = []
    for hi, lo in zip(sr_up_level, sr_dn_level):
        mid = round((hi + lo) / 2.0, 8)
        midpoints.append(mid)

    # price crossing detection for the last bar:
    crossed_over = False
    crossed_under = False
    if len(midpoints) > 0 and len(df) >= 2:
        prev_close = float(df['close'].iloc[-2])
        curr_close = float(df['close'].iloc[-1])
        for mid in midpoints:
            if prev_close <= mid and curr_close > mid:
                crossed_over = True
            if prev_close >= mid and curr_close < mid:
                crossed_under = True

    # package results
    res = {
        'levels': midpoints,
        'up_levels': sr_up_level,
        'dn_levels': sr_dn_level,
        'strength': sr_strength,
        'crossed_over': crossed_over,
        'crossed_under': crossed_under,
        'pivotvals': pivotvals  # optional for debugging
    }
    return res
