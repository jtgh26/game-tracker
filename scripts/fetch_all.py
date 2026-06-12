#!/usr/bin/env python3
"""
fetch_all.py — Daily fetch từ 16p.com (test_game API PRIMARY) + iTunes API
test_game API = tất cả trạng thái (上线/试玩/删档测试/公测...)
new_game_list API = chỉ để lấy tags/score
"""

import json, time, os, urllib.request, urllib.parse
from datetime import datetime, timezone, timedelta

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(BASE, "live_data.json")

HEADERS_16P = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Referer":    "https://www.16p.com/",
    "Accept":     "application/json",
}

TAG_VI = {
    "角色扮演":"RPG","动作":"Hành động","策略":"Chiến thuật","休闲":"Casual",
    "冒险":"Phiêu lưu","卡牌":"Thẻ bài","回合":"Turn-based","养成":"Nuôi dưỡng",
    "放置":"Idle / AFK","SLG":"SLG","MMORPG":"MMORPG","Roguelike":"Roguelike",
    "开放世界":"Open World","多人联机":"Multiplayer","二次元":"ACG / Anime",
    "模拟经营":"Quản lý mô phỏng","模拟":"Mô phỏng","沙盒":"Sandbox",
    "生存":"Sinh tồn","建造":"Xây dựng","收集":"Thu thập","解谜":"Giải đố",
    "塔防":"Tower Defense","射击":"Bắn súng","格斗":"Đối kháng",
    "三国":"Tam Quốc","武侠":"Võ hiệp","修仙":"Tu Tiên","中国风":"Phong cách TQ",
    "末日":"Tận thế","科幻":"Sci-fi","独立游戏":"Indie","抓宠":"Bắt pet",
    "自走棋":"Auto Chess","搜打撤":"Loot & Extract","割草":"Hack & Slash",
    "MOBA":"MOBA","MMO":"MMO","动漫改编":"Chuyển thể anime","体育":"Thể thao",
    "即时策略":"RTS","战术博弈":"Chiến thuật","都市":"Đô thị",
    "历史":"Lịch sử","战争":"Chiến tranh","海战":"Hải chiến","航海":"Hàng hải",
    "桌游":"Board game","战术竞技":"Battle Royale","刷宝":"Loot / Cày cuốc",
    "废土":"Wasteland","农场模拟":"Nông trại","换装":"Thời trang",
    "恋爱":"Hẹn hò","女性向":"Otome / Nữ tính","单机":"Offline / Chơi đơn",
    "足球":"Bóng đá","多结局":"Đa kết thúc","视觉小说":"Visual Novel",
    "家庭聚会":"Party Game","试玩":"Demo","合成":"Ghép/Merge",
    "温暖治愈":"Healing","竞技":"Cạnh tranh","3D":"3D","像素":"Pixel",
    "Roguelite":"Roguelite","暗黑":"Dark",
}

SKIP_TAGS = {
    '编辑推荐','近期下载飙升','多端互通','高画质','近期热门预约',
    '安心购','策略拉满','编辑精选','多平台','高自由度',
    '买断制','Steam移植','近期下载',
}

TESTTYPE_MAP = {
    "公测":                    ("公测",                    "Open Beta"),
    "上线":                    ("上线",                    "Onlive / Launch"),
    "试玩":                    ("试玩",                    "Demo"),
    "删档测试":                ("删档测试",                "Clear data Test"),
    "限量删档":                ("限量删档",                "Clear data Test (giới hạn)"),
    "限量删档测试":            ("限量删档测试",            "Clear data Test (giới hạn)"),
    "不限量不删档":            ("不限量不删档",            "Non-clear data Test (không giới hạn)"),
    "限量不删档测试":          ("限量不删档测试",          "Non-clear data Test (giới hạn)"),
    "删档计费测试":            ("删档计费测试",            "Paid Test xóa data"),
    "限量删档计费测试":        ("限量删档计费测试",        "Paid Test xóa data (giới hạn)"),
    "限量不删档计费":          ("限量不删档计费",          "Paid Test không xóa data (giới hạn)"),
    "不删档计费":              ("不删档计费",              "Paid Test không xóa data"),
    "不删档计费测试":          ("不删档计费测试",          "Paid Test không xóa data"),
    "不限量不删档计费":        ("不限量不删档计费",        "Paid Test không xóa data (không giới hạn)"),
    "计费删档内测":            ("计费删档内测",            "Paid Test nội bộ xóa data"),
    "删档内测":                ("删档内测",                "Test nội bộ xóa data"),
    "二次删档计费测试":        ("二次删档计费测试",        "Paid Test lần 2 không xóa data"),
    "不计费限量删档":          ("不计费限量删档",          "Clear data Test giới hạn, không nạp tiền"),
    "限量抢注删档计费测试":    ("限量抢注删档计费测试",    "Test giới hạn tranh suất đăng ký sớm"),
    "限量删档技术测试":        ("限量删档技术测试",        "Limited Technical Test"),
    "线下试玩会":              ("线下试玩会",              "Offline Playtest Event"),
    "新增版本":                ("新增版本",                "Cập nhật phiên bản mới"),
    "删档不计费测试":          ("删档不计费测试",          "Test xóa data không nạp tiền"),
    "限量计费删档":            ("限量计费删档",            "Giới hạn số lượng, có nạp tiền và xóa data"),
    "限量计费删档测试":        ("限量计费删档测试",        "Paid Test giới hạn xóa data"),
    "公测运营":                ("公测运营",                "Onlive / Launch"),
    "预约":                    ("预约",                    "Pre-register"),
    "技术测试":                ("技术测试",                "Technical Test"),
    "付费测试":                ("付费测试",                "Paid Test"),
    "不删档测试":              ("不删档测试",              "Non-clear data Test"),
    "限量测试":                ("限量测试",                "Limited Test"),
}

