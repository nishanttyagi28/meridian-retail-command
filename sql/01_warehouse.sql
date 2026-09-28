-- Meridian Retail Command — SQL marts on UCI Online Retail II (SQLite)

-- Sales excluding pure cancellations for revenue views still keep returns as negative qty.

CREATE VIEW IF NOT EXISTS v_sales_lines AS
SELECT
  f.*,
  p.description,
  p.median_price,
  CASE
    WHEN f.is_cancellation = 1 OR f.is_return_qty = 1 THEN 'Return/Cancel'
    WHEN f.is_non_product = 1 THEN 'Non-product'
    WHEN f.is_guest = 1 THEN 'Guest sale'
    ELSE 'Sale'
  END AS line_type
FROM fact_invoice_line f
LEFT JOIN dim_product p ON p.stock_code = f.stock_code;

CREATE VIEW IF NOT EXISTS mart_kpi_snapshot AS
SELECT
  (SELECT COUNT(*) FROM fact_invoice_line) AS line_rows,
  (SELECT COUNT(DISTINCT invoice_id) FROM fact_invoice_line) AS invoices,
  (SELECT COUNT(DISTINCT customer_id) FROM fact_invoice_line WHERE customer_id IS NOT NULL) AS customers,
  (SELECT COUNT(DISTINCT stock_code) FROM fact_invoice_line) AS skus,
  (SELECT COUNT(DISTINCT country) FROM fact_invoice_line) AS countries,
  (SELECT ROUND(SUM(line_value), 2) FROM fact_invoice_line WHERE is_cancellation = 0 AND qty > 0) AS gross_sales_gbp,
  (SELECT ROUND(SUM(ABS(line_value)), 2) FROM fact_invoice_line WHERE qty < 0 OR is_cancellation = 1) AS returns_abs_value,
  (SELECT ROUND(
      100.0 * SUM(CASE WHEN qty < 0 OR is_cancellation = 1 THEN ABS(line_value) ELSE 0 END)
      / NULLIF(SUM(CASE WHEN qty > 0 AND is_cancellation = 0 THEN line_value ELSE 0 END), 0)
    , 2)
   FROM fact_invoice_line) AS return_rate_pct,
  (SELECT ROUND(SUM(line_value) * 1.0 / NULLIF(COUNT(DISTINCT invoice_id), 0), 2)
   FROM fact_invoice_line WHERE qty > 0 AND is_cancellation = 0) AS aov,
  (SELECT ROUND(100.0 * SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2)
   FROM fact_invoice_line) AS guest_checkout_pct;

CREATE VIEW IF NOT EXISTS mart_daily_sales AS
SELECT
  invoice_date,
  country,
  SUM(CASE WHEN qty > 0 AND is_cancellation = 0 THEN line_value ELSE 0 END) AS sales,
  SUM(CASE WHEN qty < 0 OR is_cancellation = 1 THEN ABS(line_value) ELSE 0 END) AS returns_abs,
  COUNT(DISTINCT invoice_id) AS invoices,
  COUNT(DISTINCT customer_id) AS customers
FROM fact_invoice_line
GROUP BY invoice_date, country;

CREATE VIEW IF NOT EXISTS mart_monthly_trend AS
SELECT
  invoice_month,
  SUM(CASE WHEN qty > 0 AND is_cancellation = 0 THEN line_value ELSE 0 END) AS sales,
  SUM(CASE WHEN qty < 0 OR is_cancellation = 1 THEN ABS(line_value) ELSE 0 END) AS returns_abs,
  COUNT(DISTINCT invoice_id) AS invoices,
  COUNT(DISTINCT customer_id) AS customers,
  ROUND(
    SUM(CASE WHEN qty > 0 AND is_cancellation = 0 THEN line_value ELSE 0 END) * 1.0
    / NULLIF(COUNT(DISTINCT invoice_id), 0), 2
  ) AS aov
FROM fact_invoice_line
GROUP BY invoice_month
ORDER BY invoice_month;

CREATE VIEW IF NOT EXISTS mart_country_performance AS
SELECT
  country,
  COUNT(DISTINCT customer_id) AS customers,
  COUNT(DISTINCT invoice_id) AS invoices,
  ROUND(SUM(CASE WHEN qty > 0 AND is_cancellation = 0 THEN line_value ELSE 0 END), 2) AS sales,
  ROUND(SUM(CASE WHEN qty < 0 OR is_cancellation = 1 THEN ABS(line_value) ELSE 0 END), 2) AS returns_abs,
  ROUND(
    100.0 * SUM(CASE WHEN qty < 0 OR is_cancellation = 1 THEN ABS(line_value) ELSE 0 END)
    / NULLIF(SUM(CASE WHEN qty > 0 AND is_cancellation = 0 THEN line_value ELSE 0 END), 0)
  , 2) AS return_rate_pct,
  ROUND(
    SUM(CASE WHEN qty > 0 AND is_cancellation = 0 THEN line_value ELSE 0 END) * 1.0
    / NULLIF(COUNT(DISTINCT invoice_id), 0)
  , 2) AS aov
FROM fact_invoice_line
GROUP BY country
ORDER BY sales DESC;

