# -*- coding: utf-8 -*-
"""Plot daily index from ClickHouse."""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from ck_client import get_ck_client
from config_loader import ROOT


def plot_from_ck(out_path: Path):
    client = get_ck_client()
    rows = client.query(
        """
        SELECT change_date, index_value
        FROM agg_daily_index
        WHERE category_id = ''
        ORDER BY change_date
        """
    )
    if not rows:
        raise RuntimeError("agg_daily_index is empty. Run calc_daily_index.sql first.")

    dates = [r[0] for r in rows]
    values = [float(r[1]) for r in rows]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(dates, values, color="#1976D2", linewidth=1.5)
    ax.axhline(100, color="#999", linestyle="--", linewidth=0.8)
    ax.set_title("Daily E-commerce Price Index")
    ax.set_xlabel("Date")
    ax.set_ylabel("Index (Base=100)")
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    fig.autofmt_xdate()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"Saved: {out_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(ROOT / "report" / "price_index_trend.png"))
    args = parser.parse_args()
    plot_from_ck(Path(args.out))


if __name__ == "__main__":
    main()
