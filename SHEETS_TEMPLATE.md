# Google Sheets Template cho Game Tracker

## 📋 Cấu trúc Sheet

Tạo Google Sheet với tên cột CHÍNH XÁC như sau (hàng đầu tiên):

| game_name | date | dau | nru | install | ltv | arpu | revenue | retention_d1 | retention_d7 | retention_d30 | source | note |
|-----------|------|-----|-----|---------|-----|------|---------|--------------|--------------|---------------|--------|------|
| 原神 | 2026-06-01 | 15,000,000 | 500,000 | 800,000 | $45 | $3.2 | $48M | 65% | 35% | 18% | Data.ai | Tháng 6 |
| 王者荣耀 | 2026-06-01 | 80,000,000 | 1,200,000 | 2,000,000 | $12 | $1.8 | $144M | 72% | 42% | 22% | Sensor Tower | |

## 📌 Chú thích cột

- **game_name**: Tên game PHẢI KHỚP với tên trong tool (tên tiếng Trung gốc)
- **date**: Định dạng YYYY-MM-DD
- **dau**: Daily Active Users
- **nru**: New Registered Users per day
- **install**: Lượt cài đặt (tổng tích lũy hoặc per day)
- **ltv**: Life Time Value ($)
- **arpu**: Average Revenue Per User ($)
- **revenue**: Doanh thu (ghi rõ đơn vị: $1.2M, ¥500K...)
- **retention_d1/d7/d30**: Tỷ lệ giữ chân người dùng (%)
- **source**: Nguồn dữ liệu (Data.ai / Sensor Tower / Internal / Estimate)
- **note**: Ghi chú thêm

## 🔗 Cách publish Sheet thành CSV URL

1. Mở Google Sheet
2. **File** → **Share** → **Publish to web**
3. Chọn **Sheet1** (hoặc sheet bạn dùng)
4. Chọn định dạng **Comma-separated values (.csv)**
5. Click **Publish** → Copy URL

URL sẽ có dạng:
```
https://docs.google.com/spreadsheets/d/SHEET_ID/pub?gid=0&single=true&output=csv
```

6. Vào GitHub repo → **Settings** → **Secrets and variables** → **Actions**
7. Tạo secret tên: `SHEETS_CSV_URL` → paste URL vào

## ✅ Game names cần khớp (copy chính xác)

```
射雕, 燕云十六声, 代号:破晓, 星之海图, 无限暖暖, 鸣潮,
三国：谋定天下, 龙族幻想2, 暗区突围:无限, 问道手游2,
永恒纪元2, 独行侠, 凡人修仙传：人界篇, 赤核, 决战平安京2,
末世危城, 梦幻新诛仙, 勇者斗恶龙 达依的大冒险, Aether Gazer 2, 万象物语2,
原神, 王者荣耀, 和平精英, 明日方舟, 三国志·战略版,
崩坏：星穹铁道, 率土之滨, 剑与远征：启程, 逆水寒手游, 蛋仔派对,
万国觉醒, 第五人格, 光遇, 梦幻西游手游
```
