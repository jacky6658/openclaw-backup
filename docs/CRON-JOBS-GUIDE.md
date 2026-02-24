# OpenClaw 定時任務實作指南

## 目錄
1. [任務結構說明](#任務結構說明)
2. [提示詞撰寫技巧](#提示詞撰寫技巧)
3. [常見範例](#常見範例)
4. [最佳實踐](#最佳實踐)

---

## 任務結構說明

### 基本結構
```json
{
  "name": "任務名稱",
  "enabled": true,
  "schedule": { /* 時間設定 */ },
  "sessionTarget": "isolated", // main 或 isolated
  "wakeMode": "now", // now 或 next-heartbeat
  "payload": { /* 任務內容 */ },
  "delivery": { /* 回報方式 */ }
}
```

### Schedule（排程設定）

#### 1. Cron 表達式（固定時間）
```json
{
  "kind": "cron",
  "expr": "0 9 * * *",  // 每天早上 9:00
  "tz": "Asia/Taipei"
}
```

**常用 Cron 表達式：**
- `0 9 * * *` — 每天 09:00
- `30 14 * * *` — 每天 14:30
- `0 21 * * *` — 每天 21:00
- `0 9 * * 1` — 每週一 09:00
- `0 3 * * 0` — 每週日 03:00
- `0 2 31 3,6,9,12 *` — 每季最後一天 02:00

#### 2. 間隔執行（Every）
```json
{
  "kind": "every",
  "everyMs": 3600000,  // 每小時（毫秒）
  "anchorMs": 1770900308004  // 起始時間
}
```

#### 3. 一次性任務（At）
```json
{
  "kind": "at",
  "at": "2026-02-28T01:00:00.000Z"
}
```

### Payload（任務內容）

#### 類型 A：systemEvent（主 session）
```json
{
  "kind": "systemEvent",
  "text": "執行履歷池自動收集：bash /path/to/script.sh"
}
```
- 適用：直接執行腳本、簡單提醒
- sessionTarget 必須是 `"main"`

#### 類型 B：agentTurn（隔離 session）
```json
{
  "kind": "agentTurn",
  "message": "執行每日找人選...",
  "timeoutSeconds": 300,
  "model": "anthropic/claude-sonnet-4-5"
}
```
- 適用：複雜任務、需要 AI 判斷
- sessionTarget 必須是 `"isolated"`

### Delivery（回報方式）

#### 1. 不回報（適合背景任務）
```json
{
  "mode": "none"
}
```

#### 2. 發送到 Telegram
```json
{
  "mode": "announce",
  "channel": "telegram",
  "to": "-1003231629634",  // 群組 ID
  "bestEffort": true
}
```

#### 3. 發送到 Thread
```json
{
  "mode": "announce",
  "channel": "telegram",
  "to": "-1003231629634:326"  // 群組 ID:Thread ID
}
```

---

## 提示詞撰寫技巧

### 結構化提示詞（推薦）

```
執行 [任務名稱]（[時間點]）：

[職缺/背景資訊]：
職缺：1人，薪資 XXX
技能：XXX、YYY、ZZZ
經驗：X年以上

1. 執行：bash /path/to/script.sh "參數"
2. 搜尋管道：[說明搜尋策略]
3. AI 配對評分
4. Top 3 推薦發送到 [目標位置]
5. 若無符合候選人，回報 HEARTBEAT_OK
```

### 關鍵元素

1. **明確的執行步驟**（1, 2, 3...）
2. **成功/失敗判斷**（若無結果 → HEARTBEAT_OK）
3. **回報格式**（報告 XXX / 若無 YYY）
4. **檔案路徑**（完整絕對路徑）
5. **Timeout 設定**（複雜任務設 300-600 秒）

### 避免的寫法

❌ **太模糊**
```
請幫我搜尋人選
```

❌ **沒有失敗處理**
```
執行搜尋腳本，然後發送結果
```

❌ **相對路徑**
```
bash ./script.sh  # 可能找不到檔案
```

✅ **正確寫法**
```
執行搜尋腳本：bash /Users/user/clawd/hr-tools/search.sh
若找到候選人，發送結果；若無，回報 HEARTBEAT_OK
```

---

## 常見範例

### 1. 每日找人選（完整範例）

```json
{
  "name": "每日找人選 10:00 - 專案經理PM(創樂科技)",
  "enabled": true,
  "schedule": {
    "kind": "cron",
    "expr": "0 10 * * *",
    "tz": "Asia/Taipei"
  },
  "sessionTarget": "isolated",
  "wakeMode": "now",
  "payload": {
    "kind": "agentTurn",
    "message": "執行每日找人選（專案經理PM - 創樂科技有限公司）：\n\n職缺：1人，薪資 40k+\n技能：專案管理、Jira、iOS/Android App、Web設計準則、跨部門溝通\n經驗：2年以上\n地點：台北市內湖區\n\n1. 執行：bash /Users/user/clawd/hr-tools/unified-candidate-pipeline.sh \"專案經理-創樂科技\"\n2. 搜尋管道：✅ 外部優先（GitHub → LinkedIn）→ ⏸️ 履歷池（2/28 起啟用）\n3. AI 配對評分\n4. Top 3 推薦發送到 Topic 304（履歷池）\n5. 若無符合候選人，回報 HEARTBEAT_OK",
    "timeoutSeconds": 300,
    "model": "anthropic/claude-sonnet-4-5"
  },
  "delivery": {
    "mode": "announce",
    "channel": "telegram",
    "to": "-1003231629634",
    "bestEffort": true
  }
}
```

**關鍵要點：**
- ✅ 職缺資訊清楚（薪資、技能、經驗）
- ✅ 執行步驟明確（1-5）
- ✅ 有失敗處理（若無候選人 → HEARTBEAT_OK）
- ✅ 設定 timeout（300 秒）
- ✅ 發送到特定群組

---

### 2. BD 自動開發（背景任務）

```json
{
  "name": "BD自動開發-05:00（每天）",
  "enabled": true,
  "schedule": {
    "kind": "cron",
    "expr": "0 5 * * *",
    "tz": "Asia/Taipei"
  },
  "sessionTarget": "isolated",
  "wakeMode": "now",
  "payload": {
    "kind": "agentTurn",
    "message": "執行 BD 自動開發（05:00）：\n\n1. 執行腳本：bash ~/clawd/hr-tools/active/automation/auto-bd-crawler.sh\n2. 104 搜尋职缺 → 爬公司資訊 → 去重 → 匯入 BD客戶開發表\n3. 報告結果：找到幾家新公司（如果有）\n4. 若無新公司，回報 HEARTBEAT_OK",
    "timeoutSeconds": 600,
    "model": "anthropic/claude-sonnet-4-5"
  },
  "delivery": {
    "mode": "none"  // 不回報，避免打擾
  }
}
```

**關鍵要點：**
- ✅ 早上 5 點執行（避開工作時間）
- ✅ Timeout 設長一點（600 秒，因為要爬蟲）
- ✅ 不回報（mode: none）

---

### 3. 履歷池自動收集（簡單腳本）

```json
{
  "name": "履歷池自動累積 - 早上",
  "enabled": true,
  "schedule": {
    "kind": "cron",
    "expr": "0 9 * * *",
    "tz": "Asia/Taipei"
  },
  "sessionTarget": "main",
  "wakeMode": "now",
  "payload": {
    "kind": "systemEvent",
    "text": "執行履歷池自動收集：bash /Users/user/clawd/hr-tools/auto-collect-candidates.sh"
  }
}
```

**關鍵要點：**
- ✅ 使用 systemEvent（簡單腳本）
- ✅ sessionTarget: main（不需要 AI 判斷）
- ✅ 沒有設定 delivery（預設不回報）

---

### 4. 每週市場報告（複雜任務）

```json
{
  "name": "每週市場報告發佈（總覽看板 Topic 326）",
  "enabled": true,
  "schedule": {
    "kind": "cron",
    "expr": "0 9 * * 1",  // 每週一 09:00
    "tz": "Asia/Taipei"
  },
  "sessionTarget": "isolated",
  "wakeMode": "now",
  "payload": {
    "kind": "agentTurn",
    "message": "執行每週市場調查報告發佈：\n\n1. 檢查本週是否已生成新報告（market-analysis-2026.xx.xx.html）\n2. 若有新報告，發送到 HR AI招募自動化群組 Topic 326（總覽看板）\n3. 訊息格式：\n   - 標題：📊 2026 市場調查分析報告（本週）\n   - 報告日期 + 版本\n   - Part 1：市場概況摘要（Top 30 職缺、五大缺工產業）\n   - Part 2：內部職缺分析摘要（26 企業、3 職缺、履歷池、BD 進度、Pipeline）\n   - 完整報告連結：https://jacky6658.github.io/aijob-presentations/market-analysis-2026.xx.xx.html\n   - 歸檔庫連結：https://github.com/jacky6658/market-reports-archive\n4. 使用 message tool，參數：channel=telegram, target=-1003231629634, threadId=326\n5. 若本週無新報告，回報 HEARTBEAT_OK\n\n重要：確保 threadId=326（總覽看板）",
    "timeoutSeconds": 180,
    "model": "anthropic/claude-haiku-4-5"
  },
  "delivery": {
    "mode": "none"
  }
}
```

**關鍵要點：**
- ✅ 每週一執行
- ✅ 詳細的訊息格式說明
- ✅ 指定使用 message tool（而非自動 delivery）
- ✅ 有條件判斷（若無新報告 → HEARTBEAT_OK）

---

### 5. 每日備份與交接（提醒類）

```json
{
  "name": "每日備份：/Users/user/clawd → GitHub (openclaw-backup)",
  "enabled": true,
  "schedule": {
    "kind": "cron",
    "expr": "0 21 * * *",
    "tz": "Asia/Taipei"
  },
  "sessionTarget": "main",
  "wakeMode": "next-heartbeat",
  "payload": {
    "kind": "systemEvent",
    "text": "【提醒】現在是晚上 9 點（Asia/Taipei），每日 GitHub 備份時間。請在 /Users/user/clawd 執行備份：git status →（必要時更新 .gitignore，避免 node_modules/output/tmp 等）→ git add -A → git commit（訊息含日期）→ git push 到 jacky6658/openclaw-backup。完成後請到 AIJob 群組「用量回報」Thread 514 補一行：『備份：成功/失敗 + commit hash』。"
  }
}
```

**關鍵要點：**
- ✅ wakeMode: next-heartbeat（不立刻執行，等下次 heartbeat）
- ✅ 清楚的操作步驟（git status → add → commit → push）
- ✅ 提醒後續動作（回報到特定 Thread）

---

### 6. 一次性提醒（At 排程）

```json
{
  "name": "提醒：啟用履歷池搜尋（關閉對外）",
  "enabled": true,
  "deleteAfterRun": true,  // 執行後自動刪除
  "schedule": {
    "kind": "at",
    "at": "2026-02-28T01:00:00.000Z"
  },
  "sessionTarget": "main",
  "wakeMode": "now",
  "payload": {
    "kind": "systemEvent",
    "text": "【提醒】今天是 2/28，根據 Jacky 指示，需要修改找人選系統：\n\n關閉對外搜尋（GitHub/LinkedIn），啟用履歷池搜尋。\n\n修改檔案：/Users/user/clawd/hr-tools/unified-candidate-pipeline.sh\n\n請：\n1. 關閉 GitHub/LinkedIn 搜尋\n2. 啟用履歷池搜尋（python3 search-resume-pool.py）\n3. 測試確認無誤"
  }
}
```

**關鍵要點：**
- ✅ 使用 `at`（一次性）
- ✅ `deleteAfterRun: true`（自動清理）
- ✅ 清楚的任務說明

---

## 最佳實踐

### 1. Timeout 設定建議

| 任務類型 | Timeout | 原因 |
|---------|---------|------|
| 簡單腳本（systemEvent） | 無需設定 | 預設足夠 |
| 搜尋人選（agentTurn） | 300 秒 | 爬蟲 + AI 配對 |
| BD 爬蟲（agentTurn） | 600 秒 | 批量爬蟲耗時 |
| 報告生成（agentTurn） | 180 秒 | 檔案讀取 + 格式化 |

### 2. Model 選擇建議

| 任務複雜度 | Model | 原因 |
|-----------|-------|------|
| 簡單判斷 | claude-haiku-4-5 | 便宜、快速 |
| 中等複雜 | claude-sonnet-4-5 | 平衡 |
| 需要推理 | 不設定（用預設） | 自動選最佳 |

### 3. 回報策略

| 情境 | Delivery Mode | 說明 |
|------|--------------|------|
| 背景任務 | none | 不打擾 |
| 重要結果 | announce + channel | 發到群組 |
| 緊急通知 | announce + 個人 | 直接通知 |
| 需要確認 | announce + thread | 發到特定討論串 |

### 4. 失敗處理

**所有任務都應該有失敗處理：**

```
5. 若無符合候選人，回報 HEARTBEAT_OK
```

或

```
4. 若失敗，提供詳細錯誤訊息
```

### 5. 時間選擇策略

| 任務類型 | 建議時間 | 原因 |
|---------|---------|------|
| 爬蟲任務 | 05:00-07:00 | 避開反爬蟲高峰 |
| 搜尋人選 | 08:00-16:00 | 分散執行，避免集中 |
| 發信任務 | 09:30, 14:30 | 上班時段，回覆率高 |
| 備份任務 | 21:00-03:00 | 深夜，避免衝突 |
| 報告任務 | 09:00（週一） | 週初，方便規劃 |

---

## 檢查清單

建立新任務前，確認：

- [ ] 提示詞結構清晰（步驟 1, 2, 3...）
- [ ] 有失敗處理（HEARTBEAT_OK 或錯誤回報）
- [ ] 檔案路徑使用絕對路徑
- [ ] Timeout 設定合理（複雜任務 300+）
- [ ] Delivery mode 適當（需要回報嗎？）
- [ ] 時間選擇合理（避開高峰）
- [ ] sessionTarget 正確（main vs isolated）
- [ ] wakeMode 適當（now vs next-heartbeat）

---

## 常見問題

### Q1: 任務執行失敗，如何排查？

```bash
# 查看任務狀態
cron list

# 查看特定任務的執行歷史
cron runs --jobId <job-id>
```

### Q2: 如何測試任務不等到排程時間？

```bash
# 立刻執行一次
cron run --jobId <job-id> --runMode force
```

### Q3: systemEvent vs agentTurn 如何選擇？

- **systemEvent**: 簡單腳本、不需 AI 判斷
- **agentTurn**: 需要 AI 判斷、複雜邏輯、條件處理

### Q4: 如何避免任務 timeout？

1. 增加 `timeoutSeconds`
2. 簡化腳本邏輯
3. 改用背景執行（systemEvent + bash ... &）

---

## 參考資料

- OpenClaw Cron 官方文檔：[docs/CRON.md](https://docs.openclaw.ai)
- 目前所有任務：執行 `cron list`
- 任務歷史：執行 `cron runs --jobId <id>`

---

**最後更新**：2026-02-24
**維護者**：YuQi 🦞
