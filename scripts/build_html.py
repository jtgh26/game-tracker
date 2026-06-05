#!/usr/bin/env python3
"""
build_html.py
Đọc live_data.json → translate tags → inject vào index_template.html → xuất index.html
"""
import json, os, re
from datetime import datetime, timezone

BASE     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(BASE, "index_template.html")
OUTPUT   = os.path.join(BASE, "index.html")
LIVE     = os.path.join(BASE, "live_data.json")

# ── Translation tables ───────────────────────────────────────────────────────
TAG_VI = {
    "角色扮演":"RPG","动作":"Hành động","策略":"Chiến thuật","休闲":"Casual",
    "冒险":"Phiêu lưu","卡牌":"Thẻ bài","回合":"Turn-based","养成":"Nuôi dưỡng",
    "放置":"Idle / AFK","SLG":"SLG","MMORPG":"MMORPG","Roguelike":"Roguelike",
    "开放世界":"Open World","多人联机":"Multiplayer","二次元":"ACG / Anime",
    "模拟经营":"Kinh doanh","模拟":"Mô phỏng","沙盒":"Sandbox","生存":"Sinh tồn",
    "建造":"Xây dựng","收集":"Thu thập","解谜":"Giải đố","塔防":"Tower Defense",
    "射击":"Bắn súng","格斗":"Đối kháng","三国":"Tam Quốc","武侠":"Võ hiệp",
    "修仙":"Tu tiên","中国风":"Phong cách TQ","末日":"Tận thế","科幻":"Sci-fi",
    "独立游戏":"Indie","抓宠":"Bắt pet","自走棋":"Auto Chess",
    "搜打撤":"Loot & Extract","割草":"Hack & Slash","MOBA":"MOBA","MMO":"MMO",
    "动漫改编":"Chuyển thể anime","体育":"Thể thao","即时策略":"RTS",
    "经营":"Kinh doanh","多结局":"Đa kết thúc","视觉小说":"Visual Novel",
    "女性向":"Dành cho nữ","换装":"Thay trang phục","钓鱼":"Câu cá","航海":"Hàng hải",
    "3D":"3D","历史":"Lịch sử","战争":"Chiến tranh","像素":"Pixel",
    "Roguelite":"Roguelite","暗黑":"Dark","萌宠":"Cute Pet","文字":"Text/Story",
    "单机":"Single-player","都市":"Đô thị","废土":"Hậu tận thế","家庭聚会":"Party",
    "桌游":"Board game","竞技":"Cạnh tranh","足球":"Bóng đá","刷宝":"Loot/Grind",
    "高自由度":"Tự do cao","多平台":"Đa nền tảng","战术博弈":"Chiến thuật",
    "沙盘":"Sa bàn","第一人称":"Góc nhìn thứ nhất","极致视听享受":"Âm thanh & đồ họa",
    "UE5":"UE5","恐怖惊悚":"Kinh dị","克苏鲁":"Cthulhu","社交":"Xã hội",
    "竖屏":"Màn hình dọc","弹幕":"Bullet hell","涂色":"Tô màu",
    "派对游戏":"Party game","异世界":"Isekai","温暖治愈":"Healing/Ấm áp",
    "合成":"Ghép/Merge","经典重现":"Classic revival","跑酷":"Parkour",
    "音乐":"Âm nhạc","益智":"Trí tuệ","烹饪":"Nấu ăn","探索":"Khám phá",
    "国漫":"Truyện tranh TQ","小说改编":"Chuyển thể tiểu thuyết",
    "多端互通":"Cross-platform","高画质":"Đồ họa cao","竞速":"Đua xe",
    "开荒":"Khai hoang","PVP":"PVP","PVE":"PVE","挂机":"AFK/Idle",
    "策略卡牌":"Thẻ bài chiến thuật","二次元卡牌":"Thẻ bài anime",
}

SKIP_TAGS = {
    '编辑推荐','近期下载飙升','多端互通','高画质','近期热门预约',
    '安心购','策略拉满','编辑精选','买断制','Steam移植',
    '近期下载','多平台','高自由度',
}

