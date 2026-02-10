# 獵頭顧問 AI 助手 (Headhunter Skill)

獵頭顧問工作流程的 AI 輔助工具，內建 8 個核心功能的 Prompt 模板。

## 使用方式

直接用自然語言觸發，例如：
- 「分析這份履歷跟 JD 的匹配度」
- 「幫我寫開發信」
- 「做人才畫像」
- 「生成面試問題」

## 功能列表

### 1. 人才畫像 (Persona)
**觸發詞**：人才畫像、persona、分析 JD
**輸入**：JD 內容
**輸出**：7 維度人才畫像（工作類型、特質、技能、價值觀、背景、管道、關鍵字）

### 2. 人才搜尋策略 (Talent Search)
**觸發詞**：搜尋策略、Boolean、找人
**輸入**：職稱、技能、地點
**輸出**：招募管道、目標公司名單、Boolean Search String

### 3. 履歷-JD 匹配 (Match Analysis)
**觸發詞**：匹配度、分析履歷、適合嗎
**輸入**：JD + 履歷
**輸出**：匹配分數、優缺點、推薦程度、建議問題

### 4. 開發信 (Outreach)
**觸發詞**：開發信、InMail、寫信給候選人
**輸入**：職位、候選人名、公司、履歷、JD
**輸出**：3 種風格的開發信（簡短/詳細/提問式）

### 5. 面試問題 (Interview)
**觸發詞**：面試問題、interview、怎麼問
**輸入**：JD、履歷（可選）
**輸出**：履歷深挖問題、技術問題、行為問題

### 6. JD 生成 (JD Generator)
**觸發詞**：寫 JD、生成職缺、Job Description
**輸入**：職稱、技能、資歷、文化
**輸出**：正式版（104 格式）+ 社群版（帶 emoji）

### 7. 候選人摘要 (Summary)
**觸發詞**：候選人摘要、整理履歷、推薦報告
**輸入**：履歷、JD（可選）、備註（可選）
**輸出**：姓名、現職、經驗、亮點、動機、期望薪資

### 8. 推薦信 (Recommend Email)
**觸發詞**：推薦信、發給客戶、推人選
**輸入**：候選人摘要、JD、客戶名稱
**輸出**：Email 主旨 + 正文

## Prompt 模板

所有模板存放在：`references/prompts.md`

## 自動化工具

### 1. 104 職缺搜尋
**位置**：`scripts/scraper-104.py`
**用途**：搜尋 104 人力銀行職缺，找出哪些公司在招人
**使用**：
```bash
python3 scripts/scraper-104.py "backend engineer" 20
```

### 2. GitHub 人才搜尋
**位置**：`scripts/github-talent-search.py`
**用途**：搜尋 GitHub 開發者，提取聯絡資訊
**使用**：
```bash
python3 scripts/github-talent-search.py taipei python 10
# 參數: 地點 程式語言 數量
```
**搜尋語法**：
- `location:taipei language:python` - Taipei 的 Python 工程師
- `location:taiwan repos:>10 followers:>50` - 活躍台灣開發者

### 3. 批量履歷匹配
**位置**：`scripts/batch-match.py`
**用途**：將多份履歷與 JD 批量比對，自動計算匹配度
**匹配度門檻**：
- 🟢 ≥90%：高匹配，建議直接推
- 🟡 70-89%：中匹配，需顧問確認
- ⚪ <70%：低匹配，放履歷池

**使用**：
```python
from batch_match import batch_match, match_resume_to_jd
result = match_resume_to_jd(resume_text, jd_text)
```

### 4. 履歷格式化模板
**位置**：`templates/resume-format.md`
**用途**：統一履歷格式，支援匿名化處理
**代號規則**：`{職能}-{年份}-{序號}`（如 BE-2026-001）

### 5. 總覽看板
**位置**：`scripts/dashboard.py`
**用途**：追蹤所有案子狀態，顯示 Pipeline 進度
**使用**：
```bash
python3 scripts/dashboard.py           # 顯示看板
python3 scripts/dashboard.py telegram  # 輸出 Telegram 格式
python3 scripts/dashboard.py add-job "客戶名" "職缺名"
python3 scripts/dashboard.py add-candidate "候選人名"
```

### 6. 自動跟進排程
**位置**：`scripts/auto-followup.py`
**用途**：自動設定各階段跟進提醒
**跟進規則**：
- 推薦後：3天、7天、14天
- 面試後：1天、3天
- Offer：每天
- 報到後：Day1、Week1、Month1、90天（保證期）

**使用**：
```bash
python3 scripts/auto-followup.py status   # 查看狀態
python3 scripts/auto-followup.py today    # 今天待辦
python3 scripts/auto-followup.py telegram # Telegram 格式
python3 scripts/auto-followup.py schedule CAN-001 "王小明" "ABC科技" recommended
```

