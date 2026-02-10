# 履歷格式化模板

## 標準格式（給客戶看的匿名版）

```
═══════════════════════════════════════════════════════
                    候選人推薦報告
═══════════════════════════════════════════════════════

📋 基本資訊
───────────────────────────────────────────────────────
代號：        {{CANDIDATE_CODE}}
推薦日期：    {{DATE}}
推薦職缺：    {{JOB_TITLE}}
推薦顧問：    {{RECRUITER_NAME}}

👤 候選人概況
───────────────────────────────────────────────────────
現職：        {{CURRENT_COMPANY}} / {{CURRENT_TITLE}}
年資：        {{TOTAL_EXPERIENCE}} 年
學歷：        {{EDUCATION}}
期望薪資：    {{EXPECTED_SALARY}}
可到職日：    {{AVAILABLE_DATE}}

💼 工作經歷
───────────────────────────────────────────────────────
{{WORK_EXPERIENCE}}

🛠️ 技術能力
───────────────────────────────────────────────────────
{{SKILLS}}

📊 匹配分析
───────────────────────────────────────────────────────
匹配度：      {{MATCH_SCORE}}%

✅ 符合項目：
{{MATCH_ITEMS}}

⚠️ 待確認/缺口：
{{GAP_ITEMS}}

💡 推薦理由
───────────────────────────────────────────────────────
{{RECOMMENDATION_REASON}}

═══════════════════════════════════════════════════════
                    Step1ne 獵頭顧問
═══════════════════════════════════════════════════════
```

## 欄位說明

| 欄位 | 說明 | 範例 |
|------|------|------|
| CANDIDATE_CODE | 匿名代號 | BE-2026-001 |
| DATE | 推薦日期 | 2026-02-10 |
| JOB_TITLE | 推薦職缺 | Senior Backend Engineer |
| RECRUITER_NAME | 顧問姓名 | Jacky Chen |
| CURRENT_COMPANY | 現職公司（匿名） | 某知名電商平台 |
| CURRENT_TITLE | 現職職稱 | Senior Software Engineer |
| TOTAL_EXPERIENCE | 總年資 | 5 |
| EDUCATION | 學歷 | 台灣大學 資訊工程 碩士 |
| EXPECTED_SALARY | 期望薪資 | 80-90K |
| AVAILABLE_DATE | 可到職日 | 1 個月內 |
| WORK_EXPERIENCE | 工作經歷摘要 | 見下方範例 |
| SKILLS | 技術能力列表 | 見下方範例 |
| MATCH_SCORE | 匹配分數 | 85 |
| MATCH_ITEMS | 符合項目列表 | 見下方範例 |
| GAP_ITEMS | 缺口項目列表 | 見下方範例 |
| RECOMMENDATION_REASON | 推薦理由 | 見下方範例 |

## 範例填充

### WORK_EXPERIENCE 範例
```
• 2021-現在｜某知名電商平台｜Senior Software Engineer
  - 負責後端系統架構設計與開發
  - 帶領 3 人團隊完成訂單系統重構
  - 將 API 響應時間優化 40%

• 2018-2021｜某新創科技公司｜Software Engineer
  - 從零建置微服務架構
  - 開發 RESTful API 服務客戶端
```

### SKILLS 範例
```
後端：Node.js, Python, Go
框架：Express, FastAPI, Gin
資料庫：PostgreSQL, MongoDB, Redis
雲服務：AWS (EC2, RDS, S3, Lambda)
DevOps：Docker, Kubernetes, CI/CD
```

### MATCH_ITEMS 範例
```
• Node.js 5年+ 經驗 ✓
• 微服務架構經驗 ✓
• AWS 雲端部署經驗 ✓
• 有帶人經驗 ✓
```

### GAP_ITEMS 範例
```
• Kubernetes 經驗較淺（有 Docker 經驗，可快速上手）
• 無金融業經驗（但有電商高併發經驗）
```

### RECOMMENDATION_REASON 範例
```
此候選人具備紮實的後端開發經驗，尤其在電商高併發場景下有豐富實戰經驗。
雖然無金融業背景，但其系統設計能力和問題解決能力優秀，
且有明確的職涯規劃和穩定的工作態度，建議優先安排面試。
```

## 匿名化規則

1. **公司名稱**：用「某知名XX公司」「某新創科技公司」替代
2. **學校名稱**：可保留或用「國立大學」替代
3. **姓名**：用代號替代（如 BE-2026-001）
4. **聯絡方式**：完全移除

## 代號命名規則

格式：`{職能}-{年份}-{序號}`

| 職能代號 | 說明 |
|----------|------|
| BE | Backend Engineer |
| FE | Frontend Engineer |
| FS | Full Stack |
| DA | Data Analyst |
| DE | Data Engineer |
| PM | Product Manager |
| QA | QA Engineer |
| DO | DevOps |
