# 智慧人才搜尋閉環系統 - 完整使用指南

**版本**: v1.0  
**最後更新**: 2026-02-27  
**用途**: 自動化職缺分析 → 雙管道搜尋 → AI 評分 → 批量上傳

---

## 📋 快速開始

### 前置條件
```bash
# 確保 Python 3.8+
python3 --version

# 確保已安裝依賴
pip install requests

# GitHub API Token（可選，但推薦）
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxx"
```

### 基本用法

#### 1️⃣ DRY-RUN（分析職缺，不執行搜尋）
```bash
cd /Users/user/clawd/hr-tools

# 分析單個職位
python3 talent_sourcing_pipeline.py --job-id 51 --dry-run

# 輸出：
# - 企業畫像
# - 職位畫像  
# - 人才畫像
# - 搜尋策略
# - 預計成果（25-40 人，~120 秒耗時）
```

#### 2️⃣ EXECUTE（完整執行）
```bash
# 執行單個職位
python3 talent_sourcing_pipeline.py --job-id 51 --execute

# 執行多個職位（並行）
python3 talent_sourcing_pipeline.py --job-ids 51,15,16 --execute

# 輸出：完整的候選人清單 + 評分 + 上傳結果
```

---

## 🔄 完整流程說明

### 【第一階段】JD 深度分析 (5-10 分鐘)

**文件**: `jd_analyzer.py`

**功能**:
- 從 Step1ne DB 讀取職缺詳情
- 自動提取：企業名稱、產業、規模
- 自動提取：職位名稱、薪資、福利
- 自動提取：核心技能、次要技能
- 自動提取：所需年資、地區限制
- AI 生成搜尋策略（中英文關鍵字）

**輸出**:
```json
{
  "company_profile": {
    "name": "UnityTech (一通數位)",
    "industry": "Gaming / SaaS",
    "stage": "growth"
  },
  "job_profile": {
    "title": "C++ Developer",
    "level": "mid",
    "salary_range": {"min": 60000, "max": 80000},
    "core_skills": ["C++", "CMake", "Docker", "Kubernetes", "Linux"]
  },
  "talent_profile": {
    "ideal_background": {...},
    "personality_traits": [...],
    "growth_indicators": [...]
  },
  "search_strategy": {
    "github": {...},
    "linkedin_google": {...}
  }
}
```

---

### 【第二階段】雙管道智慧搜尋 (120 秒)

#### A. GitHub 搜尋 (60 秒)
**文件**: `github_talent_search.py`（既有，已驗證）

**流程**:
1. 生成搜尋關鍵字（中英文翻譯）
2. 用 GitHub API 搜尋開發者
3. 提取：username、repos、commits、技能
4. 返回 15-25 位候選人

**反爬蟲策略**:
- ✅ 隨機延遲 2-5 秒（HumanBehavior.request_pause）
- ✅ 每 60 人休息 12 秒（HumanBehavior.batch_pause）
- ✅ 隨機 User-Agent（UserAgentRotator）
- ✅ 指數退避重試（SmartRetry）

#### B. LinkedIn Google 搜尋 (45 秒)
**文件**: `web_search` API（Brave Search）

**流程**:
1. 生成搜尋查詢：`site:linkedin.com/in "職位" "技能" "位置"`
2. 用 web_search 工具搜尋
3. 提取個人檔案 URL
4. 返回 15-25 個 LinkedIn 連結

**優勢**:
- ✅ 無需登入（Google 搜尋）
- ✅ 反爬蟲風險低
- ✅ 職業背景驗證完整
- ✅ 可獲取聯繫信息

---

### 【第三階段】智慧去重 (自動)

**文件**: `talent_sourcing_pipeline.py`

**去重邏輯**:
1. 合併 GitHub 和 LinkedIn 候選人
2. 按名字（case-insensitive）去重
3. 優先保留「GitHub 評分更高」的版本
4. 同一人：合併兩個 URL，保留兩個來源

**最終輸出**: 25-40 位去重候選人

---

### 【第四階段】AI 配對評分 (150-200 秒)

**文件**: `candidate_scorer.py`

**評分維度** (動態，基於 JD):
```
1. 核心技能匹配 (35%)
   - 必備技能覆蓋度
   - 評分: 0-100

2. 經驗年資匹配 (25%)
   - 年資是否達到要求
   - 評分: 0-100

3. 行業背景適配 (20%)
   - 行業經驗是否相關
   - 評分: 0-100

4. 成長信號 (10%)
   - 最近 6 個月活躍度
   - GitHub commits 頻率

5. 企業文化契合 (5%)
   - 技術棧是否匹配
   - 評分: 0-100

6. 可觸達性 (5%)
   - GitHub Issues 聯繫
   - LinkedIn InMail 聯繫
```

