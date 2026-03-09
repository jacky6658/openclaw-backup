# BD 客戶開發定時任務規劃（擬定）

## 📋 任務概述

**任務名稱**: 定時 BD 客戶開發爬蟲

**執行頻率**: 每 1 小時

**任務類型**: isolated session (獨立執行，完成後通知)

**通知目標**: Telegram 群組 -1003231629634 Topic 364「開發」

---

## 🔄 執行流程

### 自動化步驟

1. **關鍵字輪替**
   - 從預設職位關鍵字清單中輪流選擇
   - 清單：`["AI工程師", "後端工程師", "全端工程師", "數據分析師", "產品經理"]`
   - 每次執行使用不同關鍵字，避免重複

2. **搜尋 104 招聘公司**
   - 執行：`scraper-104.py <關鍵字> 10`
   - 輸出：公司列表 JSON (包含公司名、職缺、網址)

3. **提取公司網站**
   - 執行：`fetch-104-website-final.py <公司列表>`
   - 輸出：補充官網網址欄位

4. **爬取聯絡方式**
   - 執行：`scrape-contact-from-website.sh <公司列表>`
   - 輸出：補充 Email、電話欄位

5. **過濾有效聯絡方式**
   - 篩選條件：Email 不為「待查」且格式有效
   - 輸出：可寄信公司列表

6. **整理到 Google Sheets**
   - 使用 `gog sheets append` 寫入 BD客戶開發表
   - Sheet ID: `1bkI7_cCh_Bs4qVa3HlXiy0CFzmItZlA-DYGHSPS4InE`
   - 帳號: `aiagentg888@gmail.com`

7. **批量寄送 BD 信**
   - 使用 `bd-outreach.sh send <公司> <Email> <聯絡人>`
   - 發信帳號: `aijessie88@step1ne.com`
   - 自動附上：Step1ne公司簡介.pdf
   - 每封信間隔 30 秒（避免被標記垃圾信）

8. **回報結果到 Telegram**
   - 發送到 Topic 364「開發」
   - 格式：
     ```
     ✅ BD 客戶開發完成 (關鍵字: <XXX>)
     
     📊 搜尋結果：
     • 找到 10 家公司
     • 已寄信：5 家
     • 待補充 Email：5 家
     
     📋 詳細資料：
     • 公司A - 職缺A
     • 公司B - 職缺B
     ...
     
     📂 已整理到：BD客戶開發表
     ```

---

## ⚙️ Cron Job 配置

```json
{
  "name": "BD 客戶開發定時爬蟲 (YQ2 HRYuqi)",
  "schedule": {
    "kind": "every",
    "everyMs": 3600000
  },
  "sessionTarget": "isolated",
  "wakeMode": "now",
  "payload": {
    "kind": "agentTurn",
    "message": "執行 BD 客戶開發自動化：\n\n1. 從關鍵字清單中輪替選擇一個職位（AI工程師、後端工程師、全端工程師、數據分析師、產品經理）\n2. 執行 ~/clawd/hr-tools/bd-automation.sh auto \"<關鍵字>\" 10\n3. 檢查執行結果並生成報告\n4. 如果有成功寄信的公司，整理成清單\n5. 將報告發送到 Telegram Topic 364\n\n**重要規則**：\n- 只寄給有確認 Email 的公司（不用推測）\n- 每次執行限制 10 家公司（避免短時間大量寄信）\n- 間隔 30 秒寄送（避免被標記垃圾信）\n- 若無可寄信對象，回報 HEARTBEAT_OK\n\n**關鍵字輪替機制**：\n- 讀取上次使用的關鍵字（從資料檔或預設第一個）\n- 選擇下一個關鍵字\n- 執行完畢後記錄本次使用的關鍵字",
    "timeoutSeconds": 600
  },
  "delivery": {
    "mode": "announce",
    "channel": "telegram",
    "to": "-1003231629634/364"
  }
}
```

---

## 📊 預期效果

