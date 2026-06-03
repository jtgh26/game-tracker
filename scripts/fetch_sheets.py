#!/usr/bin/env python3
"""
fetch_sheets.py
Fetch premium KPI data entered manually in Google Sheets.
Sheet must be published as CSV (File → Share → Publish to web → CSV).

Sheet structure (columns):
  game_name | date | dau | nru | install | ltv | arpu | revenue |
  retention_d1 | retention_d7 | retention_d30 | source | note
"""

import csv
import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone
from io import StringIO

# ── CONFIG ───────────────────────────────────────────────────────────────────
# Set SHEETS_CSV_URL in GitHub Secrets or .env
# Get this from: Google Sheets → File → Share → Publish to web → Sheet1 → CSV
SHEETS_CSV_URL = os.environ.get("SHEETS_CSV_URL", "")

EXPECTED_COLS = [
    "game_name", "date", "dau", "nru", "install",
    "ltv", "arpu", "revenue",
    "retention_d1", "retention_d7", "retention_d30",
    "source", "note"
]


def fetch_sheets_data(csv_url: str) -> list[dict]:
    """Download and parse CSV from Google Sheets published URL."""
    if not csv_url:
        print("  ⚠ SHEETS_CSV_URL not set, skipping Google Sheets sync")
        return []
    try:
        req = urllib.request.Request(
            csv_url,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode("utf-8")
        reader = csv.DictReader(StringIO(content))
        rows = []
        for row in reader:
            # Normalize keys to lowercase stripped
            clean = {k.strip().lower().replace(" ", "_"): v.strip() for k, v in row.items()}
            if clean.get("game_name"):
                rows.append(clean)
        print(f"  ✓ Google Sheets: {len(rows)} rows fetched")
        return rows
    except Exception as e:
        print(f"  ✗ Google Sheets error: {e}")
        return []


def merge_into_taptap(sheets_rows: list[dict], taptap_path: str):
    """Merge Sheets KPIs into taptap_data.json under each game's 'manual' key."""
    if not os.path.exists(taptap_path):
        print(f"  ✗ {taptap_path} not found, run fetch_taptap.py first")
        return

    with open(taptap_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    updated = 0
    for row in sheets_rows:
        gname = row.get("game_name", "").strip()
        if not gname:
            continue
        # Match by exact name or partial
        matched_key = None
        for key in data:
            if key == gname or gname in key or key in gname:
                matched_key = key
                break
        if not matched_key:
            print(f"  ⚠ Sheets row '{gname}' not matched in taptap_data")
            continue

        entry = {
            "date":         row.get("date", ""),
            "dau":          row.get("dau", ""),
            "nru":          row.get("nru", ""),
            "install":      row.get("install", ""),
            "ltv":          row.get("ltv", ""),
            "arpu":         row.get("arpu", ""),
            "revenue":      row.get("revenue", ""),
            "retention_d1": row.get("retention_d1", ""),
            "retention_d7": row.get("retention_d7", ""),
            "retention_d30":row.get("retention_d30", ""),
            "source":       row.get("source", "Manual"),
            "note":         row.get("note", ""),
            "synced_at":    datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        }

        if "manual" not in data[matched_key]:
            data[matched_key]["manual"] = []
        # Avoid duplicates by date
        existing_dates = {e.get("date") for e in data[matched_key]["manual"]}
        if entry["date"] not in existing_dates:
            data[matched_key]["manual"].insert(0, entry)
            updated += 1

    with open(taptap_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"  ✓ Merged {updated} new Sheets entries into taptap_data.json")


def main():
    base = os.path.join(os.path.dirname(__file__), "..")
    taptap_path = os.path.join(base, "taptap_data.json")

    rows = fetch_sheets_data(SHEETS_CSV_URL)
    if rows:
        merge_into_taptap(rows, taptap_path)
    else:
        print("  No Sheets data to merge")


if __name__ == "__main__":
    main()
