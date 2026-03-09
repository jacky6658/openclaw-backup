# step1ne-headhunter-system 爬蟲腳本清單

**Repository**: https://github.com/jacky6658/step1ne-headhunter-system  
**檢查日期**: 2026-03-04

---

## ✅ 找到爬蟲腳本！

### 📂 位置：`server/talent-sourcing/`

這是系統後端的**核心人才搜尋模組**，包含完整的爬蟲與評分系統。

---

## 🕷️ 爬蟲腳本列表

| 腳本 | 大小 | 功能描述 |
|------|------|----------|
| **search-plan-executor.py** | 33.9KB | ⭐ 主要爬蟲引擎 |
| **one-bot-pipeline.py** | 37.8KB | ⭐ 完整自動化 Pipeline |
| **candidate-scoring-system-v2.py** | 30.0KB | 候選人評分系統 v2 |
| **profile-reader.py** | 21.1KB | 個人檔案讀取器 |
| **industry-migration-analyzer.py** | 14.1KB | 產業遷移分析器 |
| **job-profile-analyzer.py** | 9.7KB | 職缺分析器 |
| **claude-conclusion-generator.py** | 9.6KB | AI 結語生成器 |
| **routes.js** | 6.1KB | API 路由 |
| **requirements.txt** | 19 bytes | Python 依賴 |

---

## 🔥 核心腳本詳解

### 1️⃣ **search-plan-executor.py** (33.9KB) ⭐⭐⭐

**Step1ne 人才搜尋執行器 v5**

**功能**：
- **LinkedIn 搜尋**：
  - 主要：Playwright 真實瀏覽器
  - 備援：Google/Bing/Brave Search API
- **GitHub 搜尋**：GitHub API
- 自動去重
- 多執行緒平行處理
- 隨機 User-Agent + 反爬蟲延遲

**技術特色**：
```python
# stdlib-only HTTP 工具（支援 gzip）
# 自動解壓縮、隨機 UA
# SSL 憑證忽略（雲端環境友善）
```

**使用方式**：
```bash
python3 search-plan-executor.py \
  --job "Java Developer" \
  --company "台積電" \
  --limit 20
```

---

### 2️⃣ **one-bot-pipeline.py** (37.8KB) ⭐⭐⭐

**Step1ne 獵頭 AI Bot 閉環管線 v2**

**完整自動化流程**：

```
┌─────────────────────────────────────┐
│ 【scrape 模式】                      │
│ 讀取 Bot 設定（目標職缺）            │
│   ↓                                  │
│ 爬取 LinkedIn / GitHub 候選人        │
│   ↓                                  │
│ 去重（跳過已存在 DB）                │
│   ↓                                  │
│ 匯入新候選人（狀態：未開始）         │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 【score 模式】                       │
│ 查詢今日「未開始」候選人             │
│   ↓                                  │
│ 6 維確定性評分                       │
│   ↓                                  │
│ AI 結語生成（Claude）                │
│   ↓                                  │
│ ≥80 分 → AI推薦                      │
│ <80 分 → 備選人才                    │
│   ↓                                  │
│ 寫入 ai_match_result                 │
└─────────────────────────────────────┘
```

**使用方式**：
```bash
# 完整模式（爬取 + 評分）
python3 one-bot-pipeline.py --mode full

# 只爬取
python3 one-bot-pipeline.py --mode scrape --job-ids 3,7,12

# 只評分
python3 one-bot-pipeline.py --mode score

# 試跑
python3 one-bot-pipeline.py --dry-run
```

**環境變數**：
```bash
API_BASE_URL=https://backendstep1ne.zeabur.app
BOT_ACTOR=AIBot-pipeline
BRAVE_KEY=your_brave_api_key
GITHUB_TOKEN=your_github_token
```

**建議 Cron 設定**：
```cron
# 每 2 小時執行一次評分
0 */2 * * * API_BASE_URL=https://backendstep1ne.zeabur.app \
            /usr/bin/python3 /path/to/one-bot-pipeline.py \
            --mode score >> /tmp/step1ne-score.log 2>&1
```

---

### 3️⃣ **candidate-scoring-system-v2.py** (30.0KB)

**候選人評分系統 v2**

**6 維度評分**：
1. 技能匹配度
2. 工作穩定性
3. 經驗年資
4. 學歷背景
5. 職涯發展軌跡
6. 特殊加分項

**輸出**：
- 總分（0-100）
- 評級（S / A+ / A / B / C）
- 詳細分析報告

---

### 4️⃣ **profile-reader.py** (21.1KB)

