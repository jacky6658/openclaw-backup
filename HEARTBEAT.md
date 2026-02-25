# HEARTBEAT.md - 系統監控任務

## 每次 Heartbeat 檢查

### 1. 系統用量監控
執行 session_status，檢查門檻：
- ⚠️ Context > 150k（75%）
- ⚠️ 單次 Token > 50k
- ⚠️ Cache hit < 50%
- 🔴 Context > 190k（95%）→ 立刻通知
- 🔴 遇到 API 限流 → 立刻通知

異常時發 Telegram 警告，正常情況安靜。

### 2. 其他定期檢查（暫不啟用）
- 郵件監控
- 日曆提醒
- 其他待補充
