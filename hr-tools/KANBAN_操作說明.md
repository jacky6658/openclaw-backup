# 顧問人選追蹤表（Kanban 看板）- AI 操作指南

**簡潔版本** - 只說如何操作看板

---

## 前端看板結構

```
┌─────────────────────────────────────────────────────────────┐
│         顧問人選追蹤表（CandidateKanbanPage）                 │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  [未開始]   [已聯繫]   [已面試]   [Offer]   [已上職]   [婉拒]  │
│  ─────────  ─────────  ─────────  ─────────  ─────────  ───   │
│  │卡片 1│  │卡片 3│  │卡片 5│  │卡片 7│  │卡片 9│  │卡片11│ │
│  │──────│  │──────│  │──────│  │──────│  │──────│  │──────│ │
│  │姓名  │  │姓名  │  │姓名  │  │姓名  │  │姓名  │  │姓名  │ │
│  │職位  │  │職位  │  │職位  │  │職位  │  │職位  │  │職位  │ │
│  │年資  │  │年資  │  │年資  │  │年資  │  │年資  │  │年資  │ │
│  │      │  │      │  │      │  │      │  │      │  │      │ │
│  │卡片 2│  │卡片 4│  │卡片 6│  │卡片 8│  │卡片10│  │卡片12│ │
│  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘ │
│                                                               │
└─────────────────────────────────────────────────────────────┘

每張卡片 = 一位候選人
列名 = 招聘狀態（status）
```

---

## AI 操作看板的方式

### 方式 1：拖拽卡片（前端操作）
```
✅ 前端用戶可以直接拖拽卡片到不同列
   ├─ 觸發 handleDrop() 函數
   ├─ 呼叫後端 updateCandidateStatus(candidateId, newStatus)
   └─ 自動更新看板

❌ AI 無法直接操作前端（沒有 Selenium/Playwright）
```

### 方式 2：AI 通過 API 更新看板（推薦）

#### 步驟 1：取得所有候選人

```bash
GET /api/candidates?limit=1000

回應：
{
  "data": [
    {
      "id": 123,
      "name": "王小明",
      "status": "已聯繫",        ← 當前在哪一列
      "position": "Java Engineer",
      "years": 5,
      "stability_score": 82,
      "progressTracking": [
        { "date": "2026-03-04", "event": "已聯繫", "by": "Jacky" }
      ]
    }
  ]
}
```

**理解：**
- `status` = 卡片所在的列
- `progressTracking` = 這張卡片的移動歷史

---

#### 步驟 2：AI 更新卡片位置（改變 status）

```bash
PUT /api/candidates/:id/pipeline-status
Content-Type: application/json

Body:
{
  "status": "已面試",      ← 移動到這一列
  "by": "Jacky-aibot"      ← AI 身份
}

回應：
{
  "success": true,
  "data": {
    "id": 123,
    "name": "王小明",
    "status": "已面試",      ← 已更新
    "progress_tracking": [
      { "date": "2026-03-04", "event": "已聯繫", "by": "Jacky" },
      { "date": "2026-03-05", "event": "已面試", "by": "Jacky-aibot" }  ← 新事件
    ]
  }
}
```

**理解：**
- API 自動更新 `status` 欄位
- 自動追加新的 `progressTracking` 事件
- 看板立即反映變化

---

## 看板的 6 列說明

| 列名 | status 值 | 含義 | SLA | AI 操作 |
|------|----------|------|-----|--------|
| **未開始** | `未開始` | 剛進系統，待評分 | 2 天 | 評分→更新狀態 |
| **已聯繫** | `已聯繫` | 已寄信/通話 | 3 天 | 追蹤→更新狀態 |
| **已面試** | `已面試` | 已面試完成 | 7 天 | 催促決定→更新狀態 |
| **Offer** | `Offer` | 已發 Offer | 5 天 | 追蹤簽署→更新狀態 |
| **已上職** | `已上職` | 候選人到職 | ∞ | 標記完成 |
| **婉拒** | `婉拒` | 候選人/客戶拒絕 | ∞ | 記錄原因 |

