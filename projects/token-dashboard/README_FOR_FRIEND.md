# 🎉 歡迎使用 OpenClaw Token Dashboard

> ⚡ 專業的 AI Token 監控工具 - 賽博朋克霓虹風格

---

## 🚀 快速開始（3 步驟）

### 步驟 1：解壓縮
將 `token-dashboard-XXXXXXXX.zip` 解壓縮到任意位置

### 步驟 2：啟動 Dashboard
**雙擊「啟動 Dashboard.command」檔案**

> 💡 首次開啟可能需要：右鍵 > 打開 > 確認

### 步驟 3：開始使用
瀏覽器會自動開啟 Dashboard 介面 ✨

---

## 📱 在手機上查看

### 方法一：QR Code（最簡單）
1. **雙擊「手機訪問指南.html」**
2. 點擊「自動偵測我的 IP」
3. 用手機相機掃描 QR Code
4. 完成！🎉

### 方法二：手動輸入
1. 確保手機和電腦連接**同一個 WiFi**
2. 在終端機視窗中找到「手機訪問」網址
3. 在手機瀏覽器輸入該網址

---

## 💻 系統需求

### 必須安裝
- ✅ **Node.js** (>= 14.0.0)
  - 下載：https://nodejs.org/
  - 選擇 LTS 版本

- ✅ **OpenClaw**（已配置）
  - 您必須先安裝並配置好 OpenClaw
  - Dashboard 會自動連接到您的 OpenClaw

### 如何確認？
```bash
# 檢查 Node.js
node -v
# 應顯示：v14.x.x 或更高

# 檢查 OpenClaw
openclaw --version
# 應顯示版本號

# 檢查 Gateway
openclaw status
# 應顯示：Gateway running
```

---

## ✨ Dashboard 功能

### 🎛️ 即時監控
- 📊 1 秒自動刷新用量數據
- 💎 當前模型與配額顯示
- 🔴 Gateway 狀態監控

### 🔄 智能模型切換
- 🎯 一鍵切換 AI 模型
- 💡 智能推薦最佳模型
- ⏱️ Cooldown 倒數計時
- 🤖 自動連動 Telegram Bot

### 📊 數據分析
- 📈 Token 消耗統計
- 💰 成本估算
- 📅 7 日歷史趨勢
- ⚡ 速率限制監控

### 🎨 賽博朋克設計
- 🌌 霓虹粉/電光藍/螢光綠配色
- ✨ 網格背景 + 發光特效
- 🎬 流暢動畫效果
- 📱 完整手機響應式

---

## 🎯 使用場景

### 場景 1：桌機監控
在電腦上隨時查看 Token 用量，避免超出預算

### 場景 2：手機查看
出門在外也能用手機監控用量

### 場景 3：快速切換
當一個模型 Cooldown 時，立即切換到其他模型

### 場景 4：成本分析
每月查看各模型成本，優化使用策略

---

## 📖 更多文檔

| 文檔 | 說明 |
|------|------|
| `README.md` | 詳細使用說明 |
| `DEPLOYMENT_GUIDE.md` | 完整部署指南 |
| `分享給朋友指南.md` | 打包分享說明 |
| `手機訪問指南.html` | 圖形化手機訪問說明 |
| `CYBERPUNK_THEME.md` | 主題配色文檔 |

---

## 🐛 遇到問題？

### 啟動器無法執行
```
右鍵點擊「啟動 Dashboard.command」
> 打開
> 打開（確認）
```

### 瀏覽器沒開啟
```
手動開啟瀏覽器，輸入：
http://localhost:3737
```

### 顯示「Gateway 未運行」
```
終端機執行：
openclaw gateway start
```

### 手機無法連接
```
1. 確認同一個 WiFi
2. 檢查防火牆設定
3. 確認電腦上 Dashboard 正在運行
```

---

## 🎊 開始使用

**雙擊「啟動 Dashboard.command」即可開始！**

或查看 `README.md` 了解更多功能 📚

---

**打造於 2026 年 · 專為 OpenClaw 使用者設計** ⚡🦞

祝您使用愉快！✨