TAPTAP_IDS = {
    "王者荣耀世界":"744415","异环-自由开放都市":"714119","三国：天下归心":"759941",
    "神泣：纷争":"839042","饥困荒野-饥荒：新家园":"194039","原神":"168332",
    "崩坏：星穹铁道":"225069","明日方舟":"158138","无限暖暖":"247283",
    "鸣潮":"234280","元气骑士":"35077","战双帕弥什":"162255",
    "鹅鸭杀":"202498","光遇":"135596","洛克王国：世界":"695501",
    "遗忘之海-记忆环游海洋开放世界":"755604",
}

def fetch_json(url, headers=None, timeout=12):
    req = urllib.request.Request(url, headers=headers or HEADERS_16P)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode('utf-8'))
    except Exception as e:
        print(f"  ✗ {url[:70]}: {e}")
        return None

def translate_tags(tags_list, max_n=6):
    res, seen = [], set()
    for t in (tags_list or []):
        if t in SKIP_TAGS: continue
        vn = TAG_VI.get(t, t)
        if vn not in seen:
            seen.add(vn); res.append(vn)
        if len(res) >= max_n: break
    return res

def tt_url(name):
    if name in TAPTAP_IDS:
        return f"https://www.taptap.cn/app/{TAPTAP_IDS[name]}"
    return f"https://www.taptap.cn/search?q={urllib.parse.quote(name)}"

def fetch_itunes(name, country='cn'):
    q = urllib.parse.quote(name)
    url = f"https://itunes.apple.com/search?term={q}&country={country}&entity=software&limit=1"
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"iTunes/12.11.0"})
        with urllib.request.urlopen(req, timeout=8) as r:
            d = json.loads(r.read().decode('utf-8'))
        res = d.get('results', [])
        if res:
            return {
                'appId':    str(res[0].get('trackId','')),
                'icon':     res[0].get('artworkUrl100','').replace('100x100bb','200x200bb'),
                'rating':   round(res[0].get('averageUserRating',0),1),
                'reviews':  res[0].get('userRatingCount',0),
                'appUrl':   res[0].get('trackViewUrl',''),
                'developer':res[0].get('artistName',''),
            }
    except: pass
    return None

def fetch_test_game_all(days_back=180, days_ahead=30):
    """
    PRIMARY SOURCE: fetch test_game API for date range.
    Returns ALL game statuses (上线/试玩/删档测试/公测/etc.)
    """
    all_games = {}
    today = datetime.now(timezone.utc)

    dates_to_fetch = []
    for d in range(-days_back, days_ahead+1, 3):  # every 3 days to reduce requests
        dt = today + timedelta(days=d)
        dates_to_fetch.append(dt.strftime('%Y-%m-%d'))

    print(f"  Fetching {len(dates_to_fetch)} date points...")
    for date_str in dates_to_fetch:
        for type_range in [2]:  # 2 = CN domestic only
            url = f"https://www.16p.com/gamecenter/api/test_game?date={date_str}&type_range={type_range}&p=1"
            data = fetch_json(url)
            if not data or 'dates' not in data: continue
            for date, games in data['dates'].items():
                for g in games:
                    gid = g.get('gameid')
                    if not gid or gid in all_games: continue
                    gd = g.get('game', {})
                    testtype = g.get('testtype','').strip()
                    all_games[gid] = {
                        'gameid':    gid,
                        'gamename':  gd.get('gamename',''),
                        'iconurl':   gd.get('iconurl',''),
                        'testtype':  testtype,
                        'testdate':  g.get('testdate', date),
                        'area':      gd.get('area',''),
                        'companys':  gd.get('companys',[]),
                        'gameplay':  [],  # filled from new_game_list
                        'review_rate': '',
                        'review_num':  '',
                        'gameweb':   gd.get('gameweb',''),
                        'androidurl': gd.get('androidurl',''),
                        'taptapurl':  gd.get('taptapurl',''),
                        'taptap_id':  str(gd.get('taptap_id','') or ''),
                        'itunes_appid': str(gd.get('itunes_appid','') or ''),
                    }
            time.sleep(0.15)

    print(f"  test_game API: {len(all_games)} unique games across all statuses")

    # Show status distribution
    counts = {}
    for g in all_games.values():
        tt = g['testtype'] or '(unknown)'
        counts[tt] = counts.get(tt,0) + 1
    print(f"  Status breakdown: {dict(sorted(counts.items(), key=lambda x:-x[1])[:8])}")

    return list(all_games.values())

