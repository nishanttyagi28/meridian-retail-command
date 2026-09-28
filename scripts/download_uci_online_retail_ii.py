#!/usr/bin/env python3
"""Download UCI Online Retail II into data/raw/."""

from __future__ import annotations

import urllib.request
from pathlib import Path

URL = "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT_XLSX = RAW / "online_retail_II.xlsx"


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    if OUT_XLSX.exists() and OUT_XLSX.stat().st_size > 1_000_000:
        print(f"Already present: {OUT_XLSX}")
        return

    import io
    import zipfile

    print(f"Downloading {URL} ...")
    with urllib.request.urlopen(URL, timeout=180) as resp:
        blob = resp.read()
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        members = [n for n in zf.namelist() if n.lower().endswith(".xlsx")]
        if not members:
            raise SystemExit(f"No xlsx in zip. Members: {zf.namelist()}")
        data = zf.read(members[0])
        OUT_XLSX.write_bytes(data)
    print(f"Wrote {OUT_XLSX} ({OUT_XLSX.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
