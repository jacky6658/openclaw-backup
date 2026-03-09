# AI 候選人評分工作流程指南

*給其他 AI 助理的標準操作手冊*

---

## 🎯 整體流程

```
1. 取得候選人名單（GitHub/LinkedIn 爬蟲）
   ↓
2. 對每位候選人進行 AI 匹配評分（6 維度評分系統）
   ↓
3. 生成面試探詢問題（5 條/人）
   ↓
4. 批量更新後端數據庫（保留原有欄位）
   ↓
5. 驗證前端顯示正確
```

---

## 📋 Step 1: 取得候選人名單

**來源**：
- GitHub 搜尋：`github-talent-search.py`
- LinkedIn（困難，暫時跳過）
- 本地履歷池：Google Sheets

**API 查詢現有候選人**：
```bash
curl "https://backendstep1ne.zeabur.app/api/candidates?limit=1000" | jq '.data[] | {id, name, status, skills}'
```

---

## 🎯 Step 2: AI 匹配評分系統（6 維度）

**評分維度**：
```json
{
  "人才畫像符合度": { "weight": 0.40, "example": "技能棧完整度" },
  "JD 職責匹配度": { "weight": 0.30, "example": "工作經驗相關性" },
  "公司適配性": { "weight": 0.15, "example": "業界背景、公司規模適配" },
  "可觸達性": { "weight": 0.10, "example": "GitHub/LinkedIn 活躍度" },
  "活躍信號": { "weight": 0.05, "example": "最近提交、開源參與" }
}
```

**最終分數計算**：
```
Score = (人才 × 0.4 + JD × 0.3 + 公司 × 0.15 + 觸達 × 0.1 + 活躍 × 0.05) × 100
```

**等級劃分**：
- 85+ → A+ (強力推薦)
- 70-84 → A (推薦)
- 55-69 → B (觀望)
- <55 → C (不推薦)

**Python 實現範例**：
```python
def evaluate_candidate(candidate):
    """對單一候選人進行 6 維度評分"""
    
    # 維度 1: 人才畫像符合度 (40%)
    skill_match_score = calculate_skill_match(candidate.skills, target_skills)
    
    # 維度 2: JD 職責匹配度 (30%)
    job_match_score = calculate_job_match(candidate.experience, jd_requirements)
    
    # 維度 3: 公司適配性 (15%)
    company_fit_score = assess_company_fit(candidate.industry, target_company_type)
    
    # 維度 4: 可觸達性 (10%)
    reachability_score = assess_github_linkedin_presence(candidate)
    
    # 維度 5: 活躍信號 (5%)
    activity_score = assess_recent_activity(candidate.github_activity)
    
    # 計算最終分數
    final_score = (
        skill_match_score * 0.40 +
        job_match_score * 0.30 +
        company_fit_score * 0.15 +
        reachability_score * 0.10 +
        activity_score * 0.05
    )
    
    return {
        "score": round(final_score, 0),
        "grade": get_grade(final_score),
        "recommendation": get_recommendation(final_score),
        "strengths": extract_strengths(candidate),
        "missing_skills": extract_missing_skills(candidate)
    }
```

---

## 💬 Step 3: 生成面試探詢問題（5 條/人）

**框架**：每條問題對應一個技能維度

**範例（Java Developer 專用）**：
```python
def generate_probing_questions(position, candidate_skills):
    """為候選人生成 5 個具體的面試問題"""
    
    questions = [
        # Q1: 核心技術深度
        f"在您的 {candidate_skills[0]} 項目中，如何實現 {key_feature_1}？",
        
        # Q2: 分佈式系統經驗
        f"在使用 {candidate_skills[2]} 時，遇過什麼生產環境的挑戰？",
        
        # Q3: API 設計
        f"您如何使用 {candidate_skills[3]} 規範設計微服務 API？",
        
        # Q4: 性能優化
        f"在高併發場景下，您如何利用 {candidate_skills[6]} 來優化系統？",
        
        # Q5: DevOps / CI/CD
        f"您對 CI/CD 流程的理解程度如何？有實戰經驗嗎？"
    ]
    
    return questions
```

**重點**：
- ✅ 問題要**具體**，涉及實際工作經驗
- ✅ 每條問題對應不同技能/維度
- ✅ 共 5 條（不多不少）
- ❌ 不要問虛無飄渺的問題（如「你的優點是什麼」）

