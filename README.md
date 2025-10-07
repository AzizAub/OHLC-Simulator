# OHLC Simulator & Aggregator

Generate simulated 1‑minute OHLCV data for a single trading day (09:30–16:00, 390 minutes), aggregate into 5‑minute, 30‑minute, and daily bars, and compute basic metrics (VWAP, 30‑minute moving average, 15‑minute moving median).

---

## Folder structure

```
.
├─ src/
│  ├─ __init__.py        # package marker
│  ├─ generator.py       # builds the 1‑minute timeline and simulates OHLCV
│  ├─ aggregate.py       # 1m → 5min / 30min / 1D resampling (open/close/high/low/volume)
│  └─ metrics.py         # VWAP (from 1m) + 30min MA / 15min median on aggregated bars
├─ main.py               # CLI entry point: run generation, aggregation, metrics, optional export
├─ requirements.txt      # pandas, numpy, pytest
└─ test.py               # minimal tests (shape, aggregation logic, metrics)
```

---

## Quick start

```bash
# 1) create & activate venv (example for Windows PowerShell)
python -m venv .venv
. .venv\Scripts\Activate.ps1

# 2) install
pip install -r requirements.txt

# 3) run
python main.py

# save CSV outputs
python main.py --out data_out

# run tests
pytest -q
# or
python -m pytest -q test.py
```

## What the project does

* **1‑minute generation**: vectorized price path (no Python loops); `high ≥ max(open, close)`, `low ≤ min(open, close)`, volumes per minute, and `tp` (typical price) for VWAP.
* **Aggregation**: resample 1m into **5min**, **30min**, and **1D** with:

  * `open`: first, `close`: last, `high`: max, `low`: min, `volume`: sum.
  * Buckets align to the first bar at **09:30** to keep exactly 78×5min and 13×30min bars.
* **Metrics**:

  * **VWAP** for 5min/30min from minute data (`sum(tp*vol)/sum(vol)` per bucket).
  * **MA‑30m** and **Median‑15m** as time‑based rolling stats on aggregated bars.

---

## Outputs (with `--out data_out`)

CSV files are written to the chosen folder:

* `bars_1m.csv` → columns: `open, high, low, close, volume, tp`
* `bars_5m.csv` → `open, high, low, close, volume, vwap, ma_30m, median_15m`
* `bars_30m.csv` → `open, high, low, close, volume, vwap, ma_30m, median_15m`
* `bars_1d.csv` → `open, high, low, close, volume` (no VWAP or rolling metrics)

---

## Notes

* Time window strings use modern forms (`"5min"`, `"30min"`) to avoid deprecated aliases.
* Design favors speed: NumPy vectorization + `pandas.resample`/`rolling`.
