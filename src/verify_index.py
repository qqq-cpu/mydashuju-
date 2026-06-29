# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ck_client import get_ck_client

rows = get_ck_client().query(
    "SELECT change_date, index_value, product_count "
    "FROM agg_daily_index WHERE category_id = '' ORDER BY change_date"
)
print("Index results:")
for r in rows:
    print(f"  {r[0]}  index={float(r[1]):.4f}  products={r[2]}")
