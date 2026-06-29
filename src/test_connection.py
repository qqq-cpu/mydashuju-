# -*- coding: utf-8 -*-
"""Test OSS or ClickHouse connection using config.yaml."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config_loader import load_config


def test_oss():
    import oss2
    cfg = load_config()["oss"]
    if cfg.get("bucket") in (None, "", "your-bucket-name"):
        print("OSS config incomplete: set oss.bucket in config.yaml")
        sys.exit(1)
    auth = oss2.Auth(cfg["access_key_id"], cfg["access_key_secret"])
    bucket = oss2.Bucket(auth, cfg["endpoint"], cfg["bucket"])
    result = bucket.list_objects(prefix="raw/daily_price/", max_keys=10)
    keys = [o.key for o in result.object_list]
    print("OSS OK")
    print(f"  Bucket: {cfg['bucket']}")
    print(f"  Files under raw/daily_price/: {len(keys)} (first page)")
    for k in keys[:5]:
        print(f"    - {k}")
    if not keys:
        print("  Tip: python src/oss_uploader.py --limit 3")


def test_ck():
    from ck_client import get_ck_client
    ck = load_config()["clickhouse"]
    client = get_ck_client()
    version = client.query("SELECT version()")[0][0]
    tables = client.query("SHOW TABLES")
    print("ClickHouse OK")
    print(f"  Host: {ck['host']}:{ck['port']} (mode={client.mode})")
    print(f"  Database: {ck['database']}")
    print(f"  Version: {version}")
    print(f"  Tables: {[t[0] for t in tables] or '(empty, run: python src/ck_loader.py ddl)'}")


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("oss", "ck"):
        print("Usage: python src/test_connection.py oss|ck")
        sys.exit(1)
    try:
        if sys.argv[1] == "oss":
            test_oss()
        else:
            test_ck()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Run: copy config.yaml.template config.yaml and fill in values")
        sys.exit(1)
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
