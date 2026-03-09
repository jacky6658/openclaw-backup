# Gmail 智慧通知系統

**帳號**: aijessie88@step1ne.com  
**建立日期**: 2026-03-04  
**Cron ID**: 2bc4b03d-0e2f-4c8e-933a-422f8c76fdb7

---

## 🎯 功能說明

自動監控 Gmail 信箱，只通知**重要郵件**：
- ✅ **候選人回信**（回覆我們的開發信）
- ✅ **客戶聯繫**（職缺、招聘相關）
- ❌ 過濾廣告信、系統通知

---

## 📋 篩選規則

### ✅ 候選人回信判斷
1. **主旨包含**: `Re:` / `回覆:` / `回复:` / `回信:`
2. **內容包含關鍵字**: 履歷、resume、面試、interview、興趣、interested、詳細、應徵

### ✅ 客戶聯繫判斷
1. **主旨包含**: 職缺、招聘、招募、人才、合作、配合、需求、job、recruit、hiring、position、vacancy
2. **公司 Email**（非免費信箱）+ 內容包含職缺相關關鍵字

### ❌ 排除條件
1. **系統通知**: no-reply、noreply、notification、donotreply、automated、mailer-daemon
2. **廣告信**: unsubscribe、marketing、newsletter、promotion、advertisement
3. **自己寄的信**: aijessie88@step1ne.com

---

## 🔔 通知方式

**Telegram 群組**: HR AI招募自動化 (`-1003231629634`)  
**Topic**: 履歷進件 (#4)

**通知格式**:
```
📧 aijessie88 重要郵件

類型：候選人回信
寄件人：john@example.com
主旨：Re: Java Developer 職缺
時間：2026-03-04 16:30

內容預覽：
感謝您的聯繫，我對此職位非常感興趣...

請至信箱查看完整內容
```

---

## ⏰ 執行排程

**Cron 表達式**: `*/30 * * * *`（每 30 分鐘）  
**執行模式**: Isolated session  
**模型**: anthropic/claude-haiku-4-5

---

## 🛠️ 檔案位置

**主腳本**: `/Users/user/clawd/hr-tools/gmail-smart-notify.sh`  
**快取檔案**: `/Users/user/clawd/hr-tools/data/gmail-notified.json`（記錄已通知的郵件 ID，避免重複）

---

## 🧪 手動測試

```bash
# 測試腳本
bash /Users/user/clawd/hr-tools/gmail-smart-notify.sh

# 查看 Cron 狀態
openclaw cron list | grep gmail

# 手動執行一次
openclaw cron run 2bc4b03d-0e2f-4c8e-933a-422f8c76fdb7

# 查看執行記錄
openclaw cron runs 2bc4b03d-0e2f-4c8e-933a-422f8c76fdb7
```

---

## 🔧 管理指令

```bash
# 停用
openclaw cron disable 2bc4b03d-0e2f-4c8e-933a-422f8c76fdb7

# 啟用
openclaw cron enable 2bc4b03d-0e2f-4c8e-933a-422f8c76fdb7

# 刪除
openclaw cron rm 2bc4b03d-0e2f-4c8e-933a-422f8c76fdb7

# 修改時間（例如改為每 15 分鐘）
openclaw cron edit 2bc4b03d-0e2f-4c8e-933a-422f8c76fdb7 --cron "*/15 * * * *"
```

---

## 📝 維護日誌

### 2026-03-04
- ✅ 初始建立
- ✅ 設定篩選規則
- ✅ 設定 Cron job（每 30 分鐘）
- ✅ 測試通過

---

## 💡 優化建議

### 短期（已實作）
- [x] 基本篩選邏輯
- [x] Telegram 通知
- [x] 去重機制

### 中期（可選）
- [ ] 自動回覆候選人（感謝信）
- [ ] 統計每日重要郵件數量
- [ ] 郵件分類（候選人 vs 客戶）

### 長期（可選）
- [ ] Gmail Push Notification（即時通知）
- [ ] AI 自動分析郵件重要性評分
- [ ] 整合到 Step1ne 系統（自動建立候選人）

---

## 🐛 常見問題

### Q1: 為什麼沒有通知？
1. 檢查是否有未讀郵件：`gog gmail search "is:unread" --account aijessie88@step1ne.com`
2. 檢查郵件是否符合篩選條件（查看腳本執行 log）
3. 檢查是否已通知過（查看 `gmail-notified.json`）

### Q2: 如何調整篩選規則？
編輯 `/Users/user/clawd/hr-tools/gmail-smart-notify.sh`，修改第 61-107 行的篩選邏輯。

### Q3: 如何改變通知頻率？
```bash
openclaw cron edit 2bc4b03d-0e2f-4c8e-933a-422f8c76fdb7 --cron "*/15 * * * *"  # 改為 15 分鐘
openclaw cron edit 2bc4b03d-0e2f-4c8e-933a-422f8c76fdb7 --cron "0 * * * *"     # 改為每小時
```

### Q4: 如何清除快取（重新通知所有郵件）？
```bash
echo "[]" > /Users/user/clawd/hr-tools/data/gmail-notified.json
```

---

**最後更新**: 2026-03-04 17:20
