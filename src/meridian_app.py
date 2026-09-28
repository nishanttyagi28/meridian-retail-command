"""Meridian Retail Command — FastAPI console over UCI Online Retail II marts."""

from __future__ import annotations

import csv
import json
from contextlib import asynccontextmanager
from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parents[1]
MART = ROOT / "data" / "mart"
META = ROOT / "data" / "build_meta.json"
WEB = ROOT / "web"

@asynccontextmanager
async def lifespan(_app: FastAPI):
    load_bundle()
    yield


app = FastAPI(
    title="Meridian Retail Command",
    description="Premium BI console on real UCI Online Retail II marts",
    version="1.0.0",
    lifespan=lifespan,
)


def _read_csv(name: str) -> list[dict[str, Any]]:
    path = MART / name
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Missing mart: {name}")
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _num(row: dict[str, Any], key: str) -> float:
    try:
        return float(row.get(key) or 0)
    except (TypeError, ValueError):
        return 0.0


@lru_cache(maxsize=1)
def load_bundle() -> dict[str, Any]:
    kpi_path = MART / "kpi_snapshot.json"
    kpi = json.loads(kpi_path.read_text(encoding="utf-8"))[0] if kpi_path.exists() else {}
    meta = json.loads(META.read_text(encoding="utf-8")) if META.exists() else {}

    monthly = _read_csv("mart_monthly_trend.csv")
    country = _read_csv("mart_country_performance.csv")
    rfm = _read_csv("mart_customer_rfm.csv")
    cohort = _read_csv("mart_cohort_retention.csv")
    pareto = _read_csv("mart_product_pareto.csv")
    returns = _read_csv("mart_returns_leakage.csv")

    # RFM segment rollup
    seg: dict[str, dict[str, float]] = {}
    for r in rfm:
        s = r.get("rfm_segment") or "Unknown"
        bucket = seg.setdefault(s, {"customers": 0, "revenue": 0.0, "returns": 0.0})
        bucket["customers"] += 1
        bucket["revenue"] += _num(r, "monetary")
        bucket["returns"] += _num(r, "returns_abs")
    segments = [
        {
            "rfm_segment": k,
            "customers": int(v["customers"]),
            "revenue": round(v["revenue"], 2),
            "returns": round(v["returns"], 2),
        }
        for k, v in sorted(seg.items(), key=lambda x: -x[1]["revenue"])
    ]

    top80 = [r for r in pareto if r.get("is_top80_pct") in ("1", "1.0", 1)]
    returns_by_country: dict[str, float] = {}
    for r in returns:
        c = r.get("country") or "Unknown"
        returns_by_country[c] = returns_by_country.get(c, 0.0) + _num(r, "return_value")
    returns_country = sorted(
        [{"country": k, "return_value": round(v, 2)} for k, v in returns_by_country.items()],
        key=lambda x: -x["return_value"],
    )[:15]

    # Cohort matrix for heatmap (limit early cohorts with enough size)
    cohort_rows = {}
    for r in cohort:
        cm = r["cohort_month"]
        cohort_rows.setdefault(cm, {"cohort_customers": int(float(r["cohort_customers"])), "points": {}})
        cohort_rows[cm]["points"][int(float(r["month_number"]))] = float(r["retention_pct"])

    cohort_matrix = []
    for cm, info in sorted(cohort_rows.items()):
        if info["cohort_customers"] < 50:
            continue
        row = {"cohort_month": cm, "cohort_customers": info["cohort_customers"]}
        for m in range(0, 13):
            row[f"m{m}"] = info["points"].get(m)
        cohort_matrix.append(row)

    at_risk_value = [
        {
            "customer_id": r["customer_id"],
            "last_purchase": r["last_purchase"],
            "recency_days": int(float(r["recency_days"])),
            "frequency": int(float(r["frequency"])),
            "monetary": _num(r, "monetary"),
            "rfm_segment": r["rfm_segment"],
        }
        for r in rfm
        if r.get("rfm_segment") in ("Champions", "Loyal", "Big spenders")
        and _num(r, "recency_days") > 90
    ]
    at_risk_value.sort(key=lambda x: -x["monetary"])

    return {
        "meta": meta,
        "kpi": kpi,
        "monthly": monthly,
        "country": sorted(country, key=lambda r: -_num(r, "sales"))[:20],
        "segments": segments,
        "cohort_matrix": cohort_matrix[:18],
        "pareto_top": pareto[:40],
        "pareto_stats": {
            "skus_top80": len(top80),
            "skus_total": len(pareto),
            "sales_top80": round(sum(_num(r, "sales") for r in top80), 2),
        },
        "returns_country": returns_country,
        "returns_top": sorted(returns, key=lambda r: -_num(r, "return_value"))[:30],
        "at_risk_value": at_risk_value[:25],
        "rfm_total_customers": len(rfm),
    }


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "product": "Meridian Retail Command"}


@app.get("/api/dashboard")
def dashboard() -> dict[str, Any]:
    return load_bundle()


@app.get("/api/mart/{name}")
def mart(
    name: str,
    limit: int = Query(500, ge=1, le=5000),
) -> dict[str, Any]:
    allowed = {
        "mart_kpi_snapshot",
        "mart_monthly_trend",
        "mart_country_performance",
        "mart_customer_rfm",
        "mart_cohort_retention",
        "mart_product_pareto",
        "mart_returns_leakage",
        "mart_daily_sales",
    }
    if name not in allowed:
        raise HTTPException(status_code=400, detail="Unknown mart")
    rows = _read_csv(f"{name}.csv")
    return {"name": name, "total": len(rows), "rows": rows[:limit]}


@app.get("/")
def index() -> FileResponse:
    return FileResponse(WEB / "pages" / "index.html")


app.mount("/static", StaticFiles(directory=WEB / "static"), name="static")
