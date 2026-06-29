# -*- coding: utf-8 -*-
"""Import CSV into ClickHouse."""
import argparse
import csv
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from ck_client import get_ck_client
from config_loader import DAILY_PRICE_DIR, ROOT, load_config


def read_csv(path: Path):
    rows = []
    with open(path, encoding="gbk") as f:
        for r in csv.DictReader(f):
            try:
                price = Decimal(r["price"])
            except Exception:
                continue
            if price <= 0:
                continue
            rows.append(
                (
                    str(r["product_id"]),
                    str(r["category_id"]),
                    r.get("name", ""),
                    float(price),
                    0,
                    datetime.strptime(r["change_date"], "%Y-%m-%d").date(),
                )
            )
    return rows


def import_file(csv_path: Path, client):
    rows = read_csv(csv_path)
    if not rows:
        print(f"No valid rows: {csv_path}")
        return 0
    change_date = rows[0][5]
    client.execute(
        f"ALTER TABLE fact_daily_price DELETE WHERE change_date = '{change_date}'"
    )
    client.insert_rows(
        "fact_daily_price",
        rows,
        ["product_id", "category_id", "product_name", "price", "sales", "change_date"],
    )
    return len(rows)


def import_dir(local_dir: Path, limit: int = 0):
    client = get_ck_client()
    files = sorted(local_dir.glob("daily_prices_*.csv"))
    if limit:
        files = files[:limit]
    if not files:
        print(f"No CSV files: {local_dir}")
        sys.exit(1)
    total = 0
    for i, f in enumerate(files, 1):
        n = import_file(f, client)
        total += n
        print(f"[{i}/{len(files)}] {f.name} -> {n} rows")
    print(f"Done. Total rows: {total}")


def run_sql_file(sql_path: Path):
    client = get_ck_client()
    sql = sql_path.read_text(encoding="utf-8")
    client.execute_many(sql)
    print(f"Executed: {sql_path.name}")


def main():
    parser = argparse.ArgumentParser(description="Load CSV into ClickHouse")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_import = sub.add_parser("import")
    p_import.add_argument("--dir", default=str(DAILY_PRICE_DIR))
    p_import.add_argument("--limit", type=int, default=3)

    p_sql = sub.add_parser("sql")
    p_sql.add_argument("file", type=str)

    sub.add_parser("ddl")

    args = parser.parse_args()
    if args.cmd == "import":
        import_dir(Path(args.dir), args.limit)
    elif args.cmd == "sql":
        run_sql_file(Path(args.file))
    elif args.cmd == "ddl":
        run_sql_file(ROOT / "sql" / "dms_tables_only.sql")


if __name__ == "__main__":
    main()