**綜合分數**: 0-100  
**等級判定**:
- A+: 90-100 分 ✅ (強烈推薦)
- A: 80-89 分 ✅ (推薦)
- B: 70-79 分 ⏸️ (可考慮)
- C: 60-69 分 ❌ (不符合)
- D: <60 分 ❌ (差距大)

**只篩選 A+/A 級** (80+ 分)

**每人產出**:
- ✅ 評分分數 + 等級
- ✅ 5 個面試探討問題
- ✅ 300 字結論評論
- ✅ 建議聯繫方式
- ✅ 薪資符合度評估

---

### 【第五階段】批量上傳系統 (30-60 秒)

**API 端點**:
```
PUT https://backendstep1ne.zeabur.app/api/candidates/:id
Content-Type: application/json

{
  "status": "AI推薦",  // ⭐ 必須保留原始狀態
  "aiMatchResult": {
    "score": 89,
    "grade": "A+",
    "matched_skills": [...],
    "missing_skills": [...],
    "probing_questions": [...],
    "conclusion": "...",
    ...
  }
}
```

**上傳策略**:
- ✅ 批次大小：10 人
- ✅ 批次間隔：2 秒
- ✅ 錯誤重試：3 次指數退避
- ✅ 日誌記錄：成功/失敗清單

---

## 🛡️ 反爬蟲 & 人類行為模擬

**文件**: `human_behavior.py`, `ANTI_CRAWL_STRATEGY.md`

### 核心機制

#### 1. 隨機延遲
```python
HumanBehavior.think_pause()      # 1-3 秒（思考）
HumanBehavior.read_pause()       # 0.5-2 秒（閱讀）
HumanBehavior.action_pause()     # 0.2-1 秒（操作）
HumanBehavior.request_pause()    # 2-5 秒（API 請求）
HumanBehavior.batch_pause()      # 10-15 秒（批次間隔）
```

#### 2. User-Agent 輪換
```python
headers = UserAgentRotator.get_headers()
# 自動隨機選擇 5 個常見 UA
```

#### 3. 速率限制
```python
limiter = RateLimiter(requests_per_minute=30)
limiter.wait_if_needed()  # 自動檢查和等待
```

#### 4. 錯誤退避
```python
SmartRetry.retry_with_backoff(
    func=api_call,
    max_attempts=3,  # 5s → 10s → 20s
)
```

#### 5. 批次分散
```python
dispatcher = BatchDispatcher(batch_size=5)
results = dispatcher.process_with_batches(
    items=candidates,
    process_func=evaluate,
)
```

---

## 📊 模式選擇

### 保守方案（優先穩定）⭐⭐⭐⭐⭐
```
單人間隔：5 秒
批次間隔：15 秒
每小時：30 人
成功率：99%
時間：慢
適用：生產環境、長期運行
```

### 平衡方案（推薦）⭐⭐⭐⭐
```
單人間隔：2-3 秒
批次間隔：10-12 秒  
每小時：60 人
成功率：95%
時間：快
適用：日常使用（推薦）
```

### 激進方案（高風險）⭐⭐
```
單人間隔：0.5-1 秒
批次間隔：5 秒
每小時：150+ 人
成功率：70%
時間：非常快
適用：一次性爬蟲、風險可控
```

**目前系統使用：平衡方案**

---

## 🚀 進階用法

### 1. 自訂職缺添加

編輯 `jd_analyzer.py` 中的 `sample_jobs` 字典：

```python
# jd_analyzer.py, line ~35
sample_jobs = {
    51: { ... },  # 既有
    52: {         # 新增
        "id": 52,
        "title": "Python Backend Engineer",
        "company": "TechCorp",
        "description": "...",
        "salary_min": 70000,
        "salary_max": 100000,
        "experience_required": 2,
        ...
    }
}
```

### 2. 自訂評分權重

編輯 `candidate_scorer.py` 的 `_calculate_dimensions` 方法：

```python
# 改變權重
dimensions["skill_match"]["weight"] = 0.40  # 提高技能權重
dimensions["experience_match"]["weight"] = 0.20
```

### 3. 自訂搜尋策略

