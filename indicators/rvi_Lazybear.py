# --- Relative Volume Indicator (LazyBear) ---

def RVI_LazyBear(df, x=60, y=2, allow_negative=False, match_volume_color=False):
    # Simple Moving Average of volume
    df['av'] = df['volume'].rolling(window=x).mean()
    
    # Standard deviation of volume
    df['sd'] = df['volume'].rolling(window=x).std()

    # Relative Volume calculation
    df['relVol'] = (df['volume'] - df['av']) / df['sd']
    df['relVol'] = df['relVol'].fillna(0)

    # Allow only positive?
    if not allow_negative:
        df['relV'] = df['relVol'].clip(lower=0)
    else:
        df['relV'] = df['relVol']

    # Volume color for bar visualization (not needed for bot logic)
    df['volColor'] = np.where(df['close'] > df['open'], "green", "red")
    df['barColor'] = np.where(df['relV'] > y,
                              df['volColor'] if match_volume_color else "black",
                              "gray")

    # Trading signals — **YOU WILL USE THIS**
    df['RVI_signal'] = np.where(df['relV'] > y, 1, 0)

    return df
