# 市場調查報告製作技能

## 📋 技能描述
快速製作獵頭產業市場調查分析報告的完整流程，從數據收集到 HTML 報告生成，20 分鐘完成專業級報告。

## 🎯 適用場景
- 每週製作市場調查報告
- 月度產業趨勢分析
- 客戶提案用市場數據
- 內部職缺分析報告

## ⚡ 快速開始（3 步驟，20 分鐘）

### Step 1：收集市場數據（13 分鐘）

**1.1 搜尋官方報告**
```bash
# 用 Google 搜尋以下關鍵字：
- "104人力銀行 2026 熱門職缺"
- "1111人力銀行 缺工產業"
- "比薪水 熱門工作"
- "台灣 薪資調查 2026"
```

**1.2 找到權威來源**
- ✅ 104 獵才顧問官方報告
- ✅ 1111 人力銀行調查
- ✅ 比薪水職場趨勢
- ✅ 勞動部統計
- ✅ 主計處薪資數據

**1.3 複製關鍵數據**
整理成 Markdown 格式：
```markdown
## 台灣 2026 熱門職缺 Top 30

| 排名 | 職位 | 成長率 | 薪資範圍 | 需求 |
|------|------|--------|----------|------|
| 1 | 生產設備工程師 | +180% | 60-90k | 極高 |
| 2 | 產品售後技術服務 | +174% | 50-80k | 極高 |
...
```

**1.4 儲存數據檔案**
```bash
# 存到臨時資料夾
~/clawd/skills/market-research/data/market-data-YYYY-MM-DD.md
```

---

### Step 2：整理內部數據（2 分鐘）

**2.1 讀取 Google Sheets**
```bash
# 使用 gog CLI 讀取
gog sheets get "[Sheet ID]" "A1:Z100" --account [email] --json
```

需要的表格：
- ✅ BD客戶開發表（企業客戶資料）
- ✅ step1ne 職缺管理（職缺清單）
- ✅ 履歷池索引（候選人數據）

**2.2 統計關鍵指標**
```bash
# 自動統計腳本
~/clawd/skills/market-research/scripts/analyze-internal-data.sh

輸出：
- 企業客戶數量
- 產業分布（%）
- 地理分布（%）
- BD 進度（已寄出/待分配/待聯繫）
- 填補難度評估
- Pipeline 狀態
```

---

### Step 3：生成 HTML 報告（5 分鐘）

**3.1 使用報告生成器**
```bash
# 執行報告生成腳本
~/clawd/skills/market-research/scripts/generate-report.sh \
  --market-data data/market-data-2026-02-11.md \
  --internal-data data/internal-stats.json \
  --output market-analysis-2026-02-11.html
```

**3.2 報告包含內容**
- ✅ 第一部分：市場概況
  - 熱門職缺 Top 30
  - 五大缺工產業
  - 薪資行情對比
  - 競爭對手分析
  - Step1ne 定位分析

- ✅ 第二部分：內部職缺分析
  - 企業客戶分析
  - 職缺人才地圖
  - 履歷池現況
  - BD 進度追蹤
  - 填補難度評估
  - Pipeline 狀態

**3.3 上傳到 GitHub Pages**
```bash
cd /path/to/aijob-presentations
git add market-analysis-YYYY-MM-DD.html
git commit -m "市場調查報告 YYYY-MM-DD"
git push
```

---

## 🛠️ 工具清單

### 必備工具
1. **gog CLI** - 讀取 Google Sheets
2. **web_search** - 搜尋市場數據
3. **web_fetch** - 抓取報告內容
4. **Git** - 版本控制 + GitHub Pages 部署

### 選用工具
1. **agent-browser** - 自動化爬蟲（進階版）
2. **Google Trends API** - 關鍵字趨勢
3. **104 API**（如果有）- 直接抓職缺數據

---

## 📊 數據來源清單

### 外部數據源
| 來源 | 用途 | 更新頻率 | 可信度 |
|------|------|----------|--------|
| 104 獵才顧問報告 | 熱門職缺、薪資趨勢 | 季度/年度 | ⭐⭐⭐⭐⭐ |
| 1111 人力銀行 | 缺工產業、企業調查 | 季度 | ⭐⭐⭐⭐ |
| 比薪水 | 職位薪資、市場趨勢 | 即時 | ⭐⭐⭐⭐ |
| 勞動部統計 | 官方失業率、就業數據 | 月度 | ⭐⭐⭐⭐⭐ |
| Google Trends | 職位關鍵字熱度 | 即時 | ⭐⭐⭐ |

### 內部數據源
| 資料 | 位置 | 更新者 | 頻率 |
|------|------|--------|------|
| BD客戶開發表 | Google Sheets | YQ2 | 即時 |
| step1ne 職缺管理 | Google Sheets | YQ2 | 即時 |
| 履歷池索引 | Google Sheets | YQ2 | 每日 |

---

## 🔄 每週自動化流程

### 設定 Cron Job
```bash
# 每週一 09:00 自動執行
cron add \
  --schedule "0 9 * * 1" \
  --command "~/clawd/skills/market-research/scripts/weekly-report.sh" \
  --name "每週市場調查報告"
```

