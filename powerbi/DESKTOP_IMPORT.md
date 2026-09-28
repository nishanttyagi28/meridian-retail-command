# Power BI Desktop import guide

**Prefer the ready project:** open [`Meridian.pbip`](Meridian.pbip) — see [`OPEN_IN_DESKTOP.md`](OPEN_IN_DESKTOP.md).

This Linux environment cannot run Power BI Desktop. The `.pbip` + pack below is what you open on Windows/Mac.

## What you get in `/powerbi`
| Path | Purpose |
|------|---------|
| `Meridian.pbip` | **Open this** — full report + semantic model |
| `Meridian.Report/` | 6 pages with bound visuals |
| `Meridian.SemanticModel/` | CSV marts, measures, RLS |
| `theme/MeridianRetailTheme.json` | Brand colours + visual defaults |
| `dax/core_measures.dax` | Extra DAX reference |
| `rls/country_roles.dax` | Extra RLS reference |
| `queries/*.pq` | Power Query M loaders (manual path) |
| `pages/PAGE_MAP.md` | Six-page report layout |

## Steps
1. Run `python scripts/build_warehouse.py` (or use committed `data/mart/*.csv`).
2. Open Power BI Desktop → **Get data → Text/CSV** → select every file in `data/mart/`.
3. Or paste each `queries/*.pq` into Advanced Editor (edit `FolderPath`).
4. **View → Themes → Browse themes** → `MeridianRetailTheme.json`.
5. Create relationships if you also load staging dims (`date_key`, `stock_code`, `customer_id`, `country`).
6. Paste measures from `core_measures.dax` (one at a time or via Tabular Editor).
7. **Modeling → Manage roles** using `country_roles.dax`.
8. Build pages from `PAGE_MAP.md`.
9. **Modeling → New parameter → Fields** for the KPI switch described in the DAX file.
10. Publish to a workspace; map Entra groups to RLS roles.

## Star schema (already built in SQLite)
- Fact: `fact_invoice_line`
- Dims: `dim_customer`, `dim_product`, `dim_date`, `dim_country`
- Marts: KPI, daily, monthly, country, product Pareto, RFM, cohort, returns

## Localhost twin
The FastAPI console in this repo reads the same mart CSVs so you can demo without Desktop.
