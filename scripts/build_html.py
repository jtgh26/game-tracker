import re

try:
    from pypinyin import lazy_pinyin
    HAS_PYPINYIN = True
except ImportError:
    HAS_PYPINYIN = False

# ── Auto EN name generator (free, no API) ──────────────────────────────────
_EN_KEYWORDS = {
    "联盟3":"Alliance 3","联盟":"Alliance","传说":"Legend","世界之光":"Light of the World",
    "开放世界":"Open World","修仙":"Cultivation","修真":"Cultivation",
    "世界":"World","英雄":"Hero","战争":"War","王者":"King","荣耀":"Glory",
    "龙":"Dragon","王国":"Kingdom","冒险":"Adventure","骑士":"Knight",
    "守望":"Overwatch","弓箭":"Arrow","侠":"Hero","仙途":"Immortal Path",
    "召唤师":"Summoner","纷争":"Strife","疯狂":"Crazy","法宝":"Treasure",
    "漫漫":"Endless","时空":"Time Space","猎人":"Hunter","猎手":"Hunter",
    "觉醒":"Awakening","彩虹":"Rainbow","攻势":"Siege","地牢":"Dungeon",
    "蛙蛙":"Frog","豹豹":"Leopard","蛙":"Frog","树屋":"Treehouse",
    "模拟器":"Simulator","野生":"Wild","狮子":"Lion","塔防":"Tower Defense",
    "对战":"Battle","魔兽":"Warcraft","放置":"Idle","史莱姆":"Slime",
    "城堡":"Castle","合并":"Merge","萌龙":"Dragon","岛":"Island",
    "失控":"Uncontrolled","进化":"Evolution","末日":"Doomsday",
    "开炮":"Cannon","天堂":"Lineage","盟约":"Covenant","六号":"Six",
    "钢琴":"Piano","小镇":"Town","出租车":"Taxi","司机":"Driver",
    "高手":"Master","精灵":"Sprite","超级":"Super","洞洞":"Hole",
    "月相":"Moon Phase","计划":"Project","终极":"Ultimate","渊":"Abyss",
    "王座":"Throne","纪元":"Era","曙光":"Dawn","蛮荒":"Savage",
    "领主":"Lord","月":"Moon","星":"Star","梦":"Dream","神":"God",
    "魂":"Soul","光":"Light","影":"Shadow","火":"Fire","剑":"Sword",
    "帝":"Emperor","崛起":"Rise","守护":"Guardian","永恒":"Eternal",
    "无敌":"Invincible","金":"Gold","银":"Silver","黑":"Black","白":"White",
    "曙光":"Dawn","风之国":"Wind Nation","亿万":"Billions","光年":"Light Year",
    "飘流":"Drifting","幻境":"Fantasy","新世界":"New World","方舟":"Ark",
    "方舟":"Ark","诡秘":"Mysterious","战场":"Battlefield",
    "峰":"Peak","界":"Realm","源":"Source",
    "的":"","·":"","之":"","与":"and",
}

def _auto_en_name(cn_name):
    if not cn_name: return ""
    sorted_kw = sorted(_EN_KEYWORDS.items(), key=lambda x: -len(x[0]))
    result = cn_name
    used = {}
    for cn, en in sorted_kw:
        if cn and cn in result:
            marker = f"«{len(used)}»"
            result = result.replace(cn, marker, 1)
            used[marker] = en
    parts = []
    tokens = re.split(r"(«\d+»)", result)
    for token in tokens:
        token = token.strip()
        if not token: continue
        if token in used:
            v = used[token]
            if v: parts.append(v)
        else:
            cn_chars = re.sub(r"[^\u4e00-\u9fff]", "", token)
            alphanums = re.sub(r"[\u4e00-\u9fff·：:！？,，。\-\s]", "", token).strip()
            if cn_chars:
                if HAS_PYPINYIN:
                    parts.append(" ".join(p.capitalize() for p in lazy_pinyin(cn_chars)))
                else:
                    parts.append(cn_chars)  # fallback: keep CN if no pypinyin
            if alphanums:
                parts.append(alphanums)
    en = " ".join(p for p in parts if p.strip())
    return re.sub(r"\s+", " ", en).strip()

