# 智慧人才搜尋系統 - 完整文檔

**版本**: v1.0  
**最後更新**: 2026-02-27  
**系統狀態**: ✅ 生產就緒

---

## 📋 快速開始

### 最簡單的用法（一行命令）

```bash
python3 /Users/user/clawd/hr-tools/talent_sourcing_pipeline.py --job-id 51 --execute
```

**效果**：
- 自動搜尋職缺 ID 51 的候選人（GitHub + LinkedIn）
- AI 評分所有候選人
- 根據等級自動分類（推薦 vs 備選）
- 上傳到系統

**耗時**: ~5-10 分鐘  
**結果**: 20-50 位候選人

---

## 🎯 系統流程（5 階段）

### 階段 1️⃣ JD 分析
```
輸入：職缺 ID
  ↓
解析：公司畫像、職位要求、人才畫像
  ↓
輸出：搜尋策略（GitHub 關鍵字 + LinkedIn 查詢）
```

**時間**: 2-3 秒

---

### 階段 2️⃣ 雙管道搜尋
```
GitHub 搜尋（60 秒）
  • 解析代碼語言、提交頻率、開源貢獻
  • 找到 10-20 位候選人

LinkedIn Google 搜尋（45 秒）
  • 使用 site:linkedin.com/in + 職位關鍵字
  • 找到 10-20 位候選人
```

**時間**: 90 秒 + 人類行為延遲（2-3 秒）  
**結果**: 20-40 位候選人

---

### 階段 3️⃣ 智慧去重
```
去除同一人的重複記錄
  ↓
【智慧回退】如果 0 人：
  • 放寬搜尋條件（降低 20% 技能要求）
  • 重試 1 次
  • 仍是 0 人 → 中止，通知使用者
```

**結果**: 15-30 位候選人

---

### 階段 4️⃣ AI 配對評分（核心）
```
每位候選人評分 6 個維度：

1. 技能匹配度 (35%)
   • 核心技能符合度
   • 進階技能加分

2. 工作經驗 (25%)
   • 相關產業年資
   • 層級匹配度

3. 產業適配性 (20%)
   • 文化相似度
   • 發展階段匹配

4. 成長信號 (10%)
   • GitHub 提交頻率
   • 學習主動性

5. 文化契合度 (5%)
   • 工作地點
   • 遠端意願

6. 可觸達性 (5%)
   • LinkedIn 活躍度
   • 聯繫方式

結果：0-100 分
```

**評分等級**：

| 等級 | 分數 | 狀態 | 說明 |
|------|------|------|------|
| S | 95+ | 🎯 AI推薦 | 完美契合，立即聯繫 |
| A+ | 90-94 | 🎯 AI推薦 | 高度契合 |
| A | 80-89 | 🎯 AI推薦 | 符合要求 |
| B | 70-79 | 🎯 AI推薦 | 可接受 |
| C | 60-69 | 📋 備選人才 | 有潛力 |
| D | <60 | 📋 備選人才 | 低優先 |

**輸出**：每位候選人包括：
- 評分 & 等級
- 5 個面試問題
- 薪資期望分析
- 完整評論（200+ 字）

---

### 階段 5️⃣ 批量上傳
```
上傳前檢查：
  • 是否已在系統中？
  • 新評分是否更高？
  
上傳邏輯：
  • A-S 級 → status = "AI推薦"
  • C-D 級 → status = "備選人才"
  
上傳結果：
  • 成功數 ✅
  • 失敗數 ❌
  • 詳細回報
```

**結果**: 所有候選人進入系統

---

## 📊 系統模式

### 1. DRY-RUN（分析模式）
```bash
python3 talent_sourcing_pipeline.py --job-id 51 --dry-run
```
**效果**：只分析 JD，不執行搜尋  
**用途**：查看搜尋策略、確認無誤後再執行

---

### 2. EXECUTE（執行模式）
```bash
python3 talent_sourcing_pipeline.py --job-id 51 --execute
```
**效果**：完整執行（搜尋 + 評分 + 上傳）  
**用途**：真實爬蟲，獲取候選人

---

### 3. TEST（測試模式）
```bash
python3 talent_sourcing_pipeline.py --job-id 51 --execute --test-zero-dedup
```
**效果**：故意讓去重後 0 人，驗證智慧回退邏輯  
**用途**：測試系統穩定性

---

### 4. 批量處理
```bash
python3 talent_sourcing_pipeline.py --job-ids 51,15,16 --execute
```
**效果**：依序處理多個職缺  
**用途**：一次搜尋多個職位

---

## 🤖 AI 智能配對 - 提示詞範本

### 給新 AI 助理的提示

**場景**：你是 Step1ne 系統的 AI 配對引擎

**你的目標**：
1. 分析職缺需求
2. 搜尋候選人（GitHub + LinkedIn）
3. AI 評分（6 維度）
4. 自動分類（推薦 vs 備選）
5. 上傳到系統

**基本命令**：
```bash
# 先 DRY-RUN 確認策略
python3 /Users/user/clawd/hr-tools/talent_sourcing_pipeline.py --job-id {JOB_ID} --dry-run

# 執行爬蟲
python3 /Users/user/clawd/hr-tools/talent_sourcing_pipeline.py --job-id {JOB_ID} --execute
```

