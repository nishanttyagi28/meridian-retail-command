"""
Build the Meridian Retail Command warehouse from UCI Online Retail II.

Dataset (real): Chen, D. Online Retail II. UCI Machine Learning Repository.
https://doi.org/10.24432/C5CG6D
UK online gift retailer transactions, Dec 2009 – Dec 2011.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[1]
RAW_XLSX = ROOT / "data" / "raw" / "online_retail_II.xlsx"
SQLITE = ROOT / "data" / "meridian.db"
STAGING = ROOT / "data" / "staging"
MART = ROOT / "data" / "mart"
EXCEL_OUT = ROOT / "data" / "excel_deliverables"


def load_raw() -> pd.DataFrame:
    frames = []
    for sheet in ["Year 2009-2010", "Year 2010-2011"]:
        part = pd.read_excel(RAW_XLSX, sheet_name=sheet)
        part["source_sheet"] = sheet
        frames.append(part)
    raw = pd.concat(frames, ignore_index=True)
    raw.columns = [c.strip() for c in raw.columns]
    return raw


def profile_quality(raw: pd.DataFrame) -> dict:
    return {
        "rows": int(len(raw)),
        "columns": list(raw.columns),
        "null_pct": {c: round(float(raw[c].isna().mean()), 4) for c in raw.columns},
        "duplicate_rows": int(raw.duplicated().sum()),
        "invoices": int(raw["Invoice"].nunique()),
        "stock_codes": int(raw["StockCode"].nunique()),
        "customers_non_null": int(raw["Customer ID"].dropna().nunique()),
        "countries": int(raw["Country"].nunique()),
        "date_min": str(pd.to_datetime(raw["InvoiceDate"]).min()),
        "date_max": str(pd.to_datetime(raw["InvoiceDate"]).max()),
        "negative_qty_rows": int((raw["Quantity"] < 0).sum()),
        "zero_price_rows": int((raw["Price"] <= 0).sum()),
        "guest_checkout_rows": int(raw["Customer ID"].isna().sum()),
    }


def clean(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    df["Invoice"] = df["Invoice"].astype(str).str.strip()
    df["StockCode"] = df["StockCode"].astype(str).str.strip().str.upper()
    df["Description"] = df["Description"].fillna("UNKNOWN ITEM").astype(str).str.strip()
    df["Country"] = df["Country"].fillna("Unknown").astype(str).str.strip()
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce").fillna(0).astype(int)
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce").fillna(0.0)
    df["Customer ID"] = pd.to_numeric(df["Customer ID"], errors="coerce")
    df["line_value"] = df["Quantity"] * df["Price"]
    df["is_cancellation"] = df["Invoice"].str.startswith("C").astype(int)
    df["is_return_qty"] = (df["Quantity"] < 0).astype(int)
    df["is_guest"] = df["Customer ID"].isna().astype(int)
    # postage / bank charges / manual often non-product
    df["is_non_product"] = df["StockCode"].str.contains(
        r"POST|DOT|BANK|M$|D$|AMAZON|GIFT|PADS|CRUK|B$", regex=True
    ).astype(int)
    df["invoice_date"] = df["InvoiceDate"].dt.date.astype(str)
    df["invoice_month"] = df["InvoiceDate"].dt.to_period("M").astype(str)
    df = df.drop_duplicates()
    return df


def build_star(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    fact = df.rename(
        columns={
            "Invoice": "invoice_id",
            "StockCode": "stock_code",
            "Description": "description",
            "Quantity": "qty",
            "Price": "unit_price",
            "Customer ID": "customer_id",
            "Country": "country",
            "InvoiceDate": "invoice_ts",
        }
    )
    fact["customer_id"] = fact["customer_id"].apply(
        lambda x: None if pd.isna(x) else str(int(x))
    )
    fact["line_id"] = np.arange(1, len(fact) + 1)
    fact["date_key"] = fact["invoice_ts"].dt.strftime("%Y%m%d").astype(int)

    dim_customer = (
        fact.dropna(subset=["customer_id"])
        .groupby("customer_id", as_index=False)
        .agg(
            country=("country", lambda s: s.mode().iloc[0] if len(s.mode()) else s.iloc[0]),
            first_purchase=("invoice_ts", "min"),
            last_purchase=("invoice_ts", "max"),
            invoice_count=("invoice_id", "nunique"),
        )
    )

    dim_product = (
        fact.groupby("stock_code", as_index=False)
        .agg(
            description=("description", lambda s: s.mode().iloc[0] if len(s.mode()) else s.iloc[0]),
            median_price=("unit_price", "median"),
            line_count=("line_id", "count"),
        )
    )

    days = pd.DataFrame({"full_date": pd.date_range(fact["invoice_ts"].min().normalize(), fact["invoice_ts"].max().normalize(), freq="D")})
    dim_date = pd.DataFrame(
        {
            "date_key": days["full_date"].dt.strftime("%Y%m%d").astype(int),
            "full_date": days["full_date"].dt.date.astype(str),
            "year": days["full_date"].dt.year,
            "quarter": days["full_date"].dt.quarter,
            "month": days["full_date"].dt.month,
            "month_name": days["full_date"].dt.strftime("%b"),
            "week": days["full_date"].dt.isocalendar().week.astype(int),
            "year_month": days["full_date"].dt.to_period("M").astype(str),
        }
    )

    dim_country = (
        fact.groupby("country", as_index=False)
        .agg(line_count=("line_id", "count"), customers=("customer_id", pd.Series.nunique))
    )

    return {
        "fact_invoice_line": fact[
            [
                "line_id",
                "invoice_id",
                "invoice_ts",
                "invoice_date",
                "invoice_month",
                "date_key",
                "stock_code",
                "customer_id",
                "country",
                "qty",
                "unit_price",
                "line_value",
                "is_cancellation",
                "is_return_qty",
                "is_guest",
                "is_non_product",
                "source_sheet",
            ]
        ],
        "dim_customer": dim_customer,
        "dim_product": dim_product,
        "dim_date": dim_date,
        "dim_country": dim_country,
    }


def write_sql_marts(engine) -> None:
    sql = (ROOT / "sql" / "01_warehouse.sql").read_text(encoding="utf-8")
    with engine.begin() as conn:
        for stmt in sql.split(";"):
            s = stmt.strip()
            if s:
                conn.execute(text(s))


def export_marts(engine) -> dict:
    MART.mkdir(parents=True, exist_ok=True)
    STAGING.mkdir(parents=True, exist_ok=True)
    out = {}
    views = [
        "mart_kpi_snapshot",
        "mart_daily_sales",
        "mart_country_performance",
        "mart_product_pareto",
        "mart_customer_rfm",
        "mart_cohort_retention",
        "mart_returns_leakage",
        "mart_monthly_trend",
    ]
    with engine.connect() as conn:
        for view in views:
            df = pd.read_sql(text(f"SELECT * FROM {view}"), conn)
            df.to_csv(MART / f"{view}.csv", index=False)
            out[view] = int(len(df))
        kpi = pd.read_sql(text("SELECT * FROM mart_kpi_snapshot"), conn)
        (MART / "kpi_snapshot.json").write_text(
            kpi.to_json(orient="records", indent=2), encoding="utf-8"
        )
    return out


def write_excel_deliverables(engine, quality: dict) -> None:
    EXCEL_OUT.mkdir(parents=True, exist_ok=True)
    with engine.connect() as conn:
        kpi = pd.read_sql(text("SELECT * FROM mart_kpi_snapshot"), conn)
        country = pd.read_sql(text("SELECT * FROM mart_country_performance"), conn)
        rfm = pd.read_sql(text("SELECT * FROM mart_customer_rfm"), conn)
        returns = pd.read_sql(text("SELECT * FROM mart_returns_leakage LIMIT 5000"), conn)
        pareto = pd.read_sql(text("SELECT * FROM mart_product_pareto"), conn)
        monthly = pd.read_sql(text("SELECT * FROM mart_monthly_trend"), conn)
        cohort = pd.read_sql(text("SELECT * FROM mart_cohort_retention"), conn)

    # CFO pack
    with pd.ExcelWriter(EXCEL_OUT / "CFO_Executive_Pack.xlsx", engine="xlsxwriter") as xl:
        kpi.to_excel(xl, sheet_name="KPI_Snapshot", index=False)
        monthly.to_excel(xl, sheet_name="Monthly_Trend", index=False)
        country.head(30).to_excel(xl, sheet_name="Top_Countries", index=False)
        quality_df = pd.DataFrame(
            [{"metric": k, "value": json.dumps(v) if isinstance(v, (dict, list)) else v} for k, v in quality.items()]
        )
        quality_df.to_excel(xl, sheet_name="Data_Quality", index=False)

    # CRM / growth pack
    with pd.ExcelWriter(EXCEL_OUT / "CRM_RFM_Segments.xlsx", engine="xlsxwriter") as xl:
        rfm.to_excel(xl, sheet_name="Customer_RFM", index=False)
        rfm.groupby("rfm_segment", as_index=False).agg(
            customers=("customer_id", "count"),
            revenue=("monetary", "sum"),
        ).sort_values("revenue", ascending=False).to_excel(xl, sheet_name="Segment_Summary", index=False)
        cohort.to_excel(xl, sheet_name="Cohort_Retention", index=False)

    # Ops / returns pack
    with pd.ExcelWriter(EXCEL_OUT / "Ops_Returns_and_SKU.xlsx", engine="xlsxwriter") as xl:
        returns.to_excel(xl, sheet_name="Returns_Sample", index=False)
        pareto.head(200).to_excel(xl, sheet_name="SKU_Pareto_Top200", index=False)


def main() -> None:
    assert RAW_XLSX.exists(), f"Missing {RAW_XLSX}. Place UCI Online Retail II xlsx there."
    print("Loading raw Excel (real UCI Online Retail II)...")
    raw = load_raw()
    quality = profile_quality(raw)
    print("Cleaning...")
    cleaned = clean(raw)
    star = build_star(cleaned)

    if SQLITE.exists():
        SQLITE.unlink()
    engine = create_engine(f"sqlite:///{SQLITE}")
    for name, frame in star.items():
        print(f"Writing {name}: {len(frame):,} rows")
        frame.to_sql(name, engine, index=False, if_exists="replace")
        frame.head(5000).to_csv(STAGING / f"{name}.csv", index=False)

    print("Creating SQL marts...")
    write_sql_marts(engine)
    counts = export_marts(engine)
    write_excel_deliverables(engine, quality)

    meta = {
        "dataset": "UCI Online Retail II",
        "citation": "Chen, D. (2019). Online Retail II. UCI Machine Learning Repository. https://doi.org/10.24432/C5CG6D",
        "company_framing": "Meridian Home & Gift — UK online retailer (analysis on public UCI Online Retail II)",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "quality": quality,
        "mart_rows": counts,
        "sqlite": str(SQLITE),
    }
    (ROOT / "data" / "build_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    (ROOT / "data" / "quality_report.json").write_text(json.dumps(quality, indent=2), encoding="utf-8")
    print(json.dumps({"rows": quality["rows"], "marts": counts, "kpi_file": str(MART / "kpi_snapshot.json")}, indent=2))


if __name__ == "__main__":
    main()