# Bảng dịch Thể loại theo file Excel "Tong_Hop_Du_Lieu_Van_Hanh_Game.xlsx"
GENRE_VI = {
    "MMO":"MMO", "MOBA":"MOBA", "Roguelike":"Roguelike", "Roguelite":"Roguelite",
    "SLG":"SLG", "二次元":"ACG / Anime", "休闲":"Casual", "体育":"Thể thao",
    "修仙":"Tu Tiên", "像素":"Pixel", "冒险":"Phiêu lưu", "动作":"Hành động",
    "即时策略":"RTS", "历史":"Lịch sử", "家庭聚会":"Party Game",
    "开放世界":"Open World", "抓宠":"Bắt pet", "搜打撤":"Loot & Extract",
    "放置":"Idle / AFK", "模拟":"Mô phỏng", "模拟经营":"Quản lý mô phỏng",
    "沙盒":"Sandbox", "策略":"Chiến thuật", "视觉小说":"Visual Novel",
    "角色扮演":"RPG", "钓鱼":"Câu cá", "高自由度":"Tự do cao",
    "MMORPG":"MMORPG", "卡牌":"Thẻ bài", "回合":"Turn-based",
    "养成":"Nuôi dưỡng", "塔防":"Tower Defense", "射击":"Bắn súng",
    "格斗":"Đối kháng", "三国":"Tam Quốc", "武侠":"Võ hiệp",
    "末日":"Tận thế", "科幻":"Sci-fi", "独立游戏":"Indie",
    "自走棋":"Auto Chess", "割草":"Hack & Slash", "战术博弈":"Chiến thuật đấu trí",
    "解谜":"Giải đố", "都市":"Đô thị", "3D":"3D", "中国风":"Phong cách TQ",
    "动漫改编":"Chuyển thể anime", "小说改编":"Chuyển thể tiểu thuyết",
    "经营":"Kinh doanh", "多结局":"Đa kết thúc", "合成":"Ghép/Merge",
    "温暖治愈":"Healing/Nhẹ nhàng", "竞技":"Cạnh tranh",
    "战争":"Chiến tranh","生存":"Sinh tồn","多人联机":"Multiplayer",
    "建造":"Xây dựng","收集":"Thu thập","剧情":"Story-rich",
    "克苏鲁":"Cthulhu","海战":"Hải chiến","航海":"Hàng hải",
    "桌游":"Board game","战术竞技":"Battle Royale","刷宝":"Loot / Cày cuốc",
    "废土":"Wasteland","农场模拟":"Nông trại","换装":"Thời trang",
    "恋爱":"Hẹn hò","女性向":"Otome / Nữ tính","单机":"Offline / Chơi đơn",
    "足球":"Bóng đá",
}

TAPTAP_IDS = {
    "王者荣耀世界":"744415","异环-自由开放都市":"714119","三国：天下归心":"759941",
    "神泣：纷争":"839042","饥困荒野-饥荒：新家园":"194039","原神":"168332",
    "崩坏：星穹铁道":"225069","明日方舟":"158138","无限暖暖":"247283",
    "鸣潮":"234280","元气骑士":"35077","战双帕弥什":"162255",
    "鹅鸭杀":"202498","光遇":"135596",
}

GAME_NAMES_EN = {
    "王者荣耀世界":"Honor of Kings World","异环-自由开放都市":"Anomaly Ring",
    "三国：天下归心":"Three Kingdoms: Unite the World","神泣：纷争":"Shenqi: Conflict",
    "肥鹅美食街":"Fat Goose Food Street","饥困荒野-饥荒：新家园":"Don't Starve Together Mobile",
    "驯龙之旅":"Dragon Journey","崩坏：因缘精灵-崩坏IP新作":"Honkai: Enchanted Elves",
    "遮天：帝路争锋":"Zhetian: Emperor's Road","七界梦谭":"Seven Realms Dream",
    "卡厄思梦境":"Caos Dream","新星足球世界":"New Star Soccer World",
    "遗忘之海-记忆环游海洋开放世界":"Forgotten Ocean",
    "斗罗大陆：诛邪传说":"Soul Land: Dragon Legend",
    "三国：百将牌":"Three Kingdoms: Hundred Generals","镭明闪击":"Radiant Strike",
    "东离剑游纪":"Thunderbolt Fantasy Mobile","灵魂潮汐2":"Aether Gazer 2",
    "旅人日记":"Traveler's Diary","斗破苍穹：斗帝之路":"Battle Through the Heavens",
    "闪耀吧！噜咪":"Shine! Lumi","曙光纪元":"Dawn Era","蛮荒领主":"Savage Lord",
    "鹅鸭杀":"Goose Goose Duck","元气骑士":"Soul Knight",
    "战双帕弥什":"Punishing: Gray Raven","原神":"Genshin Impact",
    "无限暖暖":"Infinity Nikki","鸣潮":"Wuthering Waves",
    "崩坏：星穹铁道":"Honkai: Star Rail","明日方舟":"Arknights",
    "光遇":"Sky: Children of the Light","世界之光":"Light of the World",
    "天空岛传说":"Sky Island Legend","亿万光年":"Billion Light Years",
    "头号禁区":"Forbidden Zone No.1","高能探宝团":"Energy Explorer",
    "大航海时代：起源":"Age of Sail: Origins","归环-时间循环开放世界":"Cycle: Time Loop",
    "冲吧！帕克":"Go Go Park!","我的末日小队":"My Doomsday Squad",
    "宗师之上":"Above the Grandmaster","萌神契约":"Moe God Contract",
    "英雄之时":"Heroes of Time","迷失之径":"Lost Path",
    "我嘎嘎乱杀":"I Kill Everywhere","幻想少女公会":"Fantasy Girls Guild",
    "洛克王国：世界":"Rock Kingdom World","我的奶茶屋":"My Milk Tea Shop",
    "东煌纪":"East Huang Chronicles","哀鸿：城破十日记":"Lamenting: Ten Days",
}

