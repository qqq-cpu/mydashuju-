# -*- coding: utf-8 -*-
"""Download daily_price CSV files from OSS to local directory."""
import argparse
import os
import sys
from pathlib import Path

import oss2

from config_loader import DAILY_PRICE_DIR, load_config


def download(prefix="raw/daily_price/", limit=3, out_dir=None):
    cfg = load_config()["oss"]
    auth = oss2.Auth(cfg["access_key_id"], cfg["access_key_secret"])
    bucket = oss2.Bucket(auth, cfg["endpoint"], cfg["bucket"])
    out = Path(out_dir or DAILY_PRICE_DIR)
    out.mkdir(parents=True, exist_ok=True)

    keys = []
    for obj in oss2.ObjectIterator(bucket, prefix=prefix):
        if obj.key.endswith(".csv"):
            keys.append(obj.key)
    keys.sort()
    if limit:
        keys = keys[:limit]
    if not keys:
        print(f"No CSV under oss://{cfg['bucket']}/{prefix}")
        sys.exit(1)

    for i, key in enumerate(keys, 1):
        name = os.path.basename(key)
        dest = out / name
        bucket.get_object_to_file(key, str(dest))
        print(f"[{i}/{len(keys)}] downloaded {name}")
    print("Download done")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--prefix", default="raw/daily_price/")
    args = parser.parse_args()
    download(args.prefix, args.limit)


if __name__ == "__main__":
    main()