#!/usr/bin/env python3
"""
build_html.py — SIMPLE injector
Đọc live_data.json → build RAW JS object → inject vào index_template.html → xuất index.html
KHÔNG rewrite bất kỳ logic nào — tất cả UI/JS đã nằm trong index_template.html
"""
import json, os, re, urllib.parse
from datetime import datetime, timezone

BASE     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(BASE, "index_template.html")
OUTPUT   = os.path.join(BASE, "index.html")
LIVE     = os.path.join(BASE, "live_data.json")

# ── Translation tables ────────────────────────────────────────────────────────
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
    "即时策略":"RTS","战术博弈":"Chiến thuật đấu trí","都市":"Đô thị",
    "历史":"Lịch sử","战争":"Chiến tranh","海战":"Hải chiến","航海":"Hàng hải",
    "桌游":"Board game","战术竞技":"Battle Royale","刷宝":"Loot / Cày cuốc",
    "废土":"Wasteland","农场模拟":"Nông trại","换装":"Thời trang",
    "恋爱":"Hẹn hò","女性向":"Otome / Nữ tính","单机":"Offline / Chơi đơn",
    "足球":"Bóng đá","多结局":"Đa kết thúc","视觉小说":"Visual Novel",
    "家庭聚会":"Party Game","合成":"Ghép/Merge","温暖治愈":"Healing/Ấm áp",
    "竞技":"Cạnh tranh","3D":"3D","像素":"Pixel","Roguelite":"Roguelite",
    "暗黑":"Dark",
    "PC游戏":"PC Game",
    "吉卜力画风":"Ghibli Art Style",
    "美漫风":"Marvel/Comic Style",
    "Steam高分神作":"Steam Masterpiece",
    "up主推荐":"Creator's Pick",
    "电影质感":"Cinematic",
    "奥特曼":"Ultraman IP",
    "剧情党狂喜":"Story Lover",
    "沉浸式体验":"Immersive",
    "娱乐":"Entertainment",
    "独家游戏":"Exclusive",
    "消除":"Match-3",
    "卡通":"Cartoon",
    "绝赞立绘":"Stunning Artwork",
    "日系":"Japanese Style",
    "篮球":"Basketball",
    "游戏":"Game",
    "国战":"Nation War",
    "仙侠":"Xianxia",
    "修仙":"Tu Tiên",
    "武侠":"Wuxia",
    "三国":"Tam Quốc",
    "回合制":"Turn-based",
    "策略RPG":"Strategy RPG","恐怖惊悚":"Kinh dị","克苏鲁":"Cthulhu","社交":"Xã hội",
    "横版":"2D ngang","太空":"Vũ trụ","地牢":"Dungeon","探索":"Khám phá",
    "剧情":"Story-rich","文字":"Text/Story","经营":"Kinh doanh","益智":"Trí tuệ",
    "萌宠":"Cute Pet","钓鱼":"Câu cá","音游":"Rhythm game","节奏":"Nhịp điệu",
    "闯关":"Platformer","街机":"Arcade","异世界":"Isekai","乙女":"Otome",
    "枪战":"Bắn súng","机甲":"Mecha","第一人称":"FPS","第三人称":"TPS",
    "西游":"Tây Du Ký","魔法":"Magic","种田":"Farming","手绘":"Hand-drawn",
    "温馨治愈":"Healing","解压":"Stress relief","小说改编":"Chuyển thể tiểu thuyết",
    "互动影像":"Interactive Film","类银河恶魔城":"Metroidvania",
    "资源管理":"Resource Mgmt","空间解谜":"Spatial Puzzle","烧脑":"Brain puzzle",
    "即时战斗":"Real-time Combat","装饰&装修":"Decoration","萌宠":"Cute Pet",
    "弹幕":"Bullet hell","异世界":"Isekai","经典重现":"Classic revival",
    "国漫":"Truyện tranh TQ","小说改编":"Chuyển thể tiểu thuyết",
    "高画质":"Đồ họa cao","竞速":"Đua xe","UE5":"UE5","PVP":"PVP","PVE":"PVE",
    "策略卡牌":"Thẻ bài chiến thuật","跑酷":"Parkour","音乐":"Âm nhạc",
    "益智":"Trí tuệ","烹饪":"Nấu ăn","探索":"Khám phá","试玩":"Demo",
    "经营":"Kinh doanh","模板":"Mô hình","沙漠":"Sa mạc","海洋":"Đại dương",
}
SKIP_TAGS = {
    '编辑推荐','近期下载飙升','多端互通','高画质','近期热门预约',
    '安心购','策略拉满','编辑精选','买断制','Steam移植','近期下载',
    '多平台','高自由度','极致视听享受','多端互通',
}
GENRE_VI = dict(TAG_VI)

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
    "光遇":"Sky: Children of the Light","洛克王国：世界":"Rock Kingdom World",
    "我的末日小队":"My Doomsday Squad","宗师之上":"Above the Grandmaster",
    "萌神契约":"Moe God Contract","英雄之时":"Heroes of Time",
    "迷失之径":"Lost Path","我嘎嘎乱杀":"I Kill Everywhere",
    "幻想少女公会":"Fantasy Girls Guild","三国志·战略版":"Three Kingdoms Tactics",
    "率土之滨":"Infinite Borders","蛋仔派对":"Egg Party",
    "第五人格":"Identity V","逆水寒手游":"Swords of Legends Online Mobile",
    "梦幻西游手游":"Fantasy Westward Journey Mobile","剑与远征：启程":"AFK Journey",
    "遮天世界":"Zhetian World","凡人修仙传：人界篇":"A Record of Mortal's Journey",
    "梦幻新诛仙：轻享":"New Fantasy Jade Dynasty Light","飘流幻境新世界":"Drifting Fantasy New World",
    "风之国世界":"Wind Nation World","亿万光年":"Billion Light Years",
    "世界之光":"Light of the World","头号禁区":"Forbidden Zone No.1",
    "高能探宝团":"Energy Explorer","大航海时代：起源":"Age of Sail: Origins",
    "归环-时间循环开放世界":"Cycle: Time Loop","时空猎人·觉醒":"Time Hunter: Awakening",
    "星绘友晴天-宇宙生活模拟新游":"Star Draw: Cosmic Life Sim",
    "时空猎人·觉醒":"Time Hunter: Awakening",
    "天堂2：盟约":"Lineage 2: Covenant","彩虹六号：攻势":"Rainbow Six: Siege Mobile",
    "守望联盟3":"Overwatch Alliance 3","江山北望":"Jiangshan Beiwang",
    "泰坦传说":"Titan Legend","荒无之下":"Under the Wasteland",
    "神宠大作战3":"Pet Battle 3","月相计划":"Moon Phase Project",
    "超级洞洞乐":"Super Hole Party",
    "钢琴小镇":"Piano Town",
    "出租车司机模拟器2026":"Taxi Driver Simulator 2026",
    "修真高手-开放世界修仙":"Cultivation Master: Open World",
    "合并萌龙岛":"Merge Dragon Island",
    "伊莫":"Yimo",
    "终极野生狮子模拟器3D":"Ultimate Wild Lion Simulator 3D",
    "塔防对战：魔兽大作战放置策略卡牌手游":"Tower Defense Battle: Warcraft",
    "史莱姆城堡":"Slime Castle",
    "力力普的工坊":"Lilipu's Workshop",
    "怨楼":"Grudge Tower",
    "童话师":"Fairy Tale Master",
    "地牢猎手6":"Dungeon Hunter 6",
    "我在猫村搞事业":"Business in Cat Village",
    "诡秘之主":"Lord of the Mysteries",
    "保卫加加村":"Defend Jiajia Village",
    "海域重启":"Sea Domain Restart",
    "排兵布阵":"Battle Formation",
    "失控进化":"Uncontrolled Evolution",
    "舞力全开：派对":"Just Dance: Party",
    "望月-中国都市开放世界":"Wangyue: China Urban Open World",
    "合合梦幻岛":"Merge Fantasy Island",
    "造梦西游之黎尤浩劫篇":"Dream Journey: Catastrophe Chapter",
    "守望联盟3":"Overwatch Alliance 3",
    "江山北望":"Gazing Northward",
    "泰坦传说":"Titan Legend",
    "打工吧！小精灵":"Work! Little Sprite",
    "荒无之下":"Under the Wasteland",
    "神宠大作战3":"Pet Battle Wars 3",
    "月相计划":"Moon Phase Project",
    "时空猎人·觉醒":"Time Hunter: Awakening",
    "天堂2：盟约":"Lineage 2: Covenant",
    "彩虹六号：攻势":"Rainbow Six: Siege Mobile",
    "全民游戏大亨2":"Game Tycoon 2",
    "借眼":"Borrowed Eyes",
    "龙渊王座":"Dragon Abyss Throne",
    "糟糕！我被女忍包围了！2":"Oh No! Surrounded by Kunoichi 2",
    "蛙蛙豹豹的树屋":"Frog & Leopard's Treehouse",
    "天空岛传说":"Sky Island Legend",
    "代号：深渊之歌":"Project: Abyss Song",
    "怪物惊魂夜":"Monster Fright Night",
    "星绘友晴天-宇宙生活模拟新游":"Star Draw: Cosmic Life Sim",
    "飘流幻境新世界":"Drifting Fantasy New World",
    "风之国世界":"Wind Nation World",
}

