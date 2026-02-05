# MEMORY.md - 長期記憶

## 專案

### EduMind AI 教材問答 SaaS
- 多租戶 SaaS（學生 / 老師 / 管理員）
- 技術棧：React + Vite（之後可能搬 Next.js）
- 路徑：`/Users/user/clawd/aijobcase-1`
- 已完成：
  - 學生端：讀書教練 `StudyCoachView.tsx`
  - 老師端：課程列表 `CourseList.tsx`
- 後端 API 規格：`docs/study-plans-api.md`

### AIJob 學院
- AI 培訓 AI 系統
- 老師 AI 培訓各種專業的學生 AI（HR AI、財務 AI、行銷 AI...）
- 用 `sessions_spawn` 產生子 Agent 學習

### AI 多人協作
- 同一 Telegram 群組部署多個專長 AI
- 設計訊息路由規則，避免搶答與無限循環
- 技術基礎：`sessions_send`、`sessions_spawn`、`sessions_list`

## 技術筆記

### Clawdbot 設定
- 設定檔：`~/.clawdbot/clawdbot.json`
- Gateway 重啟：`clawdbot gateway stop` → `clawdbot gateway start`
- 模型切換後要開新 Session 才會套用

### 技能狀態
- `filesystem`、`adaptive-suite` — 只是指南，沒有獨立執行檔
- `agent-browser` — 需要 `npx playwright install`

## 重要約定

1. 里程碑 + 階段交付，不說「背景一次做完很多件」
2. Jacky 回覆「OK」= 可以繼續下一個階段
3. 每次交付要：改檔案 → build 確認 → 說明改了什麼

---

*Last updated: 2026-02-02*
