#!/usr/bin/env python3
"""
fetch_all.py — Daily auto-fetch từ 16p.com + iTunes API
Thay thế fetch_taptap.py, chạy qua GitHub Actions mỗi ngày 8:00 sáng GMT+7
"""

import json, time, os, urllib.request, urllib.parse
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(BASE, "live_data.json")

HEADERS_16P = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Referer": "https://www.16p.com/",
    "Accept": "application/json",
}

TAG_VI = {
    "角色扮演":"Nhập vai RPG","动作":"Action","策略":"Chiến thuật","休闲":"Casual",
    "冒险":"Phiêu lưu","卡牌":"Thẻ bài","回合":"Turn-based","养成":"Nuôi dưỡng",
    "放置":"Idle","SLG":"SLG","MMORPG":"MMORPG","Roguelike":"Roguelike",
    "开放世界":"Thế giới mở","多人联机":"Multiplayer","二次元":"Anime/2D",
    "模拟经营":"Kinh doanh mô phỏng","模拟":"Mô phỏng","沙盒":"Sandbox",
    "生存":"Sinh tồn","建造":"Xây dựng","收集":"Thu thập","解谜":"Giải đố",
    "剧情":"Cốt truyện","塔防":"Tower Defense","射击":"Bắn súng","格斗":"Đối kháng",
    "三国":"Tam Quốc","武侠":"Võ hiệp","修仙":"Tu tiên","中国风":"Phong cách TQ",
    "末日":"Tận thế","科幻":"Khoa học viễn tưởng","买断制":"Mua một lần",
    "独立游戏":"Indie","抓宠":"Bắt pet","自走棋":"Auto Chess",
    "搜打撤":"Extraction Shooter","割草":"Hack & Slash","像素":"Pixel",
    "MOBA":"MOBA","MMO":"MMO","动漫改编":"Chuyển thể anime",
    "国漫":"Truyện tranh TQ","Steam移植":"Port Steam","视觉小说":"Visual Novel",
    "恐怖惊悚":"Kinh dị","女性向":"Dành cho nữ","换装":"Thay trang phục",
    "钓鱼":"Câu cá","航海":"Hàng hải","太空":"Vũ trụ","沙盘":"Sa bàn",
    "3D":"3D","农场模拟":"Nông trại mô phỏng","体育":"Thể thao",
}
SKIP_TAGS = {'编辑推荐','近期下载飙升','多端互通','高自由度','多平台','高画质',
             '近期热门预约','安心购','策略拉满','编辑精选'}

def translate_tags(tags_list, max_tags=5):
    result, seen = [], set()
    for tag in tags_list:
        if tag in SKIP_TAGS: continue
        vn = TAG_VI.get(tag, tag)
        if vn not in seen:
            seen.add(vn)
            result.append(vn)
        if len(result) >= max_tags: break
    return result

def fetch_json(url, headers=None, timeout=12):
    req = urllib.request.Request(url, headers=headers or HEADERS_16P)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode('utf-8'))
    except Exception as e:
        print(f"  ✗ {url[:80]}: {e}")
        return None

def fetch_16p_newgames(date_range=60, page_size=50):
    """Fetch new game list from 16p.com"""
    all_games = []
    seen = set()
    for p in [1, 2]:
        url = f"https://www.16p.com/gamecenter/api/new_game_list?p={p}&ps={page_size}&date_range={date_range}&type_range=2"
        data = fetch_json(url)
        if not data: break
        for g in data:
            if g['gameid'] not in seen:
                seen.add(g['gameid'])
                all_games.append(g)
        time.sleep(0.5)
    print(f"  16p newgames: {len(all_games)} games (date_range={date_range}d)")
    return all_games

def fetch_16p_rankings(date_range=30, page_size=30):
    """Fetch ranking list from 16p.com"""
    url = f"https://www.16p.com/gamecenter/api/new_game_list?p=1&ps={page_size}&date_range={date_range}&type_range=2"
    data = fetch_json(url)
    print(f"  16p rankings ({date_range}d): {len(data or [])} games")
    return data or []

def fetch_itunes(game_name, country='cn'):
    """Fetch app info from iTunes Search API"""
    q = urllib.parse.quote(game_name)
    url = f"https://itunes.apple.com/search?term={q}&country={country}&entity=software&limit=1"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "iTunes/12.11.0"})
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read().decode('utf-8'))
        results = data.get('results', [])
        if results:
            res = results[0]
            return {
                'appId':     str(res.get('trackId', '')),
                'appName':   res.get('trackName', ''),
                'developer': res.get('artistName', ''),
                'genre':     res.get('primaryGenreName', ''),
                'icon':      res.get('artworkUrl100', '').replace('100x100bb', '200x200bb'),
                'rating':    round(res.get('averageUserRating', 0), 1),
                'reviews':   res.get('userRatingCount', 0),
                'appUrl':    res.get('trackViewUrl', ''),
                'bundleId':  res.get('bundleId', ''),
            }
    except Exception as e:
        pass
    return None