DEV_EN = {
    "腾讯天美工作室":"Tencent TiMi Studio","腾讯天美工作室群":"Tencent TiMi Studio Group",
    "苏州幻塔":"Hotta Studio","苏州幻塔网络科技有限公司":"Hotta Studio",
    "上饶越昶网络科技有限公司":"Yuechang Network Tech",
    "米哈游®":"miHoYo Co., Ltd.","腾讯":"Tencent","网易游戏":"NetEase Games",
    "bilibili游戏":"bilibili Games","完美世界游戏":"Perfect World Games",
    "朝夕光年":"Morningstar (ByteDance)","37手游":"37Games",
    "Kuro Games":"Kuro Games","ChillyRoom":"ChillyRoom Inc.",
    "Gaggle Studios":"Gaggle Studios","贪玩游戏":"TanWan Games",
    "飞光阁工作室":"FeiGuangGe Studio","反射狐工作室":"Reflex Fox Studio",
    "猪人工作室":"Pig Studios","咪咕互动娱乐有限公司":"Migu Interactive",
}

LISTING = {
    "腾讯":"是 (HKEX: 0700.HK)","腾讯天美工作室":"是 (HKEX: 0700.HK)",
    "腾讯天美工作室群":"是 (HKEX: 0700.HK)","Tencent TiMi Studio":"是 (HKEX: 0700.HK)",
    "Shenzhen Tencent Tianyou Technology Ltd":"是 (HKEX: 0700.HK)",
    "网易游戏":"是 (NASDAQ: NTES / HKEX: 9999)","NetEase Games":"是 (NASDAQ: NTES / HKEX: 9999)",
    "米哈游®":"否 (Công ty tư nhân)","miHoYo Co., Ltd.":"否 (Công ty tư nhân)",
    "bilibili游戏":"是 (NASDAQ: BILI / HKEX: 9626)","bilibili Games":"是 (NASDAQ: BILI / HKEX: 9626)",
    "完美世界游戏":"是 (SZSE: 002624)","Perfect World Games":"是 (SZSE: 002624)",
    "朝夕光年":"否 (ByteDance tư nhân)","Kuro Games":"否 (Công ty tư nhân)",
    "37手游":"是 (SZSE: 002555)","37Games":"是 (SZSE: 002555)",
}

