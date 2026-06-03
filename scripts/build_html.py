#!/usr/bin/env python3
"""
build_html.py
Reads taptap_data.json + game_data.json → injects live TapTap stats
into the tracker HTML → outputs index.html
"""

import json
import os
import re
import shutil
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def rating_stars(score):
    """Convert 0-10 TapTap score to visual bar."""
    if not score:
        return ""
    pct = min(100, int(score * 10))
    color = "#10b981" if score >= 8 else "#f59e0b" if score >= 6 else "#ef4444"
    return f'<div style="display:inline-flex;align-items:center;gap:5px"><div style="width:50px;height:5px;background:rgba(255,255,255,0.1);border-radius:3px;overflow:hidden"><div style="width:{pct}%;height:100%;background:{color};border-radius:3px"></div></div><span style="font-size:11px;color:{color};font-weight:600">{score}</span></div>'

def main():
    taptap  = load_json(os.path.join(BASE, "taptap_data.json"))
    game_data_path = os.path.join(BASE, "game_data.json")
    
    # Load base HTML
    html_src = os.path.join(BASE, "index_template.html")
    if not os.path.exists(html_src):
        print(f"✗ Template not found: {html_src}")
        return

    with open(html_src, "r", encoding="utf-8") as f:
        html = f.read()

    # Build taptap_lookup JS object to inject
    tt_lookup = {}
    for name, info in taptap.items():
        tt_lookup[name] = {
            "rating":       info.get("taptap_rating"),
            "rating_count": info.get("taptap_rating_count_fmt", "N/A"),
            "fans":         info.get("taptap_fans_fmt", "N/A"),
            "hits":         info.get("taptap_hits_fmt", "N/A"),
            "heat":         info.get("taptap_heat"),
            "icon_url":     info.get("icon_url", ""),
            "fetched_at":   info.get("fetched_at", ""),
            "manual":       info.get("manual", []),
        }

    tt_js = json.dumps(tt_lookup, ensure_ascii=False)
    updated_at = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")


    # Inject icon_urls from taptap data into RAW game data
    if os.path.exists(game_data_path):
        with open(game_data_path, "r", encoding="utf-8") as f:
            game_data = json.load(f)
        for dataset in ["newgames","bxh_30","bxh_90","bxh_year"]:
            for g in game_data.get(dataset, []):
                name = g.get("Tên gốc","")
                if name in taptap and taptap[name].get("icon_url"):
                    g["icon_url"] = taptap[name]["icon_url"]
        game_data_js = json.dumps(game_data, ensure_ascii=False)
        html = re.sub(r'const RAW=\\{.*?\\};', f'const RAW={game_data_js};', html, count=1, flags=re.DOTALL)


    # Inject into HTML
    html = html.replace("__TAPTAP_DATA__", tt_js)
    html = html.replace("__UPDATED_AT__", updated_at)

    out_path = os.path.join(BASE, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✓ Built index.html with {len(taptap)} game stats → {out_path}")


if __name__ == "__main__":
    main()