def enrich_game(g, itunes_cache):
    """Enrich a 16p game with iTunes data"""
    name = g.get('gamename', '')
    pub  = next((c['name'] for c in g.get('companys',[]) if c.get('company_role_id')=='1'), g.get('gamepublisher',''))
    dev  = next((c['name'] for c in g.get('companys',[]) if c.get('company_role_id')=='2'), g.get('gamecompany',''))
    tags = g.get('gameplay', [])
    
    # iTunes lookup
    it = itunes_cache.get(name)
    if not it:
        it = fetch_itunes(name)
        itunes_cache[name] = it
        time.sleep(0.35)
    
    icon = (it['icon'] if it and it.get('icon') else '') or g.get('iconurl', '')
    ios_url = f"https://apps.apple.com/cn/app/id{it['appId']}" if it and it.get('appId') else ''
    taptap_url = f"https://www.taptap.cn/search?q={urllib.parse.quote(name)}"
    
    tags_vn = translate_tags(tags)
    
    # Map 16p testtype to Vietnamese status
    testtype_cn = g.get('testtype', '')
    TESTTYPE_MAP = {
        '公测': ('公测', 'Open Beta'),
        '上线': ('上线', 'Đã ra mắt'),
        '不删档测试': ('不删档测试', 'OBT (Giữ data)'),
        '删档测试': ('删档测试', 'CBT (Xóa data)'),
        '付费测试': ('付费测试', 'Paid Beta'),
        '技术测试': ('技术测试', 'Tech Test'),
        '限量测试': ('限量测试', 'Limited Test'),
        '预约': ('预约', 'Đặt trước'),
    }
    status_pair = TESTTYPE_MAP.get(testtype_cn, (testtype_cn, testtype_cn))

    return {
        'name':         name,
        'icon_url':     icon,
        'tags_cn':      ' / '.join(tags),
        'tags_vn':      tags_vn,
        'publisher':    pub,
        'developer':    dev or pub,
        'testtype_cn':  status_pair[0],
        'testtype_vn':  status_pair[1],
        'score_16p':    str(g.get('review_rate', '')),
        'reviews_16p':  str(g.get('review_num', '')),
        'pub_time':     g.get('format_time', '') or g.get('publishtime', ''),
        'ios_id':       it['appId'] if it else '',
        'ios_url':      ios_url,
        'ios_rating':   str(it['rating']) if it else '',
        'ios_reviews':  str(it['reviews']) if it else '',
        'taptap_url':   taptap_url,
        'fetched_at':   datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),
    }

def main():
    print("🎮 Starting daily fetch: 16p.com + iTunes")
    itunes_cache = {}
    
    # Load existing cache to avoid re-fetching
    if os.path.exists(OUT):
        try:
            with open(OUT,'r',encoding='utf-8') as f:
                existing = json.load(f)
            # Rebuild iTunes cache from existing data
            for dataset in ['newgames','rank30','rank90','rankyr']:
                for g in existing.get(dataset, []):
                    if g.get('ios_id') and g['ios_id'] != '0':
                        itunes_cache[g['name']] = {
                            'appId': g['ios_id'],
                            'icon':  g.get('icon_url',''),
                            'rating': float(g.get('ios_rating',0) or 0),
                            'reviews': int(g.get('ios_reviews',0) or 0),
                            'appUrl': g.get('ios_url',''),
                            'developer': g.get('developer',''),
                        }
            print(f"  Loaded {len(itunes_cache)} cached iTunes entries")
        except: pass

    # Fetch 16p data
    print("\n📡 Fetching 16p.com...")
    ng_raw  = fetch_16p_newgames(date_range=60)
    r30_raw = fetch_16p_rankings(date_range=30)
    r90_raw = fetch_16p_rankings(date_range=90)
    ryr_raw = fetch_16p_rankings(date_range=365)

    # Enrich with iTunes
    print(f"\n🍎 Enriching {len(ng_raw)+len(r30_raw)+len(r90_raw)+len(ryr_raw)} games with iTunes...")
    
    def process_list(raw_list, label):
        result = []
        for i, g in enumerate(raw_list):
            print(f"  [{i+1}/{len(raw_list)}] {g.get('gamename','')[:20]}")
            enriched = enrich_game(g, itunes_cache)
            result.append(enriched)
        print(f"  ✓ {label}: {len(result)} games enriched")
        return result

    out = {
        'newgames': process_list(ng_raw,  'newgames'),
        'rank30':   process_list(r30_raw, 'rank30'),
        'rank90':   process_list(r90_raw, 'rank90'),
        'rankyr':   process_list(ryr_raw, 'rankyr'),
        'updated_at': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),
        'source': '16p.com + iTunes API',
    }

    with open(OUT,'w',encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Saved to {OUT}")
    print(f"   newgames={len(out['newgames'])}, rank30={len(out['rank30'])}, rank90={len(out['rank90'])}, rankyr={len(out['rankyr'])}")

if __name__ == '__main__':
    main()
