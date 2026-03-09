# 智慧人才搜尋閉環系統 - 需求整理（2026-02-27）

## 🎯 核心目標

建立**自動化人才搜尋 + 評分 + 上傳系統**，用於 Step1ne 招聘平台快速篩選優質候選人。

---

## 📋 系統輸入 / 輸出

### 輸入
```
職缺 ID（例如：51 = C++ Developer）
  ↓ 系統自動讀取 JD 資訊
```

### 輸出
```
✅ 25-40 位候選人（去重後）
✅ 每人 A+/A 評分
✅ 每人 5 個面試問題
✅ 候選人已上傳到 Step1ne 系統
✅ 標記來源（GitHub / LinkedIn）
✅ 可直接聯繫（GitHub Issues 優先）
```

---

## 🔄 完整流程（5 個階段）

### 【第一階段】JD 深度分析
**目的**：從職缺描述提取關鍵搜尋信息

**需求**：
- [ ] 讀取職缺完整內容（從 Step1ne DB）
- [ ] 自動提取企業名稱、行業、規模
- [ ] 自動提取職位名稱、薪資範圍、福利
- [ ] 自動提取必備技能（用 `|` 分隔，支援中英文）
- [ ] 自動提取需求年資、地區限制
- [ ] **AI 生成搜尋策略**（中英文關鍵字、搜尋範圍、篩選條件）

**輸出範例**：
```json
{
  "job_id": 51,
  "job_title": "C++ Developer",
  "company": "UnityTech",
  "key_skills": ["C++", "CMake", "CUDA", "Linux"],
  "required_experience": 3,
  "location": "Taiwan",
  "salary_min": 60000,
  "salary_max": 80000,
  "search_strategy": {
    "github_keywords": ["C++ Developer Taiwan", "CUDA", "CMake"],
    "linkedin_query": "site:linkedin.com/in C++ Developer CUDA CMake Taiwan",
    "estimated_candidates_github": 15,
    "estimated_candidates_linkedin": 15,
    "estimated_time": 120
  }
}
```

**確認項**：
- [ ] 需要 AI 評估搜尋策略嗎？還是直接執行？

---

### 【第二階段】雙管道智慧搜尋

#### A. GitHub 搜尋（技術實力驗證）
**需求**：
- [ ] 使用 GitHub API 搜尋開發者
- [ ] 中英文關鍵字自動翻譯
- [ ] 按位置篩選（台灣優先）
- [ ] 返回 15-25 個候選人
- [ ] 提取：GitHub username、profile URL、top repos、commit history、技能推斷
- [ ] **時間限制**：60 秒內完成

**工具**：
- `github-talent-search.py`（既有）
- GitHub API Token（已配置）

#### B. LinkedIn Google 搜尋（職業背景驗證）
**需求**：
- [ ] 用 Google 搜尋 site:linkedin.com 個人檔案
- [ ] **無需登入**，直接提取 URL
- [ ] 搜尋公式：`site:linkedin.com/in "職位" "技能" "地區"`
- [ ] 返回 15-25 個 LinkedIn 個人檔案連結
- [ ] 提取：名字、頭銜、location、連結
- [ ] **時間限制**：45 秒內完成

**工具**：
- `web_search` API（Brave Search）
- 無需驗證

#### C. 智慧去重
**需求**：
- [ ] 同名候選人只保留 1 個
- [ ] GitHub + LinkedIn 同一人：合併資料，保留兩個連結
- [ ] 最終產出：**25-40 位去重候選人**

**輸出範例**：
```json
[
  {
    "id": "charkchalk",
    "name": "Charkchalk",
    "github_url": "https://github.com/charkchalk",
    "linkedin_url": "https://linkedin.com/in/charkchalk-xxx",
    "key_skills": ["C++", "CMake", "Linux"],
    "source": "github+linkedin"
  },
  ...
]
```

---

### 【第三階段】AI 配對評分

