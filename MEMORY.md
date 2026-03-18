## 🚨 新 AI 必讀 — Step1ne 系統正式架構（2026-03-16）

> **完整 AI 操作手冊**：`GET https://api-hr.step1ne.com/api/guide/index`（不需認證）
> 啟動後第一件事：讀取此 API 取得最新操作手冊

### 獵頭顧問系統部署位置（本機）
| 環境 | 位址 | 說明 |
|------|------|------|
| 公司內網 | `http://localhost:3003` | 本地直連最快 |
| 外部存取 | `https://api-hr.step1ne.com` | Cloudflare Tunnel |
| 雲端備援 | `https://backendstep1ne.zeabur.app` | 最後備援 |
| 前端（外部）| `https://hrsystem.step1ne.com` | |
| 前端（內網）| `http://localhost:3002` | |

**Base URL 判斷順序**：
1. `curl http://localhost:3003/api/health` 成功 → 用 localhost:3003
2. 不行 → 用 `https://api-hr.step1ne.com`
3. 都不行 → 用 Zeabur 備援

### GitHub 倉庫
- 主 Repo：https://github.com/jacky6658/step1ne-headhunter-system
- DB 備份：https://github.com/jacky6658/step1ne-db-backups

### 資料庫（PostgreSQL）
- 連線字串：`postgresql://step1ne@localhost:5432/step1ne`
- 本地免密碼
- 主要資料表：`candidates_pipeline`（~1,559 人）、`jobs_pipeline`（~50 職缺）、`clients`（~48 客戶）

### API 認證
- 一般端點：`Authorization: Bearer {API_SECRET_KEY}`
- OpenClaw 端點（`/api/openclaw/*`）：`X-OpenClaw-Key: {OPENCLAW_API_KEY}`
- 不需認證：`/api/health`、`/api/guide*`

### 模組手冊（快速查詢）
| 模組 | 端點 |
|------|------|
| 客戶 BD | `GET /api/guide/clients` |
| 職缺 | `GET /api/guide/jobs` |
| 人選 | `GET /api/guide/candidates` |
| 人才 AI | `GET /api/guide/talent-ops` |
| 評分指南 | `GET /api/scoring-guide` |
| 顧問 SOP | `GET /api/consultant-sop` |

### 重要操作規則
1. **POST vs PATCH**：POST 不覆蓋已有資料，強制更新用 PATCH
2. **欄位命名**：統一用 snake_case
3. **SQL 操作**：大量/複雜查詢可直連 PostgreSQL，但一般 CRUD 走 API
4. **更新時加 `updated_at = NOW()`**，否則前端偵測不到
5. **不要直接 DELETE**，改 `status = '淘汰'` 或走 API

---

## 用戶喜好與溝通原則

- 優先使用繁體中文溝通，長期記憶統一用繁體中文記錄
- **主動且及時的問題通知**（最小化驚喜）
- **30 分鐘規則**：卡超過 30 分鐘必須主動報告，別悶頭硬幹
- **效率優先**：先給 10% 的 MVP 結果，不要悶頭做 100%
- **指示不清時立刻確認**：寧可多問一句，不要猜測
- **回報格式**：預設 3 行內，除非說「解釋」才詳細
- **授權機制**：回「OK」= 授權進行下一步

---

## 🚫 硬性禁止規則

- **禁止使用 Jacky 的 LinkedIn 帳號做任何自動化操作**（爬蟲、搜尋、發訊息等一律不得用 Jacky 個人帳號）
- **長期記憶規則**：既有內容應保留。新舊衝突時先告知 Jacky 等指示，不自行覆蓋。

---

## 三個獨立分身架構

| 代號 | Bot | 身份 | 角色 |
|------|-----|------|------|
| `YQ1` | @YuQi0923_bot | 本尊 YuQi | 程式開發、專案管理、一般任務 |
| `YQ2` | @HRyuqi_bot | HR YuQi | HR 相關、招聘、公司聯繫 |
| `YQ3` | @videoyuqi_bot | 行銷 YuQi | 短影音腳本、影片製作、社群行銷 |

**共享**：MEMORY.md、memory/日誌、skills/、TOOLS.md
**獨立**：SOUL.md（每個分身各有氣質）

日誌在 `memory/YYYY-MM-DD.md` 統一記錄，格式：`[YQ1/YQ2/YQ3] 完成 XXX`