IP_MAP = {
    "王者荣耀世界":"Honor of Kings","三国：天下归心":"Tam Quốc",
    "三国：百将牌":"Tam Quốc","三国志·战略版":"Tam Quốc",
    "斗罗大陆：诛邪传说":"Đấu La Đại Lục","斗破苍穹：斗帝之路":"Đấu Phá Thương Khung",
    "东离剑游纪":"Thunderbolt Fantasy","凡人修仙传：人界篇":"Phàm Nhân Tu Tiên",
    "梦幻新诛仙：轻享":"Tru Tiên","梦幻西游手游":"Mộng Huyễn Tây Du",
    "遮天：帝路争锋":"Già Thiên","崩坏：因缘精灵-崩坏IP新作":"Honkai",
    "崩坏：星穹铁道":"Honkai","原神":"Genshin Impact","饥困荒野-饥荒：新家园":"Don't Starve",
    "洛克王国：世界":"Lạc Khắc Vương Quốc","光遇":"Sky","明日方舟":"Arknights",
    "无限暖暖":"Nikki","鹅鸭杀":"Goose Goose Duck","天堂2：盟约":"Lineage 2",
    "彩虹六号：攻势":"Rainbow Six","武林外传：十年之约":"Võ Lâm Ngoại Truyện",
    "守望联盟3":"Overwatch",
}

