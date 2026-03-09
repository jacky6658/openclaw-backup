# 🦞 AI 使用 Step1ne 系統的完整工作說明書

**版本**：v1.0  
**日期**：2026-03-05  
**目的**：定義 AI 如何與 Step1ne 獵頭系統互動、執行日常工作、追蹤招聘進度

---

## 📊 一、系統架構概覽

### 核心數據流

```
顧問 → AI → Step1ne API → 資料庫
  ↓
候選人管理 → Pipeline 追蹤 → 評分系統 → 主動獵才 → 操作日誌
```

### 四大核心模塊

| 模塊 | 功能 | AI 角色 |
|------|------|--------|
| **1. 候選人管理** | 查詢、新增、更新、刪除 | 執行 API 調用、數據驗證 |
| **2. Pipeline 追蹤** | 7 個狀態 + 備選人才 | 自動轉移狀態、計算 SLA |
| **3. 評分系統** | 穩定度 + 綜合評級 + AI 配對結語 | 分析履歷、計算分數、生成建議 |
| **4. 主動獵才** | GitHub/LinkedIn 搜尋 + 自動匯入 | 執行爬蟲、評分、批量匯入 |

---

## 🎯 二、獵頭顧問追蹤表（Kanban 看板）

### 看板結構

```
[未開始] → [已聯繫] → [已面試] → [Offer] → [已上職]
                          ↓
                    [備選人才]
                          ↓
                       [婉拒]
```

### 欄位說明

| 欄位 | 資料來源 | AI 作用 |
|------|---------|--------|
| **未開始** | `status="未開始"` | 新增候選人、評分、生成建議 |
| **今日新增** | `createdAt` 日期 == 今天 | 自動提醒、優先評分 |
| **已聯繫** | 已呼叫/寄信候選人 | 追蹤 3 天 SLA、提醒跟進 |
| **已面試** | 完成面試 | 追蹤 7 天 SLA、協助評估 |
| **Offer** | 發出 Offer | 追蹤 5 天 SLA、協議簽署 |
| **已上職** | 候選人到職 | 標記完成、統計成功率 |
| **備選人才** | `status="備選人才" && talent_level != ""` | 納入備選庫、定期更新 |
| **婉拒** | 候選人/客戶拒絕 | 記錄原因、分析改進點 |

### SLA（Service Level Agreement）

| 狀態 | 允許停留天數 | AI 監控 |
|------|-------------|--------|
| 未開始 | 2 天 | ⚠️ 超過 2 天未評分 → 提醒 |
| 已聯繫 | 3 天 | ⚠️ 超過 3 天未回應 → 催促 |
| 已面試 | 7 天 | ⚠️ 超過 7 天未決定 → 進度確認 |
| Offer | 5 天 | ⚠️ 超過 5 天未簽署 → 跟進 |
| 已上職 | 完成 | ✅ 成功標記 |

---

## 🤖 三、AI 的四大工作職責

### 職責 1：日常候選人管理

**觸發時機**：收到履歷（Email / Telegram）或顧問上傳

**工作流程**：
```
1. 新增候選人
   → POST /api/candidates
   → 提取姓名、郵件、年資、技能、教育背景

2. 分析並評分
   → 計算 stability_score（工作穩定度）
   → 計算 talent_level（綜合評級 S/A+/A/B/C）
   → 撰寫 AI 分析摘要

3. 寫回系統
   → PATCH /api/candidates/:id
   → stability_score, talent_level, notes, ai_match_result

4. 生成建議
   → 推薦職缺
   → 列出優勢 + 缺點
   → 提示面試重點
```

**責任方**：AI（自動化，無需顧問干預）

---

### 職責 2：Pipeline 進度追蹤

**觸發時機**：顧問更新狀態或 AI 檢測到 SLA 逾期

**工作流程**：
```
1. 每日掃描（晨間檢查）
   → GET /api/candidates?limit=1000
   → 檢查所有候選人的 progressTracking 最後事件日期
   → 比對 SLA 閾值

2. SLA 監控邏輯
   if (今天 - lastEvent.date) > SLA_THRESHOLD:
     → 發送警告通知
     → 自動寄信提醒 / Telegram 提示

3. 狀態轉移
   → 接收顧問指令（「這個人已面試」）
   → PUT /api/candidates/:id/pipeline-status
   → 自動記錄日期 + 操作者 + 進度事件

4. 生成日報
   → 統計各狀態候選人數
   → 計算招聘漏斗進度
   → 識別瓶頸（哪些狀態卡最多人）
```

