# Cron 自動化配置指南

## 概述

本指南說明如何將産業感知人才搜尋系統集成到日常招聘工作流程。

## 快速開始

### 1️⃣ 授予執行權限

```bash
chmod +x /Users/user/clawd/hr-tools/automated-recruiting-pipeline.sh
```

### 2️⃣ 設定 Telegram 通知（可選）

```bash
# 在 ~/.zshrc 或 ~/.bash_profile 中添加
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export TELEGRAM_CHAT_ID="your_chat_id_here"

# 重新載入
source ~/.zshrc
```

### 3️⃣ 測試管道

```bash
# 測試 Layer 1 搜尋
/Users/user/clawd/hr-tools/automated-recruiting-pipeline.sh layer1

# 查看日誌
tail -f /tmp/recruiting-pipeline/logs/pipeline-*.log
```

---

## Cron 排程配置

### 推薦配置

```bash
# Layer 1：每週一早上 8 點（P0 職缺，立即執行）
0 8 * * 1 /Users/user/clawd/hr-tools/automated-recruiting-pipeline.sh layer1 >> /tmp/cron-layer1.log 2>&1

# Layer 2：每週一早上 9 點（P1 職缺，本週執行）
0 9 * * 1 /Users/user/clawd/hr-tools/automated-recruiting-pipeline.sh layer2 >> /tmp/cron-layer2.log 2>&1

# 產業遷移分析：每週五下午 5 點
0 17 * * 5 /Users/user/clawd/hr-tools/automated-recruiting-pipeline.sh migration >> /tmp/cron-migration.log 2>&1

# 完整執行：每月第一天晚上 10 點
0 22 1 * * /Users/user/clawd/hr-tools/automated-recruiting-pipeline.sh full >> /tmp/cron-full.log 2>&1
```

### 編輯 Crontab

```bash
# macOS / Linux
crontab -e

# 貼入上面的配置，保存並退出
```

### 驗證 Cron 是否正確

```bash
# 列出當前 cron 任務
crontab -l

# 監控 cron 執行日誌（macOS）
log stream --predicate 'process == "cron"' --level debug
```

---

## 報告位置

### 自動生成的檔案

```
/tmp/recruiting-pipeline/
├── logs/
│   ├── pipeline-2026-02-26_08-00-00.log      # 詳細執行日誌
│   ├── scraper-2026-02-26_08-00-00.log       # 爬蟲日誌
│   ├── scorer-2026-02-26_08-00-00.log        # 評分日誌
│   └── ...
├── reports/
│   ├── search-results-2026-02-26_08-00-00.json      # 搜尋結果
│   ├── scoring-2026-02-26_08-00-00.json             # 評分結果
│   ├── recommendations-2026-02-26_08-00-00.json     # 推薦清單
│   ├── analytics-dashboard.html                     # 可視化儀表板
│   ├── analytics-report.json                        # 分析報告
│   └── migration-analysis-2026-02-26_08-00-00.json  # 遷移分析
└── jobs-layer1-2026-02-26_08-00-00.json            # 職缺清單
```

### 查看報告

```bash
# 查看最新推薦
cat /tmp/recruiting-pipeline/reports/recommendations-*.json | jq '.' | tail -20

# 打開儀表板（HTML）
open /tmp/recruiting-pipeline/reports/analytics-dashboard.html

# 即時監控日誌
tail -f /tmp/recruiting-pipeline/logs/pipeline-*.log
```

---

## 流程說明

### Layer 1 執行流程（P0 職缺）

```
1. 生成職缺列表
   └─ 從 Google Sheets 讀取「招募中」職缺（優先級 P0）

2. 產業感知爬蟲搜尋（unified-scraper-v4-enhanced.py）
   ├─ 客戶 → 產業映射（99% 置信度）
   ├─ 產業關鍵字庫（GitHub 搜尋詞）
   ├─ ThreadPoolExecutor 並行搜尋（3 個 workers）
   └─ 候選人結果 → JSON

3. 6 維評分系統（candidate-scoring-system-v2.py）
   ├─ 技能匹配度 (25%)
   ├─ 年資符合度 (20%)
   ├─ 地點適配度 (15%)
   ├─ 招聘意願度 (15%)
   ├─ 公司等級 (15%)
   └─ 產業經驗 (10%) ← 新增維度
   
4. 推薦生成（search-plan-executor.py）
   ├─ 按綜合評分排序
   ├─ Top 3 推薦 per 職缺
   └─ JSON + HTML 報告

5. 分析儀表板（industry-analytics-dashboard.py）
   ├─ 產業分布圓餅圖
   ├─ 評級分布條形圖
   ├─ 技能熱力圖
   └─ 候選人樣本表格

6. Telegram 通知
   └─ 發送執行結果摘要到指定聊天室
```

### Layer 2 執行流程（P1 職缺）

同 Layer 1，但：
- 搜尋範圍：P1 職缺（非立即）
- 並行度：2 個 workers（較少資源）
- 觸發條件：P1 職缺達 7 天未填滿

### 產業遷移分析（Migration）