TAPTAP_IDS = {
    "王者荣耀世界":"744415","异环-自由开放都市":"714119","三国：天下归心":"759941",
    "神泣：纷争":"839042","饥困荒野-饥荒：新家园":"194039","原神":"168332",
    "崩坏：星穹铁道":"225069","明日方舟":"158138","无限暖暖":"247283",
    "鸣潮":"234280","元气骑士":"35077","战双帕弥什":"162255",
    "鹅鸭杀":"202498","光遇":"135596","洛克王国：世界":"695501",
    "遗忘之海-记忆环游海洋开放世界":"755604","天堂2：盟约":"196349",
    "彩虹六号：攻势":"756234",
}

MAINSITES = {
    "王者荣耀世界":"https://pvp.qq.com","原神":"https://ys.mihoyo.com",
    "崩坏：星穹铁道":"https://sr.mihoyo.com","明日方舟":"https://ak.hypergryph.com",
    "无限暖暖":"https://infinitynikki.infoldgames.com","鸣潮":"https://wutheringwaves.kurogames.com",
    "光遇":"https://thatskygame.com","元气骑士":"https://chillyroom.com",
    "鹅鸭杀":"https://www.goose-goose-duck.com","饥困荒野-饥荒：新家园":"https://dontstarve.qq.com",
    "异环-自由开放都市":"https://huantaworld.com","三国：天下归心":"https://sgzly.qq.com",
    "神泣：纷争":"https://shenqi.umark.com","逆水寒手游":"https://nsh.163.com",
    "蛋仔派对":"https://danzai.163.com","第五人格":"https://dwrg.163.com",
    "梦幻西游手游":"https://mhxy.163.com","率土之滨":"https://ltsb.163.com",
}

def translate_tags(tags_list, max_n=6):
    res, seen = [], set()
    for t in (tags_list or []):
        if t in SKIP_TAGS: continue
        vn = TAG_VI.get(t, t)
        if vn not in seen:
            seen.add(vn); res.append(vn)
        if len(res) >= max_n: break
    return res

