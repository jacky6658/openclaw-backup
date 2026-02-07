# 🚀 OpenClaw Token Dashboard - 使用者部署指南

> ⚡ 超簡單！3 分鐘完成本機部署，無需雲端伺服器

---

## 📋 部署前準備

### 必備條件
- ✅ macOS / Linux（Windows 理論上也可以）
- ✅ 已安裝 OpenClaw 並配置完成
- ✅ Node.js >= 14.0.0

### 檢查 OpenClaw 是否安裝
```bash
openclaw --version
# 應該顯示版本號，例如：2026.2.3-1
```

如果未安裝，請先參考 `/Users/user/Downloads/備份指南/` 中的安裝指南。

---

## 🎯 快速部署（3 步驟）

### 步驟 1：下載專案
```bash
# 方法 1：從源頭複製
cp -r /Users/user/clawd/projects/token-dashboard ~/my-dashboard
cd ~/my-dashboard

# 方法 2：如果收到壓縮包
unzip token-dashboard.zip
cd token-dashboard
```

### 步驟 2：安裝依賴
```bash
npm install
```

### 步驟 3：啟動 Dashboard
```bash
./start.sh

# 或手動啟動
node backend/server.js
```

就這麼簡單！🎉

---

## 🌐 訪問 Dashboard

開啟瀏覽器，前往：

```
http://localhost:3737
```

### 在手機上訪問
如果想要在手機上查看：

1. **確保手機和電腦在同一個 WiFi 網路**
2. **查看電腦 IP 位址**：
   ```bash
   # macOS
   ifconfig | grep "inet " | grep -v 127.0.0.1
   
   # 或簡單方式：系統偏好設定 > 網路 > WiFi > IP 位址
   # 例如：192.168.1.100
   ```
3. **在手機瀏覽器輸入**：
   ```
   http://192.168.1.100:3737
   ```

---

## 🔒 自動連接功能

### Dashboard 如何自動讀取您的 OpenClaw 配置？

Dashboard 會自動讀取：
1. **配置文件**：`~/.openclaw/openclaw.json`
2. **執行命令**：`openclaw models`、`openclaw status`
3. **資料庫**：`backend/db/openclaw-tokens.db`

### 支援的功能
✅ 自動顯示當前使用的模型  
✅ 自動顯示所有配置的 AI Keys 狀態  
✅ 自動監控配額剩餘  
✅ 自動檢測 Cooldown 時間  
✅ 一鍵切換模型（自動重啟 Gateway）  
✅ 即時同步用量（每 1 秒）  

**無需任何額外配置！** 🎯

---

## 📱 手機響應式設計

Dashboard 已完整支援手機瀏覽：

### 自動適應
- 📱 **手機**：單列卡片佈局
- 📱 **平板**：雙列網格佈局  
- 💻 **桌機**：多列網格佈局

### 手機上的功能
✅ 滑動查看數據  
✅ 點擊切換模型  
✅ 即時通知 Toast  
✅ 完整功能無縮減  

### 測試響應式
```bash
# 啟動後，在瀏覽器中：
# 1. 按 F12 開啟開發者工具
# 2. 點擊手機圖示（Toggle device toolbar）
# 3. 選擇不同裝置尺寸測試
```

---

## 🔄 模型切換功能

### 自動連動到 Bot

當您在 Dashboard 中切換模型時，系統會：

1. ✅ **更新配置**：修改 `~/.openclaw/openclaw.json` 中的 `llm.defaultProfile.primary`
2. ✅ **重啟 Gateway**：自動執行 `openclaw gateway restart`
3. ✅ **等待就緒**：確保 Gateway 完全重啟（約 3 秒）
4. ✅ **即時反饋**：顯示 Toast 通知切換結果

**所有 Telegram Bot 對話將立即使用新模型！** 🤖

### 使用方式
1. 點擊頂部「切換模型」按鈕
2. 查看所有可用模型及其狀態
3. 選擇想要的模型，點擊「切換到此模型」
4. 等待 3 秒完成切換
5. 開始使用新模型！

---

## 🎨 介面特色

### 賽博朋克主題
- 🌌 深黑背景 + 網格線
- ⚡ 霓虹粉/電光藍/螢光綠配色
- ✨ 發光邊框與文字特效
- 🎬 流動線、掃描線、光暈動畫

### 即時監控
- 🔴 Gateway 狀態指示器（脈動動畫）
- 📊 配額圓形進度圖
- ⏱️ 1 秒即時刷新
- 🔔 Toast 即時通知

---

## 🛠️ 進階配置

### 更改端口
如果 3737 端口被佔用：

```javascript
// 編輯 backend/server.js
const PORT = process.env.PORT || 3737; // 改為 3838 或其他

// 或使用環境變數
PORT=3838 node backend/server.js
```

### 自動啟動（macOS）
創建 LaunchAgent：

```bash
# 1. 創建 plist 文件
nano ~/Library/LaunchAgents/com.openclaw.dashboard.plist
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.openclaw.dashboard</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/node</string>
        <string>/Users/YOUR_USERNAME/my-dashboard/backend/server.js</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

```bash
# 2. 載入服務
launchctl load ~/Library/LaunchAgents/com.openclaw.dashboard.plist

