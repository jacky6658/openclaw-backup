# Clawdbot 技能類型教學

## 技能有兩種類型

### 1️⃣ 指南型技能（Guide Skills）
- **特點**：只有 SKILL.md 文件，沒有可執行檔
- **作用**：告訴 Agent「你可以怎麼做」、「你應該扮演什麼角色」
- **執行方式**：Agent 用內建工具（exec、read、write）完成任務

### 2️⃣ 工具型技能（Tool Skills）
- **特點**：有獨立的 CLI 執行檔或腳本
- **作用**：提供 Agent 額外的專用工具
- **執行方式**：Agent 直接呼叫該工具的指令

---

## 範例：指南型技能

### 📁 filesystem
**教 Agent 怎麼做檔案系統操作：**

| 功能 | 說明 |
|-----|------|
| **Smart Listing** | 過濾、遞迴、排序檔案清單 |
| **Search** | glob/regex 搜尋檔名或內容 |
| **Batch Copy** | 批次複製 + dry-run 預覽 |
| **Tree** | 目錄樹狀圖 |
| **Analyze** | 統計檔案數量、大小分佈、找最大檔案 |

→ 實際執行時 Agent 用 `find`、`ls`、`tree` 等 shell 指令完成

---

### 🧠 adaptive-suite
**告訴 Agent 要當一個多功能助手：**

| 角色 | 說明 |
|-----|------|
| **Free Resource Discovery** | 優先找免費/開源方案 |
| **Adaptive Coder** | 適應使用者的 coding style |
| **Business Analyst & PM** | 商業分析、專案管理（Agile、Lean） |
| **Web & Data Developer** | 網頁開發 + 資料庫設計 |
| **NAS Metadata Scraper** | 掃描 NAS 目錄結構（唯讀） |

→ 這是行為準則，不是工具

---

## 範例：工具型技能

### 🌐 agent-browser
- 提供 `agent-browser` CLI 工具
- 可以控制無頭瀏覽器開網頁、截圖、操作頁面
- 需要先裝 Playwright：`npx playwright install`

### 📦 clawdhub
- 提供 `clawdhub` CLI 工具
- 可以搜尋、安裝、發布技能
- 已隨 Clawdbot 安裝

### 📧 gog
- 提供 Google Workspace CLI
- 可以操作 Gmail、Calendar、Drive、Sheets
- 需要 OAuth 授權

---

## 如何判斷技能類型？

1. **看 SKILL.md** — 有沒有提到具體的 CLI 指令
2. **看技能資料夾** — 有沒有可執行檔（bin、script）
3. **直接測試** — 跑一下指令看有沒有

```bash
# 檢查技能資料夾內容
ls -la ~/.nvm/versions/node/v24.13.0/lib/node_modules/clawdbot/skills/<skill-name>/
```

---

## 重點總結

| 類型 | 有執行檔？ | Agent 怎麼用？ |
|-----|----------|--------------|
| 指南型 | ❌ 沒有 | 讀 SKILL.md 學方法，用內建工具執行 |
| 工具型 | ✅ 有 | 直接呼叫該工具的 CLI 指令 |

---

*AIJob 學院教材 · 2026-02-02*