**責任方**：AI（自動化監控 + 定時提醒）

---

### 職責 3：AI 配對評分

**觸發時機**：候選人進入「未開始」狀態

**工作流程**：
```
1. 取得職缺資訊
   → GET /api/jobs
   → 找到候選人對應的職缺
   → 讀取 job_description, talent_profile, company_profile

2. 五維度評分
   ├─ 人才畫像符合度（40%）
   ├─ JD 職責匹配度（30%）
   ├─ 公司適配性（15%）
   ├─ 可觸達性（10%）
   └─ 活躍信號（5%）
   → 產出綜合分數（0-100）

3. 撰寫配對結語
   → ai_match_result JSON 物件
   → 包含：score, recommendation, matched_skills, strengths, 
     missing_skills, probing_questions, conclusion

4. 寫回系統
   → PATCH /api/candidates/:id
   → 含 ai_match_result + status 轉移（AI推薦 或 備選人才）

5. 生成推薦清單
   → TOP 3 優先聯繫排序
   → 切入點（如何開口）
   → 風險提示（缺口、待確認項）
```

**責任方**：AI（自動化評分 + 生成建議）

---

### 職責 4：主動獵才

**觸發時機**：顧問說「幫我找 XX 公司的 YY 職位人選」

**工作流程**：
```
1. 取得搜尋資訊
   → 確認公司名、職位名
   → GET /api/users/{顧問}/contact
   → 取得 GitHub Token + Brave API Key

2. 執行搜尋
   → GitHub 搜尋（2-3 頁）
   → LinkedIn 搜尋（透過 Google / Brave）
   → 提取候選人資訊（姓名、URL、技能）

3. 去重 + 驗證
   → 比對系統現有候選人
   → 檢查資料完整性
   → 過濾垃圾資訊

4. AI 評分
   → 計算每位候選人評分
   → 評級排序（S → A+ → A → B → C）

5. 批量匯入
   → POST /api/candidates/bulk
   → 寫入技能、LinkedIn URL、GitHub URL

6. 生成報告
   → 已匯入 N 位、略過 M 位
   → TOP 3 優先推薦（名字、分數、切入點）
   → 其他備選
```

**責任方**：AI（完全自動化）

---

## 📋 四、實際工作說明書（Daily Operations）

### 晨間檢查（08:00-09:00）

```
✅ 執行清單

1. 系統健康檢查
   → GET /api/health
   → 確認系統可用

2. 掃描 SLA 逾期候選人
   → GET /api/candidates?limit=1000
   → 查找停留超時的候選人
   → 生成警告清單

3. 評分今日新增
   → GET /api/candidates?created_today=true
   → 篩選 status="未開始" 的候選人
   → 逐一評分並寫回系統

4. 生成每日匯報
   → 昨日新增 N 人
   → 今日待評分 M 人
   → SLA 逾期 K 人
   → 推送到龍蝦社群 topic 15

5. 通知顧問
   → Telegram 提醒：「今日有 3 人 SLA 即將逾期」
   → 推薦優先跟進的候選人
```

---

### 常規操作（10:00-17:00）

```
✅ 當顧問說「新增候選人王小明」

1. 新增候選人
   → POST /api/candidates
   → 填入基本資訊

2. 分析評分
   → 讀取履歷（提供的或爬取的）
   → 計算 stability_score + talent_level
   → 撰寫 AI 分析摘要

3. 寫入系統
   → PATCH /api/candidates/:id
   → 更新評分 + 備註

4. 生成建議
   → 推薦最適合的職缺
   → 提示面試要點

回應格式：
「✅ 已新增王小明（ID: 2345）
📊 評分：A 級（78分）
🎯 推薦職缺：Java Backend Engineer (XYZ 公司)
⚡ 優勢：8年後端經驗，AWS 認證...
⚠️ 待確認：離職動機、期望薪資...」

---

✅ 當顧問說「幫我找一通數位的 Java Developer」

1. 取得搜尋權限
   → GET /api/users/Jacky/contact
   → 獲得 GitHub Token + Brave API Key

2. 執行獵才
   → POST /api/talent-sourcing/find-candidates
   → company: "一通數位", jobTitle: "Java Developer"

3. 處理結果
   → 已匯入 8 位、略過 2 位重複
   → 自動評分完成

4. 生成推薦清單
   → TOP 3 候選人（名字、分數、切入點）

回應格式：
「✅ 已完成搜尋！匯入 8 位新候選人

🥇 TOP 1: John Chen (A+, 88分)
   技能：Java, Spring Boot, Docker
   切入點：「Fintech 後端機會，技術棧完全對口」

🥈 TOP 2: Amy Lin (A, 78分)
   技能：Java, Kubernetes
   切入點：「遠端彈性工作，加班補償優」

...其他 6 位已存入備選庫
📊 前往系統查看完整名單」

---

✅ 當顧問說「把 ID 123、124、125 改成已面試」

1. 批量更新狀態
   → PATCH /api/candidates/batch-status
   → ids: [123, 124, 125], status: "已面試"

2. 自動記錄
   → 系統自動在 progressTracking 新增事件
   → 記錄日期 + 操作者 + 新狀態

3. 確認完成
   → 「✅ 已將 3 位候選人轉為「已面試」狀態」
```

