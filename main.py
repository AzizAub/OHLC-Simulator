import argparse
import pandas as pd
import pathlib

from src.generator import simulate_1min_ohlc
from src.aggregate import aggregate
from src.metrics import add_vwap_from_1m, add_time_rolling_metrics

def main():
    parser = argparse.ArgumentParser(description="Generate 1m OHLC, aggregate, and compute basic metrics.")
    parser.add_argument("--date", default="2025-10-07", help="Trading date (YYYY-MM-DD)")
    parser.add_argument("--start-price", type=float, default=100.0, help="Starting price")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--out", default="", help="Folder to save CSVs")
    args = parser.parse_args()
    

    # 1) 1-minute generation
    df1 = simulate_1min_ohlc(start_price=args.start_price, date=args.date, seed=args.seed)

    # 2) Aggregations
    df5  = aggregate(df1, "5min")
    df30 = aggregate(df1, "30min")
    dfd  = aggregate(df1, "1D")

    # 3) Metrics
    df5  = add_vwap_from_1m(df5, df1, "5min")
    df30 = add_vwap_from_1m(df30, df1, "30min")
    df5  = add_time_rolling_metrics(df5)
    df30 = add_time_rolling_metrics(df30)

    if args.out.strip():
        p = pathlib.Path(args.out)
        p.mkdir(parents=True, exist_ok=True)
        df1.to_csv(p / "bars_1m.csv", index=True)
        df5.to_csv(p / "bars_5m.csv", index=True)
        df30.to_csv(p / "bars_30m.csv", index=True)
        dfd.to_csv(p / "bars_1d.csv", index=True)
        print(f"\nSaved CSVs to: {p.resolve()}")

    # Print small preview
    pd.set_option("display.width", 140)
    pd.set_option("display.max_columns", 10)

    print("\n=== 1-minute (head) ===")
    print(df1.head(3))

    print("\n=== 5-minute bars (head) ===")
    print(df5.head(5)[["open","high","low","close","volume","vwap","ma_30m","median_15m"]])

    print("\n=== 30-minute bars (head) ===")
    print(df30.head(3)[["open","high","low","close","volume","vwap","ma_30m","median_15m"]])

    print("\n=== Daily bars ===")
    print(dfd[["open","high","low","close","volume"]])

if __name__ == "__main__":
    main()