### 自動化腳本內容
```bash
#!/bin/bash
# weekly-report.sh

# 1. 收集市場數據
echo "📊 收集市場數據..."
~/clawd/skills/market-research/scripts/collect-market-data.sh

# 2. 整理內部數據
echo "📋 整理內部數據..."
~/clawd/skills/market-research/scripts/analyze-internal-data.sh

# 3. 生成報告
echo "📄 生成 HTML 報告..."
~/clawd/skills/market-research/scripts/generate-report.sh

# 4. 上傳 GitHub Pages
echo "🚀 上傳報告..."
cd /tmp/aijob-presentations
git add market-analysis-$(date +%Y-%m-%d).html
git commit -m "市場調查報告 $(date +%Y-%m-%d)"
git push

# 5. 發送通知到 HR 群組
echo "📨 發送通知..."
message send \
  --channel telegram \
  --target "-1003231629634" \
  --thread 319 \
  --message "📊 本週市場調查報告已更新：https://jacky6658.github.io/aijob-presentations/market-analysis-$(date +%Y-%m-%d).html"
```

---

## 📈 改進計畫

### 下週改進（自動化數據收集）
```bash
# 新增自動爬蟲腳本
~/clawd/skills/market-research/scripts/auto-scrape-104.sh

功能：
- 自動爬取 104 熱門職缺統計頁面
- 自動爬取 1111 缺工產業報告
- 自動提取薪資數據
- 輸出標準化 JSON 格式
```

### 未來改進（趨勢分析）
```bash
# 週對週對比分析
~/clawd/skills/market-research/scripts/trend-analysis.sh

輸出：
- 哪些職缺排名上升/下降
- 薪資變化趨勢圖
- BD 進度週增長率
- 履歷池成長率
```

---

## 💡 最佳實踐

### ✅ Do（建議）
1. **每週固定時間執行**（週一 09:00）
2. **數據來源標註清楚**（可信度標記）
3. **保留歷史報告**（方便對比趨勢）
4. **自動化重複工作**（腳本 > 手動）
5. **報告格式一致**（方便閱讀）

### ❌ Don't（避免）
1. ❌ 不要手動複製貼上大量數據（用腳本）
2. ❌ 不要使用未驗證的數據來源
3. ❌ 不要忘記標註數據更新日期
4. ❌ 不要在報告中使用簡體中文
5. ❌ 不要忽略手機版 RWD

---

## 📝 報告範本

### HTML 報告結構
```html
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <!-- Step1ne 藍色配色 + RWD -->
</head>
<body>
    <header>
        <!-- 標題、日期、Logo -->
    </header>
    
    <main>
        <!-- 第一部分：市場概況 -->
        <section id="market-overview">
            <h2>市場概況</h2>
            <!-- Top 30 職缺、五大缺工產業、薪資趨勢 -->
        </section>
        
        <!-- 第二部分：內部職缺分析 -->
        <section id="internal-analysis">
            <h2>內部職缺分析</h2>
            <!-- 企業客戶、BD進度、Pipeline -->
        </section>
        
        <!-- 總結與行動建議 -->
        <section id="summary">
            <h2>總結與下一步</h2>
            <!-- 立即行動清單 -->
        </section>
    </main>
    
    <footer>
        <!-- 數據來源、更新日期 -->
    </footer>
</body>
</html>
```

---

## 🆘 常見問題

### Q1：數據來源找不到怎麼辦？
**A：** 使用備用來源
1. 主要：104 官方報告
2. 備用1：1111 統計
3. 備用2：比薪水趨勢
4. 備用3：勞動部公開數據

### Q2：內部數據不完整怎麼辦？
**A：** 標註「待補充」
- 履歷池為空 → 寫「0（待建立）」
- Pipeline 無數據 → 寫「空（待建立）」
- 不要編造數據

### Q3：報告生成失敗怎麼辦？
**A：** 檢查 3 個地方
1. 數據檔案格式是否正確（Markdown/JSON）
2. Google Sheets 權限是否正常
3. GitHub Pages 是否 push 成功

### Q4：手機版顯示跑版怎麼辦？
**A：** 檢查 CSS media queries
```css
@media (max-width: 768px) {
    /* 手機版樣式 */
}
```

---

## 📚 延伸閱讀

- [104 獵才顧問官方報告](https://hunter.104.com.tw/)
- [1111 人力銀行統計](https://www.1111.com.tw/)
- [比薪水](https://salary.tw)
- [勞動部統計查詢](https://statdb.mol.gov.tw/)
- [Google Sheets API 文件](https://developers.google.com/sheets/api)

---

## 📞 技能支援

**製作者：** YuQi (YQ1) AI 助理  
**版本：** 1.0.0  
**最後更新：** 2026-02-11  
**下次更新：** 2026-02-18（每週改進）

**問題回報：**  
- Telegram: @jackyyuqi
- GitHub Issues: [step1ne-headhunter-skill](https://github.com/jacky6658/step1ne-headhunter-skill)