def fetch_new_game_list_tags():
    """
    SECONDARY: get gameplay tags + scores from new_game_list API.
    Returns dict: gamename -> {gameplay, review_rate, review_num, gameweb, androidurl, taptap_id, itunes_appid}
    """
    tags_map = {}
    for date_range in [30, 60, 90, 180, 365]:
        for p in [1, 2]:
            url = f"https://www.16p.com/gamecenter/api/new_game_list?p={p}&ps=50&date_range={date_range}&type_range=2"
            data = fetch_json(url)
            if not data: break
            for g in data:
                name = g.get('gamename','')
                if name and name not in tags_map:
                    tags_map[name] = {
                        'gameplay':    g.get('gameplay',[]),
                        'review_rate': str(g.get('review_rate','')),
                        'review_num':  str(g.get('review_num','')),
                        'gameweb':     g.get('gameweb','') or g.get('mainsite',''),
                        'androidurl':  g.get('androidurl',''),
                        'taptapurl':   g.get('taptapurl',''),
                        'taptap_id':   str(g.get('taptap_id','') or ''),
                        'itunes_appid':str(g.get('itunes_appid','') or ''),
                        'format_time': g.get('format_time','') or g.get('publishtime',''),
                    }
            time.sleep(0.3)
    print(f"  new_game_list tags: {len(tags_map)} games")
    return tags_map

def fetch_rankings():
    results = {}
    for period, label in [(30,'rank30'),(90,'rank90'),(365,'rankyr')]:
        url = f"https://www.16p.com/gamecenter/api/new_game_list?p=1&ps=30&date_range={period}&type_range=2"
        data = fetch_json(url)
        results[label] = data or []
        time.sleep(0.3)
        print(f"  rankings {period}d: {len(results[label])} games")
    return results

def build_game(g, tags_data, itunes_cache, idx, is_rank=False):
    name = g.get('gamename','') or g.get('name','')
    if not name: return None

    # Get tags from secondary source
    td = tags_data.get(name, {})
    tags = g.get('gameplay') or td.get('gameplay', [])
    tags = [t for t in tags if t]
    tags_vn = translate_tags(tags)

    # Company info
    companys = g.get('companys', [])
    pub = next((c['name'] for c in companys if str(c.get('company_role_id',''))=='1'), '') or td.get('pub','')
    dev = next((c['name'] for c in companys if str(c.get('company_role_id',''))=='2'), '') or td.get('dev','')

    # Status - from test_game (ALL statuses)
    testtype_raw = g.get('testtype','').strip()
    status_pair = TESTTYPE_MAP.get(testtype_raw, (testtype_raw, testtype_raw or 'Open Beta'))

    # iTunes
    it = itunes_cache.get(name)
    if not it:
        it = fetch_itunes(name)
        itunes_cache[name] = it
        time.sleep(0.3)

    # Store links
    tt_id = (g.get('taptap_id') or td.get('taptap_id','') or TAPTAP_IDS.get(name,'') or '').strip()
    if tt_id and tt_id != '0':
        tt_direct = f"https://www.taptap.cn/app/{tt_id}"
    else:
        tt_direct = f"https://www.taptap.cn/search?q={urllib.parse.quote(name)}"

    ios_id  = (g.get('itunes_appid') or td.get('itunes_appid','') or (it['appId'] if it else '')).strip()
    ios_id  = ios_id if ios_id and ios_id != '0' else ''
    ios_url = f"https://apps.apple.com/app/id{ios_id}" if ios_id else ''
    mainsite = g.get('gameweb','') or td.get('gameweb','')

    pub_time = g.get('testdate','') or td.get('format_time','') or g.get('pub_time','')

    icon = (it['icon'] if it and it.get('icon') else '') or g.get('iconurl','')

    result = {
        'stt' if not is_rank else 'rank': str(idx+1),
        'name':          name,
        'icon_url':      icon,
        'tags_cn':       ' / '.join(tags),
        'tags_vn':       tags_vn,
        'publisher':     pub,
        'developer':     dev or pub,
        'testtype_cn':   status_pair[0],
        'testtype_vn':   status_pair[1],
        'score_16p':     td.get('review_rate','') or g.get('review_rate',''),
        'reviews_16p':   td.get('review_num','')  or g.get('review_num',''),
        'pub_time':      pub_time,
        'date_sort':     pub_time[:10] if len(pub_time)>=10 else pub_time,
        'ios_id':        ios_id,
        'ios_url':       ios_url,
        'ios_rating':    str(it['rating']) if it else '',
        'ios_reviews':   str(it['reviews']) if it else '',
        'store_taptap':  tt_direct,
        'store_bilibili':f"https://search.bilibili.com/all?keyword={urllib.parse.quote(name)}",
        'store_hygb':    f"https://www.taptap.cn/search?q={urllib.parse.quote(name)}",
        'Mainsite':      mainsite,
        'fetched_at':    datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),
    }
    return result