```
for each 非直接匹配的候選人:
    1. 計算技能遷移度（0-100%）
    2. 計算產業相似度（0-100%）
    3. 計算學習準備度（基於經驗）
    4. 估計學習曲線（週數）
    5. 生成遷移潛力評分（0-100）
    6. 輸出推薦與培訓計畫
```

---

## 環境要求

### Python 依賴

```bash
pip3 install requests sqlite3 json dataclasses enum

# 或使用 requirements.txt
pip3 install -r /Users/user/clawd/hr-tools/requirements-recruiting.txt
```

### 系統要求

- Python 3.8+
- Bash 4.0+
- cron 服務（默認啟用）
- 網路連接（GitHub API）

### API 限制

- **GitHub API**：60 req/hour（免認證）或 5000/hour（認證）
- **建議**：設定 GitHub PAT 以提升限額
  ```bash
  export GITHUB_TOKEN="your_pat_token_here"
  ```

---

## 監控 & 維護

### 日常監控

```bash
# 檢查最近的 cron 執行
grep CRON /var/log/system.log | tail -20

# 檢查管道健康狀態
/Users/user/clawd/hr-tools/automated-recruiting-pipeline.sh health

# 查看今天的推薦
find /tmp/recruiting-pipeline/reports -name "*recommendations*" -mtime 0 -exec cat {} \; | jq '.'
```

### 故障排除

#### Cron 沒有執行

```bash
# 1. 確認 crontab 配置
crontab -l

# 2. 檢查 cron 守護程序
sudo launchctl list | grep cron

# 3. 重啟 cron（macOS）
sudo launchctl stop com.apple.cron
sudo launchctl start com.apple.cron

# 4. 檢查執行權限
ls -la /Users/user/clawd/hr-tools/automated-recruiting-pipeline.sh
```

#### 爬蟲失敗

```bash
# 1. 檢查 GitHub API 額度
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/rate_limit | jq '.rate_limit'

# 2. 檢查網路連接
ping api.github.com

# 3. 檢查 Python 環境
python3 -c "import requests; print('OK')"
```

#### 評分結果異常

```bash
# 1. 驗證輸入格式
head -1 /tmp/recruiting-pipeline/reports/search-results-*.json | jq '.' 

# 2. 測試評分系統
python3 /Users/user/clawd/hr-tools/candidate-scoring-system-v2.py --debug
```

---

## 報告示例

### JSON 推薦結果

```json
{
  "資安工程師": {
    "customer": "遊戲橘子集團",
    "industry": "gaming",
    "total_found": 28,
    "top_recommendations": [
      {
        "rank": 1,
        "name": "Candidate_A",
        "score": 86.5,
        "level": "A+",
        "skill_match": 90,
        "experience_fit": 85,
        "industry_experience": 80,
        "key_strengths": ["技能匹配", "年資充分"]
      }
    ]
  }
}
```

### HTML 儀表板

```html
✅ 開啟 /tmp/recruiting-pipeline/reports/analytics-dashboard.html
   包含：
   - 產業分布圓餅圖
   - 評級分布條形圖
   - 技能排行表
   - 候選人樣本表格
```

---

## 進階設置

### 自定義職缺優先級

編輯 `generate_jobs_list()` 函數：

```bash
# 修改 layer1 的優先級門檻
# 目前：P0 職缺
# 可改為：多人招聘、緊急職缺等

filter_priority() {
    local priority=$1
    case "$priority" in
        "P0") headcount >= 2 ;;
        "P1") headcount >= 1 ;;
        "P2") headcount >= 1 ;;
    esac
}
```

### 自定義評分權重

編輯 `candidate-scoring-system-v2.py`：

```python
WEIGHTS = {
    'skill_match': 0.30,          # 提升至 30%
    'experience_fit': 0.20,
    'location_fit': 0.10,         # 降低至 10%
    'hiring_signal': 0.15,
    'company_level': 0.15,
    'industry_experience': 0.10,  # 可調整
}
```

### 集成 Step1ne API

```bash
# 自動導入推薦到履歷池
curl -X POST https://backendstep1ne.zeabur.app/api/candidates/bulk \
  -H "Content-Type: application/json" \
  -d @/tmp/recruiting-pipeline/reports/recommendations-*.json \
  -H "Authorization: Bearer $API_TOKEN"
```

---

## 成本評估

### 執行成本

| 層級 | API 呼叫 | 執行時間 | 頻率 | 月成本 |
|------|----------|---------|------|--------|
| Layer 1 | ~500 | 5 分鐘 | 週 1 次 | $0（免費額度內） |
| Layer 2 | ~300 | 3 分鐘 | 週 1 次 | $0（免費額度內） |
| Migration | ~200 | 2 分鐘 | 週 1 次 | $0（免費額度內） |
| Full | ~1000 | 10 分鐘 | 月 1 次 | $0（免費額度內） |

**備註**：GitHub API 免費額度 60 req/hour 足以支持本系統

---

## 聯絡與支援

如有問題：

1. 檢查日誌：`/tmp/recruiting-pipeline/logs/`
2. 查看文檔：本文件
3. 測試單個模組：`python3 <module>.py --help`
4. 聯絡技術支援：Jacky-aibot

---

**最後更新**：2026-02-26
**版本**：v2.0
**狀態**：✅ 生產就緒
