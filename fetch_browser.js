// ================================================================
// FETCH SCRIPT - Chạy trong browser Console tại 16p.com
// Bước 1: Vào https://www.16p.com/newgame
// Bước 2: Nhấn F12 → Console
// Bước 3: Copy toàn bộ script này → Paste vào Console → Enter
// Bước 4: Đợi ~3-5 phút → File live_data.json tự động tải xuống
// ================================================================

(async () => {
  const TAG_VI = {
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
    "单机":"Offline / Chơi đơn","足球":"Bóng đá","多结局":"Đa kết thúc",
    "视觉小说":"Visual Novel","家庭聚会":"Party Game","合成":"Ghép/Merge",
    "竞技":"Cạnh tranh","3D":"3D","像素":"Pixel","Roguelite":"Roguelite",
    "暗黑":"Dark","横版":"2D ngang","太空":"Vũ trụ","地牢":"Dungeon",
    "探索":"Khám phá","剧情":"Story-rich","文字":"Text/Story",
    "经营":"Kinh doanh","益智":"Trí tuệ","萌宠":"Cute Pet","钓鱼":"Câu cá",
    "音游":"Rhythm game","闯关":"Platformer","街机":"Arcade",
    "异世界":"Isekai","乙女":"Otome","机甲":"Mecha","第一人称":"FPS",
    "西游":"Tây Du Ký","魔法":"Magic","种田":"Farming","手绘":"Hand-drawn",
    "温暖治愈":"Healing","类银河恶魔城":"Metroidvania","消除":"Match-3",
    "卡通":"Cartoon","篮球":"Basketball","国战":"Nation War",
  };
  const SKIP = new Set(['编辑推荐','近期下载飙升','多端互通','高画质','近期热门预约','安心购','策略拉满','编辑精选','买断制','Steam移植','多平台','高自由度','极致视听享受']);
  const STATUS = {
    "公测":["公测","Open Beta"],"上线":["上线","Onlive / Launch"],
    "试玩":["试玩","Demo"],"删档测试":["删档测试","Clear data Test"],
    "限量删档":["限量删档","Clear data Test (giới hạn)"],
    "限量删档测试":["限量删档测试","Clear data Test (giới hạn)"],
    "不限量不删档":["不限量不删档","Non-clear data Test (không giới hạn)"],
    "限量不删档测试":["限量不删档测试","Non-clear data Test (giới hạn)"],
    "删档计费测试":["删档计费测试","Paid Test xóa data"],
    "限量删档计费测试":["限量删档计费测试","Paid Test xóa data (giới hạn)"],
    "限量不删档计费":["限量不删档计费","Paid Test không xóa data (giới hạn)"],
    "不删档计费":["不删档计费","Paid Test không xóa data"],
    "不删档计费测试":["不删档计费测试","Paid Test không xóa data"],
    "计费删档内测":["计费删档内测","Paid Test nội bộ xóa data"],
    "删档内测":["删档内测","Test nội bộ xóa data"],
    "线下试玩会":["线下试玩会","Offline Playtest Event"],
    "新增版本":["新增版本","Cập nhật phiên bản mới"],
    "公测运营":["公测运营","Onlive / Launch"],
    "预约":["预约","Pre-register"],
  };
  const TT_IDS = {
    "王者荣耀世界":"744415","异环-自由开放都市":"714119","三国：天下归心":"759941",
    "神泣：纷争":"839042","饥困荒野-饥荒：新家园":"194039","原神":"168332",
    "崩坏：星穹铁道":"225069","明日方舟":"158138","无限暖暖":"247283",
    "鸣潮":"234280","元气骑士":"35077","战双帕弥什":"162255",
    "鹅鸭杀":"202498","光遇":"135596","洛克王国：世界":"695501",
    "遗忘之海-记忆环游海洋开放世界":"755604","天堂2：盟约":"196349",
  };

  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const log = msg => console.log(`[GameTracker] ${msg}`);

  function translateTags(tags) {
    const res = [], seen = new Set();
    for (const t of tags) {
      if (SKIP.has(t)) continue;
      const vn = TAG_VI[t] || t;
      if (!seen.has(vn)) { seen.add(vn); res.push(vn); }
      if (res.length >= 6) break;
    }
    return res;
  }

  // Step 1: Fetch test_game API (all statuses, past 180 + next 30 days)
  log('Bắt đầu fetch data từ 16p.com...');
  const allGames = {};
  const today = new Date();
  const dates = [];
  for (let d = -180; d <= 30; d += 3) {
    const dt = new Date(today);
    dt.setDate(dt.getDate() + d);
    dates.push(dt.toISOString().split('T')[0]);
  }

  log(`Fetching ${dates.length} dates...`);
  for (let i = 0; i < dates.length; i++) {
    const date = dates[i];
    try {
      const r = await fetch(`/gamecenter/api/test_game?date=${date}&type_range=2&p=1`);
      const d = await r.json();
      for (const [dt, games] of Object.entries(d.dates || {})) {
        for (const g of games) {
          const gid = g.gameid;
          if (!gid || allGames[gid]) continue;
          const gd = g.game || {};
          allGames[gid] = {
            gamename: gd.gamename || '',
            iconurl: gd.iconurl || '',
            testtype: (g.testtype || '').trim(),
            testdate: g.testdate || dt,
            companys: gd.companys || [],
            gameweb: gd.gameweb || '',
          };
        }
      }
    } catch(e) {}
    if ((i+1) % 20 === 0) log(`Progress: ${i+1}/${dates.length}, ${Object.keys(allGames).length} games`);
    await sleep(120);
  }
  log(`test_game done: ${Object.keys(allGames).length} games`);

  // Step 2: Fetch tags from new_game_list
  log('Fetching tags...');
  const tagsMap = {};
  for (const dr of [30, 90, 180, 365]) {
    for (let p = 1; p <= 3; p++) {
      try {
        const r = await fetch(`/gamecenter/api/new_game_list?p=${p}&ps=50&date_range=${dr}&type_range=2`);
        const d = await r.json();
        if (!d || !d.length) break;
        for (const g of d) {
          if (g.gamename && !tagsMap[g.gamename]) {
            tagsMap[g.gamename] = {
              gameplay: g.gameplay || [],
              review_rate: String(g.review_rate || ''),
              review_num: String(g.review_num || ''),
              gameweb: g.gameweb || '',
              format_time: g.format_time || g.publishtime || '',
            };
          }
        }
        await sleep(300);
      } catch(e) { break; }
    }
  }
  log(`Tags done: ${Object.keys(tagsMap).length} games with tags`);

  // Step 3: Rankings
  log('Fetching rankings...');
  const rankings = {};
  for (const [period, key] of [[30,'rank30'],[90,'rank90'],[365,'rankyr']]) {
    try {
      const r = await fetch(`/gamecenter/api/new_game_list?p=1&ps=30&date_range=${period}&type_range=2`);
      rankings[key] = await r.json() || [];
    } catch(e) { rankings[key] = []; }
    await sleep(300);
  }

  // Step 4: Build entries
  function buildEntry(gTest, gList, idx, isRank) {
    const name = (gTest||gList||{}).gamename || '';
    if (!name) return null;
    const td = gList || {};
    const tags = (gTest && gTest.gameplay) || td.gameplay || [];
    const tagsVn = translateTags(tags);
    const companys = (gTest||{}).companys || [];
    const pub = (companys.find(c=>String(c.company_role_id)==='1')||{}).name || '';
    const dev = (companys.find(c=>String(c.company_role_id)==='2')||{}).name || pub;
    const tt = (gTest||{}).testtype || '';
    const status = STATUS[tt] || [tt, tt || 'Open Beta'];
    const ttId = TT_IDS[name] || '';
    const ttUrl = ttId ? `https://www.taptap.cn/app/${ttId}` : `https://www.taptap.cn/search?q=${encodeURIComponent(name)}`;
    const pubTime = (gTest||{}).testdate || td.format_time || '';
    const result = {
      [isRank?'rank':'stt']: String(idx+1),
      name, name_en: '',
      icon_url: (gTest||{}).iconurl || '',
      tags_cn: tags.join(' / '),
      tags_vn: tagsVn,
      publisher: pub, developer: dev,
      testtype_cn: status[0], testtype_vn: status[1],
      score_16p: td.review_rate || '',
      pub_time: pubTime,
      date_sort: pubTime.slice(0,10),
      ios_id: '', ios_url: '', ios_rating: '',
      store_taptap: ttUrl, taptap_id: ttId,
      Mainsite: (gTest||{}).gameweb || td.gameweb || '',
    };
    return result;
  }

  // Sort by date desc
  const sortedGames = Object.values(allGames).sort((a,b)=>b.testdate.localeCompare(a.testdate));
  const newgames = [];
  const seen = new Set();
  for (let i = 0; i < sortedGames.length && newgames.length < 200; i++) {
    const g = sortedGames[i];
    if (!g.gamename || seen.has(g.gamename)) continue;
    seen.add(g.gamename);
    const entry = buildEntry(g, tagsMap[g.gamename], newgames.length, false);
    if (entry) newgames.push(entry);
  }

  function buildRanks(raw, isRank) {
    return raw.slice(0,30).map((g,i) => {
      if (!g.testtype) g.testtype = '上线';
      return buildEntry(g, tagsMap[g.gamename]||{}, i, true);
    }).filter(Boolean);
  }

  const out = {
    newgames,
    rank30: buildRanks(rankings.rank30),
    rank90: buildRanks(rankings.rank90),
    rankyr: buildRanks(rankings.rankyr),
    updated_at: new Date().toISOString().replace('T',' ').slice(0,16) + ' UTC',
    source: '16p.com (browser fetch)',
  };

  // Status breakdown
  const counts = {};
  newgames.forEach(g => { counts[g.testtype_vn] = (counts[g.testtype_vn]||0)+1; });
  log(`Done! ${newgames.length} newgames`);
  log('Statuses: ' + JSON.stringify(Object.entries(counts).sort((a,b)=>b[1]-a[1]).slice(0,5).reduce((o,[k,v])=>({...o,[k]:v}),{})));

  // Download as file
  const blob = new Blob([JSON.stringify(out, null, 2)], {type: 'application/json'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'live_data.json'; a.click();
  URL.revokeObjectURL(url);
  log('✅ File live_data.json đã được tải xuống! Upload lên GitHub repo là xong.');
})();
