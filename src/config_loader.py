"""Load config.yaml from project root."""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "data"
DAILY_PRICE_DIR = DATA_DIR / "daily_price"
CATEGORIES_CSV = DATA_DIR / "categories.csv"
PRODUCTS_CSV = DATA_DIR / "products.csv"


def load_config():
    path = ROOT / "config.yaml"
    if not path.exists():
        raise FileNotFoundError(
            f"找不到 {path}，请复制 config.yaml.template 为 config.yaml 并填写"
        )
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)
