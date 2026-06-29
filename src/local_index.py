# -*- coding: utf-8 -*-
"""Compute price index locally from CSV (fallback when CK unreachable)."""
import argparse
import csv
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from config_loader import DAILY_PRICE_DIR, ROOT, load_config


def load_daily_avg(csv_path: Path):
    total, count = 0.0, 0
    with open(csv_path, encoding="gbk") as f:
        for r in csv.DictReader(f):
            try:
                p = float(r["price"])
            except (TypeError, ValueError):
                continue
            if p > 0:
                total += p
                count += 1
    if count == 0:
        return None, 0
    date_str = csv_path.stem.replace("daily_prices_", "")
    d = datetime.strptime(date_str, "%Y%m%d").date()
    return d, total / count


def compute(limit: int = 0, sample_every: int = 1):
    cfg = load_config()
    base_date = datetime.strptime(cfg["project"]["base_date"], "%Y-%m-%d").date()
    files = sorted(DAILY_PRICE_DIR.glob("daily_prices_*.csv"))
    if limit:
        files = files[:limit]
    files = files[::sample_every]

    series = []
    for f in files:
        d, avg = load_daily_avg(f)
        if d and avg:
            series.append((d, avg))

    base_avg = next((avg for d, avg in series if d == base_date), series[0][1])
    out = [(d, avg / base_avg * 100) for d, avg in series]
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--sample-every", type=int, default=7)
    parser.add_argument("--out", default=str(ROOT / "report" / "price_index_trend.png"))
    args = parser.parse_args()

    series = compute(args.limit, args.sample_every)
    dates = [x[0] for x in series]
    values = [x[1] for x in series]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(dates, values, color="#1976D2", linewidth=1.5)
    ax.axhline(100, color="#999", linestyle="--", linewidth=0.8)
    ax.set_title("Daily E-commerce Price Index (local compute)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Index (Base=100)")
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    fig.autofmt_xdate()
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved: {out}")
    print(f"Points: {len(values)}, range: {min(values):.2f} - {max(values):.2f}")


if __name__ == "__main__":
    main()
