# Cron Jobs 錯誤修正報告

**執行日期**：2026-02-13 10:50  
**執行者**：YuQi AI Assistant  
**問題**：`empty-heartbeat-file` 錯誤導致自動化腳本未實際執行

---

## ❌ 原始問題

**症狀**：
- 9 個 Cron Jobs 顯示 `lastError: "empty-heartbeat-file"`
- `lastStatus: "skipped"` - 任務被跳過，**腳本未實際執行**

**原因**：
- 這些任務使用 `sessionTarget: "main"` + `payload.kind: "systemEvent"`
- 系統檢查 HEARTBEAT.md，發現是空的，按設計跳過執行
- 但這些任務需要直接執行 bash 腳本，不應該受 HEARTBEAT.md 影響

---

## ✅ 修正方案

**改為**：`sessionTarget: "isolated"` + `payload.kind: "agentTurn"`

**好處**：
1. 不受 HEARTBEAT.md 影響，確實執行腳本
2. 每次啟動獨立 session，不汙染 main session 歷史
3. 可以設定 `delivery: {mode: "none"}` 避免不必要的通知
4. 執行結果會記錄在 isolated session，可追蹤

---

## 📝 已修正的 Cron Jobs（9 個）

### 1. 自動履歷歸檔（每小時）
- **Job ID**: `b6769222-9a27-43b6-832b-8a57d9818119`
- **變更**：
  - ❌ `sessionTarget: "main"` + `systemEvent`
  - ✅ `sessionTarget: "isolated"` + `agentTurn`
- **新流程**：
  1. 執行 auto-resume-filing.sh
  2. 檢查是否有新履歷處理
  3. 若有新履歷，報告處理結果（匯入幾筆）
  4. 若無新履歷，回報 HEARTBEAT_OK

### 2-3. BD 自動發信（09:30, 14:30）
- **Job IDs**: 
  - `508fdc90-9136-4c2d-a41f-e4ff86409e9d`（上午）
  - `b9ee81a8-a4f7-45a0-ae98-4bf7520714af`（下午）
- **變更**：同上
- **新流程**：
  1. 執行 auto-bd-send.sh
  2. 檢查 BD客戶開發表，篩選「待寄信」狀態
  3. 自動發送 BD 開發信
  4. 報告結果：發了幾封信（如果有）
  5. 若無需發信，回報 HEARTBEAT_OK

### 4-9. BD 自動開發（01:00-06:00，每 2 天）
- **Job IDs**:
  - `ebd0aec9-bacd-4897-8dfd-ee7b659966f3`（01:00）
  - `114725fc-4b12-40de-b521-edfba0af931a`（02:00）
  - `ace147a7-2b78-403c-8b9a-d52cd3449325`（03:00）
  - `4b2ff623-6c92-4d58-8b0a-5bde03045e0e`（04:00）
  - `bd7f27d5-fd3c-4a4e-8a99-73e9d0598b71`（05:00）
  - `04711538-aa6b-48f8-97f2-9773fe239144`（06:00）
- **變更**：同上
- **新流程**：
  1. 執行 auto-bd-crawler.sh
  2. 104 搜尋职缺 → 爬公司資訊 → 去重 → 匯入 BD客戶開發表
  3. 報告結果：找到幾家新公司（如果有）
  4. 若無新公司，回報 HEARTBEAT_OK
- **Timeout**：從 300 秒提升至 600 秒（爬蟲可能較慢）

---

## 📊 修正前後對比

| 項目 | 修正前 | 修正後 |
|------|--------|--------|
| Session Target | `main` | `isolated` |
| Payload Kind | `systemEvent` | `agentTurn` |
| 受 HEARTBEAT.md 影響 | ✅ 是（會跳過） | ❌ 否 |
| 實際執行腳本 | ❌ 否（被跳過） | ✅ 是 |
| 執行結果記錄 | 無 | isolated session |
| Delivery Mode | 無 | `none`（避免不必要通知） |

---

## ✅ 驗證

### 下次執行時間（已排程）
- **履歷歸檔**：每小時（下次：1 小時後）
- **BD 發信上午**：明天 09:30
- **BD 發信下午**：今天 14:30
- **BD 開發**：2/15（五）凌晨 01:00-06:00

### 預期行為
1. **有工作時**：執行腳本 → 報告結果
2. **無工作時**：回報 `HEARTBEAT_OK`（不產生通知）

### 如何確認修正成功
- 今天 14:30 後檢查：BD 發信是否實際執行
- 明天檢查 履歷歸檔 log：是否有執行記錄
- 2/15 凌晨後檢查：BD 開發是否找到新公司

---

## 📌 後續維護建議

### 新增 Cron Job 注意事項
1. **直接執行腳本的任務**：使用 `isolated` + `agentTurn`
2. **提醒/通知類任務**：使用 `main` + `systemEvent`
3. **長時間任務**：調整 `timeoutSeconds`（預設 300 秒）

### 設定 delivery mode
- `delivery: {mode: "none"}` - 不通知（背景任務）
- `delivery: {mode: "announce"}` - 有結果才通知
- 預設不設定 = 不通知

---

## 🎯 修正總結

**修正數量**：9 個 Cron Jobs  
**影響範圍**：
- ✅ 自動履歷歸檔（每小時）
- ✅ BD 自動發信（每天 2 次）
- ✅ BD 自動開發（每 2 天凌晨 6 次）

**效果**：
- ✅ 所有自動化腳本現在會實際執行
- ✅ 不再受 HEARTBEAT.md 影響
- ✅ 執行結果可追蹤

**狀態**：✅ 完成  
**下次執行**：今天 14:30（BD 自動發信-下午）