def main():
    print("🎮 Fetching 16p.com (ALL statuses) + iTunes...")

    # Load iTunes cache
    itunes_cache = {}
    if os.path.exists(OUT):
        try:
            with open(OUT,'r') as f: old = json.load(f)
            for ds in ['newgames','rank30','rank90','rankyr']:
                for g in old.get(ds,[]):
                    if g.get('ios_id') and g['ios_id'] not in ('0',''):
                        itunes_cache[g['name']] = {
                            'appId':g['ios_id'],'icon':g.get('icon_url',''),
                            'rating':float(g.get('ios_rating',0) or 0),
                            'reviews':int(g.get('ios_reviews',0) or 0),
                            'developer':g.get('developer',''),
                        }
            print(f"  Loaded {len(itunes_cache)} cached iTunes entries")
        except: pass

    # PRIMARY: test_game API → ALL statuses
    print("\n📡 test_game API (PRIMARY — ALL statuses)...")
    test_games = fetch_test_game_all(days_back=180, days_ahead=30)

    # SECONDARY: new_game_list → tags + scores
    print("\n📡 new_game_list API (tags + scores only)...")
    tags_data = fetch_new_game_list_tags()

    # Rankings
    print("\n📡 Rankings...")
    rankings = fetch_rankings()

    # Sort test_games by testdate desc
    def sort_key(g):
        d = g.get('testdate','')
        return d if d else '2000-01-01'
    test_games.sort(key=sort_key, reverse=True)

    # Build newgames list from test_game (all statuses)
    print(f"\n🍎 Enriching {min(len(test_games),150)} newgames with iTunes...")
    newgames = []
    seen = set()
    for i, g in enumerate(test_games):
        if i >= 150: break
        name = g.get('gamename','')
        if not name or name in seen: continue
        seen.add(name)
        result = build_game(g, tags_data, itunes_cache, len(newgames), False)
        if result: newgames.append(result)
        if (i+1) % 20 == 0:
            print(f"  [{i+1}/{min(len(test_games),150)}]...")

    # Build rankings
    def process_ranks(raw_list, label):
        results = []
        for i, g in enumerate(raw_list[:30]):
            name = g.get('gamename','')
            if not name: continue
            # For rankings, testtype defaults to 上线
            if not g.get('testtype'):
                g['testtype'] = '上线'
            result = build_game(g, tags_data, itunes_cache, i, True)
            if result: results.append(result)
        print(f"  ✓ {label}: {len(results)} games")
        return results

    print("\n🍎 Enriching rankings...")
    out = {
        'newgames': newgames,
        'rank30':   process_ranks(rankings['rank30'],  'rank30'),
        'rank90':   process_ranks(rankings['rank90'],  'rank90'),
        'rankyr':   process_ranks(rankings['rankyr'],  'rankyr'),
        'updated_at': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),
        'source': '16p.com test_game (ALL statuses) + new_game_list (tags) + iTunes',
    }

    with open(OUT,'w',encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    # Final stats
    print(f"\n✅ Saved {OUT}")
    print(f"   newgames={len(newgames)} | rank30={len(out['rank30'])}")
    if newgames:
        status_counts = {}
        for g in newgames:
            s = g.get('testtype_vn','?')
            status_counts[s] = status_counts.get(s,0)+1
        print(f"   Status breakdown: {dict(sorted(status_counts.items(), key=lambda x:-x[1])[:8])}")

if __name__ == '__main__':
    main()
