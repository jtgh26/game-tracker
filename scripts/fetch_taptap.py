#!/usr/bin/env python3
"""
fetch_taptap.py
Scrape TapTap rating, review count, heat score for each game.
Runs daily via GitHub Actions.
"""

import json
import time
import re
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone

# ── GAME LIST với TapTap App IDs ─────────────────────────────────────────────
GAMES = [
    # newgames
    {"name": "射雕",             "name_en": "Legend of Eagle Shooting Heroes", "taptap_id": "355258", "type": "newgame"},
    {"name": "燕云十六声",        "name_en": "Where Winds Meet",               "taptap_id": "234218", "type": "newgame"},
    {"name": "代号:破晓",         "name_en": "Project Dawn",                   "taptap_id": "370480", "type": "newgame"},
    {"name": "星之海图",          "name_en": "Star Sea Map",                   "taptap_id": "345621", "type": "newgame"},
    {"name": "无限暖暖",          "name_en": "Infinity Nikki",                 "taptap_id": "290730", "type": "newgame"},
    {"name": "鸣潮",              "name_en": "Wuthering Waves",               "taptap_id": "231682", "type": "newgame"},
    {"name": "三国：谋定天下",     "name_en": "Three Kingdoms: Strategize the World", "taptap_id": "367210", "type": "newgame"},
    {"name": "龙族幻想2",         "name_en": "Dragon Raja 2",                 "taptap_id": "372156", "type": "newgame"},
    {"name": "暗区突围:无限",      "name_en": "Escape from Tarkov Mobile CN",  "taptap_id": "358890", "type": "newgame"},
    {"name": "问道手游2",          "name_en": "Wendao Mobile 2",               "taptap_id": "351200", "type": "newgame"},
    {"name": "永恒纪元2",          "name_en": "Eternal City 2",                "taptap_id": "369012", "type": "newgame"},
    {"name": "独行侠",             "name_en": "Lone Ranger",                   "taptap_id": "362540", "type": "newgame"},
    {"name": "凡人修仙传：人界篇", "name_en": "A Record of Mortal's Journey",  "taptap_id": "301584", "type": "newgame"},
    {"name": "赤核",               "name_en": "Red Core",                      "taptap_id": "368421", "type": "newgame"},
    {"name": "决战平安京2",        "name_en": "Onmyoji Arena 2",               "taptap_id": "374012", "type": "newgame"},
    {"name": "末世危城",           "name_en": "Last Shelter: Survival City",   "taptap_id": "361580", "type": "newgame"},
    {"name": "梦幻新诛仙",         "name_en": "New Fantasy Jade Dynasty",      "taptap_id": "357890", "type": "newgame"},
    {"name": "勇者斗恶龙 达依的大冒险", "name_en": "DQ Dai's Big Adventure",  "taptap_id": "376043", "type": "newgame"},
    {"name": "Aether Gazer 2",    "name_en": "Aether Gazer 2",                "taptap_id": "371290", "type": "newgame"},
    {"name": "万象物语2",          "name_en": "Sdorica 2",                     "taptap_id": "353401", "type": "newgame"},
    # rankings
    {"name": "原神",               "name_en": "Genshin Impact",                "taptap_id": "168332", "type": "ranking"},
    {"name": "王者荣耀",           "name_en": "Honor of Kings",                "taptap_id": "35893",  "type": "ranking"},
    {"name": "和平精英",           "name_en": "PUBG Mobile CN",                "taptap_id": "33592",  "type": "ranking"},
    {"name": "明日方舟",           "name_en": "Arknights",                     "taptap_id": "158138", "type": "ranking"},
    {"name": "三国志·战略版",      "name_en": "Three Kingdoms Tactics",        "taptap_id": "87448",  "type": "ranking"},
    {"name": "崩坏：星穹铁道",     "name_en": "Honkai: Star Rail",             "taptap_id": "225069", "type": "ranking"},
    {"name": "率土之滨",           "name_en": "Infinite Borders",              "taptap_id": "22243",  "type": "ranking"},
    {"name": "剑与远征：启程",     "name_en": "AFK Journey",                   "taptap_id": "270267", "type": "ranking"},
    {"name": "逆水寒手游",         "name_en": "Swords of Legends Online",      "taptap_id": "188318", "type": "ranking"},
    {"name": "蛋仔派对",           "name_en": "Egg Party",                     "taptap_id": "220613", "type": "ranking"},
    {"name": "万国觉醒",           "name_en": "Rise of Kingdoms",              "taptap_id": "67569",  "type": "ranking"},
    {"name": "第五人格",           "name_en": "Identity V",                    "taptap_id": "20491",  "type": "ranking"},
    {"name": "光遇",               "name_en": "Sky: Children of the Light",    "taptap_id": "135596", "type": "ranking"},
    {"name": "梦幻西游手游",       "name_en": "Fantasy Westward Journey",      "taptap_id": "6614",   "type": "ranking"},
    {"name": "无限暖暖",           "name_en": "Infinity Nikki",                "taptap_id": "290730", "type": "ranking"},
]


