# OpenClaw Windows 安裝教學

**系統需求**：Windows 10/11  
**所需時間**：約 15-20 分鐘  
**難度**：⭐⭐☆☆☆（適合新手）

---

## 📋 目錄

1. [前置準備](#前置準備)
2. [安裝 Node.js](#安裝-nodejs)
3. [安裝 OpenClaw](#安裝-openclaw)
4. [初始設定](#初始設定)
5. [啟動 Gateway](#啟動-gateway)
6. [驗證安裝](#驗證安裝)
7. [常見問題](#常見問題)

---

## 前置準備

### 系統需求

- ✅ Windows 10 (版本 1809 或更新) 或 Windows 11
- ✅ 至少 4GB RAM
- ✅ 2GB 可用硬碟空間
- ✅ 網路連線

### 需要的軟體

1. **Node.js**（版本 18.0.0 或更新）
2. **PowerShell**（Windows 10/11 內建）
3. **文字編輯器**（建議 VS Code 或 Notepad++）

---

## 安裝 Node.js

### 步驟 1：下載 Node.js

1. 前往 Node.js 官網：https://nodejs.org/
2. 下載 **LTS（長期支援）版本**（例如：22.22.0）
3. 選擇 **Windows Installer (.msi)** 64-bit

### 步驟 2：安裝 Node.js

1. 執行下載的 `.msi` 檔案
2. 點擊 **Next** 繼續
3. 同意授權條款（勾選 "I accept..."）
4. 選擇安裝路徑（建議使用預設）
5. **重要**：勾選 "Automatically install the necessary tools"
6. 點擊 **Install** 開始安裝
7. 安裝完成後點擊 **Finish**

### 步驟 3：驗證 Node.js 安裝

1. 按 `Win + X`，選擇 **Windows PowerShell** 或 **終端機**
2. 輸入以下指令：

```powershell
node --version
```

應該會顯示類似：`v22.22.0`

3. 再輸入：

```powershell
npm --version
```

應該會顯示類似：`10.5.0`

✅ 如果都有顯示版本號，代表 Node.js 安裝成功！

---

## 安裝 OpenClaw

### 步驟 1：開啟 PowerShell

1. 按 `Win + X`
2. 選擇 **Windows PowerShell（系統管理員）** 或 **終端機（系統管理員）**

> 💡 **提示**：以系統管理員身份執行可以避免權限問題

### 步驟 2：設定執行政策（首次安裝需要）

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

- 如果出現提示，輸入 `Y` 並按 Enter

### 步驟 3：安裝 OpenClaw

```powershell
npm install -g openclaw
```

- 安裝過程大約需要 2-5 分鐘
- 會看到下載進度和安裝訊息

### 步驟 4：驗證 OpenClaw 安裝

```powershell
openclaw --version
```

應該會顯示類似：`2026.2.3-1`

✅ 如果顯示版本號，代表 OpenClaw 安裝成功！

---

## 初始設定

### 步驟 1：建立 Workspace 目錄

```powershell
# 建立 Workspace 目錄（可自訂路徑）
New-Item -ItemType Directory -Path "$HOME\openclaw-workspace"

# 進入 Workspace
cd "$HOME\openclaw-workspace"
```

### 步驟 2：執行設定精靈

```powershell
openclaw configure
```

設定精靈會引導你完成以下設定：

#### 2.1 選擇模式
```
? How would you like to run OpenClaw?
  ❯ Local (on this machine)
    Gateway (remote access)
```
- 新手選擇：**Local**

#### 2.2 設定 Workspace
```
? Where should OpenClaw store its files?
  ❯ C:\Users\YourName\openclaw-workspace (推薦)
    Custom path...
```
- 建議使用預設路徑

#### 2.3 選擇 AI 模型

```
? Which AI model would you like to use?
  ❯ Google Gemini (free, requires API key)
    Claude (requires API key)
    OpenAI GPT (requires API key)
```

**選項說明**：
- **Google Gemini**：免費，但需要 API Key
- **Claude**：需要 API Key（付費）
- **OpenAI GPT**：需要 API Key（付費）

#### 2.4 輸入 API Key

以 Google Gemini 為例：

```
? Enter your Google API Key:
  [輸入你的 API Key]
```

**如何取得 API Key**：
- Google Gemini：https://makersuite.google.com/app/apikey
- Anthropic Claude：https://console.anthropic.com/
- OpenAI：https://platform.openai.com/api-keys

#### 2.5 設定 Telegram Bot（選填）

```
? Would you like to connect a Telegram bot?
  ❯ Yes
    No (skip for now)
```

如果選擇 Yes：
1. 前往 Telegram 搜尋 `@BotFather`
2. 發送 `/newbot` 建立新 bot
3. 取得 Bot Token（格式：`1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`）
4. 將 Token 貼到設定精靈

### 步驟 3：完成設定

設定完成後會顯示：

```
✅ Configuration saved!
📍 Config file: C:\Users\YourName\.openclaw\openclaw.json
🚀 You can now start OpenClaw with: openclaw gateway
```

---

## 啟動 Gateway

### 方法 1：前台啟動（測試用）

```powershell
openclaw gateway
```

- Gateway 會在前台運行
- 按 `Ctrl + C` 停止
- 關閉 PowerShell 視窗會停止 Gateway

### 方法 2：背景啟動（推薦）

#### 2.1 使用 Task Scheduler（開機自動啟動）

```powershell
# 建立排程任務
$Action = New-ScheduledTaskAction -Execute "openclaw" -Argument "gateway"
$Trigger = New-ScheduledTaskTrigger -AtStartup
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "OpenClaw Gateway" -Action $Action -Trigger $Trigger -Settings $Settings -Description "OpenClaw Gateway 自動啟動"

# 立即啟動
Start-ScheduledTask -TaskName "OpenClaw Gateway"
```

#### 2.2 驗證 Gateway 運行

```powershell
openclaw gateway status
```

應該會顯示：
```
Runtime: running
RPC probe: ok
Listening: 127.0.0.1:18789
```

---

## 驗證安裝

### 1. 開啟 Dashboard

在瀏覽器輸入：
```
http://localhost:18789
```

應該會看到 OpenClaw Dashboard

### 2. 測試 Telegram Bot（如果有設定）

1. 在 Telegram 搜尋你的 Bot
2. 發送 `/start`
3. Bot 應該會回應

### 3. 測試基本功能

在 Telegram 或 Dashboard 輸入：
```
你好，介紹一下你自己
```

如果 AI 有回應，代表安裝成功！ 🎉

---

## 常見問題

### Q1：安裝時出現「拒絕存取」錯誤

**解決方法**：
```powershell
# 以系統管理員身份執行 PowerShell
# 1. 按 Win + X
# 2. 選擇「Windows PowerShell（系統管理員）」
# 3. 重新執行安裝指令
```

### Q2：`openclaw` 指令找不到

**解決方法**：
```powershell
# 1. 檢查 npm 全域路徑是否在 PATH 中
npm config get prefix

# 2. 將輸出的路徑加入環境變數
# 例如：C:\Users\YourName\AppData\Roaming\npm

# 3. 關閉並重新開啟 PowerShell
```

### Q3：Node.js 版本太舊

**解決方法**：
```powershell
# 使用 nvm-windows 管理 Node.js 版本
# 1. 下載 nvm-windows：https://github.com/coreybutler/nvm-windows/releases
# 2. 安裝後執行：
nvm install 22.22.0
nvm use 22.22.0
```

### Q4：Gateway 無法啟動（Port 被佔用）

**解決方法**：
```powershell
# 1. 檢查 Port 18789 是否被佔用
netstat -ano | findstr :18789

# 2. 如果有輸出，找到 PID（最後一欄數字）
# 3. 停止該程序
Stop-Process -Id <PID> -Force

# 4. 或更改 Gateway Port（編輯 ~/.openclaw/openclaw.json）
```

### Q5：Telegram Bot 無法連線

**檢查清單**：
1. ✅ Bot Token 正確（在 BotFather 取得）
2. ✅ Gateway 正在運行（`openclaw gateway status`）
3. ✅ 網路連線正常
4. ✅ 防火牆沒有阻擋 OpenClaw

### Q6：API Key 無效

**解決方法**：
1. 確認 API Key 正確複製（沒有多餘空格）
2. 確認 API Key 有效期限
3. 檢查 API Key 的使用限制
4. 重新執行 `openclaw configure` 更新 API Key

---

## 🎯 下一步

安裝完成後，你可以：

1. **閱讀使用指南**
   - [OpenClaw Windows 終端機指令大全](./OpenClaw-Windows-終端機指令大全.md)
   - [緊急切換模型指南](./緊急切換模型指南.md)

2. **安裝 Skills**
   ```powershell
   openclaw skills search youtube
   openclaw skills install youtube-data
   ```

3. **設定 Cron 排程**
   ```powershell
   openclaw cron add --name "每日提醒" --schedule "0 9 * * *" ...
   ```

4. **探索 Dashboard**
   - 前往：http://localhost:18789
   - 查看 Sessions、Models、Logs

---

## 📞 需要協助？

- 📖 官方文檔：https://docs.openclaw.ai
- 💬 Discord 社群：https://discord.com/invite/clawd
- 🐛 回報問題：https://github.com/openclaw/openclaw/issues

---

**安裝完成！** 🎉  
**最後更新**：2026-02-06  
**版本**：1.0
