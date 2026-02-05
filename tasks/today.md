# 2026-02-02 (Tomorrow) - Priority Tasks & Future Roadmap

## 🎯 優先收尾事項 (Tomorrow - Must Complete)

### A. 技能啟用與基礎測試 (Enable & Test Skills) ✅ 完成
*   **目標**：確保所有已下載的技能可被 Agent 調用，為新模組開發做準備。
*   **結論**：`filesystem` 和 `adaptive-suite` 是「指南型技能」，無獨立執行檔，Agent 用內建工具完成。
*   **待辦**：
    1.  [x] **GUI** 啟用 `clawhub`, `filesystem`, `adaptive-suite` 技能。
    2.  [x] 開啟新 Session / 重啟 Agent。
    3.  [x] 實際測試 → 結論：指南型技能，無 CLI。
    4.  [x] 更新技能說明到「可複製模板/skills/README.md」。

### B. LINE 平台接入規劃 (LINE Integration Planning) 🔄 進行中
*   **目標**：完成 LINE 接入的技術可行性分析與最小化設計。
*   **文件**：`docs/LINE-integration-plan.md` ✅ 已建立
*   **待辦**：
    1.  [x] 釐清 LINE 接入的最終使用情境（個人/群組協作，需不需要訊息互傳）。
    2.  [x] 確定是使用「外部 Webhook 服務」還是「現有 Gateway 插件擴展」。
    3.  [x] 在 `docs/` 建立 `LINE-integration-plan.md` 記錄技術選型。

---

## 🗺️ 未來開發產品的待辦事項 (Future Roadmap)

### 1. 【最高優先】AI 助理(員工)多人協作
*   **目標**：在同一個 Telegram 群組裡，部署多個專長不同的 AI 助理，讓它們可以分工合作、互相溝通。
*   **核心功能**：
    - 多個 AI 在同一群組裡各司其職（HR AI、財務 AI、行銷 AI...）
    - AI 之間可以互相補充、討論、協作
    - 設計訊息路由規則（誰該回答、誰該安靜）
    - 避免搶答與無限循環
*   **技術基礎**：`sessions_send`、`sessions_spawn`、`sessions_list`

### 2. 【最高優先】AIJob 學院 —— AI 培訓 AI
*   **目標**：建立一個 AI 培訓系統，由「老師 AI」培訓各種專業的「學生 AI」。
*   **核心功能**：
    - 設計課程：為每種 AI 助理寫「培訓手冊」（SKILL.md + 規則模板）
    - 產生學生：用 `sessions_spawn` 產生子 Agent 來學習
    - 測試考核：設計任務測試學生 AI 是否合格
    - 持續優化：根據實際表現調整培訓內容
*   **培訓對象**：HR AI、財務 AI、行銷 AI、Crypto AI、客服 AI 等
*   **關聯項目**：AI 多人協作、Moltbook 社群

### 3. 模組化收尾 (Module Finalization)
*   **目標**：將剩餘的 **財務、CRM、Slack/Notion 模組** 整合進老闆助理框架。

### 3. 新 AI 助理模組研發 (New AI Assistant Modules)
*   **3.1 區塊鏈與加密貨幣 (Blockchain & Crypto)**
    *   **MVP 範圍**：決定核心功能（Price Check, On-chain Data, News Aggregation）。
    *   **技術探勘**：研究適合的 Crypto API（需要 **Web Search** 還是特定 **Skill**）。
    *   **文件化**：建立 `docs/crypto-assistant-spec.md`。

*   **2.2 私域 AI 助理 (Private Group Assistant)**
    *   **目標**：設計一個可以安全地在 **Discord, LINE, Telegram** 群組中協作的 AI 模式。
    *   **考量點**：群組訊息識別、權限管理、如何避免在不相關的閒聊中回應。

*   **2.3 社群媒體影片分析 AI 助手 (Social Media Video Analysis)**
    *   **目標**：利用 YouTube/TikTok/IG 連結，生成摘要或分析趨勢。
    *   **技能準備**：研究你提供的影片下載/摘要技能（`youtube-video-downloader` 等）。

*   **3.4 HR 招募 AI 助理模組**
    *   **目標**：設計一個可以協助篩選履歷、生成面試問題的助手。
    *   **文件化**：設計資料輸入格式（履歷 PDF/Doc 處理）。

*   **3.5 短影音 Agent + Clawdbot**
    *   **目標**：整合短影音平台（TikTok、IG Reels、YouTube Shorts）的內容分析與自動化處理。
    *   **技能準備**：研究 `youtube-video-downloader`、`youtube-summarize` 等技能。

*   **3.6 Clawdbot 設定可視化使用者介面（開發者用）**
    *   **目標**：為 Clawdbot 開發一個圖形化的設定介面，讓開發者可以更直覺地管理技能、Agent、通道等設定。
    *   **技術選型**：Web UI（React/Vue）或桌面應用（Electron）。

*   **3.7 自動化更新 OAuth 授權（Google / AI 模型）**
    *   **目標**：設計一套機制，在 OAuth token 即將過期時，自動提醒並引導用戶完成重新授權，減少手動操作。
    *   **參考**：已在資安防護說明中定義的「模型授權更新策略」。
    *   **技術方向**：cron / heartbeat 定期檢查 + 主動通知 + 一鍵重登流程。

*   **3.8 生活服務 AI 助理（手機打電話）**
    *   **目標**：讓 AI 可以用手機直接打電話（點餐、預約、叫車），不需要 Twilio 等第三方費用。
    *   **技術方向**：開發手機端 App，接收 AI 指令 → 撥打電話 → 播放 AI 語音 → 回傳對話內容。
    *   **備註**：此功能由其他 bot 開發。

---
**Reminder for self**：針對 **Gateway Restart Error**，我已將「未來遇到 Gateway 錯誤時應主動回報」的規則寫入通用模板。