---

### 傍晚總結（17:00-18:00）

```
✅ 每日收尾工作

1. 重新掃描 SLA
   → 統計各狀態停留時間
   → 識別急迫項（明日即將逾期的）

2. 生成日報
   → 完成數：X 位
   → 進行中：Y 位
   → SLA 逾期：Z 位
   → 推送到龍蝦社群 + 發財基地

3. 數據備份
   → 匯出 candidates 清單
   → 保存日報副本

4. 準備明日
   → 預先列出明日待評分候選人
   → 預警即將逾期 SLA
```

---

## 🔧 五、系統使用規則（Golden Rules）

### 必遵守規則

| 規則 | 說明 | 違反後果 |
|------|------|--------|
| **Rule 1：身份識別** | 所有 API 呼叫必須帶入 `actor="{顧問}-aibot"` | 日誌無法追蹤、系統判定為手動操作 |
| **Rule 2：狀態轉移** | 只能用 `PUT /pipeline-status`，不能直接改 status 欄位 | 進度事件遺失、看板顯示錯誤 |
| **Rule 3：備註追加** | `notes` 欄位是整個覆蓋，不能直接追加 | 舊資訊遺失 |
| **Rule 4：備選人才** | 必須同時更新 status + talent_level + progressTracking 三個欄位 | 候選人卡片消失在看板 |
| **Rule 5：去重檢查** | 新增前必須先搜尋，避免重複 | 系統數據混亂、漏斗變形 |
| **Rule 6：API 認證** | 某些功能需要顧問提供 Token（GitHub / Brave） | 搜尋失敗、速率限制 |

---

### 常見錯誤 & 修正

```
❌ 錯誤 1：直接改 status 欄位
PATCH /candidates/123 {"status": "已面試"}

✅ 正確做法：
PUT /candidates/123/pipeline-status {"status": "已面試", "by": "Jacky-aibot"}

---

❌ 錯誤 2：覆蓋 notes 後丟失舊資訊
PATCH /candidates/123 {"notes": "新備註"}

✅ 正確做法：
GET /candidates/123
# 讀取現有 notes
# 追加新資訊：notes = 舊 + "\n[2026-03-05] Jacky-aibot：新備註"
PATCH /candidates/123 {"notes": notes}

---

❌ 錯誤 3：備選人才只改 status 和 talent_level
PATCH /candidates/123 {"status": "備選人才", "talent_level": "B"}

✅ 正確做法：
GET /candidates/123
# 讀取現有 progressTracking
# 追加新事件：{event: "備選人才", date: today, by: "Jacky-aibot"}
PATCH /candidates/123 {
  "status": "備選人才",
  "talent_level": "B",
  "progressTracking": [..., {event: "備選人才", ...}],
  "actor": "Jacky-aibot"
}

---

❌ 錯誤 4：匯入新候選人沒檢查是否已存在
POST /candidates/bulk [王小明, 李大華, ...]

✅ 正確做法：
GET /candidates?limit=1000
# 逐一檢查候選人是否已存在
# 去重後再 POST

---

❌ 錯誤 5：AI 配對評分只提供分數，沒有配對結語
PATCH /candidates/123 {"talent_level": "A+", "stability_score": 82}

✅ 正確做法：
PATCH /candidates/123 {
  "talent_level": "A+",
  "stability_score": 82,
  "ai_match_result": {
    "score": 87,
    "recommendation": "推薦",
    "job_title": "Java Developer",
    "matched_skills": [...],
    "strengths": [...],
    "probing_questions": [...],
    "conclusion": "...",
    "evaluated_at": "...",
    "evaluated_by": "Jacky-aibot"
  }
}
```

---

