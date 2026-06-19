#!/usr/bin/env python3
"""
fetch_all.py — Fetch qua Cloudflare Worker proxy (không bị block)
Chạy tự động mỗi ngày trong GitHub Actions
"""
import json, time, os, urllib.request, urllib.parse
from datetime import datetime, timezone, timedelta

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(BASE, 'live_data.json')

# Cloudflare Worker proxy URL — set trong GitHub Secrets
PROXY_URL = os.environ.get('PROXY_URL', '').rstrip('/')
if not PROXY_URL:
    print("❌ PROXY_URL not set in environment/secrets")
    print("   Add PROXY_URL to GitHub Secrets (Settings → Secrets → Actions)")
    exit(1)

def proxy_fetch(path, retries=2):
    """Fetch 16p.com API qua Cloudflare Worker proxy"""
    url = f"{PROXY_URL}?path={urllib.parse.quote(path)}"
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "GameTracker/1.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception as e:
            if attempt < retries:
                time.sleep(2)
            else:
                print(f"  ✗ {path}: {e}")
    return None

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
    "即时策略":"RTS","都市":"Đô thị","历史":"Lịch sử","战争":"Chiến tranh",
    "海战":"Hải chiến","航海":"Hàng hải","桌游":"Board game",
    "战术竞技":"Battle Royale","刷宝":"Loot / Cày cuốc","废土":"Wasteland",
    "换装":"Thời trang","恋爱":"Hẹn hò","女性向":"Otome / Nữ tính",
    "单机":"Offline / Chơi đơn","足球":"Bóng đá","视觉小说":"Visual Novel",
    "家庭聚会":"Party Game","合成":"Ghép/Merge","竞技":"Cạnh tranh",
    "3D":"3D","像素":"Pixel","Roguelite":"Roguelite","暗黑":"Dark",
    "横版":"2D ngang","太空":"Vũ trụ","地牢":"Dungeon","探索":"Khám phá",
    "剧情":"Story-rich","文字":"Text/Story","经营":"Kinh doanh","益智":"Trí tuệ",
    "萌宠":"Cute Pet","钓鱼":"Câu cá","音游":"Rhythm game","闯关":"Platformer",
    "街机":"Arcade","异世界":"Isekai","乙女":"Otome","机甲":"Mecha",
    "第一人称":"FPS","西游":"Tây Du Ký","魔法":"Magic","种田":"Farming",
    "手绘":"Hand-drawn","类银河恶魔城":"Metroidvania","消除":"Match-3",
    "卡通":"Cartoon","篮球":"Basketball","国战":"Nation War","修真":"Cultivation",
}
SKIP_TAGS = {
    '编辑推荐','近期下载飙升','多端互通','高画质','近期热门预约',
    '安心购','策略拉满','编辑精选','买断制','Steam移植','多平台','高自由度',
}
TESTTYPE_MAP = {
    "公测":("公测","Open Beta"),"上线":("上线","Onlive / Launch"),
    "试玩":("试玩","Demo"),"删档测试":("删档测试","Clear data Test"),
    "限量删档":("限量删档","Clear data Test (giới hạn)"),
    "限量删档测试":("限量删档测试","Clear data Test (giới hạn)"),
    "不限量不删档":("不限量不删档","Non-clear data Test (không giới hạn)"),
    "限量不删档测试":("限量不删档测试","Non-clear data Test (giới hạn)"),
    "删档计费测试":("删档计费测试","Paid Test xóa data"),
    "限量删档计费测试":("限量删档计费测试","Paid Test xóa data (giới hạn)"),
    "限量不删档计费":("限量不删档计费","Paid Test không xóa data (giới hạn)"),
    "不删档计费":("不删档计费","Paid Test không xóa data"),
    "不删档计费测试":("不删档计费测试","Paid Test không xóa data"),
    "不限量不删档计费":("不限量不删档计费","Paid Test không xóa data (không giới hạn)"),
    "计费删档内测":("计费删档内测","Paid Test nội bộ xóa data"),
    "删档内测":("删档内测","Test nội bộ xóa data"),
    "线下试玩会":("线下试玩会","Offline Playtest Event"),
    "新增版本":("新增版本","Cập nhật phiên bản mới"),
    "删档不计费测试":("删档不计费测试","Test xóa data không nạp tiền"),
    "限量计费删档":("限量计费删档","Giới hạn số lượng, có nạp tiền và xóa data"),
    "公测运营":("公测运营","Onlive / Launch"),
    "预约":("预约","Pre-register"),
}
TAPTAP_IDS = {
    "王者荣耀世界":"744415","异环-自由开放都市":"714119","三国：天下归心":"759941",
    "神泣：纷争":"839042","饥困荒野-饥荒：新家园":"194039","原神":"168332",
    "崩坏：星穹铁道":"225069","明日方舟":"158138","无限暖暖":"247283",
    "鸣潮":"234280","元气骑士":"35077","战双帕弥什":"162255",
    "鹅鸭杀":"202498","光遇":"135596","洛克王国：世界":"695501",
    "遗忘之海-记忆环游海洋开放世界":"755604","天堂2：盟约":"196349",
}