DEV_EN = {
    "腾讯天美工作室":"Tencent TiMi Studio","腾讯天美工作室群":"Tencent TiMi Studio Group",
    "苏州幻塔":"Hotta Studio","苏州幻塔网络科技有限公司":"Hotta Studio",
    "上饶越昶网络科技有限公司":"Yuechang Network Tech","米哈游®":"miHoYo Co., Ltd.",
    "猪人工作室":"Pig Studios","咪咕互动娱乐有限公司":"Migu Interactive",
    "帝路争锋工作室":"Emperor's Road Studio","飞光阁工作室":"FeiGuangGe Studio",
    "bilibili游戏":"bilibili Games","反射狐工作室":"Reflex Fox Studio",
    "朝夕光年":"Morningstar (ByteDance)","北京瓜栗科技":"Beijing Guali Tech",
    "成都星启兴网络有限责任公司":"Chengdu Xingqixing Network",
    "厦门炉火网络科技有限公司":"Xiamen Luhuo Network","贪玩游戏":"TanWan Games",
    "37手游":"37Games","网易游戏":"NetEase Games","腾讯":"Tencent",
    "完美世界游戏":"Perfect World Games","西铭游戏":"Ximing Games",
    "广州灵犀互动娱乐有限公司":"Linxi Interactive","浩凡游戏":"Haofan Games",
    "HK HORTOR TECHNOLOGY LIMITED":"HORTOR TECHNOLOGY (HK)",
    "Zhejiang UmarkNetwork Technology Co.,Ltd":"Zhejiang UmarkNetwork",
    "Shenzhen Tencent Tianyou Technology Ltd":"Tencent Tianyou Tech",
    "Shangrao Yuechang Network Technology Co., Ltd":"Yuechang Network Tech",
    "Shenzhen Qianhai Hongcheng Games Co.,Ltd":"Hongcheng Games",
    "世界之光工作室":"Light of World Studio","鱼小齐工作室":"Fish Xiaoqi Studio",
    "海气泡游戏":"Haiqipao Games","零创游戏":"Lingchuang Games",
    "勾陈一工作室":"Gouchen Yi Studio","大千互娱":"Daqian Interactive",
    "苏州茉莉":"Suzhou Moli Games","灰阶映射工作室":"Grayscale Mapping Studio",
    "雷霆游戏":"TaoTao (Thunder) Games","未知矩阵":"Unknown Matrix Studio",
    "烛月游戏":"Zhuyue Games","萨罗斯网络科技（深圳）有限公司":"Saros Network Tech",
    "脑浆炸裂工作室":"Brain Explosion Studio","游一点意思工作室":"Youdian Yisi Studio",
    "6kwgame":"6kwgame","六阿哥游戏工作室":"Liu Ago Game Studio",
    "Gaggle Studios":"Gaggle Studios","ChillyRoom":"ChillyRoom Inc.",
    "Kuro Games":"Kuro Games (Kuro Technology)","37手游":"37Games",
    "游艺春秋":"Youyi Chunqiu","厦门游乐互动科技有限公司":"Xiamen Youle Interactive",
    "Gamersky Games":"Gamersky Games","小王个人工作室":"Xiao Wang Solo Studio",
    "游戏玄学":"Game Metaphysics Studio","瓜乒乓工作室":"Gua Pingpang Studio",
    "冠诺网络":"Guannuo Network","觉诺网络":"Juenuo Network",
}


