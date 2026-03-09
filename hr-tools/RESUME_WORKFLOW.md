# 履歷處理標準流程 SOP
> 最後更新：2026-03-04
> 適用：YuQi HR AI 及所有接手此流程的 AI Agent

---

## 📌 基本設定

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
- ⚠️ 已存在 → 告知 Jacky ID + 現有狀態，詢問是否更新

### Step 2｜分析履歷 → 送人條件檢核

**送人條件（硬性，缺一不可）：**
- ≥ 2 段相關工作經驗（Java 或 運維/SRE/DevOps）
- 每段 ≥ 1 年
- 薪資水位：中階 7 萬 / 高階 8 萬

**加分項：**
- AliCloud / 阿里雲（DevOps #53 黃金加分）
- Spring Cloud、Kafka、Kubernetes
- 金融 / 證券 / 交易所背景
- 三竹資訊 或 精誠資訊 出身（+1分）

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
  "skills": "Java, Spring Boot, Kafka",
  "location": "台北",
  "consultant": "Jacky",
  "status": "AI推薦"
}
```
> ⚠️ 所有 POST 必須帶 Header：`X-Actor: Jacky-aibot`，否則 timeout

**PATCH 補充詳細資料：**
```json
{
  "target_job_id": 52,
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

## 📋 職缺對照表（一通數位）

| 職缺 ID | 職位 | 相關技術 |
|---------|------|----------|
| #51 | C++ Developer | 金融/證券 C++, 高頻交易, Fintech |
| #52 | Java Developer | Java, Spring Boot/Cloud, Kafka |
| #53 | DevOps/維運工程師 | SRE, Kubernetes, Ansible, AliCloud, Zabbix |

> 一通數位：香港正規持牌證券商（Nasdaq: TOP），台北內湖軟體研發中心

---

## ⚙️ API 重要規則

| 規則 | 說明 |
|------|------|
| POST snake_case | `current_position`, `years_experience`, `job_changes`, `avg_tenure_months`, `recent_gap_months` — camelCase 會靜默失敗 |
| POST only 欄位 | `job_changes`, `avg_tenure_months`, `recent_gap_months` — 只能在 POST 設定，如需修改須刪除重建 |
| 查重端點 | 用 `GET /api/candidates?q=xxx`，禁止用 `/api/candidates/search`（會觸發路由 bug）|
| target_job_id | 直接 PATCH `{"target_job_id": 52}`，不要放在 ai_match_result 內 |
| 備選人才 | POST 後系統會自動指派 Jacky，需補 PATCH `{"consultant":"待指派","recruiter":"待指派"}` |

---

## 🔍 重複檢查規則
1. 先用姓名查：`GET /api/candidates?q=姓名`
2. 若找到 → 告知 Jacky ID + 現有狀態
3. 若沒找到 → 進行 POST 新增
4. **進件前必查，避免重複資料**

---

## 📨 聯絡開發信

- **寄件帳號**：`aijessie88@step1ne.com`
- **指令**：`gog gmail send --account aijessie88@step1ne.com --to {email} --subject "..." --body-html "..."`
- **信中必含**：Jacky 的 LinkedIn：`https://www.linkedin.com/in/jacky-chen-0a8a6416a/`
- 寄信後 PATCH status → `已聯繫`

---

## 🚫 紅線規則

- ❌ 不挖客戶（一通數位）的現有員工
- ❌ 非工程師職缺（Sales/BD/PM）→ consultant=待指派
- ❌ 人在海外且短期無法回台 → 備選
- ❌ 只有 1 段相關工作 → 備選（除非 Jacky 特別指示）
