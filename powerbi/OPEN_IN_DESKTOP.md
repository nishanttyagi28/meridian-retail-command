# Open Meridian in Power BI Desktop (your PC)

Yeh Cloud Linux pe Desktop nahi chal sakta — isliye **poora Power BI Project (`.pbip`)** banaya hai. Tumhare Windows PC pe double-click se report + model dono khulte hain.

## Files

| Path | What |
|------|------|
| `powerbi/Meridian.pbip` | **Isse open karo** |
| `powerbi/Meridian.Report/` | 6 pages + visuals (Pulse → Returns) |
| `powerbi/Meridian.SemanticModel/` | Tables, DAX measures, RLS roles, CSV queries |
| `data/mart/*.csv` | Data (Refresh ke baad cards fill honge) |

## Steps (Windows)

1. Install [Power BI Desktop](https://powerbi.microsoft.com/desktop/) (free).
2. **File → Options → Preview features** → enable:
   - Power BI Project (.pbip) save option
   - Store reports using enhanced metadata format (PBIR) *(if listed)*
3. Clone this repo (ya ZIP download):
   ```text
   https://github.com/nishanttyagi28/meridian-retail-command
   ```
4. Double-click:
   ```text
   powerbi\Meridian.pbip
   ```
5. Pehli baar data blank dikhe to:
   - **Transform data → Edit parameters**
   - `MartFolder` = tumhara local path, example:
     ```text
     C:\Users\<you>\source\meridian-retail-command\data\mart
     ```
   - **Home → Close & Apply** → **Refresh**
6. Pages left pe: **01 Pulse … 06 Returns**. Theme already wired (`MeridianRetailTheme`).

## What’s already built in the report

- **01 Pulse** — 6 KPI cards + monthly sales/returns line + month table  
- **02 Markets** — country bar + scorecard  
- **03 RFM CRM** — Champions cards + segment donut + customer table  
- **04 Cohorts** — retention matrix  
- **05 Assortment** — Pareto SKU chart + top SKUs table  
- **06 Returns** — return value cards + by-country bar + lines table  

Model measures (GBP): Gross Sales, Return Rate, AOV, RFM Revenue, Champions Revenue, Top 80 SKU Count, etc.

RLS roles: `UK_Market`, `Executive_All` (Modeling → Manage roles → View as).

## After it opens

Optional: **File → Save as → Power BI files (*.pbix)** if you want a single binary for LinkedIn demo.

## Regenerate from repo

```bash
python scripts/generate_pbip.py
```

Mart CSVs change ho to sirf Desktop mein Refresh; generator dubara tab chalao jab pages/model edit karni ho.