def translate_tags(tags, max_n=6):
    res, seen = [], set()
    for t in (tags or []):
        if t in SKIP_TAGS: continue
        vn = TAG_VI.get(t, t)
        if vn not in seen:
            seen.add(vn); res.append(vn)
        if len(res) >= max_n: break
    return res

def fetch_test_game(days_back=180, days_ahead=30):
    all_games = {}
    today = datetime.now(timezone.utc)
    dates = []
    for d in range(-days_back, days_ahead+1, 3):
        dt = today + timedelta(days=d)
        dates.append(dt.strftime('%Y-%m-%d'))

    print(f"  Fetching {len(dates)} dates via proxy...")
    for i, date_str in enumerate(dates):
        path = f"/gamecenter/api/test_game?date={date_str}&type_range=2&p=1"
        data = proxy_fetch(path)
        if not data or 'dates' not in data: continue
        for date, games in data['dates'].items():
            for g in games:
                gid = g.get('gameid')
                if not gid or gid in all_games: continue
                gd = g.get('game', {})
                all_games[gid] = {
                    'gamename': gd.get('gamename', ''),
                    'iconurl':  gd.get('iconurl', ''),
                    'testtype': g.get('testtype', '').strip(),
                    'testdate': g.get('testdate', date),
                    'companys': gd.get('companys', []),
                    'gameweb':  gd.get('gameweb', ''),
                }
        if (i+1) % 20 == 0:
            print(f"    [{i+1}/{len(dates)}] {len(all_games)} games")
        time.sleep(0.15)

    counts = {}
    for g in all_games.values():
        counts[g['testtype']] = counts.get(g['testtype'], 0) + 1
    print(f"  ✓ {len(all_games)} games | {dict(sorted(counts.items(),key=lambda x:-x[1])[:5])}")
    return list(all_games.values())

def fetch_tags():
    tags_map = {}
    for dr in [30, 90, 180, 365]:
        for p in [1, 2, 3]:
            path = f"/gamecenter/api/new_game_list?p={p}&ps=50&date_range={dr}&type_range=2"
            data = proxy_fetch(path)
            if not data: break
            for g in data:
                name = g.get('gamename', '')
                if name and name not in tags_map:
                    tags_map[name] = {
                        'gameplay':    g.get('gameplay', []),
                        'review_rate': str(g.get('review_rate', '')),
                        'review_num':  str(g.get('review_num', '')),
                        'gameweb':     g.get('gameweb', ''),
                        'format_time': g.get('format_time', '') or g.get('publishtime', ''),
                    }
            time.sleep(0.2)
    print(f"  ✓ Tags: {len(tags_map)} games")
    return tags_map

