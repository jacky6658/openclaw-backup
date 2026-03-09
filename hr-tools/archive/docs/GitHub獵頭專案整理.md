# GitHub 獵頭專案整理

## 📊 目前狀況

### 現有 GitHub Repos（5 個）

#### 1. **openclaw-backup** (主要工作區)
- **URL**: https://github.com/jacky6658/openclaw-backup
- **位置**: `/Users/user/clawd/`
- **內容**: 
  - `hr-tools/` - 所有 Shell 腳本工具
  - `skills/headhunter/` - 獵頭技能庫
  - `hr-recruitment/` - 履歷資料
  - `memory/` - 工作日誌
  - 所有配置檔案 (TOOLS.md, MEMORY.md 等)
- **用途**: 每日自動備份（21:00）
- **狀態**: ✅ 活躍

#### 2. **headhunter-system**
- **URL**: https://github.com/jacky6658/headhunter-system
- **位置**: `/Users/user/clawd/projects/headhunter/`
- **內容**: 
  - 獵頭系統文件
  - 爬蟲指南
  - 前置作業說明
- **最近提交**: 2026-02-10 (公司聯絡資訊爬取指南)
- **狀態**: ✅ 活躍

#### 3. **step1ne-hr-dashboard**
- **URL**: https://github.com/jacky6658/step1ne-hr-dashboard
- **位置**: `/Users/user/clawd/projects/hr-dashboard/`
- **內容**: 
  - Next.js Web 應用
  - HR 總覽看板
  - Google Sheets API 整合
- **最近提交**: 2026-02-10 (Google API 設定指南)
- **狀態**: ✅ 活躍

#### 4. **step1nehrai** (舊專案)
- **URL**: https://github.com/jacky6658/step1nehrai
- **位置**: `/Users/user/clawd/projects/step1nehrai/`
- **內容**: 
  - 舊的獵頭 AI 專案
  - BD 自動化腳本
  - Gemini Service
- **最近提交**: 2026-02-10 (升級 BD 自動化爬蟲)
- **狀態**: ⚠️ 活躍但可能重複

#### 5. **step1ne-api**
- **URL**: https://github.com/jacky6658/step1ne-api
- **位置**: `/Users/user/clawd/projects/step1ne-api/`
- **內容**: 
  - Node.js API 服務
  - 8 個端點 (auth, jobs, candidates, etc.)
  - 自動化流程圖
- **最近提交**: 2026-02-10 (自動化流程圖)
- **狀態**: ✅ 活躍

---

## 📁 檔案分佈狀況

### 工具腳本
- ✅ **openclaw-backup**: `/hr-tools/*.sh`
- ⚠️ **step1nehrai**: 也有一些舊的腳本

### 技能庫 (Prompts)
- ✅ **openclaw-backup**: `/skills/headhunter/`
- ⚠️ **step1nehrai**: 也有 skills/ 資料夾

### Web 應用
- ✅ **step1ne-hr-dashboard**: Next.js 看板

### API 服務
- ✅ **step1ne-api**: Node.js API

### 文件說明
- ✅ **headhunter-system**: 爬蟲指南、前置作業
- ✅ **openclaw-backup**: README、INSTALL.md
- ✅ **step1nehrai**: 執行手冊、簡報

### GitHub Pages (HTML 簡報)
- **aijob-presentations** (未在本地，單獨管理)
  - https://jacky6658.github.io/aijob-presentations/headhunter-full-guide.html
  - https://jacky6658.github.io/aijob-presentations/step1ne-operations-manual.html

---

## 🤔 問題點

### 1. 重複內容
- `step1nehrai` 和 `openclaw-backup` 有重複的腳本
- 技能庫在兩個地方都有

### 2. 結構不清晰
- 不確定哪個是「主 repo」
- 新人不知道要 clone 哪個

### 3. 更新同步困難
- 修改工具腳本時，要在多個 repo 更新？
- 或只更新一個？

---

## 💡 建議方案

### 方案 A：統一到單一 Repo（推薦）

**新 Repo: `step1ne-headhunter` (統一主專案)**

