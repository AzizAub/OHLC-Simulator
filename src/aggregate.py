import pandas as pd

# '5T' -> '5min', '30T' -> '30min'
def _normalize_rule(rule: str) -> str:
    r = rule.strip().lower()
    if r.endswith("t") and r[:-1].isdigit():
        return f"{r[:-1]}min"
    if r.endswith("min"):
        return r
    if r in ("1d", "d"):
        return "1D"
    return rule

# Aggregate 1-minute OHLCV into higher timeframes (5min, 30min, 1D).
def aggregate(df_1m: pd.DataFrame, rule: str) -> pd.DataFrame:
    if df_1m.empty:
        return df_1m.copy()

    norm = _normalize_rule(rule)

    # Align resampling buckets to the very first minute (09:30).
    origin = df_1m.index[0]

    # One resampler for all columns, then aggregate with a clear map.
    resampler = df_1m.resample(norm, label="left", closed="left", origin=origin)

    out = resampler.agg({
        "open":  "first",
        "high":  "max",
        "low":   "min",
        "close": "last",
        "volume":"sum",
    })

    return out