def fetch_rankings():
    results = {}
    for period, label in [(30,'rank30'),(90,'rank90'),(365,'rankyr')]:
        path = f"/gamecenter/api/new_game_list?p=1&ps=30&date_range={period}&type_range=2"
        results[label] = proxy_fetch(path) or []
        time.sleep(0.3)
    return results

def build_entry(g, tags_data, idx, is_rank=False):
    name = g.get('gamename', '')
    if not name: return None
    td = tags_data.get(name, {})
    tags = g.get('gameplay', []) or td.get('gameplay', [])
    tags_vn = translate_tags(tags)
    companys = g.get('companys', [])
    pub = next((c['name'] for c in companys if str(c.get('company_role_id',''))=='1'), '')
    dev = next((c['name'] for c in companys if str(c.get('company_role_id',''))=='2'), '') or pub
    tt = g.get('testtype', '').strip()
    status = TESTTYPE_MAP.get(tt, (tt, tt or 'Open Beta'))
    tt_id = TAPTAP_IDS.get(name, '')
    tt_url = f"https://www.taptap.cn/app/{tt_id}" if tt_id else \
             f"https://www.taptap.cn/search?q={urllib.parse.quote(name)}"
    pub_time = g.get('testdate', '') or td.get('format_time', '')
    return {
        'stt' if not is_rank else 'rank': str(idx+1),
        'name':         name,
        'name_en':      '',
        'icon_url':     g.get('iconurl', ''),
        'tags_cn':      ' / '.join(tags),
        'tags_vn':      tags_vn,
        'publisher':    pub,
        'developer':    dev,
        'testtype_cn':  status[0],
        'testtype_vn':  status[1],
        'score_16p':    td.get('review_rate', ''),
        'pub_time':     pub_time,
        'date_sort':    pub_time[:10] if len(pub_time) >= 10 else pub_time,
        'ios_id':       '',
        'ios_url':      '',
        'ios_rating':   '',
        'store_taptap': tt_url,
        'taptap_id':    tt_id,
        'Mainsite':     g.get('gameweb', '') or td.get('gameweb', ''),
    }

def main():
    print(f"🎮 fetch_all.py via Cloudflare proxy: {PROXY_URL[:40]}...")
    print(f"   {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")

    print("\n📡 test_game API (ALL statuses)...")
    test_games = fetch_test_game()

    print("\n📡 new_game_list (tags + scores)...")
    tags_data = fetch_tags()

    print("\n📡 Rankings...")
    rankings = fetch_rankings()

    test_games.sort(key=lambda g: g.get('testdate',''), reverse=True)

    newgames, seen = [], set()
    for i, g in enumerate(test_games):
        if i >= 200: break
        name = g.get('gamename', '')
        if not name or name in seen: continue
        seen.add(name)
        entry = build_entry(g, tags_data, len(newgames), False)
        if entry: newgames.append(entry)

    def build_ranks(raw):
        res = []
        for i, g in enumerate(raw[:30]):
            if not g.get('testtype'): g['testtype'] = '上线'
            entry = build_entry(g, tags_data.get(g.get('gamename',''),{}), i, True)
            if entry: res.append(entry)
        return res

    out = {
        'newgames': newgames,
        'rank30':   build_ranks(rankings['rank30']),
        'rank90':   build_ranks(rankings['rank90']),
        'rankyr':   build_ranks(rankings['rankyr']),
        'updated_at': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),
        'source': '16p.com via Cloudflare Worker proxy',
    }

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    counts = {}
    for g in newgames:
        s = g.get('testtype_vn','?')
        counts[s] = counts.get(s,0)+1

    print(f"\n✅ Saved {OUT}")
    print(f"   newgames={len(newgames)} | rank30={len(out['rank30'])}")
    print(f"   Statuses: {dict(sorted(counts.items(),key=lambda x:-x[1])[:5])}")

if __name__ == '__main__':
    main()
