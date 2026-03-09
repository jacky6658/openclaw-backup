# 履歷處理標準流程 SOP（通用版）
> 最後更新：2026-03-04
> 適用：YuQi HR AI 及所有接手此流程的 AI Agent

---

## 📌 當前職缺設定（由人類顧問填入）

> ⚠️ 每次啟用新職缺前，先填好此區。AI 依此區參數執行篩選。

| 項目 | 填入值 |
|------|--------|
| 公司名稱 | `{公司名稱}` |
| 職缺 ID | `{job_id}` |
| 職位名稱 | `{職位名稱}` |
| 相關工作定義 | `{例：Java 後端開發、SRE/DevOps 運維}` |
| 最低段數 | `≥ {N} 段` |
| 最短年資 | `每段 ≥ {N} 年` |
| 中階薪資水位 | `{N} 萬` |
| 高階薪資水位 | `{N} 萬` |
| 加分條件 | `{例：特定技術棧、特定產業背景、特定前雇主}` |
| 禁忌條件 | `{例：不挖客戶現有員工、不接受特定產業}` |

---

## 📌 系統基本設定

| 項目 | 值 |
|------|-----|
| API Base URL | `https://backendstep1ne.zeabur.app` |
| Actor Header | `X-Actor: Jacky-aibot`（所有 POST 必須帶） |
| Google Drive 帳號 | `aijessie88@step1ne.com` |
| 履歷雲端資料夾 | `https://drive.google.com/drive/folders/16IOJW0jR2mBgzBnc5QI_jEHcRBw3VnKj` |

---

## 🔄 標準流程（5步驟）

### Step 1｜收到 PDF → 查重複
```bash
curl "https://backendstep1ne.zeabur.app/api/candidates?q=姓名" \
  -H "X-Actor: Jacky-aibot"
```
- ✅ 無重複 → 繼續 Step 2
- ⚠️ 已存在 → 告知顧問 ID + 現有狀態，詢問是否更新

### Step 2｜分析履歷 → 送人條件檢核

**送人條件（依上方「當前職缺設定」填入，硬性，缺一不可）：**
- ≥ `{最低段數}` 段 `{相關工作定義}` 工作經驗
- 每段 ≥ `{最短年資}` 年
- 薪資水位：中階 `{N}` 萬 / 高階 `{N}` 萬

**加分項（依職缺設定填入）：**
- `{加分條件 1}`
- `{加分條件 2}`
- `{加分條件 3}`

**禁忌條件（依職缺設定填入）：**
- `{禁忌條件 1}`

**不符合條件 → 建議備選人才（consultant=待指派）**

### ⚠️ AI推薦人選必填規範（2026-03-04 Jacky 確認）

每位 **AI推薦** 人選的 `ai_match_result` 必須包含：

**1. 推薦原因（match_reason）— 明確列出 5 點**
```
1. [技術匹配點]：具體技能/工具與職缺需求的對應
2. [產業/背景匹配]：相關產業或業務場景經驗
3. [年資/段數符合]：工作段數與年資說明
4. [加分條件]：超出基本要求的亮點
5. [綜合評估]：整體推薦理由與信心說明
```

**2. 針對此職缺的確認問題（probing_questions）— 至少 3 題**
```
- 針對技術疑慮的確認問題
- 針對穩定性/離職原因的問題
- 針對薪資期望/上班條件的問題
```

> ✅ 這兩項必須在 PATCH ai_match_result 時一併填入，不得留空。
> ❌ 分數和等級單獨存在、沒有文字說明 = 不合格

### Step 3｜進件（POST + PATCH）

**POST 建立人選（snake_case 必填）：**
```json
{
  "name": "姓名",
  "current_position": "職位",
  "years_experience": 5,
  "job_changes": 3,
  "avg_tenure_months": 24,
  "recent_gap_months": 0,
  "stability_score": 80,
  "linkedin_url": "https://www.linkedin.com/in/xxx/",
  "email": "xxx@gmail.com",
  "skills": "技能1, 技能2, 技能3",
  "location": "台北",
  "consultant": "Jacky",
  "status": "AI推薦"
}
```
> ⚠️ 所有 POST 必須帶 Header：`X-Actor: Jacky-aibot`，否則 timeout

**PATCH 補充詳細資料：**
```json
{
  "target_job_id": "{job_id}",
  "work_history": [...],
  "education_details": [...],
  "ai_match_result": {
    "score": 85,
    "grade": "A",
    "match_reason": "...",
    "concerns": "..."
  },
  "notes": "【送人條件檢核】✅ 符合\n..."
}
```

### Step 4｜更新 Pipeline 狀態
```bash
PUT /api/candidates/{id}/pipeline-status
Body: {"status": "AI推薦", "by": "Jacky-aibot"}
```

**可用狀態：**
`未開始` / `AI推薦` / `已聯繫` / `已面試` / `Offer` / `已上職` / `婉拒` / `備選人才`

> ⚠️ 必須用此 endpoint 更新狀態，才能同步 progressTracking，卡片才會移到正確欄位

### Step 5｜上傳 PDF 到 Google Drive + 存連結

**1. 上傳 PDF：**
```bash
gog drive upload {PDF路徑} \
  --account aijessie88@step1ne.com \
  --parent 16IOJW0jR2mBgzBnc5QI_jEHcRBw3VnKj \
  --json
```
> 每次上傳時建立新子資料夾（格式：`YYYY-MM-DD 說明`）

**2. 取得 Drive 連結：**
```
https://drive.google.com/file/d/{FILE_ID}/view
```

**3. 存入人選 notes：**
```bash
PATCH /api/candidates/{id}
Body: {"notes": "現有備註\n📎 LinkedIn PDF：https://drive.google.com/file/d/{id}/view"}
```

---

## ⚙️ API 重要規則

| 規則 | 說明 |
|------|------|
| POST snake_case | `current_position`, `years_experience`, `job_changes`, `avg_tenure_months`, `recent_gap_months` — camelCase 會靜默失敗 |
| POST only 欄位 | `job_changes`, `avg_tenure_months`, `recent_gap_months` — 只能在 POST 設定，如需修改須刪除重建 |
| 查重端點 | 用 `GET /api/candidates?q=xxx`，禁止用 `/api/candidates/search`（會觸發路由 bug）|
| target_job_id | 直接 PATCH `{"target_job_id": {job_id}}`，不要放在 ai_match_result 內 |
| 備選人才 | POST 後系統會自動指派 Jacky，需補 PATCH `{"consultant":"待指派","recruiter":"待指派"}` |

---

## 🔍 重複檢查規則
1. 先用姓名查：`GET /api/candidates?q=姓名`
2. 若找到 → 告知顧問 ID + 現有狀態
3. 若沒找到 → 進行 POST 新增
4. **進件前必查，避免重複資料**

---

## 📨 聯絡開發信

- **寄件帳號**：`aijessie88@step1ne.com`
- **指令**：`gog gmail send --account aijessie88@step1ne.com --to {email} --subject "..." --body-html "..."`
- **信中必含**：顧問的 LinkedIn 或聯絡方式
- 寄信後 PATCH status → `已聯繫`

---

## 🚫 紅線規則（通用）

- ❌ 非相關職能（PM/Sales/BD 等）→ consultant=待指派
- ❌ 人在海外且短期無法回台 → 備選
- ❌ 只有 1 段相關工作 → 備選（除非顧問特別指示）
- ❌ `{禁忌條件}`（依職缺填入）