```
step1ne-headhunter/
├── tools/                  # 工具腳本 (從 hr-tools/ 搬過來)
│   ├── bd-automation.sh
│   ├── bd-outreach.sh
│   ├── jd-manager.sh
│   ├── start-dashboard.sh
│   └── ...
├── skills/                 # 技能庫 (Prompts)
│   └── headhunter/
│       ├── SKILL.md
│       └── references/
├── dashboard/              # Web 看板 (從 hr-dashboard 搬過來)
│   ├── app/
│   ├── public/
│   └── package.json
├── api/                    # API 服務 (從 step1ne-api 搬過來)
│   ├── api-server.js
│   └── ...
├── docs/                   # 文件
│   ├── INSTALL.md
│   ├── README-JD管理.md
│   ├── CRON-BD定時任務規劃.md
│   └── 教學-如何教Bot執行定時BD爬蟲.md
└── README.md               # 主說明文件
```

**優點**：
- ✅ 所有內容集中一處
- ✅ 結構清晰
- ✅ 易於維護和分享
- ✅ 新人只需 clone 一個 repo

**缺點**：
- ❌ 需要搬移檔案
- ❌ 需要更新所有文件中的路徑

---

### 方案 B：保持現狀，明確分工

保留 5 個 repos，但明確定義職責：

#### 主 Repo: **openclaw-backup**
- 包含所有工具腳本 (`hr-tools/`)
- 技能庫 (`skills/headhunter/`)
- 配置檔案
- **這是唯一的真實來源 (Single Source of Truth)**

#### 子專案 Repos:
1. **step1ne-hr-dashboard**: 只放 Web 看板 (Next.js 應用)
2. **step1ne-api**: 只放 API 服務 (Node.js)
3. **headhunter-system**: 只放文件（指南、教學）
4. **step1nehrai**: 封存或刪除（重複內容）

**優點**：
- ✅ 不需搬移檔案
- ✅ 各專案獨立部署

**缺點**：
- ❌ 結構較複雜
- ❌ 新人需要了解多個 repos

---

### 方案 C：Monorepo with Git Submodules

在 `step1ne-headhunter` 使用 Git Submodules：

```
step1ne-headhunter/
├── tools/                  # Git submodule → openclaw-backup/hr-tools
├── dashboard/              # Git submodule → step1ne-hr-dashboard
├── api/                    # Git submodule → step1ne-api
└── README.md
```

**優點**：
- ✅ 統一入口
- ✅ 各子專案保持獨立

**缺點**：
- ❌ Git submodules 較複雜
- ❌ 同步困難

---

## 📝 我的推薦

### 建議採用：**方案 A（統一 Repo）**

**理由**：
1. 獵頭專案本質上是「一個完整系統」
2. 工具、API、看板、文件是緊密相關的
3. 未來可能有更多 AI Bot 需要學習這個系統
4. 統一 Repo 最容易理解和維護

**執行步驟**：
1. 建立新 Repo: `step1ne-headhunter`
2. 從 `openclaw-backup` 複製 `hr-tools/` → `tools/`
3. 從 `step1ne-hr-dashboard` 複製 → `dashboard/`
4. 從 `step1ne-api` 複製 → `api/`
5. 從 `openclaw-backup/skills/headhunter/` 複製 → `skills/`
6. 整理所有文件到 `docs/`
7. 撰寫統一的 `README.md`
8. 封存舊 repos (step1nehrai, headhunter-system)

---

## ❓ 需要確認的問題

請 Jacky 回答以下問題，我再根據你的決定執行整理：

### Q1: 你偏好哪個方案？
- [ ] 方案 A - 統一 Repo
- [ ] 方案 B - 保持現狀，明確分工
- [ ] 方案 C - Monorepo with Submodules
- [ ] 其他想法？

### Q2: 如果選方案 A，新 Repo 名稱？
- [ ] `step1ne-headhunter` (推薦)
- [ ] `step1ne-hr-system`
- [ ] `headhunter-ai-system`
- [ ] 其他名稱：________________

### Q3: 舊的 `step1nehrai` repo 要如何處理？
- [ ] 封存（Archive）
- [ ] 刪除
- [ ] 保留但標記為 Deprecated

### Q4: GitHub Pages (aijob-presentations) 要保留嗎？
- [ ] 保留（HTML 簡報很方便分享）
- [ ] 合併到主 Repo 的 docs/

### Q5: openclaw-backup 每日備份要繼續嗎？
- [ ] 繼續（備份整個工作區很重要）
- [ ] 停止（主專案已在 GitHub）

---

## 🚀 如果你決定了

請告訴我你的選擇，我會：
1. 立即建立新 Repo 結構
2. 搬移檔案
3. 更新所有路徑
4. 撰寫統一的 README
5. 封存舊 repos

**預估時間**：30-60 分鐘

---

**整理日期**: 2026-02-10 22:25 GMT+8
**整理人**: YuQi (YQ1)
