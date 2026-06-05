#!/usr/bin/env python3
"""
fetch_all.py — Daily fetch từ 16p.com (test_game API) + iTunes API
16p test_game API trả về testtype chính xác + game mới nhất
"""
import json, time, os, urllib.request, urllib.parse
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(BASE, "live_data.json")

HEADERS_16P = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Referer":    "https://www.16p.com/",
    "Accept":     "application/json",
}

TAG_VI = {
    "角色扮演":"Nhập vai RPG","动作":"Action","策略":"Chiến thuật","休闲":"Casual",
    "冒险":"Phiêu lưu","卡牌":"Thẻ bài","回合":"Turn-based","养成":"Nuôi dưỡng",
    "放置":"Idle","SLG":"SLG","MMORPG":"MMORPG","Roguelike":"Roguelike",
    "开放世界":"Thế giới mở","多人联机":"Multiplayer","二次元":"Anime/2D",
    "模拟经营":"Kinh doanh","模拟":"Mô phỏng","沙盒":"Sandbox","生存":"Sinh tồn",
    "建造":"Xây dựng","收集":"Thu thập","解谜":"Giải đố","塔防":"Tower Defense",
    "射击":"Bắn súng","格斗":"Đối kháng","三国":"Tam Quốc","武侠":"Võ hiệp",
    "修仙":"Tu tiên","中国风":"Phong cách TQ","末日":"Tận thế","科幻":"Sci-fi",
    "独立游戏":"Indie","抓宠":"Bắt pet","自走棋":"Auto Chess",
    "搜打撤":"Extraction Shooter","割草":"Hack & Slash","MOBA":"MOBA","MMO":"MMO",
    "动漫改编":"Chuyển thể anime","体育":"Thể thao","即时策略":"RTS",
    "经营":"Kinh doanh","多结局":"Đa kết thúc","视觉小说":"Visual Novel",
    "女性向":"Dành cho nữ","换装":"Thay trang phục","钓鱼":"Câu cá",
    "航海":"Hàng hải","3D":"3D","历史":"Lịch sử","战争":"Chiến tranh",
    "像素":"Pixel","Roguelite":"Roguelite","暗黑":"Dark","萌宠":"Cute Pet",
    "文字":"Text/Story","单机":"Single-player","都市":"Đô thị","废土":"Hậu tận thế",
    "家庭聚会":"Party","桌游":"Board game","竞技":"Cạnh tranh","足球":"Bóng đá",
    "刷宝":"Loot/Grind","高自由度":"Tự do cao","多平台":"Đa nền tảng",
    "战术博弈":"Chiến thuật","沙盘":"Sa bàn","第一人称":"Góc nhìn thứ nhất",
    "极致视听享受":"Âm thanh & đồ họa","UE5":"UE5","恐怖惊悚":"Kinh dị",
    "克苏鲁":"Cthulhu","开荒":"Khai hoang","社交":"Xã hội","竖屏":"Màn hình dọc",
    "弹幕":"Bullet hell","涂色":"Tô màu","派对游戏":"Party game","异世界":"Isekai",
}
SKIP = {'编辑推荐','近期下载飙升','多端互通','高画质','近期热门预约',
        '安心购','策略拉满','编辑精选','买断制','Steam移植','近期下载'}

TESTTYPE_MAP = {
    "公测":     ("公测",     "Open Beta"),
    "上线":     ("上线",     "Đã ra mắt"),
    "不删档测试": ("不删档测试","OBT (Giữ data)"),
    "删档测试":  ("删档测试", "CBT (Xóa data)"),
    "付费测试":  ("付费测试", "Paid Beta"),
    "技术测试":  ("技术测试", "Tech Test"),
    "限量测试":  ("限量测试", "Limited Test"),
    "预约":     ("预约",     "Đặt trước"),
}

