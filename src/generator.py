import numpy as np
import pandas as pd

TRADING_MINUTES = 390

# Build a DatetimeIndex for one trading day.
def make_trading_index(date: str = "2025-10-07") -> pd.DatetimeIndex:
    return pd.date_range(
        start=f"{date} 09:30",
        periods=TRADING_MINUTES,
        freq="1min",
        tz=None,
    )

# Simulate 1-minute OHLCV bars for one trading day.
def simulate_1min_ohlc(
    start_price: float = 100.0,
    date: str = "2025-10-07",
    mu: float = 0.0,
    sigma: float = 0.0018,
    seed: int | None = 42,
) -> pd.DataFrame:
 
    # Build the time index for one day
    idx = make_trading_index(date)
    n = len(idx)

    # Random generator
    rng = np.random.default_rng(seed)

    # Close: simulate log-normal returns and build a price series
    returns = rng.normal(loc=mu, scale=sigma, size=n)
    close = start_price * np.exp(np.cumsum(returns))

    # Open: previous minute's close (and the very first open = start_price)
    open_ = np.empty(n, dtype=float)
    open_[0] = start_price
    open_[1:] = close[:-1]

    # Create an intraminute range so that high/low wrap open and close
    intrarange = np.abs(
        rng.normal(loc=0.0, scale=sigma * 6, size=n)
    ) * np.maximum(open_, close)

    high = np.maximum(open_, close) + 0.5 * intrarange
    low = np.minimum(open_, close) - 0.5 * intrarange

    # Prevent negative or zero prices
    low = np.clip(low, 0.01, None)

    # Volume: random integers in a simple realistic band
    volume = rng.integers(low=3000, high=20000, size=n)

    # Typical price
    tp = (high + low + close) / 3.0

    # Build the DataFrame
    df = pd.DataFrame(
        {
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
            "tp": tp,
        },
        index=idx,
    )
    df.index.name = "timestamp"
    return df