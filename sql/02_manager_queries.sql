-- Meridian Retail Command — manager-grade queries on meridian.db
-- Dataset: UCI Online Retail II (Chen, 2019). Currency = GBP.

-- 1) Executive snapshot
SELECT * FROM mart_kpi_snapshot;

-- 2) MoM sales + return rate (window)
WITH m AS (
  SELECT
    invoice_month,
    sales,
    returns_abs,
    invoices,
    customers,
    aov,
    LAG(sales) OVER (ORDER BY invoice_month) AS prev_sales
  FROM mart_monthly_trend
)
SELECT
  invoice_month,
  sales,
  returns_abs,
  ROUND(100.0 * returns_abs / NULLIF(sales, 0), 2) AS return_rate_pct,
  invoices,
  customers,
  aov,
  ROUND(100.0 * (sales - prev_sales) / NULLIF(prev_sales, 0), 2) AS mom_sales_pct
FROM m
ORDER BY invoice_month;

-- 3) Country concentration (Pareto of markets)
WITH c AS (
  SELECT
    country,
    sales,
    customers,
    return_rate_pct,
    aov,
    SUM(sales) OVER (ORDER BY sales DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_sales,
    SUM(sales) OVER () AS total_sales
  FROM mart_country_performance
)
SELECT
  country,
  sales,
  customers,
  return_rate_pct,
  aov,
  ROUND(100.0 * sales / NULLIF(total_sales, 0), 2) AS pct_of_sales,
  ROUND(100.0 * running_sales / NULLIF(total_sales, 0), 2) AS cumulative_pct
FROM c
ORDER BY sales DESC;

-- 4) RFM segment economics
SELECT
  rfm_segment,
  COUNT(*) AS customers,
  ROUND(SUM(monetary), 2) AS revenue_gbp,
  ROUND(AVG(monetary), 2) AS avg_monetary,
  ROUND(AVG(frequency), 2) AS avg_frequency,
  ROUND(AVG(recency_days), 1) AS avg_recency_days,
  ROUND(SUM(returns_abs), 2) AS returns_gbp
FROM mart_customer_rfm
GROUP BY rfm_segment
ORDER BY revenue_gbp DESC;

-- 5) Champions at risk of churn (high value, rising recency)
SELECT customer_id, last_purchase, recency_days, frequency, monetary, rfm_segment
FROM mart_customer_rfm
WHERE rfm_segment IN ('Champions', 'Loyal', 'Big spenders')
  AND recency_days > 90
ORDER BY monetary DESC
LIMIT 50;

-- 6) Cohort retention heatmap seed (Month 0–6)
SELECT cohort_month, month_number, retention_pct, active_customers, cohort_customers
FROM mart_cohort_retention
WHERE month_number BETWEEN 0 AND 6
ORDER BY cohort_month, month_number;

-- 7) SKU Pareto — how many SKUs drive 80% of sales
SELECT
  COUNT(*) AS skus_in_top80,
  ROUND(SUM(sales), 2) AS sales_in_top80,
  (SELECT COUNT(*) FROM mart_product_pareto) AS total_skus_with_sales
FROM mart_product_pareto
WHERE is_top80_pct = 1;

-- 8) Top return leakage lines by value
SELECT invoice_id, invoice_date, stock_code, description, country, qty, return_value, customer_id
FROM mart_returns_leakage
ORDER BY return_value DESC
LIMIT 40;

-- 9) Guest checkout exposure by country
SELECT
  country,
  COUNT(*) AS lines,
  SUM(CASE WHEN is_guest = 1 THEN 1 ELSE 0 END) AS guest_lines,
  ROUND(100.0 * SUM(CASE WHEN is_guest = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS guest_pct,
  ROUND(SUM(CASE WHEN qty > 0 AND is_cancellation = 0 THEN line_value ELSE 0 END), 2) AS sales_gbp
FROM fact_invoice_line
GROUP BY country
HAVING COUNT(*) > 200
ORDER BY guest_pct DESC
LIMIT 20;

-- 10) Repeat-purchase rate (identified customers)
WITH freq AS (
  SELECT customer_id, COUNT(DISTINCT invoice_id) AS invoices
  FROM fact_invoice_line
  WHERE customer_id IS NOT NULL AND qty > 0 AND is_cancellation = 0
  GROUP BY customer_id
)
SELECT
  COUNT(*) AS identified_customers,
  SUM(CASE WHEN invoices >= 2 THEN 1 ELSE 0 END) AS repeaters,
  ROUND(100.0 * SUM(CASE WHEN invoices >= 2 THEN 1 ELSE 0 END) / COUNT(*), 2) AS repeat_rate_pct
FROM freq;