TAPTAP_IDS = {
    "王者荣耀世界":"744415","异环-自由开放都市":"714119","三国：天下归心":"759941",
    "神泣：纷争":"839042","饥困荒野-饥荒：新家园":"194039","原神":"168332",
    "崩坏：星穹铁道":"225069","明日方舟":"158138","无限暖暖":"247283",
    "鸣潮":"234280","元气骑士":"35077","战双帕弥什":"162255",
    "鹅鸭杀":"202498","光遇":"135596",
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
        if t in SKIP: continue
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

def fetch_16p_test_game():
    """Fetch from test_game API - has real testtype + more tags"""
    all_games = {}
    now = datetime.now(timezone.utc)
    # Fetch current month + next month (upcoming) + last 2 months (recent)
    months = []
    for delta in [-2,-1,0,1]:
        m = now.month + delta
        y = now.year + (m-1)//12
        m = ((m-1)%12)+1
        months.append(f"{y}-{m:02d}-01")

    for date_str in months:
        for type_range in [1, 2]:  # 1=all, 2=CN
            url = f"https://www.16p.com/gamecenter/api/test_game?date={date_str}&type_range={type_range}&p=1"
            data = fetch_json(url)
            if not data or 'dates' not in data: continue
            for date, games in data['dates'].items():
                for g in games:
                    gid = g.get('gameid')
                    if gid and gid not in all_games:
                        gd = g.get('game', {})
                        all_games[gid] = {
                            'gameid':   gid,
                            'gamename': gd.get('gamename',''),
                            'iconurl':  gd.get('iconurl',''),
                            'testtype': g.get('testtype','公测'),
                            'testdate': g.get('testdate', date),
                            'area':     gd.get('area',''),
                            'companys': gd.get('companys',[]),
                        }
            time.sleep(0.3)
    print(f"  test_game API: {len(all_games)} unique games")
    return list(all_games.values())

def fetch_16p_newgame_list(date_range=60):
    """Fetch from new_game_list API - has gameplay tags"""
    all_games = []
    seen = set()
    for p in [1,2,3]:
        url = f"https://www.16p.com/gamecenter/api/new_game_list?p={p}&ps=50&date_range={date_range}&type_range=2"
        data = fetch_json(url)
        if not data: break
        for g in data:
            if g['gameid'] not in seen:
                seen.add(g['gameid']); all_games.append(g)
        time.sleep(0.4)
    print(f"  new_game_list API: {len(all_games)} games")
    return all_games

def fetch_16p_rankings():
    results = {}
    for period, label in [(30,'rank30'),(90,'rank90'),(365,'rankyr')]:
        url = f"https://www.16p.com/gamecenter/api/new_game_list?p=1&ps=30&date_range={period}&type_range=2"
        data = fetch_json(url)
        results[label] = data or []
        time.sleep(0.4)
        print(f"  rankings {period}d: {len(results[label])} games")
    return results

def build_game(g_test, g_list, itunes_cache, idx, is_rank=False):
    """Merge test_game + new_game_list data"""
    name = (g_test or g_list or {}).get('gamename') or (g_list or {}).get('gamename','')
    if not name: return None

    # testtype from test_game API
    testtype_raw = (g_test or {}).get('testtype','公测')
    status_pair = TESTTYPE_MAP.get(testtype_raw, (testtype_raw, testtype_raw))

    # tags from new_game_list API
    tags = (g_list or {}).get('gameplay',[]) if g_list else []

    # companies
    companys = (g_test or g_list or {}).get('companys',[])
    pub = next((c['name'] for c in companys if c.get('company_role_id')=='1'), '')
    dev = next((c['name'] for c in companys if c.get('company_role_id')=='2'), pub)

    # iTunes
    it = itunes_cache.get(name)
    if not it:
        it = fetch_itunes(name)
        itunes_cache[name] = it
        time.sleep(0.3)

    icon = (it['icon'] if it and it.get('icon') else '') or (g_test or {}).get('iconurl','') or (g_list or {}).get('iconurl','')
    ios_id = it['appId'] if it else ''
    ios_url = f"https://apps.apple.com/cn/app/id{ios_id}" if ios_id else ''

    result = {
        'stt' if not is_rank else 'rank': str(idx+1),
        'name':          name,
        'icon_url':      icon,
        'tags_cn':       ' / '.join(tags),
        'tags_vn':       translate_tags(tags),
        'publisher':     pub or (it['developer'] if it else ''),
        'developer':     dev or pub or (it['developer'] if it else ''),
        'testtype_cn':   status_pair[0],
        'testtype_vn':   status_pair[1],
        'score_16p':     str((g_list or {}).get('review_rate','')),
        'reviews_16p':   str((g_list or {}).get('review_num','')),
        'pub_time':      (g_test or {}).get('testdate','') or (g_list or {}).get('format_time',''),
        'ios_id':        ios_id,
        'ios_url':       ios_url,
        'ios_rating':    str(it['rating']) if it else '',
        'ios_reviews':   str(it['reviews']) if it else '',
        'taptap_url':    tt_url(name),
        'fetched_at':    datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),
    }
    return result