**需求**：
- [ ] 對每位候選人進行 **6 維度評分**
  1. **人才畫像符合度** (40%)：技能、經驗、背景匹配
  2. **JD 職責匹配度** (30%)：工作經歷是否涵蓋職位需求
  3. **公司適配性** (15%)：行業經驗、企業文化符合度
  4. **可觸達性** (10%)：GitHub Issues、LinkedIn 聯繫方式
  5. **活躍信號** (5%)：recent commits、profile update 時間
  6. **薪資符合度** (可選)：履歷年資 vs 職缺薪資

- [ ] 最終分數：0-100，分級為 A+（90+）/ A（80-89）/ B（70-79）
- [ ] **只篩選 A+/A 級候選人**（80+ 分）

- [ ] 生成 **5 個面試探討問題**，包含：
  1. 技術深度問題
  2. 專案經驗問題
  3. 團隊協作問題
  4. 學習動力問題
  5. 公司適配問題

- [ ] 生成 **AI 評論結論**（200-300 字）
  - 為什麼推薦
  - 主要優勢
  - 需要確認的技能點
  - 建議聯繫方式

**輸出結構**（`aiMatchResult`）：
```json
{
  "score": 89,
  "grade": "A+",
  "date": "2026-02-27",
  "position": "C++ Developer",
  "company": "UnityTech",
  "matched_skills": ["C++", "CMake", "Linux"],
  "missing_skills": ["CUDA 實戰經驗"],
  "strengths": ["活躍開發者", "開源貢獻"],
  "probing_questions": [
    "請介紹你最複雜的 C++ 專案架構...",
    "在 CMake 跨平台編譯中遇過的挑戰...",
    "...共 5 題"
  ],
  "salary_fit": "符合預算",
  "conclusion": "技能與職缺高度匹配，建議優先聯繫...",
  "contact_method": "GitHub Issues（推薦）或 LinkedIn InMail",
  "github_url": "https://github.com/charkchalk",
  "linkedin_url": "https://linkedin.com/in/charkchalk-xxx",
  "evaluated_by": "YuQi",
  "evaluated_at": "2026-02-27T20:30:00+08:00"
}
```

---

### 【第四階段】批量上傳系統

**需求**：
- [ ] 連接到 Step1ne 後端 API：`https://backendstep1ne.zeabur.app/api`
- [ ] 批量 PUT `/api/candidates/:id` 更新候選人評分
- [ ] **重要**：保留原始 `status` 欄位（不被覆蓋）
- [ ] 批次大小：每次 10-20 人，間隔 1-2 秒（避免限流）
- [ ] 錯誤重試：失敗自動重試 3 次
- [ ] 完整日誌記錄（成功/失敗清單）

**API 呼叫範例**：
```bash
PUT /api/candidates/540
Content-Type: application/json

{
  "status": "AI推薦",  # ⭐ 必須保留
  "aiMatchResult": { ... }  # 新增評分結果
}
```

**輸出**：
```
📤 批量上傳進度
─────────────────
[1/32]  charkchalk (#540) ... ✅
[2/32]  melody-nien-chi-yu (#541) ... ✅
[3/32]  magic-len (#542) ... ✅
...
[32/32] eric-liu (#563) ... ✅

✅ 成功：32/32
❌ 失敗：0

🔗 查看結果：https://step1ne.zeabur.app?status=AI推薦&company=UnityTech
```

---

### 【第五階段】驗證 & 回報

**需求**：
- [ ] 前端即時驗證（3-5 個候選人抽查）
- [ ] 確認 `aiMatchResult` 在前端正確顯示
- [ ] 確認面試問題、評論結論、聯繫方式都有
- [ ] 生成最終報告（成果清單 + 系統連結）

---

## ⚙️ 技術選擇確認

| 項目 | 選擇 | 備註 |
|------|------|------|
| **GitHub 搜尋** | `github-talent-search.py` (既有) | ✅ 已驗證可行 |
| **LinkedIn 搜尋** | Google `web_search` API | ✅ 無需登入，簡單可靠 |
| **AI 評分** | Claude API | ✅ 使用 6 維度框架 |
| **批量上傳** | Step1ne REST API | ✅ 已測試 PATCH/PUT |
| **編排器** | Python 主腳本 | ✅ 支援 --dry-run 和 --execute |
| **日誌** | JSON + 控制台輸出 | ✅ 便於回溯 |