# 3. 啟動服務
launchctl start com.openclaw.dashboard
```

### 背景運行
```bash
# 使用 nohup（簡單）
nohup node backend/server.js > dashboard.log 2>&1 &

# 使用 PM2（推薦）
npm install -g pm2
pm2 start backend/server.js --name openclaw-dashboard
pm2 save
pm2 startup
```

---

## 🧪 測試部署

### 檢查清單
```bash
# 1. 檢查 OpenClaw
openclaw status
# 應該顯示 Gateway running

# 2. 檢查 Node.js
node -v
# 應該 >= v14.0.0

# 3. 檢查配置文件
cat ~/.openclaw/openclaw.json
# 應該有 llm.defaultProfile 設定

# 4. 啟動 Dashboard
./start.sh

# 5. 訪問測試
curl http://localhost:3737/api/health
# 應該返回：{"status":"ok","timestamp":"..."}
```

---

## 🐛 常見問題

### Q: Dashboard 無法啟動
**A:** 檢查端口是否被佔用
```bash
lsof -i :3737
# 如果有輸出，代表端口被佔用
# 解決：殺掉進程或更改端口
```

### Q: 顯示「Gateway 未運行」
**A:** 啟動 OpenClaw Gateway
```bash
openclaw gateway start
# 或
openclaw gateway install  # 安裝為系統服務
```

### Q: 切換模型沒反應
**A:** 手動檢查並重啟
```bash
# 1. 檢查配置
cat ~/.openclaw/openclaw.json | grep primary

# 2. 手動重啟 Gateway
openclaw gateway restart

# 3. 查看日誌
openclaw logs --follow
```

### Q: 手機無法訪問
**A:** 檢查防火牆
```bash
# macOS 允許端口
sudo pfctl -d  # 暫時關閉防火牆測試

# 或在系統偏好設定 > 安全性與隱私 > 防火牆 > 防火牆選項
# 允許 Node.js 接收連線
```

### Q: 資料不更新
**A:** 檢查資料收集腳本
```bash
# 手動執行一次
node backend/collector/collect.js

# 設定 cron（每 5 分鐘收集）
crontab -e
# 加入：
# */5 * * * * cd /path/to/token-dashboard && node backend/collector/collect.js
```

---

## 📊 使用說明

### 總覽頁
- 查看今日/本週/本月 Token 消耗
- 查看 Input/Output 分佈
- 查看使用的模型列表

### 模型頁
- 查看所有模型配額狀態
- 綠色：配額充足（≥70%）
- 黃色：配額偏低（30-69%）
- 紅色：配額不足（<30%）

### 速率限制頁
- 監控 RPM（每分鐘請求數）
- 監控 TPM（每分鐘 Token 數）
- 查看 Cooldown 狀態

### 歷史頁
- 查看最近 7 天用量趨勢
- 對比每日消耗量

### 成本頁
- 估算今日/本週/本月成本
- 查看各模型成本分解
- 預測月底總成本

---

## 🔐 安全性

### 本機訪問（推薦）
Dashboard 預設綁定 `localhost:3737`，只能從本機訪問，最安全。

### 區域網路訪問
如果需要在手機/平板訪問：
- ⚠️ 只在私人 WiFi 網路中使用
- ⚠️ 不要在公共 WiFi 中開啟
- ⚠️ 不要暴露到公網

### 為什麼不需要雲端？
1. ✅ 所有數據都在本機
2. ✅ 配置文件在 `~/.openclaw/`
3. ✅ OpenClaw Gateway 在本機運行
4. ✅ Dashboard 只是讀取和操作本機資源
5. ✅ 無需擔心數據洩漏

---

## 📦 分享給其他人

### 打包專案
```bash
# 1. 複製整個專案
cp -r /path/to/token-dashboard ~/Desktop/token-dashboard-package

# 2. 清理 node_modules（太大）
rm -rf ~/Desktop/token-dashboard-package/node_modules

# 3. 壓縮
cd ~/Desktop
zip -r token-dashboard.zip token-dashboard-package

# 4. 分享 token-dashboard.zip
```

### 接收者部署步驟
```bash
# 1. 解壓縮
unzip token-dashboard.zip
cd token-dashboard-package

# 2. 安裝依賴
npm install

# 3. 啟動
./start.sh
```

**接收者必須先安裝並配置好 OpenClaw！**

---

## 🎓 學習資源

- **OpenClaw 文檔**：`/Users/user/Downloads/備份指南/`
- **專案 README**：`README.md`
- **詳細升級說明**：`UPGRADE_NOTES.md`
- **配色文檔**：`CYBERPUNK_THEME.md`

---

## 🙋 需要幫助？

1. 查看 `README.md` 快速開始
2. 查看 `UPGRADE_NOTES.md` 詳細功能
3. 查看本文件的「常見問題」章節
4. 聯繫您的 AI 助手 🦞

---

## ✨ 享受您的 Dashboard！

**所有功能開箱即用，無需複雜配置！** 🎉

立即啟動體驗：
```bash
./start.sh
```

然後開啟瀏覽器訪問：**http://localhost:3737** ⚡

---

**打造於 2026 年 · 專為 OpenClaw 使用者設計** 🦞⚡