-- Pareto of SKUs by sales
CREATE VIEW IF NOT EXISTS mart_product_pareto AS
WITH sku_sales AS (
  SELECT
    stock_code,
    MAX(description) AS description,
    ROUND(SUM(CASE WHEN qty > 0 AND is_cancellation = 0 THEN line_value ELSE 0 END), 2) AS sales,
    SUM(CASE WHEN qty > 0 AND is_cancellation = 0 THEN qty ELSE 0 END) AS units
  FROM v_sales_lines
  WHERE is_non_product = 0
  GROUP BY stock_code
),
ordered AS (
  SELECT
    *,
    SUM(sales) OVER (ORDER BY sales DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_sales,
    SUM(sales) OVER () AS total_sales
  FROM sku_sales
  WHERE sales > 0
)
SELECT
  stock_code,
  description,
  sales,
  units,
  ROUND(100.0 * sales / NULLIF(total_sales, 0), 4) AS pct_of_sales,
  ROUND(100.0 * running_sales / NULLIF(total_sales, 0), 4) AS cumulative_pct,
  CASE WHEN 100.0 * running_sales / NULLIF(total_sales, 0) <= 80 THEN 1 ELSE 0 END AS is_top80_pct
FROM ordered
ORDER BY sales DESC;

-- RFM on identified customers only (manager CRM staple)
CREATE VIEW IF NOT EXISTS mart_customer_rfm AS
WITH base AS (
  SELECT
    customer_id,
    MAX(invoice_date) AS last_purchase,
    COUNT(DISTINCT invoice_id) AS frequency,
    ROUND(SUM(CASE WHEN qty > 0 AND is_cancellation = 0 THEN line_value ELSE 0 END), 2) AS monetary,
    ROUND(SUM(CASE WHEN qty < 0 OR is_cancellation = 1 THEN ABS(line_value) ELSE 0 END), 2) AS returns_abs
  FROM fact_invoice_line
  WHERE customer_id IS NOT NULL
  GROUP BY customer_id
),
scored AS (
  SELECT
    *,
    CAST(julianday('2011-12-10') - julianday(last_purchase) AS INTEGER) AS recency_days,
    -- High R = recent buyers (low days). Order DESC so dormant get low bucket first, recent get 5.
    NTILE(5) OVER (ORDER BY CAST(julianday('2011-12-10') - julianday(last_purchase) AS INTEGER) DESC) AS r_score,
    NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
    NTILE(5) OVER (ORDER BY monetary ASC) AS m_score
  FROM base
)
SELECT
  customer_id,
  last_purchase,
  recency_days,
  frequency,
  monetary,
  returns_abs,
  r_score,
  f_score,
  m_score,
  (r_score + f_score + m_score) AS rfm_sum,
  CASE
    WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
    WHEN r_score >= 4 AND f_score >= 3 THEN 'Loyal'
    WHEN r_score >= 4 AND m_score >= 4 THEN 'Big spenders'
    WHEN r_score <= 2 AND f_score <= 2 THEN 'At risk / hibernating'
    WHEN r_score <= 2 AND m_score >= 4 THEN 'Need attention'
    WHEN r_score >= 3 AND f_score <= 2 THEN 'Promising / new'
    ELSE 'Core'
  END AS rfm_segment
FROM scored;

-- Monthly cohort retention (first purchase month cohorts)
CREATE VIEW IF NOT EXISTS mart_cohort_retention AS
WITH firsts AS (
  SELECT customer_id, MIN(invoice_month) AS cohort_month
  FROM fact_invoice_line
  WHERE customer_id IS NOT NULL AND qty > 0 AND is_cancellation = 0
  GROUP BY customer_id
),
activity AS (
  SELECT DISTINCT customer_id, invoice_month
  FROM fact_invoice_line
  WHERE customer_id IS NOT NULL AND qty > 0 AND is_cancellation = 0
),
joined AS (
  SELECT
    f.cohort_month,
    a.invoice_month,
    ROUND(
      (CAST(substr(a.invoice_month, 1, 4) AS INTEGER) - CAST(substr(f.cohort_month, 1, 4) AS INTEGER)) * 12
      + (CAST(substr(a.invoice_month, 6, 2) AS INTEGER) - CAST(substr(f.cohort_month, 6, 2) AS INTEGER))
    , 0) AS month_number,
    a.customer_id
  FROM firsts f
  JOIN activity a ON a.customer_id = f.customer_id
),
cohort_sizes AS (
  SELECT cohort_month, COUNT(DISTINCT customer_id) AS cohort_customers
  FROM firsts
  GROUP BY cohort_month
)
SELECT
  j.cohort_month,
  j.month_number,
  COUNT(DISTINCT j.customer_id) AS active_customers,
  c.cohort_customers,
  ROUND(100.0 * COUNT(DISTINCT j.customer_id) / NULLIF(c.cohort_customers, 0), 2) AS retention_pct
FROM joined j
JOIN cohort_sizes c ON c.cohort_month = j.cohort_month
WHERE j.month_number >= 0 AND j.month_number <= 12
GROUP BY j.cohort_month, j.month_number, c.cohort_customers
ORDER BY j.cohort_month, j.month_number;

CREATE VIEW IF NOT EXISTS mart_returns_leakage AS
SELECT
  invoice_id,
  invoice_date,
  stock_code,
  description,
  customer_id,
  country,
  qty,
  unit_price,
  ROUND(ABS(line_value), 2) AS return_value,
  is_cancellation,
  is_return_qty
FROM v_sales_lines
WHERE qty < 0 OR is_cancellation = 1;
