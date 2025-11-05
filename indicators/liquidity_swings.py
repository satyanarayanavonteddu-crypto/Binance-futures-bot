import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple

# ---------------------------
# Part 1-3 conversion (pivot + zone counts)
# ---------------------------

def is_pivothigh(series: pd.Series, idx: int, left:int, right:int) -> bool:
    """Return True if series[idx] is strictly the maximum over window [idx-left .. idx+right]."""
    if idx - left < 0 or idx + right >= len(series):
        return False
    window = series.iloc[idx-left: idx+right+1]
    return series.iloc[idx] == window.max()

def is_pivotlow(series: pd.Series, idx: int, left:int, right:int) -> bool:
    """Return True if series[idx] is strictly the minimum over window [idx-left .. idx+right]."""
    if idx - left < 0 or idx + right >= len(series):
        return False
    window = series.iloc[idx-left: idx+right+1]
    return series.iloc[idx] == window.min()

def find_pivots(df: pd.DataFrame, length:int=14, area:str='Wick Extremity', max_pivots:int=100) -> Dict[str, List[Dict[str,Any]]]:
    """
    Scan dataframe and return pivot highs and pivot lows in most-recent-first order (like Pine's pivot)
    Each pivot item: {'index': idx, 'top': value_top, 'btm': value_btm, 'bar_index': df.index[idx]}
    area: 'Wick Extremity' uses wick-based top/btm, 'Full Range' uses full bar
    """
    highs = df['high']
    lows = df['low']
    opens = df['open']
    closes = df['close']
    n = len(df)

    ph_list = []
    pl_list = []

    # pivot detection approach: for idx from length .. n-length-1 check pivot
    for idx in range(length, n - length):
        if is_pivothigh(highs, idx, length, length):
            # determine top/btm per Pine logic
            if area == 'Wick Extremity':
                top = highs.iloc[idx]
                btm = max(closes.iloc[idx-length], opens.iloc[idx-length])  # using left bar close/open like pine
            else:
                top = highs.iloc[idx]
                btm = lows.iloc[idx-length]
            ph_list.insert(0, {'idx': idx, 'top': float(top), 'btm': float(btm), 'bar_index': idx})
            if len(ph_list) >= max_pivots:
                break
        if is_pivotlow(lows, idx, length, length):
            if area == 'Wick Extremity':
                top = min(closes.iloc[idx-length], opens.iloc[idx-length])
                btm = lows.iloc[idx]
            else:
                top = highs.iloc[idx-length]
                btm = lows.iloc[idx]
            pl_list.insert(0, {'idx': idx, 'top': float(top), 'btm': float(btm), 'bar_index': idx})
            if len(pl_list) >= max_pivots:
                break

    return {'pivot_highs': ph_list, 'pivot_lows': pl_list}


def get_counts_for_zone(df: pd.DataFrame, top: float, btm: float, length:int, filter_by: str='Count') -> Tuple[int, float]:
    """
    Counts how many bars in the window [ -length ] intersect the zone [btm, top],
    and sums volume for those bars.
    This is simplified version of get_counts() — intrabar precision and lower-tf aggregation omitted for now.
    """
    if len(df) < length + 1:
        return 0, 0.0

    # we'll look at the bar that created the pivot at index -length (like Pine uses [length])
    check_idx = -length
    # take the single bar at -length for pivot origin and count in history up to that point
    # But LuxAlgo counts occurrences across the same indexed bar: use df.iloc[-length]
    window_slice = df.iloc[-length - 200 : -length + 1]  # check a reasonable history before the pivot recent bar
    count = 0
    vol_sum = 0.0
    for i, row in window_slice.iterrows():
        if row['low'] < top and row['high'] > btm:
            count += 1
            vol_sum += float(row.get('volume', 0.0))
    return count, vol_sum


def build_sr_zones_from_pivots(df: pd.DataFrame, length:int=14, area:str='Wick Extremity',
                               show_top:bool=True, show_btm:bool=True,
                               filter_by:str='Count', filter_value:float=0.0) -> Dict[str, Any]:
    """
    Reconstruct zones similarly to Part3: create zone records from detected pivots.
    Returns dict:
      {
        'ph_zones': [ {top,btm,idx,count,vol,crossed}, ... ],
        'pl_zones': [ ... ],
      }
    Zones lists are sorted by recency (most recent first).
    """
    piv = find_pivots(df, length=length, area=area)
    phs = piv['pivot_highs']
    pls = piv['pivot_lows']

    ph_zones = []
    for p in phs:
        top = p['top']
        btm = p['btm']
        # compute counts and volume for that zone
        cnt, vol = get_counts_for_zone(df, top, btm, length, filter_by)
        crossed = float(df['close'].iloc[-1]) > top
        ph_zones.append({
            'top': top, 'btm': btm, 'idx': p['idx'], 'count': cnt, 'vol': vol, 'crossed': crossed
        })

    pl_zones = []
    for p in pls:
        top = p['top']
        btm = p['btm']
        cnt, vol = get_counts_for_zone(df, top, btm, length, filter_by)
        crossed = float(df['close'].iloc[-1]) < btm
        pl_zones.append({
            'top': top, 'btm': btm, 'idx': p['idx'], 'count': cnt, 'vol': vol, 'crossed': crossed
        })

    return {'ph_zones': ph_zones, 'pl_zones': pl_zones}


def detect_zone_crosses(df: pd.DataFrame, zones: List[Dict[str,Any]]) -> Dict[str, List[Dict[str,Any]]]:
    """
    For each zone set crossed=True/False based on last bar close crossing the zone midpoint.
    Returns updated zones.
    """
    updated = []
    prev_close = float(df['close'].iloc[-2]) if len(df) >= 2 else None
    curr_close = float(df['close'].iloc[-1])
    for z in zones:
        mid = (z['top'] + z['btm']) / 2.0
        crossed_over = (prev_close is not None and prev_close <= mid and curr_close > mid)
        crossed_under = (prev_close is not None and prev_close >= mid and curr_close < mid)
        z['crossed_over'] = crossed_over
        z['crossed_under'] = crossed_under
        updated.append(z)
    return updated
