# Meridian Retail Command

End-to-end **data analyst** project on a **real** public dataset: [UCI Online Retail II](https://doi.org/10.24432/C5CG6D) (Chen, 2019) — a UK online gift retailer’s invoice lines from Dec 2009 to Dec 2011 (~1.07M raw rows).

Framed as the internal BI stack for **Meridian Home & Gift**: Python ETL → SQLite star schema → advanced SQL marts → Excel packs → Power BI Desktop pack (theme / DAX / RLS) → premium localhost command console.

Not a multi-tenant SaaS. Local analysis you can run, open in Power BI Desktop, and put on a portfolio.

## Business problem

Leadership cannot answer, from the raw ledger alone:

1. **Where does cash concentrate?** UK vs export markets, AOV, return rate by country.
2. **Who should CRM protect?** Identified buyers need RFM segments and a “high value cooling off” list.
3. **Does acquisition stick?** Month-0 cohorts and M1–M12 retention.
4. **Is the catalogue too long?** Pareto of SKUs — how many drive 80% of sales.
5. **Where does revenue leak?** Cancellation / negative-qty return lines ranked by value.
6. **How clean is the source?** Null Customer IDs (~23% guest lines), duplicates, non-product codes.

## Approach

| Layer | What shipped |
|-------|----------------|
| Ingest | `scripts/download_uci_online_retail_ii.py` + Excel load of both yearly sheets |
| Quality | Null %, dupes, guest share, date span → `data/quality_report.json` |
| Model | Star: `fact_invoice_line` + customer / product / date / country dims |
| SQL | CTEs, window functions, RFM NTILE, cohort retention, product Pareto |
| Excel | CFO / CRM / Ops workbooks stakeholders can open tomorrow |
| Power BI | Theme, DAX measures, country RLS roles, page map, Power Query M |
| Console | FastAPI + Chart.js command UI over the same marts |

## Measured snapshot (from marts)

| KPI | Value |
|-----|-------|
| Gross sales | **£20.76M** |
| Return value / rate | **£1.52M · 7.34%** |
| AOV | **£494.84** |
| Identified customers | **5,942** |
| SKUs / countries | **5,131 · 43** |
| Guest checkout lines | **23.02%** |

Currency is **GBP** (source is UK sterling). Numbers come from `data/mart/`, not invented ROI.

## Market skills map (what JDs ask for)

| Skill hiring managers list | Evidence in this repo |
|----------------------------|------------------------|
| SQL (CTE, window, aggregations) | `sql/01_warehouse.sql`, `sql/02_manager_queries.sql` |
| RFM / customer segmentation | `mart_customer_rfm` + CRM Excel pack |
| Cohort retention | `mart_cohort_retention` + console heatmap |
| Pareto / ABC assortment | `mart_product_pareto` |
| Python ETL + pandas | `scripts/build_warehouse.py` |
| Data quality profiling | `quality_report.json` + CFO Data_Quality sheet |
| Star schema / dimensional model | fact + dims in SQLite |
| Excel for stakeholders | `data/excel_deliverables/*.xlsx` |
| Power BI — DAX | `powerbi/dax/core_measures.dax` |
| Power BI — theme & storytelling | theme JSON + `pages/PAGE_MAP.md` bookmarks |
| Power BI — RLS | `powerbi/rls/country_roles.dax` |
| KPI design & narrative | Pulse view insights + README business case |
| Git / reproducible pipeline | download → build → marts → API |

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# If data/raw/online_retail_II.xlsx is missing:
python scripts/download_uci_online_retail_ii.py

python scripts/build_warehouse.py
uvicorn meridian_app:app --app-dir src --host 127.0.0.1 --port 8765
```

Open [http://127.0.0.1:8765](http://127.0.0.1:8765).

Committed `data/mart/*.csv` and Excel packs let the console run without rebuilding; rebuild when you change SQL.

### Power BI Desktop

See [`powerbi/DESKTOP_IMPORT.md`](powerbi/DESKTOP_IMPORT.md). This environment does not run Desktop; the pack is import-ready on Windows/Mac.

### Tests

```bash
pytest -q
```

## Dataset citation

Chen, D. (2019). Online Retail II. UCI Machine Learning Repository. https://doi.org/10.24432/C5CG6D

## Repo layout

```
scripts/           download + warehouse build
sql/               marts + manager queries
data/mart/         analysis-ready CSVs (+ kpi JSON)
data/excel_deliverables/
powerbi/           theme, DAX, RLS, M queries, page map
src/meridian_app.py
web/               premium command console
tests/
```
