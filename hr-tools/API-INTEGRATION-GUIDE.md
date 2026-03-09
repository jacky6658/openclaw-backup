# Step1ne API 集成指南

## 概述

本指南說明如何自動將招聘搜尋結果導入 Step1ne 履歷池。

---

## 🚀 快速開始

### 1️⃣ 驗證 API 連線

```bash
# 測試 API 健康狀態
curl https://backendstep1ne.zeabur.app/api/health

# 預期回應
{"success":true,"status":"ok","database":"connected"}
```

### 2️⃣ 乾執行模式（預覽）

```bash
# 預覽將導入的候選人，但不實際導入
python3 /Users/user/clawd/hr-tools/api-integration-sync.py \
  --recommendations /tmp/search-execution/recommendations.json \
  --dry-run
```

### 3️⃣ 真正導入

```bash
# 實際導入到履歷池
python3 /Users/user/clawd/hr-tools/api-integration-sync.py \
  --recommendations /tmp/search-execution/recommendations.json
```

### 4️⃣ 檢查結果

```bash
# 查看同步結果
cat /tmp/recruiting-pipeline/reports/sync-result-*.json | jq '.'
```

---

## 📋 完整流程

```
推薦結果
├─ /tmp/search-execution/recommendations.json
│
↓ api-integration-sync.py
│
├─ Step 1: API 健康檢查
├─ Step 2: 讀取推薦
├─ Step 3: 去重檢查（避免重複）
├─ Step 4: 轉換為 API 格式
├─ Step 5: 批量導入
│
↓
│
├─ 履歷池更新
│  └─ 新增 5 位候選人
│
├─ 去重記錄
│  └─ /tmp/recruiting-pipeline/dedup.db
│
└─ 同步報告
   └─ /tmp/recruiting-pipeline/reports/sync-result-*.json
```

---

## 🔄 自動化集成

### 與管道腳本集成

管道已包含自動 API 同步：

```bash
# Layer 1 執行時自動同步
/Users/user/clawd/hr-tools/automated-recruiting-pipeline.sh layer1

# 流程包含：
# 1. 爬蟲搜尋 ✅
# 2. 6 維評分 ✅
# 3. 推薦生成 ✅
# 4. API 同步 ✅（新增）
# 5. 報告生成 ✅
```

### Cron 自動排程

編輯 crontab：

```bash
crontab -e

# 添加以下行（自動同步）
0 8 * * 1 /Users/user/clawd/hr-tools/automated-recruiting-pipeline.sh layer1
```

每週一早上 08:00 自動運行，包含：
- 搜尋 5 位候選人
- 6 維評分
- 自動導入到履歷池

---

## 📊 數據格式

### 推薦輸入格式

```json
{
  "recommendations": {
    "資安工程師": {
      "customer": "遊戲橘子集團",
      "industry": "gaming",
      "total_found": 5,
      "top_recommendations": [
        {
          "rank": 1,
          "name": "John Doe",
          "score": 94,
          "level": "S",
          "github_url": "https://github.com/johndoe"
        }
      ]
    }
  }
}
```

### API 導入格式

自動轉換為：

```json
{
  "name": "John Doe",
  "position": "資安工程師",
  "location": "台北",
  "years_experience": "5",
  "skills": "DevOps, Linux, Security",
  "source": "Automated Search - GAMING",
  "recruiter": "Jacky",
  "notes": "自動搜尋推薦 | 職缺：資安工程師 | 綜合評分：94 分【S】 | 技能匹配：90%",
  "github_url": "https://github.com/johndoe",
  "actor": "Jacky-aibot"
}
```

---

## 🛡️ 去重機制

### 工作原理

每個候選人生成唯一 hash：

```
hash = MD5(姓名 + 職位 + GitHub URL)
```

如果 hash 已存在於 `/tmp/recruiting-pipeline/dedup.db`：
- ✅ 跳過（避免重複）
- 📝 記錄在日誌中

### 查詢導入歷史

```python
from api_integration_sync import DeduplicationManager

mgr = DeduplicationManager()
history = mgr.get_import_history(days=30)
for record in history:
    print(f"{record[2]} - {record[3]} (ID: {record[4]})")
```

### 清除去重記錄（謹慎）

```bash
# 刪除 7 天前的記錄
sqlite3 /tmp/recruiting-pipeline/dedup.db \
  "DELETE FROM imported_candidates WHERE imported_at < datetime('now', '-7 days')"
```

---

## ❌ 常見問題

### Q1：導入失敗，錯誤 "API 連線失敗"

**原因**：API 伺服器離線或網路中斷

**解決**：
```bash
# 檢查 API 狀態
curl -v https://backendstep1ne.zeabur.app/api/health

# 檢查網路連接
ping backendstep1ne.zeabur.app

# 重試導入
python3 api-integration-sync.py --recommendations <file>
```

### Q2：導入成功但候選人沒出現在 UI

**原因**：
1. 前端快取問題
2. 履歷池頁面未刷新
3. 篩選設定不符

