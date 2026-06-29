-- 清洗 + 分类均价 + 链式指数（基日见 project.base_date）
ALTER TABLE db_price_index.agg_daily_index DELETE WHERE category_id = '';

INSERT INTO db_price_index.agg_daily_index
(
    change_date,
    category_id,
    weighted_avg_price,
    index_value,
    product_count
)
WITH clean AS (
    SELECT
        product_id,
        category_id,
        product_name,
        price,
        sales,
        change_date
    FROM db_price_index.fact_daily_price
    WHERE price IS NOT NULL
      AND price > 0
),
cat_daily AS (
    SELECT
        change_date,
        category_id,
        sum(toFloat64(price) * if(sales = 0, 1, sales))
            / sum(if(sales = 0, 1, sales)) AS cat_avg_price,
        count() AS product_count
    FROM clean
    GROUP BY change_date, category_id
),
market_daily AS (
    SELECT
        change_date,
        avg(cat_avg_price) AS market_avg_price,
        sum(product_count) AS product_count
    FROM cat_daily
    GROUP BY change_date
),
base AS (
    SELECT market_avg_price AS base_avg
    FROM market_daily
    WHERE change_date = toDate('2025-05-17')
    LIMIT 1
)
SELECT
    m.change_date,
    '',
    toDecimal64(m.market_avg_price, 4),
    m.market_avg_price / b.base_avg * 100,
    m.product_count
FROM market_daily m
CROSS JOIN base b
ORDER BY m.change_date;