LISTING = {
    "腾讯":"是 (HKEX: 0700.HK)",
    "腾讯天美工作室":"是 (HKEX: 0700.HK)",
    "腾讯天美工作室群":"是 (HKEX: 0700.HK)",
    "腾讯光子工作室群":"是 (HKEX: 0700.HK)",
    "Shenzhen Tencent Tianyou Technology Ltd":"是 (HKEX: 0700.HK)",
    "Tencent TiMi Studio":"是 (HKEX: 0700.HK)",
    "Tencent TiMi Studio Group":"是 (HKEX: 0700.HK)",
    "Tencent Tianyou Tech":"是 (HKEX: 0700.HK)",
    "网易游戏":"是 (NASDAQ: NTES / HKEX: 9999)",
    "网易":"是 (NASDAQ: NTES / HKEX: 9999)",
    "NetEase Games":"是 (NASDAQ: NTES / HKEX: 9999)",
    "米哈游®":"否 (Công ty tư nhân)",
    "miHoYo Co., Ltd.":"否 (Công ty tư nhân)",
    "bilibili游戏":"是 (NASDAQ: BILI / HKEX: 9626)",
    "bilibili Games":"是 (NASDAQ: BILI / HKEX: 9626)",
    "完美世界游戏":"是 (SZSE: 002624)",
    "Perfect World Games":"是 (SZSE: 002624)",
    "朝夕光年":"否 (ByteDance tư nhân)",
    "Morningstar (ByteDance)":"否 (ByteDance tư nhân)",
    "Kuro Games":"否 (Công ty tư nhân)",
    "Kuro Games (Kuro Technology)":"否 (Công ty tư nhân)",
    "37手游":"是 (SZSE: 002555)",
    "37Games":"是 (SZSE: 002555)",
    "Hypergryph Co., Ltd.":"否 (Công ty tư nhân)",
    "Lilith Games Co., Ltd.":"否 (Công ty tư nhân)",
    "ChillyRoom Inc.":"否 (Công ty tư nhân)",
    "Gaggle Studios":"否 (Công ty tư nhân)",
    "西山居":"是 (Kingsoft HKEX: 3888.HK)",
    "Seasun Games (Kingsoft)":"是 (Kingsoft HKEX: 3888.HK)",
    "Netmarble Corp.":"是 (KRX: 251270)",
    "Square Enix Co., Ltd.":"是 (TYO: 9684)",
    "中手游（CMG）":"是 (HKEX: 0302.HK)",
    "Charme Games (CMG)":"是 (HKEX: 0302.HK)",
    "巨人网络":"是 (SZSE: 002558)",
    "Giant Network Group":"是 (SZSE: 002558)",
    "TanWan Games":"否 (Công ty tư nhân)",
    "贪玩游戏":"否 (Công ty tư nhân)",
}

HL_TAGS = {'slg','mmorpg','cbg','casual','turn-based','shooting','extraction'}

def is_highlight(tags_list):
    tl = ' '.join(tags_list).lower()
    # CN tags check
    cn_hl = any(t in ' '.join(tags_list) for t in ['SLG','MMORPG','塔防','射击'])
    return cn_hl or any(k in tl for k in HL_TAGS)

def translate_tags(tags_list, max_n=6):
    res, seen = [], set()
    for t in (tags_list or []):
        if t in SKIP_TAGS: continue
        vn = TAG_VI.get(t, t)
        if vn not in seen:
            seen.add(vn); res.append(vn)
        if len(res) >= max_n: break
    return res

def fmt_time(t):
    if not t: return ''
    t = str(t).strip()
    if re.match(r'^\d{4}-\d{2}-\d{2}$', t):
        p = t.split('-'); return f"{p[2]}/{p[1]}/{p[0]}"
    elif re.match(r'^\d{2}-\d{2}$', t):
        return f"2026-{t}"  # MM-DD → keep as-is with year
    elif re.match(r'^\d{4}-\d{2}$', t):
        p = t.split('-'); return f"{p[1]}/{p[0]}"
    return t

def tt_url(name):
    if name in TAPTAP_IDS:
        return f"https://www.taptap.cn/app/{TAPTAP_IDS[name]}"
    import urllib.parse
    return f"https://www.taptap.cn/search?q={urllib.parse.quote(name)}"

def esc(obj):
    if isinstance(obj, dict): return {k: esc(v) for k, v in obj.items()}
    if isinstance(obj, list): return [esc(i) for i in obj]
    if isinstance(obj, str): return obj.replace('\n', '\\n').replace('\r', '')
    return obj

