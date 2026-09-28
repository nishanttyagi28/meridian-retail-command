"""Smoke tests for Meridian Retail Command marts + API."""

from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
MART = ROOT / "data" / "mart"
DB = ROOT / "data" / "meridian.db"


@pytest.fixture(scope="module")
def client():
    import sys

    sys.path.insert(0, str(ROOT / "src"))
    from meridian_app import app

    return TestClient(app)


def test_mart_files_exist():
    required = [
        "kpi_snapshot.json",
        "mart_kpi_snapshot.csv",
        "mart_monthly_trend.csv",
        "mart_country_performance.csv",
        "mart_customer_rfm.csv",
        "mart_cohort_retention.csv",
        "mart_product_pareto.csv",
        "mart_returns_leakage.csv",
    ]
    for name in required:
        assert (MART / name).exists(), name


def test_kpi_shape_and_gbp():
    kpi = json.loads((MART / "kpi_snapshot.json").read_text(encoding="utf-8"))[0]
    assert "gross_sales_gbp" in kpi
    assert kpi["gross_sales_gbp"] > 1_000_000
    assert 0 < kpi["return_rate_pct"] < 30
    assert kpi["customers"] == 5942
    assert kpi["countries"] == 43


def test_rfm_recency_score_direction():
    with (MART / "mart_customer_rfm.csv").open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    by_score = {}
    for r in rows:
        s = int(float(r["r_score"]))
        by_score.setdefault(s, []).append(int(float(r["recency_days"])))
    med = {s: sorted(v)[len(v) // 2] for s, v in by_score.items()}
    # Higher R score must mean more recent (lower days)
    assert med[5] < med[1]


def test_champions_exist():
    with (MART / "mart_customer_rfm.csv").open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    champs = [r for r in rows if r["rfm_segment"] == "Champions"]
    assert len(champs) > 50


def test_sqlite_views_if_present():
    if not DB.exists():
        pytest.skip("meridian.db not built in this environment")
    con = sqlite3.connect(DB)
    try:
        n = con.execute("SELECT COUNT(*) FROM mart_monthly_trend").fetchone()[0]
        assert n == 25
        cols = [r[1] for r in con.execute("PRAGMA table_info(mart_kpi_snapshot)").fetchall()]
        # views report via pragma differently — query instead
        row = con.execute("SELECT gross_sales_gbp FROM mart_kpi_snapshot").fetchone()
        assert row and row[0] > 0
    finally:
        con.close()


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_dashboard_api(client):
    r = client.get("/api/dashboard")
    assert r.status_code == 200
    body = r.json()
    assert "kpi" in body and "monthly" in body and "segments" in body
    assert body["kpi"]["gross_sales_gbp"] > 0
    assert len(body["monthly"]) == 25


def test_index_html(client):
    r = client.get("/")
    assert r.status_code == 200
    assert b"Meridian" in r.content
