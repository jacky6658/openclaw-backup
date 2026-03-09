# Step1ne 候選人卡片 API 操作指南

> **API Base URL**: `https://backendstep1ne.zeabur.app` (生產) / `http://localhost:3001` (本地開發)
>
> **最後更新**: 2026-03-05

---

## 目錄

1. [候選人狀態 (CandidateStatus)](#1-候選人狀態)
2. [移動卡片 — 單筆狀態更新 API](#2-移動卡片--單筆狀態更新)
3. [移動卡片 — 批量狀態更新 API](#3-移動卡片--批量狀態更新)
4. [匯入候選人 — 單筆 API](#4-匯入候選人--單筆)
5. [匯入候選人 — 批量 API](#5-匯入候選人--批量)
6. [更新候選人 — PATCH API](#6-更新候選人--patch)
7. [候選人完整欄位對照表](#7-候選人完整欄位對照表)
8. [JSONB 欄位結構說明](#8-jsonb-欄位結構說明)
9. [系統日誌 (Audit Trail)](#9-系統日誌)
10. [完整 curl 範例](#10-完整-curl-範例)

---

## 1. 候選人狀態

### CandidateStatus 列舉

| 狀態值 | Enum Key | 說明 | Kanban 看板欄位 |
|--------|----------|------|----------------|
| `未開始` | NOT_STARTED | 新匯入，尚未處理 | 未開始 |
| `AI推薦` | AI_RECOMMENDED | AI 自動推薦 | AI推薦 |
| `聯繫階段` | CONTACTED | 已聯繫候選人 | 聯繫階段 |
| `面試階段` | INTERVIEWED | 安排或進行面試 | 面試階段 |
| `Offer` | OFFER | 已發 Offer | Offer |
| `on board` | ONBOARDED | 已報到上班 | on board |
| `婉拒` | REJECTED | 候選人或公司婉拒 | 婉拒 |
| `備選人才` | OTHER | 暫時保留觀望 | 備選人才 |

### 移動規則

- 今日新增欄位是**唯讀**自動欄位，不可手動移入
- 卡片可在上述 8 個狀態之間**自由移動**（無固定順序限制）
- 移動到「婉拒」時，可附帶 `notes` 記錄婉拒原因
- 每次移動會自動記錄到 `progress_tracking` 陣列 + `system_logs` 審計表

---

## 2. 移動卡片 — 單筆狀態更新

### `PUT /api/candidates/:id/pipeline-status`

**用途**: 更新單一候選人的 Pipeline 狀態（給 AIbot 及外部系統使用）

**Request**:

```http
PUT /api/candidates/123/pipeline-status
Content-Type: application/json

{
  "status": "聯繫階段",
  "by": "Jacky"
}
```

| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `status` | string | ✅ | 目標狀態（見上方 8 個合法值） |
| `by` | string | 選填 | 操作者名稱（顧問名或 AIbot 名稱），預設 "system" |
| `notes` | string | 選填 | 附加備註（移到「婉拒」時可記錄原因） |

**Response** (200):

```json
{
  "success": true,
  "data": {
    "id": 123,
    "name": "John Doe",
    "status": "聯繫階段",
    "progress_tracking": [
      { "date": "2026-03-01", "event": "未開始", "by": "system" },
      { "date": "2026-03-05", "event": "聯繫階段", "by": "Jacky" }
    ]
  },
  "message": "Pipeline 狀態已更新為「聯繫階段」"
}
```

**Error Responses**:

| 狀態碼 | 情況 |
|--------|------|
| 400 | status 不在合法值內 |
| 404 | 找不到該候選人 |
| 500 | 伺服器錯誤 |

**自動副作用**:
1. 自動在 `progress_tracking` JSONB 陣列尾端 append 一筆記錄
2. 寫入 `system_logs` 表（action = `PIPELINE_CHANGE`）

---

## 3. 移動卡片 — 批量狀態更新

### `PATCH /api/candidates/batch-status`

**用途**: 一次更新多位候選人的狀態（批量操作）

**Request**:

```http
PATCH /api/candidates/batch-status
Content-Type: application/json

{
  "ids": [123, 124, 125],
  "status": "面試階段",
  "actor": "Jacky-aibot",
  "note": "批量完成初篩面試"
}
```

| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `ids` | number[] | ✅ | 候選人 ID 陣列（最多 200 筆） |
| `status` | string | ✅ | 目標狀態 |
| `actor` | string | 選填 | 操作者，預設 "AIbot" |
| `note` | string | 選填 | 備註，會附加到每筆 progress_tracking |

**Response** (200):

```json
{
  "success": true,
  "status": "面試階段",
  "succeeded_count": 2,
  "failed_count": 1,
  "total": 3,
  "succeeded": [
    { "id": 123, "name": "John Doe" },
    { "id": 124, "name": "Jane Smith" }
  ],
  "failed": [
    { "id": 999, "reason": "找不到此候選人" }
  ],
  "message": "批量更新完成：2 位成功，1 位失敗"
}
```

**限制**:
- 單次最多 200 筆
- 如有找不到的 ID，不影響其他成功的更新

---

## 4. 匯入候選人 — 單筆

### `POST /api/candidates`

**用途**: 智慧匯入單一候選人（重複姓名自動合併補充）

**Request**:

```http
POST /api/candidates
Content-Type: application/json

{
  "name": "Alice Johnson",
  "email": "alice@example.com",
  "phone": "0912345678",
  "location": "Taipei",
  "current_position": "Frontend Engineer",
  "years_experience": "5",
  "skills": "React、TypeScript、CSS",
  "source": "LinkedIn",
  "status": "聯繫階段",
  "recruiter": "Jacky",
  "talent_level": "A",
  "actor": "Jacky"
}
```

**完整欄位列表** — 見 [第 7 節](#7-候選人完整欄位對照表)

**行為**:
- **姓名不存在** → 建立新記錄 (status=201, action="created")
- **姓名已存在** → 僅補充空白欄位，不覆蓋已有值 (status=200, action="updated")

**Response** (201 / 200):

```json
{
  "success": true,
  "action": "created",
  "data": {
    "id": 456,
    "name": "Alice Johnson",
    "status": "聯繫階段"
  },
  "message": "新增候選人：Alice Johnson"
}
```

---

## 5. 匯入候選人 — 批量

### `POST /api/candidates/bulk`

**用途**: 批量匯入多位候選人

**Request**:

```http
POST /api/candidates/bulk
Content-Type: application/json

{
  "candidates": [
    {
      "name": "Bob Smith",
      "email": "bob@example.com",
      "current_position": "Backend Engineer",
      "skills": "Python、Go、PostgreSQL",
      "source": "GitHub"
    },
    {
      "name": "Carol Davis",
      "email": "carol@example.com",
      "current_position": "QA Engineer",
      "skills": "Selenium、Cypress",
      "source": "LinkedIn"
    }
  ],
  "actor": "AIbot-Phoebe"
}
```

| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `candidates` | object[] | ✅ | 候選人陣列（每筆同 POST /api/candidates 格式） |
| `actor` | string | 選填 | 操作者，預設 "AIbot" |

**限制**: 單次最多 100 筆

**Response** (200):

```json
{
  "success": true,
  "message": "匯入完成：新增 2 筆，補充更新 1 筆，失敗 0 筆（共 3 筆）",
  "created_count": 2,
  "updated_count": 1,
  "failed_count": 0,
  "data": {
    "created": [
      { "id": 456, "name": "Bob Smith" },
      { "id": 457, "name": "Carol Davis" }
    ],
    "updated": []
  },
  "failed": []
}
```

---

## 6. 更新候選人 — PATCH

### `PATCH /api/candidates/:id`

**用途**: 部分更新候選人資料（只更新提供的欄位，未提供的保持不變）

**Request**:

```http
PATCH /api/candidates/123
Content-Type: application/json

{
  "status": "面試階段",
  "notes": "已完成初篩電話面試",
  "recruiter": "Jacky",
  "talent_level": "A",
  "actor": "Jacky"
}
```

**欄位名稱彈性支援**（camelCase / snake_case 皆可）:

| 可用名稱 | 對應 DB 欄位 |
|----------|-------------|
| `notes` 或 `remarks` | notes |
| `linkedin_url` 或 `linkedinUrl` | linkedin_url |
| `github_url` 或 `githubUrl` | github_url |
| `position` 或 `current_position` | current_position |
| `years` 或 `years_experience` | years_experience |
| `by` 或 `actor` | actor (用於日誌) |

**自動行為**:
- 若只傳 `status`（不傳 `progressTracking`），系統自動在 `progress_tracking` 追加事件
- 偵測 AIBot actor 名稱 (`/aibot|bot$/i`) 自動標記 actor_type

---

## 7. 候選人完整欄位對照表

### candidates_pipeline 資料表

| 欄位 | 類型 | 預設值 | 必填 | 說明 |
|------|------|--------|------|------|
| `id` | SERIAL | 自動遞增 | — | 主鍵 |
| `name` | VARCHAR(255) | — | ✅ | 候選人姓名（唯一識別用） |
| `phone` | VARCHAR | "" | | 電話 |
| `email` | VARCHAR(255) | "" | | Email |
| `linkedin_url` | VARCHAR(500) | "" | | LinkedIn 連結 |
| `github_url` | VARCHAR(500) | "" | | GitHub 連結 |
| `contact_link` | VARCHAR | "" | | 其他聯繫連結 |
| `location` | VARCHAR | "" | | 所在地區 |
| `current_position` | VARCHAR | "" | | 現任職稱 |
| `years_experience` | VARCHAR | "0" | | 年資 |
| `skills` | TEXT | "" | | 技能（用「、」分隔） |
| `education` | VARCHAR | "" | | 學歷摘要 |
| `source` | VARCHAR | "GitHub" | | 來源管道 |
| `status` | VARCHAR(100) | "未開始" | | Pipeline 狀態 |
| `recruiter` | VARCHAR | "Jacky" | | 負責顧問 |
| `notes` | TEXT | "" | | 備註 |
| `stability_score` | VARCHAR | "0" | | 穩定度分數 |
| `personality_type` | VARCHAR | "" | | DISC 人格類型 |
| `job_changes` | VARCHAR | "0" | | 換工作次數 |
| `avg_tenure_months` | VARCHAR | "0" | | 平均任職月數 |
| `recent_gap_months` | VARCHAR | "0" | | 近期空窗月數 |
| `work_history` | JSONB | null | | 工作經歷（見下方結構） |
| `education_details` | JSONB | null | | 教育經歷（見下方結構） |
| `leaving_reason` | VARCHAR | "" | | 離職原因 |
| `talent_level` | VARCHAR | "" | | 人才等級 (A/B/C/S) |
| `ai_match_result` | JSONB | null | | AI 配對評估結果 |
| `target_job_id` | INTEGER | null | | 目標職缺 ID (FK → jobs_pipeline.id) |
| `progress_tracking` | JSONB | '[]' | | 進度追蹤事件陣列 |
| `created_at` | TIMESTAMP | NOW() | | 建立時間 |
| `updated_at` | TIMESTAMP | NOW() | | 更新時間 |

---

## 8. JSONB 欄位結構說明

### progress_tracking — 進度追蹤

```json
[
  {
    "date": "2026-03-01",
    "event": "未開始",
    "by": "system"
  },
  {
    "date": "2026-03-03",
    "event": "聯繫階段",
    "by": "Jacky",
    "note": "已電話聯繫，候選人有興趣"
  },
  {
    "date": "2026-03-05",
    "event": "面試階段",
    "by": "Jacky"
  }
]
```

| 欄位 | 類型 | 說明 |
|------|------|------|
| `date` | string | 日期 (YYYY-MM-DD) |
| `event` | string | 狀態事件（對應 CandidateStatus 值） |
| `by` | string | 操作者（顧問名或 AIbot 名稱） |
| `note` | string | 選填備註 |

---

### work_history — 工作經歷

```json
[
  {
    "company": "台積電",
    "title": "Senior Backend Engineer",
    "start": "2020-01",
    "end": "2022-06",
    "duration_months": 30,
    "location": "Hsinchu",
    "description": "Led microservices migration project"
  }
]
```

---

### education_details — 教育經歷

```json
[
  {
    "school": "國立台灣大學",
    "degree": "Bachelor",
    "major": "Computer Science",
    "start": "2012",
    "end": "2016",
    "gpa": 3.8
  }
]
```

---

### ai_match_result — AI 配對評估

```json
{
  "score": 88,
  "recommendation": "強力推薦",
  "job_id": 5,
  "job_title": "Senior Backend Engineer",
  "matched_skills": ["Python", "JavaScript", "React"],
  "missing_skills": ["Go", "Kubernetes"],
  "required_skills_count": 5,
  "strengths": ["10+ years experience", "Strong system design"],
  "probing_questions": ["Experience with distributed systems?"],
  "salary_fit": "Expected salary within budget",
  "conclusion": "Excellent fit for the role with minor skill gaps",
  "evaluated_at": "2026-03-05T12:30:00Z",
  "evaluated_by": "AIBot-Jacky"
}
```

| recommendation 值 | 說明 |
|-------------------|------|
| `強力推薦` | 高度符合 |
| `推薦` | 符合 |
| `觀望` | 部分符合 |
| `不推薦` | 不符合 |

---

## 9. 系統日誌

所有 API 操作自動記錄到 `system_logs` 表。

### 日誌 action 類型

| Action | 觸發來源 | 說明 |
|--------|---------|------|
| `PIPELINE_CHANGE` | PUT pipeline-status, PATCH with status | 狀態變更 |
| `UPDATE` | PATCH candidates/:id | 欄位更新 |
| `IMPORT_CREATE` | POST candidates | 新增候選人 |
| `IMPORT_UPDATE` | POST candidates (重複姓名) | 補充更新 |
| `BULK_IMPORT` | POST candidates/bulk | 批量匯入 |
| `DELETE` | DELETE candidates/:id | 刪除候選人 |

### 日誌結構

```json
{
  "id": 1001,
  "action": "PIPELINE_CHANGE",
  "actor": "Jacky",
  "actor_type": "HUMAN",
  "candidate_id": 123,
  "candidate_name": "John Doe",
  "detail": {
    "from": "聯繫階段",
    "to": "面試階段"
  },
  "created_at": "2026-03-05T08:30:00Z"
}
```

---

## 10. 完整 curl 範例

### 範例 1: 移動卡片（單筆）

```bash
curl -X PUT https://backendstep1ne.zeabur.app/api/candidates/123/pipeline-status \
  -H "Content-Type: application/json" \
  -d '{
    "status": "面試階段",
    "by": "Jacky"
  }'
```

### 範例 2: 批量移動卡片

```bash
curl -X PATCH https://backendstep1ne.zeabur.app/api/candidates/batch-status \
  -H "Content-Type: application/json" \
  -d '{
    "ids": [123, 124, 125],
    "status": "聯繫階段",
    "actor": "Jacky-aibot",
    "note": "已完成初步篩選"
  }'
```

### 範例 3: 匯入單一候選人

```bash
curl -X POST https://backendstep1ne.zeabur.app/api/candidates \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "phone": "0912345678",
    "location": "Taipei",
    "current_position": "Frontend Engineer",
    "years_experience": "5",
    "skills": "React、TypeScript、CSS",
    "source": "LinkedIn",
    "status": "聯繫階段",
    "recruiter": "Jacky",
    "talent_level": "A",
    "actor": "Jacky"
  }'
```

### 範例 4: 批量匯入候選人

```bash
curl -X POST https://backendstep1ne.zeabur.app/api/candidates/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "candidates": [
      {
        "name": "Bob Smith",
        "email": "bob@example.com",
        "current_position": "Backend Engineer",
        "skills": "Python、Go、PostgreSQL",
        "source": "GitHub",
        "recruiter": "Phoebe"
      },
      {
        "name": "Carol Davis",
        "email": "carol@example.com",
        "current_position": "QA Engineer",
        "skills": "Selenium、Cypress",
        "source": "LinkedIn",
        "recruiter": "Jacky"
      }
    ],
    "actor": "AIbot-Phoebe"
  }'
```

### 範例 5: 部分更新候選人

```bash
curl -X PATCH https://backendstep1ne.zeabur.app/api/candidates/123 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "Offer",
    "notes": "2026-03-05 已發 Offer，待回覆",
    "talent_level": "A",
    "actor": "Jacky"
  }'
```

### 範例 6: 匯入帶 AI 評估結果的候選人

```bash
curl -X POST https://backendstep1ne.zeabur.app/api/candidates \
  -H "Content-Type: application/json" \
  -d '{
    "name": "David Lee",
    "email": "david@example.com",
    "current_position": "Senior DevOps Engineer",
    "years_experience": "8",
    "skills": "Docker、Kubernetes、AWS、Terraform、Jenkins",
    "source": "GitHub",
    "recruiter": "Jacky",
    "target_job_id": 5,
    "ai_match_result": {
      "score": 92,
      "recommendation": "強力推薦",
      "job_id": 5,
      "job_title": "DevOps Lead",
      "matched_skills": ["Docker", "Kubernetes", "AWS", "Terraform"],
      "missing_skills": ["Azure"],
      "strengths": ["8 years DevOps experience", "Strong cloud infrastructure background"],
      "probing_questions": ["Multi-cloud strategy experience?"],
      "conclusion": "Top candidate with comprehensive DevOps expertise"
    },
    "work_history": [
      {
        "company": "Trend Micro",
        "title": "Senior DevOps Engineer",
        "start": "2022-03",
        "end": "present",
        "duration_months": 36,
        "location": "Taipei"
      }
    ],
    "actor": "AIbot-Jacky"
  }'
```

---

> 📌 **注意事項**:
> - 所有 API 回傳 JSON 格式，`Content-Type: application/json`
> - 候選人姓名為唯一識別（大小寫不敏感），重複匯入自動合併
> - `status` 值必須完全匹配上方 8 個合法值之一
> - `progress_tracking` 陣列為自動追蹤，一般不需手動傳入
> - 批量操作有數量限制：匯入 100 筆/次、狀態更新 200 筆/次
