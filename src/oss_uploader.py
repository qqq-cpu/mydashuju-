"""Upload local CSV files to Aliyun OSS."""
import argparse
import os
import sys
from pathlib import Path

import oss2

from config_loader import DAILY_PRICE_DIR, load_config


def get_bucket(cfg):
    auth = oss2.Auth(cfg["oss"]["access_key_id"], cfg["oss"]["access_key_secret"])
    return oss2.Bucket(auth, cfg["oss"]["endpoint"], cfg["oss"]["bucket"])


def upload_file(local_path: Path, oss_key: str, bucket) -> str:
    bucket.put_object_from_file(oss_key, str(local_path))
    return oss_key


def upload_daily_dir(local_dir: Path, prefix: str = "raw/daily_price/", limit: int = 0):
    cfg = load_config()
    bucket = get_bucket(cfg)
    files = sorted(local_dir.glob("daily_prices_*.csv"))
    if limit:
        files = files[:limit]
    if not files:
        print(f"未找到 CSV: {local_dir}")
        sys.exit(1)

    print(f"准备上传 {len(files)} 个文件到 oss://{cfg['oss']['bucket']}/{prefix}")
    for i, f in enumerate(files, 1):
        key = prefix + f.name
        upload_file(f, key, bucket)
        print(f"[{i}/{len(files)}] {key}")
    print("上传完成")


def main():
    parser = argparse.ArgumentParser(description="上传 daily_price CSV 到 OSS")
    parser.add_argument(
        "--dir",
        default=str(DAILY_PRICE_DIR),
        help="本地 daily_price 目录（默认 price-index/data/data/daily_price）",
    )
    parser.add_argument("--limit", type=int, default=0, help="只上传前 N 个文件，0=全部")
    parser.add_argument("--prefix", default="raw/daily_price/")
    args = parser.parse_args()
    upload_daily_dir(Path(args.dir), args.prefix, args.limit)


if __name__ == "__main__":
    main()
