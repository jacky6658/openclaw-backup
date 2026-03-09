# HR Tools - 獵頭顧問自動化工具集

**最後更新**：2026-02-12  
**維護者**：YuQi AI Assistant

---

## 📂 目錄結構

```
hr-tools/
├── active/                    # 正在使用的腳本
│   ├── automation/            # 自動化系統（Cron Jobs）
│   ├── crawlers/              # 爬蟲工具
│   ├── batch/                 # 批次處理
│   └── tools/                 # 工具腳本
├── data/                      # 運行資料
└── README.md                  # 本文件
```

---

## 🤖 automation/ - 自動化系統

**Cron Jobs 使用的腳本**

| 腳本 | 功能 | Cron 時間 |
|------|------|-----------|
| `auto-bd-crawler.sh` | BD 客戶開發（104 爬蟲） | 每 2 天凌晨 01:00-06:00 |
| `auto-bd-send.sh` | BD 自動發信 | 每天 09:30, 14:30 |
| `auto-resume-filing.sh` | 履歷自動歸檔 | 每小時 |
| `auto-sourcing.sh` | 自動找人選（LinkedIn + GitHub） | 每週一 10:00 |
| `auto-sourcing-search.py` | 候選人搜尋引擎 | 由 auto-sourcing.sh 呼叫 |

---

## 🕷️ crawlers/ - 爬蟲工具

**網頁爬取與資料提取**

| 腳本 | 功能 |
|------|------|
| `scraper-104.py` | 104 職缺爬蟲 |
| `scraper-stable/` | 穩定版 BD 爬蟲（100% 成功率） |
| `fetch-company-contact.py` | 公司聯絡資訊提取 |
| `fetch-104-website.py` | 104 公司網址提取 |
| `scrape-contact-from-website.sh` | 官網聯絡資訊爬取 |
| `batch-scrape-contacts.sh` | 批次聯絡資訊爬取 |
| `scrape-104-full.sh` | 104 完整資料爬取 |
| `scraper-linkedin.sh` | LinkedIn 資料爬取 |

---

## 📦 batch/ - 批次處理

**大量資料處理工具**

| 腳本 | 功能 |
|------|------|
| `batch-parse-resumes.py` | 批次履歷解析（PDF → JSON） |
| `batch_match.py` | 候選人-職缺批次配對 |
| `convert-html-to-md.sh` | HTML 轉 Markdown |
| `analyze-pipeline.sh` | Pipeline 資料分析 |

---

## 🛠️ tools/ - 工具腳本

**手動執行的輔助工具**

| 腳本 | 功能 |
|------|------|
| `jd-manager.sh` | 職缺管理 CLI |
| `jd-bot-handler.sh` | Telegram Bot 命令處理 |
| `resume-pool.sh` | 履歷池管理 |
| `market-analysis.sh` | 市場分析報告生成 |
| `quarterly-archive.sh` | 季度報告歸檔 |
| `start-dashboard.sh` | 啟動 HR 總覽看板 |
| `bd-automation.sh` | BD 手動執行工具 |
| `bd-outreach.sh` | BD 開發信發送 |
| `fill-bd-contacts.sh` | BD 聯絡資訊補齊 |
| `google-linkedin-search.sh` | LinkedIn 公開搜尋 |

---

## 📊 data/ - 運行資料

**系統運行產生的資料檔案**

| 檔案 | 說明 |
|------|------|
| `processed-resumes.log` | 已處理履歷清單 |
| `bim_companies_*.json` | BIM 公司爬取結果 |
| `companies_*.json` | 其他公司爬取結果 |

---

## 🔄 更新記錄

### 2026-02-12 - 大掃除與重構
- 重組目錄結構（automation/crawlers/batch/tools）
- 刪除 12 個測試/舊版腳本
- 清理 24 個測試 JSON 檔案
- 建立 README.md 文檔

---

## 🚀 快速開始

### 執行自動化系統

所有自動化系統由 OpenClaw Cron Jobs 管理，查看狀態：
```bash
openclaw cron list
```

### 手動執行工具

```bash
cd /Users/user/clawd/hr-tools/active/tools

# 職缺管理
./jd-manager.sh list

# 履歷池管理
./resume-pool.sh search "關鍵字"

# 市場分析
./market-analysis.sh
```

### 爬蟲工具

```bash
cd /Users/user/clawd/hr-tools/active/crawlers

# 104 職缺爬蟲
python3 scraper-104.py "BIM工程師"

# 穩定版 BD 爬蟲
cd scraper-stable
python3 main.py
```

---

## 📝 相關文件

- **技能文檔**：`/Users/user/clawd/skills/headhunter/SKILL.md`
- **操作手冊**：`/Users/user/clawd/projects/step1nehrai/獵頭工作流執行手冊.md`
- **GitHub Repo**：https://github.com/jacky6658/step1ne-headhunter-skill

---

## 🐛 問題回報

如有問題，請聯繫 YuQi AI Assistant via Telegram。
