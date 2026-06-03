# 🎮 Game Market Tracker – 16p.com

Auto-updating game tracker với TapTap live data + Google Sheets KPIs.

**Live site:** https://jtgh26.github.io/game-tracker/

---

## 🏗 Cấu trúc repo

```
game-tracker/
├── index.html                  ← File HTML cuối (được build tự động)
├── index_template.html         ← Template gốc (có __TAPTAP_DATA__ placeholder)
├── taptap_data.json            ← Data TapTap fetch về (auto-generated)
├── game_data.json              ← Static game database
├── scripts/
│   ├── fetch_taptap.py         ← Scrape TapTap ratings, fans, heat
│   ├── fetch_sheets.py         ← Sync Google Sheets premium KPIs
│   └── build_html.py           ← Rebuild index.html từ template + data
├── .github/workflows/
│   └── daily-update.yml        ← GitHub Actions: chạy mỗi ngày 8:00 AM GMT+7
├── SHEETS_TEMPLATE.md          ← Hướng dẫn cấu trúc Google Sheets
└── README.md
```

---

## ⚙️ Setup lần đầu (15 phút)

### Bước 1 — Upload lên GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/jtgh26/game-tracker.git
git push -u origin main
```

### Bước 2 — Bật GitHub Pages

1. Vào repo → **Settings** → **Pages**
2. Source: **Deploy from a branch** → branch `main` → folder `/ (root)`
3. Save → đợi 1-2 phút → site live tại `https://jtgh26.github.io/game-tracker/`

### Bước 3 — Tạo Google Sheet

1. Tạo Google Sheet theo cấu trúc trong `SHEETS_TEMPLATE.md`
2. Publish thành CSV (xem hướng dẫn trong file đó)
3. Vào repo → **Settings** → **Secrets and variables** → **Actions**
4. Tạo secret:
   - Name: `SHEETS_CSV_URL`
   - Value: URL CSV của Google Sheet

### Bước 4 — Chạy lần đầu

1. Vào tab **Actions** trong repo
2. Chọn workflow **"🎮 Daily Game Data Update"**
3. Click **"Run workflow"** → **"Run workflow"**
4. Đợi ~2 phút → site tự động update

---

## 🔄 Auto Update Schedule

| Trigger | Thời gian |
|---------|-----------|
| Tự động hàng ngày | 8:00 AM GMT+7 (1:00 UTC) |
| Thủ công | Actions tab → Run workflow |

---

## 📊 Data Sources

| Nguồn | Loại | Cập nhật | Chỉ số |
|-------|------|----------|--------|
| **TapTap** | Auto fetch | Daily | Rating, Reviews, Fans, Heat Score, Hits |
| **Google Sheets** | Nhập tay | Mỗi khi bạn update sheet | DAU, NRU, Install, LTV, ARPU, Revenue, Retention |

---

## 🛠 Chạy thủ công local

```bash
# Fetch TapTap data
python scripts/fetch_taptap.py

# Sync Google Sheets (cần set env var)
export SHEETS_CSV_URL="https://docs.google.com/spreadsheets/d/..."
python scripts/fetch_sheets.py

# Build HTML
python scripts/build_html.py

# Mở index.html trong browser
open index.html
```

---

## ❓ Troubleshooting

**TapTap fetch bị lỗi:** TapTap có thể block request. Workflow có `continue-on-error: true` nên sẽ dùng data cũ nếu fetch thất bại.

**Google Sheets không sync:** Kiểm tra secret `SHEETS_CSV_URL` đã được set chưa, và sheet đã được publish chưa.

**GitHub Pages chưa update:** Đợi 1-2 phút sau khi workflow chạy xong.
