# Skills checklist vs common Data Analyst JDs (2025–2026)

Use this when writing LinkedIn / resume bullets. Every row is demonstrable in the repo.

| JD phrase | Where to point |
|-----------|----------------|
| Advanced SQL | `sql/01_warehouse.sql` — windows, NTILE RFM, cohort math |
| Business problem framing | README “Business problem” + Pulse insights |
| Stakeholder Excel packs | `data/excel_deliverables/` |
| Power BI dashboards | `powerbi/` pack + localhost twin |
| DAX measures | `powerbi/dax/core_measures.dax` |
| Row-level security | `powerbi/rls/country_roles.dax` |
| Python data wrangling | `scripts/build_warehouse.py` |
| Data cleaning / QA | `data/quality_report.json` |
| Customer analytics (RFM) | CRM view + `CRM_RFM_Segments.xlsx` |
| Retention / cohorts | Cohort view |
| Product performance | Pareto mart |
| Returns / leakage analysis | Returns view + Ops workbook |
| Dimensional modeling | Star schema in SQLite |
| Storytelling with data | Six Power BI pages + console tabs |
| Version control | This GitHub repo |

## Suggested LinkedIn project blurb

> Built Meridian Retail Command on the public UCI Online Retail II ledger (~1.07M UK gift-retail invoice lines): Python ETL, star schema, SQL marts (RFM, cohorts, Pareto, returns), Excel packs for CFO/CRM/Ops, and a Power BI pack (DAX, theme, country RLS) with a localhost command console on the same marts. Gross sales £20.8M, return rate 7.3%, 5.9k identified customers — numbers from the warehouse, not slide fiction.