---

## 🔄 Step 4: 批量更新後端數據庫

### 關鍵點：**保留原有 status，只更新 aiMatchResult**

**❌ 錯誤做法**（會清空 status）：
```bash
curl -X PUT "https://backendstep1ne.zeabur.app/api/candidates/540" \
  -H "Content-Type: application/json" \
  -d '{"aiMatchResult": {...}}'
```

**✅ 正確做法**（保留 status）：
```bash
curl -X PUT "https://backendstep1ne.zeabur.app/api/candidates/540" \
  -H "Content-Type: application/json" \
  -d '{"status": "AI推薦", "aiMatchResult": {...}}'
```

### Python 批量更新腳本：
```python
#!/usr/bin/env python3
import requests
import json

def batch_update_candidates(candidate_list, ai_match_results):
    """批量更新候選人的 AI 評分"""
    
    headers = {"Content-Type": "application/json"}
    updated = 0
    failed = 0
    
    for candidate_id, ai_match in zip(candidate_list, ai_match_results):
        try:
            # 構建 PUT 請求
            url = f"https://backendstep1ne.zeabur.app/api/candidates/{candidate_id}"
            
            payload = {
                "status": "AI推薦",  # ⚠️ 必須保留原狀態！
                "aiMatchResult": ai_match
            }
            
            response = requests.put(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code in [200, 201]:
                updated += 1
                print(f"✅ #{candidate_id}: 更新成功")
            else:
                failed += 1
                print(f"❌ #{candidate_id}: HTTP {response.status_code}")
        
        except Exception as e:
            failed += 1
            print(f"❌ #{candidate_id}: {str(e)}")
    
    print(f"\n📊 總結：{updated} 成功，{failed} 失敗")
    return updated, failed

# 使用範例
candidate_ids = [540, 541, 542, ...]  # 所有候選人 ID
ai_results = [
    {
        "score": 89,
        "grade": "A+",
        "recommendation": "強力推薦",
        "job_title": "Java Developer",
        "company": "UnityTech",
        "matched_skills": ["Java", "Spring Boot", ...],
        "missing_skills": ["金融科技經驗", ...],
        "strengths": ["Java", "Spring Boot", ...],
        "probing_questions": [
            "Q1: 在 Spring Boot 微服務中...",
            "Q2: 使用 Docker 時...",
            ...
        ],
        "salary_fit": "期望薪資待確認...",
        "conclusion": "本候選人在 Java 後端...",
        "suggestion": "技能與職缺完全對口...",
        "evaluated_by": "AIBot",
        "evaluated_at": "2026-02-27",
        "github_url": "https://github.com/..."
    },
    ...
]

batch_update_candidates(candidate_ids, ai_results)
```

### aiMatchResult 欄位完整結構：
```json
{
  "score": 89,                    // 0-100 分
  "grade": "A+",                  // A+/A/B/C
  "recommendation": "強力推薦",    // 推薦等級
  "job_title": "Java Developer",  // 對應職缺
  "company": "UnityTech",         // 公司名
  "matched_skills": [...],        // 符合的技能清單
  "missing_skills": [...],        // 缺少的技能清單
  "strengths": [...],             // 優勢亮點（前 8 項）
  "probing_questions": [          // 面試問題（必須 5 項）
    "Q1: ...",
    "Q2: ...",
    "Q3: ...",
    "Q4: ...",
    "Q5: ..."
  ],
  "salary_fit": "期望薪資待確認 | 職缺薪資範圍：XX-XX | 符合度：...",
  "conclusion": "本候選人在... 整體評估：強力推薦進行技術面試。",
  "suggestion": "技能與職缺完全對口，建議透過 GitHub/LinkedIn 聯繫",
  "evaluated_by": "AIBot",        // 評分者
  "evaluated_at": "2026-02-27",   // 評分日期
  "github_url": "https://github.com/..."
}
```

---

## ✅ Step 5: 驗證前端顯示

**查詢單一候選人評分**：
```bash
curl -s "https://backendstep1ne.zeabur.app/api/candidates/540" | jq '.data.aiMatchResult'
```

**前端檢查清單**：
- [ ] 「AI評分」tab 顯示分數（例：89）
- [ ] 「優勢亮點」區塊顯示技能列表
- [ ] 「待確認」區塊顯示缺少的技能
- [ ] **「面談重點」區塊顯示 Q1-Q5**（這是最容易遺漏的）
- [ ] 「AI 完整結論」區塊顯示完整評論
- [ ] 手機版 RWD 所有內容完整可見