---

## 📅 執行計畫確認

### 階段 1：Dry-run（先分析，不執行搜尋）
```bash
python3 talent-sourcing-pipeline.py \
  --job-id 51 \
  --sources github,linkedin-google \
  --dry-run
```
- [ ] 預計時間：5-10 分鐘
- [ ] 輸出：JD 分析報告 + 搜尋策略 + 預計候選人數
- **你確認後** → 進入階段 2

### 階段 2：完整執行（搜尋 + 評分 + 上傳）
```bash
python3 talent-sourcing-pipeline.py \
  --job-id 51 \
  --sources github,linkedin-google \
  --execute
```
- [ ] 預計時間：3-5 分鐘
- [ ] 輸出：25-40 位候選人已上傳

### 階段 3：驗證
- [ ] 前端查看候選人清單
- [ ] 抽查 3-5 人的評分細節
- [ ] 確認面試問題和結論

### 階段 4：批量處理其他職位
```bash
python3 talent-sourcing-pipeline.py \
  --job-ids 15,16,17,18 \
  --sources github,linkedin-google \
  --execute \
  --parallel 2
```
- [ ] 預計時間：20-30 分鐘（4 個職位）

---

## ✅ 待你確認的項目

### 1. 搜尋策略
- [ ] **方案 A**：GitHub + LinkedIn Google 混合（推薦）
  - 時間：120 秒/職位
  - 候選人：25-40 位（去重後）
  - 優點：完整覆蓋、質量最高

- [ ] **方案 B**：GitHub 優先（如果時間緊張）
  - 時間：60 秒/職位
  - 候選人：15-25 位
  - 缺點：LinkedIn 驗證不足

### 2. 優先級
- [ ] 先做 C++ Developer (id 51) 完整測試
- [ ] 再做 Information Security (id 15)
- [ ] 再做 DevOps / 其他職位

### 3. 評分標準
- [ ] 是否同意「只保留 80+ 分的候選人」（A+/A）？
- [ ] 6 維度權重是否需要調整？
  - 人才畫像 40%
  - JD 匹配度 30%
  - 公司適配 15%
  - 可觸達性 10%
  - 活躍信號 5%

### 4. 時間預期
- [ ] 這週五要完成嗎？還是可以等到下週？
- [ ] 一次爬多少職位？（1 個 vs 多個）

### 5. 其他需求
- [ ] 需要自動化 Cron 嗎？（例如每天 09:00 自動爬某職位）
- [ ] 需要生成週報嗎？（每週彙總新候選人）

---

## 📊 預期成果（以 C++ Developer 為例）

```
輸入：職缺 ID 51 (C++ Developer @ UnityTech)
  ↓
【JD 分析】 ✅ 5 分鐘
  必備技能：C++, CMake, CUDA, Linux
  搜尋策略已生成
  
【搜尋】 ✅ 120 秒
  GitHub：18 位
  LinkedIn：22 位
  去重後：32 位
  
【評分】 ✅ 3 分鐘
  所有候選人評分完成
  32 位都是 A+/A（80+ 分）
  
【上傳】 ✅ 2 分鐘
  32/32 成功上傳到系統
  
【驗證】 ✅ 2 分鐘
  前端確認所有數據正確顯示

【總耗時】約 15-20 分鐘，自動完成 ✅
```

---

## 🚀 下一步

**請按優先級回答：**

1. **搜尋方案**：方案 A（GitHub + LinkedIn Google）還是方案 B（GitHub 優先）？
2. **起始職位**：C++ Developer (51) 還是其他職位？
3. **評分標準**：80+ 分（A+/A）是否可以？
4. **時間框架**：本週五完成一個職位，還是下週再做？
5. **自動化**：需要設定定期 Cron 嗎？

---

確認以上，我立刻開始寫代碼！ 🚀