def build_game(g, is_rank=False, idx=0):
    name     = g.get('name','')
    tags_raw = [t.strip() for t in (g.get('tags_cn','') or '').split('/') if t.strip()]
    tags_vn  = translate_tags(tags_raw)
    genre_cn = tags_raw[0] if tags_raw else ''
    genre_vn = TAG_VI.get(genre_cn, genre_cn)

    dev_cn = g.get('developer','') or g.get('publisher','')
    dev_en = DEV_EN.get(dev_cn, dev_cn)

    ios_id  = g.get('ios_id','')
    ios_url = g.get('ios_url','') or (f"https://apps.apple.com/cn/app/id{ios_id}" if ios_id and ios_id != '0' else '')

    core_vn = '\\n'.join(f'• {t}' for t in tags_vn) if tags_vn else ''

    result = {
        "Tên gốc":                  name,
        "Tên tiếng Trung (nếu khác)": "",
        "Tên tiếng Anh (nếu khác)": GAME_NAMES_EN.get(name, ''),
        "Thể loại":                 genre_vn,
        "Trạng thái phát hành":     g.get('testtype_cn','公测'),
        "Trạng thái (Tiếng Việt)":  g.get('testtype_vn','Open Beta'),
        "Thời gian":                fmt_time(g.get('pub_time','')),
        "Khu vực phát hành":        "Trung Quốc",
        "Developer":                dev_cn,
        "Developer EN":             dev_en,
        "Quốc gia/ Vùng lãnh thổ": "Trung Quốc",
        "Năm thành lập":            "",
        "Niêm yết 上市":             LISTING.get(dev_cn, LISTING.get(dev_en, "")),
        "Core Gameplay":            g.get('tags_cn',''),
        "Core Gameplay VN":         core_vn,
        "Highlight":                "⭐ HIGHLIGHT" if is_highlight(tags_raw) else "",
        "Mainsite":                 "",
        "AppStore":                 ios_url,
        "GooglePlay":               "",
        "Store CN":                 f"TapTap: {tt_url(name)}",
        "ios_id":                   ios_id,
        "taptap_id":                TAPTAP_IDS.get(name,''),
        "icon_url":                 g.get('icon_url',''),
        "score_16p":                str(g.get('score_16p','')),
        "reviews_16p":              str(g.get('reviews_16p','')),
    }
    if is_rank:
        result["Hạng"] = str(g.get('rank', idx+1))
    else:
        result["STT"] = str(g.get('stt', idx+1))

    return result

def main():
    # Read template
    if not os.path.exists(TEMPLATE):
        if os.path.exists(OUTPUT):
            import shutil; shutil.copy(OUTPUT, TEMPLATE)
            print("  Created template from index.html")
        else:
            print("✗ No template found"); return

    with open(TEMPLATE, 'r', encoding='utf-8') as f:
        html = f.read()

    updated_at = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")

    if os.path.exists(LIVE):
        with open(LIVE, 'r', encoding='utf-8') as f:
            live = json.load(f)

        new_raw = {
            "newgames": [build_game(g, False, i) for i,g in enumerate(live.get('newgames',[]))],
            "bxh_30":   [build_game(g, True,  i) for i,g in enumerate(live.get('rank30',[]))],
            "bxh_90":   [build_game(g, True,  i) for i,g in enumerate(live.get('rank90',[]))],
            "bxh_year": [build_game(g, True,  i) for i,g in enumerate(live.get('rankyr',[]))],
        }

        data_js = json.dumps(esc(new_raw), ensure_ascii=False)
        assert '\n' not in data_js.replace('\\n',''), "newline leak!"

        html = re.sub(r'const RAW=\{.*?\};', f'const RAW={data_js};', html, count=1, flags=re.DOTALL)

        # Stats
        ng  = new_raw['newgames']
        hl  = sum(1 for g in ng if g.get('Highlight'))
        print(f"  ✓ Built: {len(ng)} newgames, {hl} highlights")
        print(f"  Sample: {ng[0]['Tên gốc']} | {ng[0]['Thể loại']} | {ng[0]['Trạng thái (Tiếng Việt)']} | {ng[0]['Thời gian']}")
    else:
        print("  ⚠ No live_data.json")

    # Update timestamp
    html = re.sub(r'(id="last-updated">)[^<]*(<)', f'\\g<1>{updated_at}\\g<2>', html)
    html = html.replace('__UPDATED_AT__', updated_at)

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✓ index.html built ({len(html):,} bytes) — {updated_at}")

if __name__ == '__main__':
    main()
