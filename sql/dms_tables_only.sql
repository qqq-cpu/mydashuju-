CREATE TABLE IF NOT EXISTS db_price_index.fact_daily_price
(
    product_id   String,
    category_id  String,
    product_name String,
    price        Decimal64(4),
    sales        UInt32 DEFAULT 0,
    change_date  Date,
    load_time    DateTime DEFAULT now()
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(change_date)
ORDER BY (change_date, category_id, product_id);

CREATE TABLE IF NOT EXISTS db_price_index.agg_daily_index
(
    change_date        Date,
    category_id        String DEFAULT '',
    weighted_avg_price Decimal64(4),
    index_value        Float64,
    product_count      UInt32,
    calc_time          DateTime DEFAULT now()
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(change_date)
ORDER BY (change_date, category_id);
