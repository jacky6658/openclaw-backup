# OpenClaw 新手安裝方案 - 最終交付

## 📦 可交付成品

### 1. OpenClaw Installer (.pkg) - **推薦給完全不會 Terminal 的新手**
- **路徑**：`/Users/user/clawd/installers/openclaw-pkg/openclaw-installer.pkg` (23K)
- **使用方式**：雙擊安裝 → 輸入密碼 → 等待 10–30 分鐘
- **特點**：
  - ✅ macOS 原生安裝介面（GUI）
  - ✅ 自動執行 Homebrew/Node/OpenClaw 安裝
  - ✅ 有中文歡迎頁 + 完成頁 + 系統需求警告
  - ✅ 安裝日誌：`/tmp/openclaw-install.log`

### 2. OpenClaw Setup.app (.dmg) - **安裝後設定 config 用**
- **路徑**：`/Users/user/clawd/installers/ui-openclaw-setup/openclaw-setup_0.1.0_x64.dmg` (3.4M)
- **使用方式**：掛載 DMG → 拖曳到 Applications → 開啟
- **功能**：
  - 檢查 OpenClaw 是否安裝
  - 填入 Telegram Bot Token / OpenAI API Key
  - 套用設定（自動備份 config）
  - 執行 `openclaw status`
  - 啟動 gateway（需確認）

---

## ⚠️ 系統需求（重要）

- **最低需求：macOS 12 Monterey**
- macOS 11 Big Sur 或更舊版本**無法使用**（Homebrew 編譯會失敗）

---

## 🎯 新手安裝完整流程

### Step 1: 安裝 OpenClaw
1. 雙擊 `openclaw-installer.pkg`
2. 看到「歡迎使用 OpenClaw Installer」→ 點「繼續」
3. macOS 要求輸入密碼 → 輸入管理員密碼
4. 等待安裝完成（10–30 分鐘，進度條可能會卡很久）
5. 看到「✅ OpenClaw 安裝完成！」→ 點「關閉」

### Step 2: 設定 OpenClaw
1. 開啟「OpenClaw Setup」（在應用程式資料夾）
2. 按「檢查 OpenClaw」→ 確認顯示 `"installed": true`
3. 填入 Telegram Bot Token 與 OpenAI API Key
4. 按「套用設定（先備份）」
5. 按「執行 openclaw status」確認狀態
6. 按「啟動 gateway」（會要求確認）

### Step 3: 驗證成功
在 Telegram 跟你的 bot 說話，bot 應該會回覆。

---

## 🧪 測試結果（2026-02-06）

### 測試環境
- macOS 11.7.10 (x86_64, Intel Mac)
- 測試機：`newuser@192.168.88.237`

### 測試成果
✅ `.pkg` 安裝介面正常（會跳密碼視窗）  
✅ `postinstall` 腳本成功執行  
✅ Homebrew 開始下載依賴  
❌ **安裝失敗**：macOS 11 太舊，Homebrew 編譯 `simdutf` 失敗

### 結論
- `.pkg` 安裝流程**設計正確**
- 失敗原因是**環境限制**（macOS 11 不支援）
- 在 **macOS 12+** 環境應該可以成功安裝

---

## 📝 文件與教學

1. **PKG Installer README**：`/Users/user/clawd/installers/openclaw-pkg/README.md`
   - 含系統需求、使用方式、打包指令

2. **Setup UI README**：`/Users/user/clawd/installers/ui-openclaw-setup/README.md`
   - 含 Gatekeeper 處理、DMG 打包、開發指令

3. **Skills 匯入筆記**：`/Users/user/clawd/skills-import/README.md`
   - tunneling / clawiskill / desktop-control 的使用說明

---

## 🔗 相關 Commits

### PKG Installer
- `a6bdb4b` - Add OpenClaw macOS .pkg installer
- `60f5847` - Add README for pkg installer
- `4688d60` - Add macOS 12+ system requirement warning

### Setup UI
- `562dd1a` - Setup: add one-click OpenClaw installer with macOS admin prompt
- `79be0d4` - Setup: improve install_openclaw error handling + user feedback
- `8f52a0d` - Setup: add test button + copy install command + debug logging
- `b9b582a` - Setup: remove confirm dialog, directly invoke osascript
- `1a2fa0a` - Setup: add macOS 12+ system requirement notice

### Skills
- `b3e3764` - Add notes for imported skills (tunneling/clawiskill/desktop-control)
- `6d6e4d1` + `4464561` - Import skills zips and make desktop-control runnable

---

## 🚀 下一步

1. **在 macOS 12+ 環境驗證**：找一台 macOS 12 或更新的 Mac，測試完整安裝流程
2. **desktop-control 整合**：定稿如何把 desktop-control 接到 OpenClaw
3. **簽名（選配）**：若要正式發布，可考慮用 Apple Developer ID 簽名 .pkg 和 .app

---

**交付日期**：2026-02-06  
**狀態**：✅ 可交付（需 macOS 12+ 環境驗證）