def fmt_date(t):
    if not t: return ''
    t = str(t).strip()
    if re.match(r'^\d{4}-\d{2}-\d{2}$', t): return t
    if re.match(r'^\d{2}/\d{2}/\d{4}$', t):
        p=t.split('/'); return f"{p[2]}-{p[1]}-{p[0]}"
    if re.match(r'^\d{2}/\d{4}$', t):
        p=t.split('/'); return f"{p[1]}-{p[0]}"
    if re.match(r'^\d{4}-\d{2}$', t): return t
    if re.match(r'^\d{4}$', t): return t
    return t

def esc(obj):
    if isinstance(obj, dict): return {k:esc(v) for k,v in obj.items()}
    if isinstance(obj, list): return [esc(i) for i in obj]
    if isinstance(obj, str): return obj.replace('\n','\\n').replace('\r','')
    return obj

def build_game(g, idx, is_rank=False):
    name    = g.get('name','')
    tags    = [t.strip() for t in (g.get('tags_cn','') or '').split('/') if t.strip()]
    # If tags_cn empty, use tags_vn from live_data (already translated list)
    live_tags_vn = g.get('tags_vn', [])
    if isinstance(live_tags_vn, str):
        live_tags_vn = [t.replace('•','').strip() for t in live_tags_vn.split('\\n') if t.strip()]
    # If no tags from 16p, try iTunes genre as fallback
    if not tags:
        itunes_genre = g.get('itunes_genre','')
        ITUNES_MAP = {
            'Role Playing':['角色扮演'],'Action':['动作'],'Strategy':['策略'],
            'Casual':['休闲'],'Puzzle':['解谜'],'Adventure':['冒险'],
            'Simulation':['模拟'],'Sports':['体育'],'Racing':['竞速'],
            'Card':['卡牌'],'Music':['音乐'],'Entertainment':[],
        }
        for k,v in ITUNES_MAP.items():
            if k.lower() in itunes_genre.lower() and v:
                tags = v; break
    tags_vn = translate_tags(tags)
    # When tags_cn is empty, use tags_vn from live_data directly
    if not tags_vn and live_tags_vn:
        tags_vn = [t for t in live_tags_vn if not re.search(r'[\u4e00-\u9fff]', t)]
    genre_cn = tags[0] if tags else ''
    if not genre_cn and tags_vn:
        genre_cn = ''  # No CN genre available
    genre_vn = GENRE_VI.get(genre_cn, genre_cn)
    genre_bi = f"{genre_cn} / {genre_vn}" if genre_cn and genre_vn != genre_cn else (genre_vn or genre_cn)

    dev_cn  = g.get('developer','') or g.get('publisher','')
    dev_en  = DEV_EN.get(dev_cn, dev_cn)
    listing = LISTING.get(dev_cn, LISTING.get(dev_en, ''))

    ios_id  = g.get('ios_id','')
    ios_url = (g.get('ios_url','') or (f"https://apps.apple.com/cn/app/id{ios_id}" if ios_id else ''))
    if ios_url and '/app/id' in ios_url and '/cn/' not in ios_url:
        ios_url = ios_url.replace('/app/id', '/cn/app/id')

    tt_id   = TAPTAP_IDS.get(name,'') or g.get('taptap_id','') or ''
    tt_url  = f"https://www.taptap.cn/app/{tt_id}" if tt_id else \
              f"https://www.taptap.cn/search?q={urllib.parse.quote(name)}"

    mainsite = MAINSITES.get(name,'') or g.get('Mainsite','')

    pub_time = fmt_date(g.get('pub_time','') or g.get('testdate',''))
    status_cn = g.get('testtype_cn','公测') or '公测'
    status_vn = g.get('testtype_vn','Open Beta') or 'Open Beta'

    result = {
        "Tên gốc":                  name,
        "Tên tiếng Trung (nếu khác)":"",
        "Tên tiếng Anh (nếu khác)": GAME_NAMES_EN.get(name,'') or g.get('name_en','') or _auto_en_name(name),
        "Thể loại":                 genre_bi,
        "Trạng thái phát hành":     f"{status_cn} / {status_vn}",
        "Trạng thái (Tiếng Việt)":  status_vn,
        "Thời gian":                pub_time,
        "date_sort":                pub_time[:10] if len(pub_time)>=10 else pub_time,
        "Khu vực phát hành":        "Trung Quốc",
        "Developer":                dev_cn,
        "Developer EN":             dev_en,
        "Quốc gia/ Vùng lãnh thổ": "Trung Quốc",
        "Năm thành lập":            "",
        "Niêm yết 上市":             listing,
        "Core Gameplay":            ' / '.join(tags),
        "Core Gameplay VN":         '\\n'.join(f'• {t}' for t in (tags_vn or live_tags_vn)),
        "Highlight":                "⭐ HIGHLIGHT" if isHL(genre_bi) else "",
        "IP":                       IP_MAP.get(name,''),
        "Mainsite":                 mainsite,
        "AppStore":                 ios_url,
        "GooglePlay":               "",
        "Store CN":                 f"TapTap: {tt_url}",
        "ios_id":                   ios_id,
        "taptap_id":                tt_id,
        "store_taptap":             tt_url,
        "store_bilibili":           "",
        "store_hygb":               "",
        "icon_url":                 g.get('icon_url',''),
        "score_16p":                str(g.get('score_16p','')),
        "reviews_16p":              str(g.get('reviews_16p','')),
        "taptap_rating":            str(g.get('taptap_rating','')),
        "ios_rating":               str(g.get('ios_rating','')),
    }
    if is_rank:
        result["Hạng"] = str(idx+1)
    else:
        result["STT"] = str(idx+1)
    return result