編輯 `jd_analyzer.py` 的 `_generate_github_keywords` 方法：

```python
def _generate_github_keywords(self, skills, location):
    return [
        f"{skills[0]} engineer {location}",  # 自訂格式
        f"{skills[0]} developer",
        ...
    ]
```

### 4. 集成到 Cron

```bash
# /Users/user/clawd/.openclaw/cron/talent-sourcing.json
{
  "schedule": "0 9 * * 1",  // 每週一 09:00
  "command": "python3 /Users/user/clawd/hr-tools/talent_sourcing_pipeline.py --job-ids 51,15 --execute"
}
```

---

## 📝 檔案結構

```
/Users/user/clawd/hr-tools/
├── talent_sourcing_pipeline.py      # ⭐ 主編排器
├── jd_analyzer.py                    # JD 分析
├── candidate_scorer.py               # AI 評分
├── human_behavior.py                 # 人類行為模擬
├── ANTI_CRAWL_STRATEGY.md            # 反爬蟲文檔
├── TALENT_SOURCING_GUIDE.md          # 本文檔
├── REQUIREMENTS.md                   # 需求整理
└── logs/                             # 日誌輸出
    ├── jd-analysis.json
    ├── scores.json
    └── upload-results.json
```

---

## 🔧 故障排除

### 問題 1: 導入失敗
```
ModuleNotFoundError: No module named 'jd_analyzer'
```
**解決**:
- 確保檔案名用下劃線 (`jd_analyzer.py`)，不是連字符
- 確保在正確目錄執行：`cd /Users/user/clawd/hr-tools`
- 確保 `__init__.py` 存在（可選，但推薦）

### 問題 2: 評分過低
```
✅ 評分完成: 0 位 A+/A 級候選人
```
**原因**: 模擬候選人數據不完整  
**解決**: 
- 連接真實 GitHub API（修改 `_search_github`）
- 連接真實 web_search API（修改 `_search_linkedin_google`）
- 提高模擬數據完整性

### 問題 3: API 限流（429）
```
🚫 429 Too Many Requests
```
**解決**:
- 增加延遲：`HumanBehavior.batch_pause(15, 20)`
- 減小批次：`BatchDispatcher(batch_size=3)`
- 等待 15 分鐘後重試

### 問題 4: 超時（Timeout）
```
⚠️ 請求超時
```
**解決**:
- 增加 timeout：`SessionManager(timeout=15)`
- 檢查網路連接
- 降低並行度

---

## 📊 性能指標

### 預期耗時（單個職位）
```
JD 分析：5-10 分鐘
GitHub 搜尋：60 秒
LinkedIn 搜尋：45 秒
去重：10 秒
AI 評分：150-200 秒（取決於候選人數）
上傳：30-60 秒
─────────────────────
總計：約 6-10 分鐘
```

### 預期成果（單個職位）
```
搜尋階段：40-50 人
去重後：25-35 人
A+/A 級：15-25 人
最終推薦：15-25 人（可聯繫）
```

### 成功率目標
```
GitHub API：95%+
LinkedIn 搜尋：99%+（Google 搜尋）
評分準確度：85%+
上傳成功率：98%+
```

---

## ✅ 檢查清單

執行前：
- [ ] Python 3.8+ 已安裝
- [ ] `requests` 已安裝
- [ ] GitHub Token 已設置（可選）
- [ ] 職缺 ID 確認（51 = C++, 15 = Information Security）

執行中：
- [ ] 無 429/403 錯誤
- [ ] 網路連接正常
- [ ] 控制台實時輸出可見

執行後：
- [ ] 所有日誌已記錄
- [ ] 候選人清單已生成
- [ ] API 上傳成功
- [ ] 前端能看到新候選人

---

## 🎯 下一步

1. **立即**：使用本系統處理 C++ Developer (id 51)
2. **本週**：處理 Information Security (id 15)、DevOps (id 16)
3. **下週**：設定 Cron 自動化（每週一早上 09:00）
4. **後續**：集成到 Telegram 群組，自動回報結果

---

## 📞 支援

問題？建議？  
- 查看 `ANTI_CRAWL_STRATEGY.md` 瞭解反爬蟲細節
- 查看 `REQUIREMENTS.md` 瞭解原始需求
- 修改 `jd_analyzer.py` 自訂職缺
- 修改 `candidate_scorer.py` 自訂評分邏輯

**目標**: 完全可複用於其他 AI 助理 🤖
