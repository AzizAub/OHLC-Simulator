import pandas as pd

# Turn '5T' -> '5min', '30T' -> '30min'.
def _normalize_rule(rule: str) -> str:
    r = rule.strip().lower()
    if r.endswith("t") and r[:-1].isdigit():
        return f"{r[:-1]}min"
    if r.endswith("min"):
        return r
    if r in ("1d", "d"):
        return "1D"
    return rule

# Add VWAP to aggregated bars using the original 1-minute data.
def add_vwap_from_1m(df_agg: pd.DataFrame, df_1m: pd.DataFrame, rule: str) -> pd.DataFrame:
    out = df_agg.copy()
    if df_1m.empty or df_agg.empty:
        out["vwap"] = pd.NA
        return out

    norm = _normalize_rule(rule)
    if norm not in ("5min", "30min"):
        out["vwap"] = pd.NA
        return out

    origin = df_1m.index[0]

    # Typical price from 1-minute bars.
    tp_1m = (df_1m["high"] + df_1m["low"] + df_1m["close"]) / 3.0

    # Sum(tp * vol) and sum(vol) over the same resample buckets.
    num = (tp_1m * df_1m["volume"]).resample(norm, label="left", closed="left", origin=origin).sum()
    den = df_1m["volume"].resample(norm, label="left", closed="left", origin=origin).sum()

    # Safe alignment to the aggregated index.
    out["vwap"] = (num / den).reindex(out.index)
    return out

# Add 30-minute moving average and 15-minute moving median on aggregated bars.
def add_time_rolling_metrics(df_agg: pd.DataFrame) -> pd.DataFrame:
    out = df_agg.copy()
    out["ma_30m"] = out["close"].rolling("30min").mean()
    out["median_15m"] = out["close"].rolling("15min").median()
    return out