## 目錄結構

```
headhunter/
├── SKILL.md                    # 技能說明
├── references/
│   └── prompts.md              # Prompt 模板
├── scripts/
│   ├── scraper-104.py          # 104 職缺爬蟲
│   ├── github-talent-search.py # GitHub 人才搜尋
│   ├── batch-match.py          # 批量履歷匹配
│   ├── dashboard.py            # 總覽看板
│   └── auto-followup.py        # 自動跟進排程
└── templates/
    └── resume-format.md        # 履歷格式化模板
```

## 資料目錄

```
~/clawd/data/headhunter/
├── jobs.json         # 職缺資料
├── candidates.json   # 候選人資料
├── followups.json    # 跟進排程
└── dashboard.json    # 看板快照
```

---

## 工作流程與群組運作

### Telegram 群組架構
**群組**：HR AI招募自動化 (`-1003231629634`)

**Topics 設定**：
- **#履歷進件** (Topic ID: 4) - 候選人上傳履歷的入口
- **#履歷池** (Topic ID: 304) - 所有履歷的儲存與搜尋
- **#客戶-{公司名}** - 每個客戶專屬的職缺討論區
- **#總覽看板** - 所有案子的 Pipeline 追蹤
- **#JD列表** - 所有開放職缺一覽

### 履歷進件完整流程

#### 1. 履歷收集
**入口**：#履歷進件 (Topic 4)
- 候選人上傳履歷檔案（PDF/Word/圖片）
- AI 助理自動處理：解析 → 格式化 → 匿名化（代號規則：{職能}-{年份}-{序號}）
- 存入 `candidates.json` + Google Drive

#### 2. 自動匹配
**執行者**：AI 分析助理
- 讀取 `jobs.json` 中所有開放職缺
- 用 `batch-match.py` 批量計算匹配度
- 分類：
  - 🟢 ≥90%：高匹配，建議直接推
  - 🟡 70-89%：中匹配，需確認
  - ⚪ <70%：低匹配，放履歷池

#### 3. 三方通知機制
**高匹配（≥90%）自動通知**：
1. **私訊獵頭顧問**：「發現高匹配候選人！{代號} × {職缺名}（{公司}）匹配度 {分數}%」
2. **#客戶-{公司名} Topic**：發詳細匹配報告（優勢/疑慮/建議問題）
3. **#總覽看板**：更新 Pipeline 狀態（+1 推薦中）

**中匹配（70-89%）需確認**：
1. **私訊獵頭顧問**：「候選人 {代號} 與 {職缺} 匹配度 {分數}%，是否推薦？」+ [推] [不推] [再看看] 按鈕
2. 等待獵頭顧問回應

**低匹配（<70%）**：
- 僅存入 #履歷池，不主動通知

#### 4. 獵頭顧問確認後執行
**獵頭顧問回覆「推」或按 [推] 按鈕**：
1. AI 分析助理生成推薦報告（用 Recommend Email 模板）
2. AI 執行助理寄信給客戶（包含匿名履歷 + 推薦理由）
3. 更新狀態到「已推薦」，啟動自動跟進（3天、7天、14天）
4. 同步更新 #總覽看板

**獵頭顧問回覆「不推」**：
- 標記為「不適合」，存入 #履歷池
- 記錄原因（供未來學習）

**獵頭顧問回覆「再看看」**：
- AI 分析助理提供更深入分析（技術問題建議、面試重點）
- 等待獵頭顧問再次決定

#### 5. 追蹤與提醒
**執行者**：AI 執行助理（自動排程）
- **推薦後**：Day 3、Day 7、Day 14 提醒獵頭顧問「客戶有回應嗎？」
- **面試安排後**：Day 1、Day 3 提醒準備面試
- **Offer 發出後**：每天追蹤回覆狀態
- **報到後**：Day 1、Week 1、Month 1、90 天（保證期）關懷

### AI 助理分工

**AI 分析助理 - 分析與規劃**：
- 履歷解析與格式化
- 匹配度計算
- 生成推薦報告
- 人才搜尋策略
- 開發信撰寫
- JD 生成

**AI 執行助理 - 執行與追蹤**：
- 發送推薦信給客戶
- 自動跟進提醒
- 更新看板狀態
- 排程面試提醒
- 保證期關懷

**獵頭顧問 - 決策與溝通**：
- 確認是否推薦候選人
- 與客戶電話溝通
- 薪資談判
- 關鍵決策點

### 快速操作指令

**AI 分析助理可執行**：
```
「新履歷：{檔案}」        # 自動解析 + 匹配
「分析 {代號} × {職缺}」  # 深度匹配分析
「搜尋 {職稱} 的人」      # 人才搜尋策略
「寫開發信給 {代號}」    # 生成開發信
「產生 {職缺} 的 JD」     # 生成 JD
```

