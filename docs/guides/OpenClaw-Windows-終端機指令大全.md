# OpenClaw Windows 終端機指令大全

**適用版本**：OpenClaw 2026.2.x  
**系統需求**：Windows 10/11 (PowerShell 5.1+ 或 PowerShell 7+)  
**最後更新**：2026-02-06

---

## 📋 目錄

1. [安裝與設定](#安裝與設定)
2. [基本指令](#基本指令)
3. [Gateway 管理](#gateway-管理)
4. [模型管理](#模型管理)
5. [Session 管理](#session-管理)
6. [Cron 排程](#cron-排程)
7. [技能管理](#技能管理)
8. [日誌與偵錯](#日誌與偵錯)
9. [常見問題](#常見問題)

---

## 安裝與設定

### 方法 1：透過 npm 安裝（推薦）

```powershell
# 檢查 Node.js 版本（需要 18.0.0 或更新）
node --version

# 全域安裝 OpenClaw
npm install -g openclaw

# 驗證安裝
openclaw --version

# 首次設定（啟動設定精靈）
openclaw configure
```

### 方法 2：透過 Chocolatey 安裝（未來支援）

```powershell
# 安裝 Chocolatey（如果尚未安裝）
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# 安裝 OpenClaw（目前尚未支援）
# choco install openclaw
```

### 初始化 Workspace

```powershell
# 建立 Workspace 目錄
New-Item -ItemType Directory -Path "$HOME\openclaw-workspace"
cd "$HOME\openclaw-workspace"

# 初始化（會建立 AGENTS.md, SOUL.md 等核心檔案）
openclaw init
```

---

## 基本指令

### 系統狀態

```powershell
# 查看 OpenClaw 狀態
openclaw status

# 查看版本資訊
openclaw --version
openclaw -v

# 查看幫助
openclaw --help
openclaw help
openclaw help <command>  # 特定指令的說明
```

### 設定管理

```powershell
# 查看設定檔位置
openclaw config get

# 查看設定檔 schema
openclaw config schema

# 編輯設定檔（會開啟預設編輯器）
openclaw config edit

# 重新執行設定精靈
openclaw configure

# 驗證設定檔
openclaw config validate
```

---

## Gateway 管理

### 啟動與停止

```powershell
# 啟動 Gateway（前台運行）
openclaw gateway

# 啟動 Gateway（背景運行，需搭配 Task Scheduler）
Start-Process -NoNewWindow openclaw -ArgumentList "gateway"

# 停止 Gateway
# 在前台運行時：按 Ctrl+C
# 在背景運行時：
Get-Process -Name "node" | Where-Object {$_.CommandLine -like "*openclaw*gateway*"} | Stop-Process

# 重啟 Gateway
# 先停止再啟動（Windows 沒有 restart 指令）
```

### Gateway 狀態

```powershell
# 查看 Gateway 狀態
openclaw gateway status

# 查看 Gateway 日誌
Get-Content -Path "$env:TEMP\openclaw\openclaw-$(Get-Date -Format 'yyyy-MM-dd').log" -Tail 50 -Wait

# 測試 Gateway 連線
Test-NetConnection -ComputerName 127.0.0.1 -Port 18789
```

### 設定 Gateway 自動啟動（Task Scheduler）

```powershell
# 建立排程任務（開機自動啟動）
$Action = New-ScheduledTaskAction -Execute "openclaw" -Argument "gateway"
$Trigger = New-ScheduledTaskTrigger -AtStartup
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "OpenClaw Gateway" -Action $Action -Trigger $Trigger -Settings $Settings -Description "OpenClaw Gateway 自動啟動"

# 手動啟動排程任務
Start-ScheduledTask -TaskName "OpenClaw Gateway"

# 停止排程任務
Stop-ScheduledTask -TaskName "OpenClaw Gateway"

# 查看排程任務狀態
Get-ScheduledTask -TaskName "OpenClaw Gateway"

# 移除排程任務
Unregister-ScheduledTask -TaskName "OpenClaw Gateway" -Confirm:$false
```

---

## 模型管理

### 查看模型

```powershell
# 查看所有可用模型
openclaw models

# 查看模型詳細資訊
openclaw models --verbose

# 查看特定 provider 的模型
openclaw models | Select-String "anthropic"
openclaw models | Select-String "google"
```

### 模型認證

```powershell
# 新增 Anthropic API Token
openclaw auth add anthropic --token "sk-ant-xxxxx"

# 新增 Google OAuth
openclaw auth add google-antigravity --oauth

# 查看認證狀態
openclaw auth list

# 移除認證
openclaw auth remove <profile-name>
```

### 切換模型

```powershell
# 在 Telegram 或 WebUI 中使用指令
/model gemini-2.5-pro
/model google-antigravity/claude-opus-4-5-thinking
/model default

# 或直接修改設定檔
# 編輯 ~/.openclaw/openclaw.json
# 找到 "agents.defaults.model.primary"
```

---

## Session 管理

### 查看 Sessions

```powershell
# 列出所有 sessions
openclaw sessions list

# 列出最近 10 個 sessions
openclaw sessions list --limit 10

# 查看特定 session 的歷史
openclaw sessions history <session-key>
```

### 發送訊息到 Session

```powershell
# 發送訊息到特定 session
openclaw sessions send <session-key> "你好"

# 發送訊息並等待回應
openclaw sessions send <session-key> "完成這個任務" --timeout 60
```

---

## Cron 排程

### 查看排程任務

```powershell
# 列出所有 cron jobs
openclaw cron list

# 查看 cron 狀態
openclaw cron status
```

### 新增排程任務

```powershell
# 每天 21:00 執行（使用 cron 表達式）
openclaw cron add `
  --name "每日匯報" `
  --schedule "0 21 * * *" `
  --session-target isolated `
  --payload-kind agentTurn `
  --message "整理今日工作報告"

# 每 5 分鐘執行一次
openclaw cron add `
  --name "Token 收集" `
  --schedule "*/5 * * * *" `
  --session-target isolated `
  --payload-kind agentTurn `
  --message "收集 token 用量"

# 一次性排程（在特定時間執行）
openclaw cron add `
  --name "提醒事項" `
  --at "2026-02-07T10:00:00+08:00" `
  --session-target isolated `
  --payload-kind agentTurn `
  --message "記得開會"
```

### 管理排程任務

```powershell
# 執行排程任務
openclaw cron run <job-id>

# 查看執行歷史
openclaw cron runs <job-id>

# 停用排程任務
openclaw cron update <job-id> --enabled false

# 啟用排程任務
openclaw cron update <job-id> --enabled true

# 刪除排程任務
openclaw cron remove <job-id>
```

---

## 技能管理

### 查看技能

```powershell
# 列出已安裝的技能
openclaw skills list

# 搜尋技能（ClawHub）
openclaw skills search "youtube"

# 查看技能詳情
openclaw skills info <skill-name>
```

### 安裝技能

```powershell
# 從 ClawHub 安裝
openclaw skills install <skill-name>

# 從本地安裝
openclaw skills install ./my-skill/

# 安裝特定版本
openclaw skills install <skill-name>@1.0.0
```

### 管理技能

```powershell
# 更新技能
openclaw skills update <skill-name>

# 更新所有技能
openclaw skills update --all

# 移除技能
openclaw skills uninstall <skill-name>

# 啟用/停用技能
openclaw skills enable <skill-name>
openclaw skills disable <skill-name>
```

---

## 日誌與偵錯

### 查看日誌

```powershell
# 即時查看 Gateway 日誌（追蹤模式）
Get-Content -Path "$env:TEMP\openclaw\openclaw-$(Get-Date -Format 'yyyy-MM-dd').log" -Tail 50 -Wait

# 查看最近 100 行日誌
Get-Content -Path "$env:TEMP\openclaw\openclaw-$(Get-Date -Format 'yyyy-MM-dd').log" -Tail 100

# 搜尋日誌中的錯誤
Get-Content -Path "$env:TEMP\openclaw\openclaw-*.log" | Select-String "error" -Context 2,2

# 查看特定日期的日誌
Get-Content -Path "$env:TEMP\openclaw\openclaw-2026-02-06.log"
```

### 偵錯模式

```powershell
# 以偵錯模式啟動 Gateway
$env:DEBUG="*"; openclaw gateway

# 只顯示特定模組的偵錯訊息
$env:DEBUG="openclaw:*"; openclaw gateway

# 關閉偵錯模式
Remove-Item Env:\DEBUG
```

### 清理日誌

```powershell
# 刪除 7 天前的日誌
Get-ChildItem -Path "$env:TEMP\openclaw" -Filter "openclaw-*.log" | 
  Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-7)} | 
  Remove-Item

# 刪除所有日誌（謹慎使用）
Remove-Item -Path "$env:TEMP\openclaw\*.log" -Force
```

---

## 常見問題

### 1. 權限問題

```powershell
# 執行政策錯誤
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 以管理員身份執行 PowerShell
Start-Process powershell -Verb RunAs
```

### 2. Node.js 版本問題

```powershell
# 檢查 Node.js 版本（需要 18.0.0+）
node --version

# 使用 nvm-windows 管理 Node.js 版本
# 下載：https://github.com/coreybutler/nvm-windows/releases

# 安裝特定版本
nvm install 22.22.0
nvm use 22.22.0
```

### 3. Gateway 無法啟動

```powershell
# 檢查 Port 18789 是否被佔用
netstat -ano | findstr :18789

# 停止佔用 Port 的程序
# 找到 PID 後執行
Stop-Process -Id <PID> -Force

# 更改 Gateway Port（編輯 ~/.openclaw/openclaw.json）
# "gateway": { "port": 18790 }
```

### 4. Workspace 路徑問題

```powershell
# 查看目前 Workspace
openclaw config get agents.defaults.workspace

# 設定 Workspace
# 編輯 ~/.openclaw/openclaw.json
# "agents": { "defaults": { "workspace": "C:\\Users\\YourName\\openclaw-workspace" } }
```

### 5. 環境變數設定

```powershell
# 設定環境變數（當前 session）
$env:OPENCLAW_API_KEY="your-api-key"

# 永久設定環境變數（系統層級）
[System.Environment]::SetEnvironmentVariable('OPENCLAW_API_KEY', 'your-api-key', 'User')

# 查看環境變數
Get-ChildItem Env: | Where-Object {$_.Name -like "*OPENCLAW*"}
```

---

## 🔧 實用腳本

### 自動備份設定檔

```powershell
# backup-openclaw-config.ps1
$BackupDir = "$HOME\openclaw-backups"
New-Item -ItemType Directory -Path $BackupDir -Force
$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
Copy-Item "$HOME\.openclaw\openclaw.json" "$BackupDir\openclaw-$Timestamp.json"
Write-Host "✅ 備份完成：$BackupDir\openclaw-$Timestamp.json"
```

### 快速啟動 Gateway

```powershell
# start-openclaw.ps1
Write-Host "🚀 啟動 OpenClaw Gateway..."
Start-Process -NoNewWindow openclaw -ArgumentList "gateway"
Start-Sleep 3
Write-Host "✅ Gateway 已啟動"
Write-Host "📊 Dashboard: http://localhost:18789"
```

### 檢查系統狀態

```powershell
# check-openclaw.ps1
Write-Host "=== OpenClaw 系統狀態 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "📌 版本資訊："
openclaw --version
Write-Host ""
Write-Host "📌 Gateway 狀態："
openclaw gateway status
Write-Host ""
Write-Host "📌 模型狀態："
openclaw models | Select-String "usage"
Write-Host ""
Write-Host "📌 認證狀態："
openclaw auth list
```

---

## 📚 相關連結

- 官方文檔：https://docs.openclaw.ai
- GitHub：https://github.com/openclaw/openclaw
- ClawHub：https://clawhub.com
- Discord：https://discord.com/invite/clawd

---

**最後更新**：2026-02-06  
**版本**：1.0  
**適用系統**：Windows 10/11