### 每小時產出
- 搜尋 10 家招聘公司
- 寄信 3-7 家（估計 30-70% 有有效 Email）
- 新增 10 筆公司資料到 Google Sheets

### 每日產出
- 搜尋 240 家公司（24 小時 × 10 家）
- 寄信 72-168 封（估計 30-70% 有效）
- 新增 240 筆公司資料

### 每週產出
- 搜尋 1,680 家公司
- 寄信 504-1,176 封
- 新增 1,680 筆公司資料

---

## 🛡️ 防呆機制

### 1. 重複公司檢查
- 在 Google Sheets 中檢查公司名稱是否已存在
- 若已存在，跳過該公司（不重複寄信）

### 2. Email 驗證
- 正則表達式檢查 Email 格式
- 不寄給「待查」或無效 Email

### 3. 錯誤處理
- 爬蟲失敗 → 跳過該公司，繼續下一家
- API 錯誤 → 記錄日誌，稍後重試
- 寄信失敗 → 標記「寄信失敗」，不影響其他公司

### 4. 頻率限制
- 每次執行限制 10 家公司
- 寄信間隔 30 秒
- 每小時執行 1 次（避免短時間大量請求）

---

## 📝 資料儲存

### 本地檔案
- 公司列表 JSON: `~/clawd/data/headhunter/bd_<timestamp>.json`
- 關鍵字輪替狀態: `~/clawd/data/headhunter/bd_keyword_state.txt`
- 執行日誌: `~/clawd/data/headhunter/bd_log.txt`

### Google Sheets
- BD客戶開發表: `1bkI7_cCh_Bs4qVa3HlXiy0CFzmItZlA-DYGHSPS4InE`
- 欄位：公司名稱、聯絡電話、Email、網址、目前職缺、來源、狀態、開發日期、負責顧問、備註

---

## 🚨 注意事項

### 合規性
- 確保符合台灣個人資料保護法
- 公開資訊來源（104 招聘頁面、公司官網）
- 提供退訂機制（BD 信件中包含聯絡方式）

### 信箱安全
- 使用專用信箱 `aijessie88@step1ne.com`
- 避免短時間大量寄信（間隔 30 秒）
- 監控退信率和垃圾信標記

### 資料品質
- 定期檢查 Google Sheets 是否有重複資料
- 定期清理「待查」聯絡方式（可能需手動補充）
- 追蹤回覆率和轉換率

---

## 📈 成效追蹤

### 建議指標
1. **搜尋效率**: 每小時找到多少家公司
2. **聯絡方式完整度**: 有效 Email 比例
3. **寄信成功率**: 成功發送 / 嘗試發送
4. **回覆率**: 收到回覆 / 已寄信
5. **轉換率**: 成功合作 / 已寄信

### 優化方向
- 調整關鍵字清單（依據回覆率）
- 調整寄信頻率（依據回覆率和垃圾信標記）
- 優化 BD 信件內容（A/B 測試）

---

## ✅ 啟用前確認清單

在實際建立 Cron Job 前，請確認：

- [ ] `bd-automation.sh` 已測試成功
- [ ] `scraper-104.py` 可正常搜尋公司
- [ ] `fetch-104-website-final.py` 可提取網站
- [ ] `scrape-contact-from-website.sh` 可爬取聯絡方式
- [ ] `bd-outreach.sh` 可成功寄信
- [ ] Google Sheets 授權正常 (`aiagentg888@gmail.com`)
- [ ] Gmail 授權正常 (`aijessie88@step1ne.com`)
- [ ] Step1ne公司簡介.pdf 存在
- [ ] Telegram Topic 364「開發」已建立
- [ ] 已測試完整流程至少 1 次

---

## 🎯 下一步

1. **Jacky 確認**：是否同意此規劃？
2. **調整參數**：是否需修改頻率、數量、關鍵字清單？
3. **建立任務**：確認後，執行 `cron add` 建立定時任務
4. **監控運行**：首週密切觀察效果，必要時調整

---

**規劃完成日期**: 2026-02-10
**規劃人**: YuQi (YQ2 HR YuQi)
