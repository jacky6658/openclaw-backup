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

### 2. AI工作進度 複篩（每天主要任務）
呼叫 Step1ne API 檢查是否有 `status='爬蟲初篩'` 的候選人：
```
GET https://backendstep1ne.zeabur.app/api/openclaw/pending?limit=100
Header: X-OpenClaw-Key: openclaw-dev-key
```
- 有候選人 → 立即執行 AI 複篩（3閘門 + 5維度評分），回寫結果，通知 Jacky
- 沒有候選人 → 安靜，不通知

回寫 API：
```
POST https://backendstep1ne.zeabur.app/api/openclaw/batch-update
Header: X-OpenClaw-Key: openclaw-dev-key
```
評分完成後 A/B → status: `AI推薦`，C/D → status: `備選人才`

### 3. 其他定期檢查（暫不啟用）
- 郵件監控
- 日曆提醒
