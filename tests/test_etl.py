import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MINI = ROOT / "tests" / "data" / "mini.csv"


def read_rows(path=MINI):
    rows = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if not r.get("price"):
                continue
            price = Decimal(r["price"])
            if price <= 0:
                continue
            rows.append(r)
    return rows


def calc_index_for_date(rows, target_date):
    day_rows = [r for r in rows if r["change_date"] == target_date]
    if not day_rows:
        return None
    prices = [float(r["price"]) for r in day_rows]
    return sum(prices) / len(prices)


def test_parse_date():
    d = datetime.strptime("2025-05-17", "%Y-%m-%d").date()
    assert str(d) == "2025-05-17"


def test_filter_null_and_zero():
    rows = read_rows()
    assert len(rows) == 8
    assert all(float(r["price"]) > 0 for r in rows)


def test_base_index_equals_100():
    rows = read_rows()
    base = calc_index_for_date(rows, "2025-05-17")
    later = calc_index_for_date(rows, "2025-05-18")
    index = later / base * 100
    assert round(index, 2) == 104.29