**個人檔案讀取器**

**功能**：
- 解析 LinkedIn 個人檔案
- 提取工作經歷
- 提取教育背景
- 技能分析

---

## 📦 其他支援模組

### server/ 目錄

| 檔案 | 大小 | 功能 |
|------|------|------|
| **talentSourceService.js** | 25.0KB | 人才智能搜尋服務（Node.js） |
| **githubAnalysisService.js** | 24.4KB | GitHub 深度分析 |
| **resumeService.js** | 12.2KB | 履歷處理服務 |
| **personaService.js** | 11.6KB | 人才畫像服務 |

---

## 🚀 完整工作流程

### Step1ne 系統的完整人才搜尋流程：

```
1. 職缺分析
   ├─ job-profile-analyzer.py
   └─ jobsService.js

2. 搜尋計畫生成
   └─ talentSourceService.js

3. 執行爬蟲搜尋
   ├─ search-plan-executor.py
   │  ├─ LinkedIn (Playwright + Brave API)
   │  └─ GitHub API
   └─ githubAnalysisService.js

4. 候選人去重
   └─ one-bot-pipeline.py (內建去重邏輯)

5. 評分與分析
   ├─ candidate-scoring-system-v2.py
   ├─ profile-reader.py
   ├─ industry-migration-analyzer.py
   └─ claude-conclusion-generator.py

6. 匯入系統
   └─ POST /api/candidates

7. 狀態更新
   └─ PUT /api/candidates/:id/pipeline-status
```

---

## 🔧 技術亮點

### 1. **無外部依賴爬蟲**
- 使用 Python stdlib only（urllib, json, ssl）
- 不依賴 requests, beautifulsoup4
- 雲端環境友善（Zeabur 部署）

### 2. **多層備援機制**
```
LinkedIn 搜尋：
  主要：Playwright 真實瀏覽器
    ↓ 失敗
  備援 1：Brave Search API
    ↓ 失敗
  備援 2：Google Search
    ↓ 失敗
  備援 3：Bing Search
```

### 3. **智慧反爬蟲**
- 隨機 User-Agent
- 動態延遲（2-5 秒）
- 多執行緒平行處理
- gzip 自動解壓

### 4. **完整閉環 Pipeline**
- 爬取 → 去重 → 評分 → 匯入 → 狀態管理
- 全自動化，無需人工介入

---

## 📊 與本地 hr-tools 的關係

### GitHub 上的版本（step1ne-headhunter-system）

**優勢**：
- ✅ 整合進系統後端
- ✅ API 直接呼叫
- ✅ 雲端部署就緒
- ✅ 完整閉環 Pipeline

**位置**：
- Repository: https://github.com/jacky6658/step1ne-headhunter-system
- 路徑: `/server/talent-sourcing/`

### 本地版本（hr-tools）

**優勢**：
- ✅ 獨立運行
- ✅ 快速測試
- ✅ 靈活調整
- ✅ 多版本並存

**位置**：
- `/Users/user/clawd/hr-tools/`
- 30+ 個獨立爬蟲腳本

---

## 🎯 使用建議

### 場景 1：系統內建自動化
**使用 GitHub 版本**
```bash
# 透過 API 呼叫
POST /api/talent-sourcing/find-candidates
{
  "company": "台積電",
  "jobTitle": "Java Developer"
}
```

### 場景 2：本地快速測試
**使用本地 hr-tools**
```bash
cd /Users/user/clawd/hr-tools
python3 unified-scraper-v4.py --job "Java Developer"
```

### 場景 3：完整閉環自動化
**使用 one-bot-pipeline.py**
```bash
cd /path/to/step1ne-headhunter-system/server/talent-sourcing
python3 one-bot-pipeline.py --mode full
```

---

## 🔄 同步建議

**本地 → GitHub**：
- 新功能在本地測試成功後
- 整合到 step1ne-headhunter-system
- 部署到 Zeabur 雲端

**GitHub → 本地**：
- 定期 git pull 保持同步
- 重要更新手動同步到 hr-tools

---

## 📝 維護紀錄

### 2026-03-04
- ✅ 發現 step1ne-headhunter-system 中的完整爬蟲模組
- ✅ 確認 talent-sourcing/ 目錄包含 9 個核心腳本
- ✅ 分析完整工作流程
- ✅ 整理技術文件

---

**總結**：step1ne-headhunter-system 包含**完整的企業級爬蟲系統**，整合進後端 API，支援雲端部署，比本地 hr-tools 更適合生產環境使用。

**文件產出時間**：2026-03-04 17:40