## 📊 六、建議工作方案（推薦架構）

### 方案 A：完全自動化（推薦 ⭐⭐⭐）

**模式**：AI 主動監控 + 自動化執行

**優點**：
- ✅ 最小化顧問操作
- ✅ 無遺漏（自動提醒 SLA）
- ✅ 實時反饋

**缺點**：
- ❌ 需要預先配置規則
- ❌ 異常情況需要 fallback

**工作流程**：
```
Cron 08:00
  → 掃描 SLA + 評分今日新增 + 生成日報

Cron 17:00
  → 傍晚總結 + 明日預告

即時觸發（Telegram/Email）
  → 新增履歷 → AI 自動評分 → 推送建議
  → 「幫我找 XX」 → AI 自動獵才 → 推送名單
  → 顧問更新狀態 → AI 自動記錄 + 追蹤 SLA

實時監控
  → 發現 SLA 逾期 → Telegram 警告
  → 發現重複候選人 → 自動去重
```

**實施難度**：⭐⭐⭐（中等）

---

### 方案 B：半自動化（次選 ⭐⭐）

**模式**：AI 執行 + 顧問確認

**優點**：
- ✅ 保留人工控制
- ✅ 更好的容錯

**缺點**：
- ❌ 依賴顧問反饋
- ❌ 可能遺漏

**工作流程**：
```
AI 提供建議
  → 「發現 SLA 逾期的候選人：
      1. 王小明（已聯繫，逾期 1 天）→ 建議催促
      2. 李大華（已面試，逾期 2 天）→ 建議決策
     需要我自動跟進嗎？」

顧問確認
  → 「好，幫我跟進」 → AI 自動執行
  → 「先不用，明天再說」 → AI 等待

實時操作
  → 新增履歷時 AI 提提建議，顧問 OK 後執行
```

**實施難度**：⭐（簡單）

---

### 方案 C：按需手動（保守 ⭐）

**模式**：顧問主動要求 → AI 執行

**優點**：
- ✅ 完全由顧問控制
- ✅ 無自動化風險

**缺點**：
- ❌ 容易遺漏
- ❌ 增加顧問工作量

**工作流程**：
```
顧問主動操作
  → 「評分一下這份履歷」 → AI 評分
  → 「幫我找 XX 的人」 → AI 獵才
  → 「更新候選人進度」 → AI 記錄

AI 無主動行動
  → 除非顧問明確要求
```

**實施難度**：⭐（最簡單）

---

## 🎯 七、推薦實施方案（針對 Jacky）

基於你的需求，我建議 **方案 A + 方案 B 混合**：

```
日常工作（自動化）
├─ 08:00 自動掃描 + 評分 + 日報
├─ 17:00 傍晚總結
└─ 全天監控 SLA + 警告

臨時需求（半自動化）
├─ 新增履歷 → AI 建議 → Jacky OK → 自動執行
├─ 「幫我找 XX」 → AI 確認細節 → 執行搜尋 → 推薦名單
└─ 状態更新 → AI 自動追蹤 + SLA 監控

零碎操作（手動）
├─ 一時查詢（某候選人資料）
└─ 特殊調整（特例處理）
```

**預期效果**：
- 📊 80% 工作自動化，減輕顧問 80% 低價值工作
- ⚡ 實時 SLA 監控，無遺漏
- 💡 AI 智能建議，加快決策速度
- 📈 數據自動彙總，易於分析

---

## ✅ 八、實施檢查清單

### 準備工作

- [ ] 確認 AI 身份（Jacky-aibot？）
- [ ] 配置 GitHub Token（用於獵才）
- [ ] 配置 Brave API Key（用於搜尋）
- [ ] 讀完 API 指南 + 評分規則
- [ ] 設置 Cron 定時任務（晨間 + 傍晚）
- [ ] 配置 Telegram 通知頻道

### 首週測試

- [ ] 手動新增 3 位候選人，測試評分流程
- [ ] 執行 1 次獵才測試（小規模）
- [ ] 驗證 SLA 監控邏輯
- [ ] 檢查日報格式 + 推送時間
- [ ] 測試 Telegram 通知

### 正式上線

- [ ] 啟動自動評分 Cron
- [ ] 啟動 SLA 監控 Cron
- [ ] 啟動日報推送 Cron
- [ ] 與顧問溝通工作流程
- [ ] 定期檢查系統日誌

---

**下一步**：你想先選哪個方案實施？我可以幫你詳細規劃 Cron 腳本 + API 呼叫邏輯。