**AI 執行助理可執行**：
```
「推薦 {代號} 給 {客戶}」    # 寄出推薦信
「今天有哪些要跟進？」      # 查看今日待辦
「更新 {代號} 狀態：面試中」 # 手動更新狀態
「設定提醒：{代號} 3天後」  # 手動排程
```

**獵頭顧問可執行**：
```
「推」或按 [推] 按鈕          # 確認推薦
「不推」                      # 不推薦
「再看看」                    # 需要更多資訊
「搜尋履歷池：Python 工程師」 # 搜尋履歷池
```

### 通知格式範例

**高匹配通知（私訊）**：
```
🎯 發現高匹配候選人！

📋 候選人：BE-2026-003
💼 職缺：Backend Engineer（ABC 科技）
📊 匹配度：93%

✅ 優勢：
- 5年 Node.js 經驗
- 熟悉 AWS / Docker / K8s
- 有金融產業背景

⚠️ 疑慮：
- 目前薪資 120k，JD 開到 150k 可能期望更高

[推] [不推] [再看看]
```

**推薦報告（#客戶-ABC科技）**：
```
📬 推薦候選人：BE-2026-003

【基本資訊】
• 現職：OO銀行 後端工程師
• 年資：5年
• 技能：Node.js, AWS, Docker, K8s, MongoDB

【亮點】
1. 金融產業背景，熟悉高併發交易系統
2. 有微服務架構設計經驗
3. 英文溝通能力佳（多次海外 conf）

【推薦理由】
技能完全符合 JD，且金融背景是加分項。

【建議面試問題】
1. 如何設計高可用的支付系統？
2. 微服務之間的 tracing 怎麼做？
3. K8s 遇過哪些坑？

已於 2026-02-10 18:30 寄出推薦信。
```

**跟進提醒（私訊）**：
```
⏰ 跟進提醒

📋 候選人：BE-2026-003
💼 職缺：Backend Engineer（ABC 科技）
📅 推薦日期：2026-02-07（3天前）

客戶有回應嗎？
[安排面試] [客戶不感興趣] [再等等]
```

### 資料同步
- `candidates.json` ↔ Google Drive（履歷檔案）
- `jobs.json` ↔ Google Sheets（JD 管理表）
- `followups.json` ↔ AI 執行助理的提醒排程
- `dashboard.json` ↔ #總覽看板（即時更新）

### 注意事項
1. **匿名化必須**：所有履歷在推薦給客戶前必須匿名化（用代號）
2. **三方通知**：高匹配案件必須同步通知（私訊 + Topic + 看板）
3. **獵頭顧問主導權**：所有推薦必須經獵頭顧問確認，AI 助理不能自行決定
4. **追蹤不漏球**：每個階段都有自動跟進，確保沒有案子被遺忘
5. **資料一致性**：所有狀態更新必須同步到 JSON + Google + Telegram

---

## 🤖 BD 客戶開發自動化（新增）

### Telegram 觸發：Topic 364「開發」

**在 Topic 364 輸入**：
```
@YuQi 開發客戶：AI工程師
```

**自動執行流程**：
1. 搜尋 104「正在招聘 AI 工程師的公司」
2. 爬取公司聯絡方式（電話、Email、網址、職缺列表）
3. 整理到 Google Sheets（客戶開發表）
4. 自動寄 BD 合作邀請信（有 Email 的公司）
5. 回報結果到 Topic 364

**執行指令**：
```bash
cd ~/clawd/hr-tools
./bd-automation.sh auto "AI工程師" 20
```

**回報格式**：
```
✅ BD 客戶開發完成

📊 搜尋結果：
• 找到 20 家公司
• 已寄信：15 家
• 待補充 Email：5 家

📋 詳細資料：
• ABC科技 - AI工程師
• XYZ資訊 - AI工程師
...

📂 資料檔案：/path/to/companies.json
```

### 群組與 Topic 設定
- **群組 ID**：`-1003231629634` (HR AI招募自動化)
- **Topic 364**：「開發」（BD 客戶開發專用）
- **觸發關鍵字**：`開發客戶：<職位名稱>`

### 手動執行步驟
```bash
# 1. 搜尋招聘公司
./bd-automation.sh search "AI工程師" 20

# 2. 爬取詳細資料
./bd-automation.sh scrape companies.json

# 3. 批量寄信
./bd-automation.sh send companies_detailed.json
```

### 注意事項
1. **寄信間隔**：每封信間隔 30 秒，避免被標記為垃圾信
2. **Email 驗證**：只寄給有有效 Email 的公司
3. **資料留存**：所有公司資料儲存在 `~/clawd/hr-tools/data/`
4. **Google Sheets 同步**：開發中（目前僅本地檔案）