def main():
    print("🎮 Fetching 16p.com + iTunes...")

    # Load iTunes cache
    itunes_cache = {}
    if os.path.exists(OUT):
        try:
            with open(OUT,'r') as f: old = json.load(f)
            for ds in ['newgames','rank30','rank90','rankyr']:
                for g in old.get(ds,[]):
                    if g.get('ios_id') and g['ios_id'] != '0':
                        itunes_cache[g['name']] = {
                            'appId':g['ios_id'],'icon':g.get('icon_url',''),
                            'rating':float(g.get('ios_rating',0) or 0),
                            'reviews':int(g.get('ios_reviews',0) or 0),
                            'developer':g.get('developer',''),
                        }
            print(f"  Loaded {len(itunes_cache)} cached iTunes entries")
        except: pass

    # Fetch 16p data
    print("\n📡 test_game API (for testtype)...")
    test_games = fetch_16p_test_game()
    test_by_name = {g['gamename']: g for g in test_games if g.get('gamename')}

    print("\n📡 new_game_list API (for tags + scores)...")
    list_games = fetch_16p_newgame_list(60)
    list_by_name = {g['gamename']: g for g in list_games if g.get('gamename')}

    print("\n📡 Rankings...")
    rankings = fetch_16p_rankings()

    # Merge: use list_games as primary (has tags), enrich with test_game (has testtype)
    # For newgames: combine both sources
    all_names_ordered = []
    seen_names = set()
    # Priority: list_games (sorted by score/recency)
    for g in list_games:
        n = g.get('gamename','')
        if n and n not in seen_names:
            all_names_ordered.append(n); seen_names.add(n)
    # Add any from test_games not in list
    for g in test_games:
        n = g.get('gamename','')
        if n and n not in seen_names:
            all_names_ordered.append(n); seen_names.add(n)

    print(f"\n🍎 Enriching {len(all_names_ordered)} newgames with iTunes...")
    newgames = []
    for i, name in enumerate(all_names_ordered[:100]):
        print(f"  [{i+1}] {name[:20]}")
        result = build_game(
            test_by_name.get(name),
            list_by_name.get(name),
            itunes_cache, i, False
        )
        if result: newgames.append(result)

    def process_ranks(raw_list, label):
        results = []
        print(f"\n🍎 Enriching {label}...")
        for i, g in enumerate(raw_list[:30]):
            name = g.get('gamename','')
            if not name: continue
            result = build_game(test_by_name.get(name), g, itunes_cache, i, True)
            if result: results.append(result)
        print(f"  ✓ {label}: {len(results)} games")
        return results

    out = {
        'newgames':   newgames,
        'rank30':     process_ranks(rankings['rank30'],  'rank30'),
        'rank90':     process_ranks(rankings['rank90'],  'rank90'),
        'rankyr':     process_ranks(rankings['rankyr'],  'rankyr'),
        'updated_at': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),
        'source':     '16p.com test_game+new_game_list + iTunes API',
    }

    with open(OUT,'w',encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Saved: ng={len(newgames)}, r30={len(out['rank30'])}")

    # Show sample
    if newgames:
        g = newgames[0]
        print(f"  Sample: {g['name']} | status={g['testtype_vn']} | tags={g['tags_cn'][:50]}")

if __name__ == '__main__':
    main()
