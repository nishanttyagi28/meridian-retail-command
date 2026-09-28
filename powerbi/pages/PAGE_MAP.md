# Power BI Desktop — page map (Meridian Retail Command)

Build these six pages after loading mart CSVs + applying `theme/MeridianRetailTheme.json` and `dax/core_measures.dax`.

## 1. Executive Pulse
- **Cards:** KPI Gross Sales, KPI Return Rate, KPI AOV, invoices, customers, guest checkout %
- **Line + column:** monthly sales vs returns (`mart_monthly_trend`)
- **Donut:** UK vs Rest sales share
- **Narrative text box:** “UK gift retailer · Dec 2009–Dec 2011 · public UCI Online Retail II”
- **Bookmark:** “Board pack” (hide filters)

## 2. Market Scorecard
- **Table / matrix:** `mart_country_performance` sorted by sales
- **Bar:** top 15 countries by sales
- **Scatter:** AOV (x) vs return rate (y), size = sales
- **Slicer:** country (sync across pages)
- **RLS note:** regional roles in `rls/country_roles.dax`

## 3. Customer RFM
- **Stacked bar:** customers by `rfm_segment`
- **Tree map or bar:** revenue by segment
- **Table:** Champions / Loyal with recency > 90 (at-risk high value)
- **Cards:** Champions Revenue, At Risk Customers
- **Field parameter:** KPI Switch (sales / frequency / monetary)

## 4. Cohort Retention
- **Matrix:** rows = `cohort_month`, columns = `month_number` (0–12), values = `retention_pct` (conditional formatting green→amber→rust)
- **Card:** Avg M3 Retention %
- **Line:** selected cohort retention curve

## 5. Assortment Pareto
- **Table:** top 50 SKUs from `mart_product_pareto`
- **Card:** Top 80 SKU Count
- **Area chart:** cumulative_pct by rank
- **Insight callout:** “~X% of SKUs drive 80% of sales” (measure-driven)

## 6. Returns Leakage
- **Table:** top return lines (`mart_returns_leakage`)
- **Bar:** returns by country
- **KPI:** Return Rate % with target line at 5%
- **Drillthrough:** from Market Scorecard country → this page

## Bookmarks & storytelling
1. Create bookmarks: Board / CRM / Ops
2. Selection pane: show/hide narrative boxes per bookmark
3. Button navigator on each page header
4. Optional: tooltips page with RFM definition glossary