**手機清快取方式**：
- iOS Safari：上方地址欄長按 → 重新載入
- Android Chrome：右上角⋮ → 設定 → 清除瀏覽資料

---

## ⚠️ 常見陷阱

| 問題 | 原因 | 解決方案 |
|------|------|--------|
| 面談重點不顯示 | `probing_questions` 為空陣列或缺失 | 確保傳 5 個問題 |
| 狀態被清空 | PUT 只傳 `aiMatchResult` | 必須同時傳 `status: "AI推薦"` |
| 前端顯示「未評分」 | DB 欄位返回 null | 確認 ai_match_result 已正確寫入 DB |
| 手機內容溢出 | RWD 沒做好 | 使用 `w-[95vw] sm:w-full` 等響應式類 |
| 批量更新超時 | 網路慢或請求太多 | 分批處理，每批 10-20 人，間隔 1 秒 |

---

## 📊 工作量估算

| 任務 | 時間 | 備註 |
|------|------|------|
| 爬蟲取得 20-50 人 | 5-10 分鐘 | 取決於 API 限流 |
| 對每人進行 AI 評分（自動） | 30 秒 | Python 快速評分 |
| 生成 5 個面試問題 | 10 秒 | 模板化生成 |
| 批量更新後端（50 人） | 2-3 分鐘 | 包含 API 調用 |
| **總計（50 人）** | **15-20 分鐘** | 包含驗證 |

---

## 🎓 範例：完整流程（Java Developer）

```python
# 1. 定義職缺和目標技能
JOB_CONFIG = {
    "position": "Java Developer (後端工程師)",
    "company": "UnityTech",
    "required_skills": ["Java", "Spring Boot", "微服務", "OpenAPI", "Message Queue", "Docker", "Kubernetes", "Redis"],
    "nice_to_have": ["金融科技經驗", "CI/CD 經驗"],
    "min_score": 85
}

# 2. 從 GitHub 爬蟲取得候選人
candidates = scrape_github_developers(
    keywords="Java Engineer",
    location="Taiwan",
    min_followers=100
)

# 3. 對每人進行評分
ai_evaluations = []
for candidate in candidates:
    evaluation = evaluate_candidate(candidate, JOB_CONFIG)
    
    # 篩選（只要 85 分以上）
    if evaluation['score'] >= 85:
        # 生成面試問題
        evaluation['probing_questions'] = generate_probing_questions(
            position=JOB_CONFIG['position'],
            skills=candidate.skills
        )
        
        ai_evaluations.append(evaluation)

# 4. 批量更新後端
batch_update_candidates(
    candidate_ids=[c.id for c in candidates if c_score >= 85],
    ai_match_results=ai_evaluations
)

# 5. 輸出結果
print(f"✅ 評分完成：{len(ai_evaluations)} 位候選人達 A+ 等級")
print(f"📋 前 5 推薦：{ai_evaluations[:5]}")
```

---

## 📞 後續聯繫流程

對於評分 ≥ 85 的候選人：

1. **GitHub Issues**（推薦）：
   ```markdown
   Hi @{username}，
   
   我們是一通數位有限公司，正在尋找 Java Backend Engineer。
   
   您的技能與我們職缺完全對應（Spring Boot/Docker/Kubernetes）。
   
   有興趣瞭解更多嗎？
   ```

2. **LinkedIn InMail**：相同內容，稍微正式些

3. **備註博客聯繫表單**：如果有個人部落格，用聯繫表單

---

## 📚 相關檔案位置

- **爬蟲腳本**：`/Users/user/clawd/hr-tools/github-talent-search.py`
- **評分系統**：`/Users/user/clawd/hr-tools/candidate-scoring-system-v2.py`
- **後端 API**：`https://backendstep1ne.zeabur.app/api/candidates`
- **前端頁面**：`https://step1ne.zeabur.app` (登入需 Jacky 帳號)

---

**最後提醒**：
- ✅ 永遠保留 `status` 在 PUT 請求中
- ✅ `probing_questions` 必須有 5 項
- ✅ 批量操作要做驗證（抽查 3-5 筆確認前端顯示）
- ✅ 有問題先檢查 DB 資料，再檢查前端映射邏輯

祝好運！🚀