# iOS App IDs for icon fetching
IOS_IDS = {
    "射雕": "6736413744", "燕云十六声": "6503336700", "无限暖暖": "6547858329",
    "鸣潮": "6448443855", "永恒纪元2": "6502856738", "凡人修仙传：人界篇": "6470714651",
    "末世危城": "6470327048", "勇者斗恶龙 达依的大冒险": "6736407038", "万象物语2": "6504321890",
    "原神": "1517783697", "王者荣耀": "917464478", "和平精英": "1200002998",
    "明日方舟": "1454208647", "三国志·战略版": "1451036521", "崩坏：星穹铁道": "6448525073",
    "率土之滨": "1190336148", "剑与远征：启程": "6474849223", "逆水寒手游": "1569224264",
    "蛋仔派对": "1609659690", "万国觉醒": "1354260888", "第五人格": "1229972113",
    "光遇": "1462117269", "梦幻西游手游": "914875288",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://www.taptap.cn/",
    "X-UA": "V=1&PN=TapTap&LANG=zh_CN&CH=default&UID=&VN=3.28.0&VNC=328&LOC=CN",
}


def fetch_taptap(app_id: str) -> dict:
    """Fetch game info from TapTap API."""
    url = f"https://api.taptap.cn/tds-game-client-service/v2/app/{app_id}?X-UA=V=1&PN=TapTap&LANG=zh_CN&CH=default"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        app = data.get("data", {}).get("app", {})
        stat = app.get("stat", {})
        return {
            "taptap_rating":       round(float(stat.get("rating", {}).get("score", 0)), 1),
            "taptap_rating_count": int(stat.get("rating", {}).get("total_count", 0)),
            "taptap_fans":         int(stat.get("fans_count", 0)),
            "taptap_hits_total":   int(stat.get("hits_total", 0)),
            "taptap_heat":         round(float(app.get("heat_value", {}).get("value", 0)), 1),
            "taptap_status":       app.get("publish", {}).get("status", ""),
            "fetched_at":          datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "error": None,
        }
    except Exception as e:
        print(f"  ✗ TapTap {app_id}: {e}")
        return {
            "taptap_rating": None, "taptap_rating_count": None,
            "taptap_fans": None,   "taptap_hits_total": None,
            "taptap_heat": None,   "taptap_status": None,
            "fetched_at":  datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "error": str(e),
        }


def fmt_number(n):
    """Format large numbers: 1200000 → 1.2M"""
    if n is None:
        return "N/A"
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)



def fetch_itunes_icon(ios_id: str) -> str:
    """Fetch app artwork URL from iTunes lookup API (server-side, no CORS)."""
    if not ios_id:
        return ""
    url = f"https://itunes.apple.com/lookup?id={ios_id}&country=us&entity=software"
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "iTunes/12.11.0 (Macintosh; OS X 10.15.7)"
        })
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        results = data.get("results", [])
        if results:
            # Use 100x100 artwork, replace with 120x120 for retina
            artwork = results[0].get("artworkUrl100", "")
            return artwork.replace("100x100bb", "120x120bb") if artwork else ""
    except Exception as e:
        print(f"  iTunes icon {ios_id}: {e}")
    return ""

def main():
    out_path = os.path.join(os.path.dirname(__file__), "..", "taptap_data.json")
    
    # Load existing data to preserve manual entries
    existing = {}
    if os.path.exists(out_path):
        with open(out_path, "r", encoding="utf-8") as f:
            existing = json.load(f)

    results = {}
    seen_ids = set()

    for game in GAMES:
        app_id = game["taptap_id"]
        game["ios_id"] = IOS_IDS.get(game["name"], "")
        if app_id in seen_ids:
            # Reuse already-fetched data
            results[game["name"]] = results.get(game["name"], existing.get(game["name"], {}))
            continue
        seen_ids.add(app_id)

        print(f"  Fetching [{app_id}] {game['name']}...")
        info = fetch_taptap(app_id)

        # Fetch iTunes icon (server-side, no CORS)
        ios_id = game.get("ios_id", "")
        icon_url = fetch_itunes_icon(ios_id) if ios_id else                    existing.get(game["name"], {}).get("icon_url", "")

        results[game["name"]] = {
            "name":      game["name"],
            "name_en":   game["name_en"],
            "taptap_id": app_id,
            "type":      game["type"],
            "icon_url":  icon_url,
            # TapTap live data
            "taptap_rating":             info["taptap_rating"],
            "taptap_rating_count":       info["taptap_rating_count"],
            "taptap_rating_count_fmt":   fmt_number(info["taptap_rating_count"]),
            "taptap_fans":               info["taptap_fans"],
            "taptap_fans_fmt":           fmt_number(info["taptap_fans"]),
            "taptap_hits_total":         info["taptap_hits_total"],
            "taptap_hits_fmt":           fmt_number(info["taptap_hits_total"]),
            "taptap_heat":               info["taptap_heat"],
            "taptap_status":             info["taptap_status"],
            "fetched_at":                info["fetched_at"],
            "error":                     info["error"],
            # Preserve manual premium data from previous run / Google Sheets
            "manual": existing.get(game["name"], {}).get("manual", {}),
        }
        time.sleep(0.8)  # polite rate limit

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    ok  = sum(1 for v in results.values() if not v.get("error"))
    err = sum(1 for v in results.values() if v.get("error"))
    print(f"\n✓ Done: {ok} OK, {err} errors → {out_path}")


if __name__ == "__main__":
    main()