def isHL(genre):
    HL = ['mmorpg','rpg','slg','casual','shooting','turn-based','card battle','角色扮演','修仙']
    parts = (genre or '').lower().split('/')
    parts = [p.strip() for p in parts]
    return any(h in ' '.join(parts) for h in HL)

def main():
    if not os.path.exists(TEMPLATE):
        print(f"✗ Template not found: {TEMPLATE}"); return

    with open(TEMPLATE,'r',encoding='utf-8') as f:
        html = f.read()

    updated_at = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")

    if os.path.exists(LIVE):
        with open(LIVE,'r',encoding='utf-8') as f:
            live = json.load(f)

        new_raw = {
            "newgames": [build_game(g, i, False) for i,g in enumerate(live.get('newgames',[]))],
            "bxh_30":   [build_game(g, i, True)  for i,g in enumerate(live.get('rank30',[]))],
            "bxh_90":   [build_game(g, i, True)  for i,g in enumerate(live.get('rank90',[]))],
            "bxh_year": [build_game(g, i, True)  for i,g in enumerate(live.get('rankyr',[]))],
        }

        data_js = json.dumps(esc(new_raw), ensure_ascii=False)
        assert '\n' not in data_js.replace('\\n',''), "newline leak!"

        # Inject into template placeholder
        html = html.replace('const RAW=__LIVE_DATA__;', f'const RAW={data_js};')

        ng = new_raw['newgames']
        hl = sum(1 for g in ng if g.get('Highlight'))
        status_counts = {}
        for g in ng:
            s = g.get('Trạng thái (Tiếng Việt)','?')
            status_counts[s] = status_counts.get(s,0)+1
        print(f"  ✓ Built: {len(ng)} newgames, {hl} highlights")
        print(f"  Statuses: {dict(sorted(status_counts.items(),key=lambda x:-x[1])[:5])}")
    else:
        print("  ⚠ No live_data.json — keeping template data")

    html = html.replace('__UPDATED_AT__', updated_at)

    with open(OUTPUT,'w',encoding='utf-8') as f:
        f.write(html)
    print(f"✓ Built index.html ({len(html):,} bytes) — {updated_at}")

if __name__ == '__main__':
    main()