**監控指標**：
- ✅ 成功上傳的候選人數
- 📊 A-S 級（推薦）的比例
- ⏱️ 總耗時

**成功標準**：
- 找到 15+ 位候選人
- A-B 級佔 60%+ （或有智慧回退的必要性）
- 0 個上傳失敗

---

## 📁 檔案結構

```
/Users/user/clawd/hr-tools/
├── talent_sourcing_pipeline.py     ⭐ 主程式
├── jd_analyzer.py                  分析職缺
├── candidate_scorer.py             AI 評分
├── human_behavior.py               反爬蟲防禦
├── deduplication_handler.py        去重邏輯
├── TALENT_SOURCING_SYSTEM.md       ← 本文檔
└── TALENT_SOURCING_GUIDE.md        其他 AI 專用指南
```

---

## 🔧 核心參數

### 搜尋策略配置

**GitHub 搜尋**：
- 關鍵字：從 JD 提取（e.g., `C++`, `Docker`, `Linux`）
- 結果數：最多 20 位
- 篩選：按 stars 和最近活動排序

**LinkedIn Google 搜尋**：
- 查詢：`site:linkedin.com/in + {職位名} + {地點}`
- 結果數：最多 20 位
- 篩選：按相關性排序

---

## ⚡ 人類行為模擬（反爬蟲）

系統內建 5 層反爬蟲防禦：

```
Layer 1: 隨機延遲（1-15 秒，context-aware）
Layer 2: User-Agent 輪換（5 種瀏覽器）
Layer 3: 速率限制（30 requests/min）
Layer 4: 指數退避重試（5s → 10s → 20s）
Layer 5: 批次分散（10-15 秒間隔）
```

**結果**：避免被 IP 封鎖或限流

---

## 💾 輸出格式

### API 上傳數據結構

```json
{
  "status": "AI推薦" | "備選人才",
  "recruitment_source": "自動爬蟲",
  "added_date": "2026-02-27",
  "aiMatchResult": {
    "score": 89,
    "grade": "A",
    "position": "C++ Developer",
    "company": "UnityTech",
    "matched_skills": ["C++", "Docker", "Linux"],
    "missing_skills": ["Kubernetes"],
    "strengths": ["高活躍度", "技術深度"],
    "probing_questions": [
      "請分享你最複雜的 C++ 項目經驗",
      "你如何處理 Docker 容器化中的性能優化？",
      "...（5 個問題）"
    ],
    "salary_fit": "期望 100-150K TWD，符合 80%",
    "conclusion": "技能與職缺高度匹配...",
    "github_url": "https://github.com/...",
    "linkedin_url": "https://linkedin.com/in/...",
    "sourced_from": "talent-sourcing-pipeline",
    "auto_sourced_at": "2026-02-27T22:00:00Z"
  }
}
```

---

## 📈 效能指標

| 指標 | 目標 | 實際 |
|------|------|------|
| 搜尋時間 | <2分鐘 | 90s + 延遲 |
| 候選人數 | 20-50人 | ✅ |
| 評分準確 | A-S 級 60%+ | ✅ |
| 上傳成功率 | >95% | ✅ |
| 無重複 | 100% | ✅ |

---

## 🚀 擴展選項

### 實時監控
```bash
# 每 30 秒檢查進度
watch -n 30 'tail -20 /tmp/upload-report-*.txt'
```

### 定時任務
```bash
# 每天 09:00 自動搜尋 C++ Developer
0 9 * * * /Users/user/clawd/hr-tools/talent_sourcing_pipeline.py --job-id 51 --execute
```

### 多職位並行
```bash
# 同時搜尋 3 個職位
parallel python3 /Users/user/clawd/hr-tools/talent_sourcing_pipeline.py --job-id {} --execute ::: 51 15 16
```

---

## ❓ 常見問題

**Q: 去重後 0 人怎麼辦？**  
A: 系統自動觸發「智慧回退」，放寬搜尋條件重試 2 次。如果仍是 0 人，會通知你。

**Q: 如何修改評分維度？**  
A: 編輯 `candidate_scorer.py` 中的 `_calculate_dimensions()` 方法。

**Q: 支援其他職位嗎？**  
A: 支援任何在系統中的職缺 ID。只需改 `--job-id` 參數。

**Q: 可以調整等級閾值嗎？**  
A: 可以。在 `candidate_scorer.py` 中修改 `_determine_grade()` 方法的分數區間。

---

## 🔐 API 端點

系統使用以下 API：

```
GET /api/candidates        # 查詢現有候選人（去重）
GET /api/candidates/{id}   # 查詢單一候選人詳情
PATCH /api/candidates/{id} # 更新候選人評分
POST /api/candidates       # 新增候選人
```

**認證**：Bearer Token（自動）

---

## 📞 支援與反饋

- **問題報告**: 查看 `/tmp/upload-report-*.txt`
- **日誌查看**: `tail -f /tmp/talent-sourcing.log`
- **文檔更新**: 編輯本文件並提交 GitHub

---

**最後更新**：2026-02-27  
**系統狀態**：✅ 生產環境就緒  
**下一步**：選擇職缺 ID 開始爬蟲！ 🚀