---

## 核心技能

### YQ3（行銷 YuQi）
- 技能位置：`/Users/user/clawd/skills/installed/short-video-pro/`
- 功能：短影音腳本生成、選題、帳號定位、拍攝/剪輯建議
- 支援平台：Reels / TikTok / 小紅書

---

## 強制執行規則（從歷史教訓濃縮）

> 詳細歷史記錄見 `memory/archive-lessons.md`

1. **不編造內容** — 先讀所有相關資料，不確定就問，寧可少寫不要編造
2. **匯入資料前必做**：清理 `\n`、欄位用 `|` 分隔（內部用逗號）、測試 1 筆、驗證欄位數、確認後才批量
3. **禁止 `gog sheets update "A2" "$DATA"` 整行更新**（逗號會被當換行，會炸）→ 用逐欄更新
4. **Email 必須轉 HTML 或純文字**，不能直接發 markdown 格式
5. **sub-agent 完成後必須驗證檔案存在**，不能只看回報訊息
6. **每個數字、費率、合約細節都要仔細確認**，不要想當然耳
7. **服務聲明只列實際提供的服務**，不為了好聽而誇大

---

## LinkedIn 自動發布職缺規則（2026-02-16）

- App: "jacky 行銷貼文用" (Client ID: 869d8fxxyre7ul)
- Access Token 有效期: 60 天（2026-04-17 過期）
- 腳本：`/Users/user/clawd/hr-tools/linkedin-post-job-anonymous.py`

**發布規則**：所有職缺必須匿名、派遣職缺必須標注、自動偵測節日加問候語

**匿名化**：遊戲公司→"知名遊戲公司"、科技公司→"科技公司"/"AI科技公司"、製造業→"製造業集團"、其他→"知名企業"

---

## 反爬蟲策略

- Layer 1：隨機延遲 2-5 秒/操作、批量間隔 120 秒/公司（≤30 次/小時）
- Layer 2：BD 用 agent-browser（低頻）、市場調查人工搜尋→AI 整理、履歷用 Gmail API

---

## 履歷處理流程（2026-02-24）🔒

**流程**：收到 PDF → 上傳 Drive（`16IOJW0jR2mBgzBnc5QI_jEHcRBw3VnKj`）→ 深度解析 → 更新履歷池
**檔名**：`{姓名}-{應徵公司}.pdf`（公司由 AI 跟顧問確認）
**帳號**：aijessie88@step1ne.com

### 匯入標準（20 欄）
```
姓名|Email|電話|地點|目前職位|總年資(年)|轉職次數|平均任職(月)|最近gap(月)|技能|學歷|來源|工作經歷JSON|離職原因|穩定性評分|學歷JSON|DISC/Big Five|狀態|獵頭顧問|備註
```
- 欄位間用 `|`，欄位內技能用逗號（`PLM, PDM, MAX`）
- 使用 `update` 而非 `append`
- 資料必須單行（無換行符號）
- 腳本：`/Users/user/clawd/projects/step1ne-headhunter-skill/skills/headhunter/scripts/import-resume-to-pool.sh`

---

## Email 寄送規則

**正確流程**：
- HTML 格式：`gog mail send --html --body-file xxx.html`
- 純文字：移除所有 markdown 符號

**寄信前檢查**：格式正確、附件已上傳、連結可點擊、收件人正確、主旨明確

---

## 日報設置

**每天 21:00 Taiwan Time** 發到龍蝦社群 topic 15（`-1003793194829:15`）

```
📊 日報 (YYYY-MM-DD) Jacky

✅ 完成（1-3項，每項1行）
📌 可用/交付（有就寫）
⏳ 進行中（有就寫）
🔴 卡點（有就寫）
⏭️ 明天計畫（1-2項）
```

原則：只寫結果不寫過程、每項最多1行、標記用 Jacky

YQ2/YQ3 保留舊格式日報。

---

## 常用群組

- **龍蝦社群**：`-1003793194829`（日報發送群）
- **HR AI招募自動化**：`-1003231629634`
  - Topic 4：履歷進件（含「👔 負責顧問」）
  - Topic 304：履歷池
  - Topic 319：JD列表
  - Topic 326：總覽看板（市場調查報告）
  - Topic 364：BD 開發

---

## HR 履歷 - 獵頭顧問自動標記

