#!/usr/bin/env python3
"""
build_html.py
Đọc live_data.json → inject vào index_template.html → xuất index.html
Nếu không có live_data.json thì giữ nguyên index_template.html
"""
import json, os, re
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(BASE, "index_template.html")
OUTPUT   = os.path.join(BASE, "index.html")
LIVE     = os.path.join(BASE, "live_data.json")

def esc(obj):
    if isinstance(obj, dict): return {k: esc(v) for k, v in obj.items()}
    if isinstance(obj, list): return [esc(i) for i in obj]
    if isinstance(obj, str): return obj.replace('\n', '\\n').replace('\r', '')
    return obj

def main():
    # Read template
    if not os.path.exists(TEMPLATE):
        # Fallback: copy index.html as template if template missing
        if os.path.exists(OUTPUT):
            import shutil
            shutil.copy(OUTPUT, TEMPLATE)
            print(f"  Created template from existing index.html")
        else:
            print("✗ No template found"); return

    with open(TEMPLATE, 'r', encoding='utf-8') as f:
        html = f.read()

    updated_at = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")

    # Inject live data if available
    if os.path.exists(LIVE):
        with open(LIVE, 'r', encoding='utf-8') as f:
            live = json.load(f)

        TAG_VI = {
            "角色扮演":"Nhập vai RPG","动作":"Action","策略":"Chiến thuật",
            "休闲":"Casual","冒险":"Phiêu lưu","卡牌":"Thẻ bài","回合":"Turn-based",
            "养成":"Nuôi dưỡng","放置":"Idle","SLG":"SLG","MMORPG":"MMORPG",
            "Roguelike":"Roguelike","开放世界":"Thế giới mở","多人联机":"Multiplayer",
            "二次元":"Anime/2D","模拟经营":"Kinh doanh","模拟":"Mô phỏng",
            "沙盒":"Sandbox","生存":"Sinh tồn","建造":"Xây dựng","收集":"Thu thập",
            "塔防":"Tower Defense","射击":"Bắn súng","三国":"Tam Quốc",
            "武侠":"Võ hiệp","修仙":"Tu tiên","末日":"Tận thế","科幻":"Sci-fi",
            "独立游戏":"Indie","抓宠":"Bắt pet","自走棋":"Auto Chess",
            "搜打撤":"Extraction Shooter","割草":"Hack & Slash","MOBA":"MOBA",
            "MMO":"MMO","动漫改编":"Chuyển thể anime","视觉小说":"Visual Novel",
            "女性向":"Nữ tính","换装":"Thay trang phục","钓鱼":"Câu cá",
            "航海":"Hàng hải","3D":"3D","农场模拟":"Nông trại","体育":"Thể thao",
        }
        SKIP = {'编辑推荐','近期下载飙升','多端互通','高自由度','多平台',
                '高画质','近期热门预约','安心购','策略拉满'}

        def translate_tags(tags_list, n=5):
            res, seen = [], set()
            for t in (tags_list or []):
                if t in SKIP: continue
                vn = TAG_VI.get(t, t)
                if vn not in seen:
                    seen.add(vn); res.append(vn)
                if len(res) >= n: break
            return res

        def is_hl(tags):
            tl = ' '.join(tags).lower()
            return any(k in tl for k in ['slg','mmorpg','cbg','casual','turn','射击','塔防'])

        import urllib.parse
        TAPTAP_IDS = {
            "王者荣耀世界":"744415","异环-自由开放都市":"714119",
            "三国：天下归心":"759941","神泣：纷争":"839042",
            "饥困荒野-饥荒：新家园":"194039","原神":"168332",
            "崩坏：星穹铁道":"225069","明日方舟":"158138",
            "无限暖暖":"247283","鸣潮":"234280","元气骑士":"35077",
            "战双帕弥什":"162255","鹅鸭杀":"202498","光遇":"135596",
        }

        def tt_url(name):
            if name in TAPTAP_IDS:
                return f"https://www.taptap.cn/app/{TAPTAP_IDS[name]}"
            return f"https://www.taptap.cn/search?q={urllib.parse.quote(name)}"

        def build_game(g, is_rank=False):
            tags = (g.get('tags_cn') or '').split(' / ')
            tags = [t.strip() for t in tags if t.strip()]
            tags_vn = translate_tags(tags)
            ios_id  = g.get('ios_id') or g.get('appStoreId', '')
            ios_url = g.get('ios_url') or (f"https://apps.apple.com/cn/app/id{ios_id}" if ios_id and ios_id != '0' else '')
            name = g.get('name', '')
            base = {
                "Tên gốc": name,
                "Tên tiếng Trung (nếu khác)": "",
                "Tên tiếng Anh (nếu khác)": "",
                "Thể loại": tags[0] if tags else '',
                "Trạng thái phát hành": "公测运营" if is_rank else "公测",
                "Trạng thái (Tiếng Việt)": "Open Beta / Đang vận hành" if is_rank else "Open Beta",
                "Khu vực phát hành": "Trung Quốc",
                "Developer": g.get('developer') or g.get('publisher', ''),
                "Developer EN": g.get('developer') or g.get('publisher', ''),
                "Quốc gia/ Vùng lãnh thổ": "Trung Quốc",
                "Năm thành lập": "", "Niêm yết 上市": "",
                "Core Gameplay": ' / '.join(tags),
                "Core Gameplay VN": '\\n'.join(f'• {t}' for t in tags_vn),
                "Highlight": "⭐ HIGHLIGHT" if is_hl(tags) else "",
                "Mainsite": "", "AppStore": ios_url, "GooglePlay": "",
                "Store CN": f"TapTap: {tt_url(name)}",
                "ios_id": ios_id, "taptap_id": TAPTAP_IDS.get(name,''),
                "icon_url": g.get('icon') or g.get('icon_url',''),
                "score_16p": str(g.get('score_16p','')),
                "reviews_16p": str(g.get('reviews_16p','')),
            }
            if is_rank:
                base["Hạng"] = str(g.get('rank',''))
                base["Thời gian"] = ""
            else:
                base["STT"] = str(g.get('stt', ''))
                base["Thời gian"] = str(g.get('pub_time','') or g.get('pubTime',''))
            return base

        new_raw = {
            "newgames": [build_game(g, False) for g in live.get('newgames', [])],
            "bxh_30":   [build_game(g, True)  for g in live.get('rank30', [])],
            "bxh_90":   [build_game(g, True)  for g in live.get('rank90', [])],
            "bxh_year": [build_game(g, True)  for g in live.get('rankyr', [])],
        }

        data_js = json.dumps(esc(new_raw), ensure_ascii=False)
        assert '\n' not in data_js.replace('\\n',''), "newline leak!"
        html = re.sub(r'const RAW=\{.*?\};', f'const RAW={data_js};', html, count=1, flags=re.DOTALL)
        print(f"  ✓ Injected live data: {len(new_raw['newgames'])} newgames, {len(new_raw['bxh_30'])} rank30")
    else:
        print("  ⚠ No live_data.json — using template data as-is")

    # Update timestamp
    html = re.sub(
        r'(id="last-updated">)[^<]*(<)',
        f'\\g<1>{updated_at}\\g<2>',
        html
    )
    # Also replace placeholder
    html = html.replace('__UPDATED_AT__', updated_at)

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✓ Built index.html ({len(html):,} bytes) — {updated_at}")

if __name__ == '__main__':
    main()