---

## AI 在日常工作中如何操作看板

### 場景 1：收到新履歷

```
顧問 → 「我收到王小明的履歷」
  ↓
AI:
  1. POST /api/candidates  → 新增候選人 (status="未開始")
  2. 分析履歷，計算評分
  3. PATCH /api/candidates/:id  → 更新 stability_score, talent_level
  4. 看板自動顯示新卡片在「未開始」列

結果：看板出現新卡片 👤 王小明（未開始列）
```

### 場景 2：顧問說「我已聯繫他」

```
顧問 → 「我已聯繫李大華了」
  ↓
AI:
  1. PUT /api/candidates/:id/pipeline-status
     { "status": "已聯繫", "by": "Jacky-aibot" }
  2. 後端自動追加事件：
     { date: "2026-03-05", event: "已聯繫", by: "Jacky-aibot" }

結果：卡片從「未開始」移到「已聯繫」列 → 🏃 → 📌
      progressTracking 記錄移動時間
```

### 場景 3：AI 監控 SLA 逾期

```
AI (每日 08:00):
  1. GET /api/candidates
  2. 計算停留天數：today - progressTracking[-1].date
  3. 檢查是否超過 SLA 閾值
  
  if (status == "已聯繫" && stayDays > 3):
     → 推送警告：「李大華已聯繫 4 天，需要跟進」
     → 不改變 status，只提醒
     
  if (stayDays > 5):
     → 升級警告：「🔴 李大華已聯繫 5 天！」
```

### 場景 4：檢查一個候選人的進度

```
顧問 → 「王小明進到哪一步了？」
  ↓
AI:
  1. GET /api/candidates/:id
  2. 讀取 status 和 progressTracking
  
  回複：「王小明目前在『已面試』列（自 2026-03-04）
         進度記錄：
         - 2026-03-03：未開始 (新增)
         - 2026-03-04：已聯繫 (Jacky)
         - 2026-03-05：已面試 (Jacky)」
```

---

## 核心 API（只需這 3 個）

| API | 方法 | 用途 |
|-----|------|------|
| `/api/candidates` | GET | 取得看板上所有卡片 |
| `/api/candidates/:id/pipeline-status` | PUT | 移動卡片（改變 status） |
| `/api/candidates/:id` | PATCH | 更新卡片詳細資訊（但不改狀態） |

**就這樣。** 其他都是輔助。

---

## progressTracking 的重要性

每張卡片的移動都被記錄：

```json
"progressTracking": [
  { "date": "2026-03-03", "event": "未開始", "by": "system" },
  { "date": "2026-03-04", "event": "已聯繫", "by": "Jacky" },
  { "date": "2026-03-05", "event": "已面試", "by": "Jacky-aibot" },
  { "date": "2026-03-05", "event": "Offer", "by": "Jacky" }
]
```

**AI 的工作：**
- 讀取最後一個事件：` { date: "2026-03-05", event: "Offer", ... }`
- 計算停留天數：`today - 2026-03-05 = 0 天`
- 檢查 SLA：`0 < 5 天`，🟢 正常

---

## 不要做的事

❌ **不要直接改 `status` 欄位**（不用 API）
   → progressTracking 不會更新
   → 看板歷史記錄丟失

❌ **不要手動追加 progressTracking**
   → PUT /pipeline-status 已自動做了
   → 會造成重複記錄

❌ **不要一直查詢全部候選人**
   → 改用 GET /api/candidates?limit=1000 做本地過濾
   → 減輕伺服器負擔

---

## 總結

**AI 操作看板 = 改變 candidate.status**

```
AI 的核心循環：

1. 取得候選人       GET /api/candidates
2. 判斷他在哪一列    candidate.status
3. 決定要移到哪列    newStatus
4. 更新狀態         PUT /pipeline-status
5. 看板自動更新     ← 完成

就這麼簡單。
```

---

**下一步：** 要我寫具體的 Python/JS 代碼嗎？或者你想看「SLA 監控」的實現？
