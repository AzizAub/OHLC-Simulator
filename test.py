from __future__ import annotations
import numpy as np
import pandas as pd

from src.generator import simulate_1min_ohlc, make_trading_index
from src.aggregate import aggregate
from src.metrics import add_vwap_from_1m, add_time_rolling_metrics

def test_generate_shape_and_invariants():
    # 390 rows from 09:30 to 15:59 and basic OHLC rules hold
    idx = make_trading_index("2025-10-07")
    assert len(idx) == 390
    assert str(idx[0].time()) == "09:30:00"
    assert str(idx[-1].time()) == "15:59:00"

    df = simulate_1min_ohlc(date="2025-10-07", seed=1)
    assert len(df) == 390
    assert (df["high"] >= df[["open","close"]].max(axis=1)).all()
    assert (df["low"]  <= df[["open","close"]].min(axis=1)).all()
    assert (df["low"] > 0).all()
    assert (df["volume"] > 0).all()

def test_aggregate_sizes_and_first_bucket_logic():
    df1 = simulate_1min_ohlc(seed=2)
    df5 = aggregate(df1, "5min")
    df30 = aggregate(df1, "30min")
    dfd = aggregate(df1, "1D")

    # exact bar counts for the trading session
    assert len(df5) == 78
    assert len(df30) == 13
    assert len(dfd) == 1

    # check the very first 5-minute bucket precisely
    start = df5.index[0]
    end = start + pd.Timedelta(minutes=5) - pd.Timedelta(minutes=1)
    window = df1.loc[start:end]
    assert np.isclose(df5.loc[start, "open"],  window["open"].iloc[0])
    assert np.isclose(df5.loc[start, "close"], window["close"].iloc[-1])
    assert np.isclose(df5.loc[start, "high"],  window["high"].max())
    assert np.isclose(df5.loc[start, "low"],   window["low"].min())
    assert np.isclose(df5.loc[start, "volume"], window["volume"].sum())

def test_vwap_and_rolling_metrics_basic():
    df1 = simulate_1min_ohlc(seed=3)
    df5 = aggregate(df1, "5min")
    df5 = add_vwap_from_1m(df5, df1, "5min")
    df5 = add_time_rolling_metrics(df5)

    # VWAP lies between low and high of the bar
    mask = df5["vwap"].notna()
    assert ((df5.loc[mask, "vwap"] >= df5.loc[mask, "low"]) & (df5.loc[mask, "vwap"] <= df5.loc[mask, "high"])).all()

    # After 35 minutes, rolling windows should be filled
    ready = df5.index >= (df5.index[0] + pd.Timedelta(minutes=35))
    assert df5.loc[ready, "ma_30m"].notna().all()
    assert df5.loc[ready, "median_15m"].notna().all()