**解決**：
1. 重新整理頁面（Cmd+R）
2. 清除瀏覽器快取（Cmd+Shift+Delete）
3. 檢查是否有「隱藏」篩選

### Q3：收到 "skipped duplicates" 通知

**原因**：該候選人已導入過

**解決**：
正常行為。系統防止重複導入。

如需強制重導：
```bash
# 清除特定候選人的去重記錄
sqlite3 /tmp/recruiting-pipeline/dedup.db \
  "DELETE FROM imported_candidates WHERE name = '候選人姓名'"
```

### Q4：導入後無法修改候選人資訊

**原因**：API 返回 201（已創建），但 ID 無法取得

**解決**：
1. 手動在 UI 中修改（暫時方案）
2. 查詢 API 獲取 ID
3. 使用 PATCH 端點更新

---

## 🔗 API 端點參考

### 新增候選人

```bash
POST https://backendstep1ne.zeabur.app/api/candidates

Content-Type: application/json
Authorization: （無需）

{
  "name": "John Doe",
  "position": "Engineer",
  "location": "Taipei",
  "skills": "Python, Go",
  "actor": "Jacky-aibot"
}
```

### 批量新增

```bash
POST https://backendstep1ne.zeabur.app/api/candidates/bulk

[
  { "name": "Person 1", ... },
  { "name": "Person 2", ... }
]
```

### 查詢候選人

```bash
GET https://backendstep1ne.zeabur.app/api/candidates

# 篩選
GET https://backendstep1ne.zeabur.app/api/candidates?source=Automated%20Search
```

### 更新候選人

```bash
PATCH https://backendstep1ne.zeabur.app/api/candidates/:id

{
  "notes": "已聯繫，安排面試",
  "actor": "Jacky-aibot"
}
```

---

## 📈 監控與報告

### 同步統計

```bash
# 查看最新同步結果
cat /tmp/recruiting-pipeline/reports/sync-result-$(date +%Y-%m-%d)*.json | jq '.{successfully_imported, skipped_duplicates, failed}'

# 預期輸出
{
  "successfully_imported": 5,
  "skipped_duplicates": 2,
  "failed": 0
}
```

### 日誌查看

```bash
# 最新 API 同步日誌
tail -50 /tmp/recruiting-pipeline/logs/api-sync-*.log

# 監控日誌（即時）
tail -f /tmp/recruiting-pipeline/logs/api-sync-*.log
```

### 去重記錄查詢

```bash
# 查看導入歷史
sqlite3 /tmp/recruiting-pipeline/dedup.db "SELECT name, job_title, imported_at FROM imported_candidates LIMIT 10"

# 統計導入數量
sqlite3 /tmp/recruiting-pipeline/dedup.db "SELECT COUNT(*) as total FROM imported_candidates"

# 按日期分布
sqlite3 /tmp/recruiting-pipeline/dedup.db "SELECT DATE(imported_at), COUNT(*) as count FROM imported_candidates GROUP BY DATE(imported_at)"
```

---

## 🔐 安全考慮

### actor 身份

所有 API 呼叫必須包含 `actor` 欄位：

```python
actor = "Jacky-aibot"  # 標準格式
```

此欄位用於：
- ✅ 審計追蹤（誰做的）
- ✅ 權限驗證
- ✅ 日誌記錄

### 環境變數（可選）

```bash
# 如果需要認證（目前不需）
export STEP1NE_API_TOKEN="your_token"
export STEP1NE_API_BASE="https://custom-api.example.com"
```

---

## 💾 備份與還原

### 備份去重數據庫

```bash
# 備份
cp /tmp/recruiting-pipeline/dedup.db /backup/dedup-$(date +%Y-%m-%d).db

# 定時備份（Cron）
0 2 * * * cp /tmp/recruiting-pipeline/dedup.db /backup/dedup-$(date +\%Y-\%m-\%d).db
```

### 還原

```bash
# 如果誤操作，從備份還原
cp /backup/dedup-YYYY-MM-DD.db /tmp/recruiting-pipeline/dedup.db
```

---

## 📊 性能優化

### 批量導入大小

預設：10 位候選人/批次

調整（如需）：

```bash
python3 api-integration-sync.py \
  --recommendations <file> \
  --batch-size 20  # 提升到 20
```

### API 呼叫延遲

當前實現：無額外延遲（快速）

如需限流（防止過載）：

```python
# 在 api-integration-sync.py 中修改
time.sleep(0.5)  # 每個候選人間隔 500ms
```

---

## 📞 支援

### 遇到問題

1. 檢查日誌：`/tmp/recruiting-pipeline/logs/api-sync-*.log`
2. 測試 API：`curl https://backendstep1ne.zeabur.app/api/health`
3. 乾執行驗證：`--dry-run` 旗標
4. 聯繫技術支援：Jacky-aibot

### 反饋與改進

有建議嗎？
- 編輯 `api-integration-sync.py`
- 提交更改到 GitHub
- 與 Jacky 討論

---

**最後更新**：2026-02-26  
**版本**：v1.0  
**狀態**：✅ 生產就緒