- Jacky（userId `8365775688`）→ 顧問 = "Jacky"
- Phoebe（username `@behe10`）→ 顧問 = "Phoebe"

---

## Phoebe 團隊成員

- Telegram: @behe10
- Pipeline 追蹤表: 1Fh6S5tSpCIacuDrCHs3mewWWqAEhTAPaNXSuQHt6Phk
- 角色: 獵頭顧問
- 專屬文檔: https://github.com/jacky6658/step1ne-headhunter-skill/blob/main/PHOEBE-AI-GUIDE.md

---

## 業務定位

- **身份**：獵頭顧問（Headhunter），不是企業內部 HR
- **無 104 企業版**，找人管道：GitHub、LinkedIn、社群、Referral、CakeResume/Yourator、Gmail 履歷進件
- 優先使用免費/開源工具，聚焦高價值活動（電話溝通、面試安排、談判協調）

---

## Step1ne 操作指南

### 主要端點
| 功能 | 方法 | 端點 |
|------|------|------|
| 所有候選人 | GET | `/api/candidates` |
| 今日新增 | GET | `/api/candidates?created_today=true` |
| 新增候選人 | POST | `/api/candidates` |
| 批量匯入 | POST | `/api/candidates/bulk` |
| 更新 Pipeline | PUT | `/api/candidates/:id/pipeline-status` |
| 局部更新 | PATCH | `/api/candidates/:id` |
| 所有職缺 | GET | `/api/jobs` |
| 主動獵才 | POST | `/api/talent-sourcing/find-candidates` |

### Pipeline 狀態值
`未開始` → `已聯繫` → `已面試` → `Offer` → `已上職` / `婉拒` / `其他`
特殊：`備選人才`（需用 PATCH）

### 候選人卡片更新 — 兩個端點嚴格分開
| 端點 | 方法 | 處理欄位 |
|------|------|---------|
| `/api/candidates/:id` | **PUT** | `status`, `notes`, `consultant`, `progressTracking`, `aiMatchResult` |
| `/api/candidates/:id` | **PATCH** | `position`, `skills`, `education`, `work_history`, `target_job_id`, `recruiter`, `talent_level`, `years` 等 |

- 不能混用：aiMatchResult 只能 PUT，target_job_id 只能 PATCH
- PUT 會覆蓋 notes：先 GET 取舊 notes 帶入
- `target_job_id` 用 snake_case
- 所有 API 呼叫帶 `actor: "Jacky-aibot"`

### 職缺狀態更新
- `PATCH /api/jobs/:id/status`，body：`{"job_status": "關閉", "actor": "Jacky-aibot"}`
- 有效值：`招募中` / `暫停` / `已滿額` / `關閉`

### 爬蟲系統
- Repo：https://github.com/jacky6658/headhunter-crawler
- Web UI：`http://localhost:5000`
- LinkedIn 4 層備援：Playwright → Google → Bing → Brave API

### OpenClaw 本地 AI API
- URL: `http://localhost:18789/v1/chat/completions`
- Token: `9b3cb3f2d661fe14d0d267a2380c3da397b4b6673539bcd7`

---

## 已簽約客戶（共 34 家）

睿聲光電、速聯 SRAM、HackMD、格拉墨科技、伊諾科技、大儀、財聖國際保險經紀人、遊悅科技、富聯國際、天旭國際科技、統一數網、睿世軟體科技、比特數字科技、布納星科技、Joint Venture、一通數位、經緯智慧科技、HTC 宏達國際電子、宏願數位（HTC 集團）、畢博科技、均一平台教育基金會、通量三維、星裕國際、蓋亞資訊、全亞國際實業、全曜財經資訊（CMoney）、眾鼎、仁大資訊、蟻力（遊戲橘子旗下）、士芃科技、律准科技、瑞典商英鉑科台灣分公司、創樂科技、優服（遊戲橘子集團共用合約）

BD 中（未簽）：志邦企業、美德醫療

---

## 通關密碼設定（2026-03-13）🔐

- 已啟用語音通關密碼保護
- Hash（SHA-256）：ce6e67e8a9550440996c32601b611d538758c88874c51ee42f9c89afd7d3f36f
- 規則：有人問敏感資料前必須先通過語音驗證
- 驗證通過：✅ 驗證通過（不重複密碼內容）
- 驗證失敗：❌ 驗證失敗，拒絕執行
