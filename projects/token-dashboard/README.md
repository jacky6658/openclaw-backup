# 🦞 OpenClaw Token Dashboard v2.0

> 專業的 OpenClaw Token 用量監控與模型管理儀表板  
> ⚡ 全新賽博朋克主題 - 霓虹未來科技風

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Node](https://img.shields.io/badge/node-%3E=14.0.0-green)
![License](https://img.shields.io/badge/license-MIT-orange)
![Theme](https://img.shields.io/badge/theme-Cyberpunk-ff0080)

---

## ✨ 功能特色

### 🎛️ 即時監控
- **1 秒即時同步**：OpenClaw 用量數據每秒自動更新
- **當前模型顯示**：清楚顯示正在使用的 AI 模型
- **Gateway 狀態**：即時監控 Gateway 服務運行狀態
- **配額視覺化**：圓形進度圖直觀展示配額剩餘
- **所有 AI Keys 狀態**：自動偵測並顯示所有配置的 Provider（Anthropic/Google/OpenAI）

### 🔄 智能模型切換
- **一鍵切換**：在 UI 中直接切換 AI 模型，無需手動編輯配置文件
- **智能推薦**：自動推薦配額充足的最佳模型
- **Cooldown 顯示**：倒數計時器顯示模型恢復可用時間
- **自動重啟**：切換後自動重啟 Gateway，無需手動操作
- **Bot 自動連動**：切換後所有 Telegram Bot 對話立即使用新模型

### 📊 數據分析
- **Token 消耗統計**：今日/本週/本月用量一目了然
- **成本估算**：自動計算各模型使用成本
- **歷史趨勢**：7 日用量趨勢圖表
- **速率限制監控**：RPM/TPM 使用狀況

### 🎨 賽博朋克主題設計
- **霓虹美學**：深黑背景 + 霓虹粉/電光藍/螢光綠配色
- **特效滿載**：網格背景、霓虹流動線、脈動光暈、發光邊框
- **流暢動畫**：掃描線、旋轉光暈、懸停發光等互動特效
- **Icon 圖示**：使用 Lucide Icons 替代 emoji，更專業美觀
- **Toast 通知**：毛玻璃效果 + 滑入動畫

### 📱 完整響應式設計
- **多裝置支援**：桌機、平板、手機完美適配
- **5 個斷點**：>1024px / 769-1024px / 481-768px / ≤480px / 橫向
- **自適應佈局**：卡片自動調整為 4列/2列/1列
- **手機優化**：縮小字體、全寬按鈕、簡化導航
- **觸控友善**：適合手指操作的按鈕大小

---

## 🚀 快速開始

### 方法一：圖形化啟動（推薦）⭐

**雙擊「啟動 Dashboard.command」檔案**

> 💡 首次開啟需要：右鍵 > 打開 > 確認

會自動：
- ✅ 檢查環境
- ✅ 安裝依賴（首次）
- ✅ 啟動 Gateway
- ✅ 開啟瀏覽器
- ✅ 顯示手機訪問資訊

### 方法二：終端機啟動

```bash
cd /Users/user/clawd/projects/token-dashboard

# 首次使用：安裝依賴
npm install

# 啟動
./start.sh

# 或直接執行
node backend/server.js
```

---

## 🌐 訪問 Dashboard

### 💻 電腦訪問
```
http://localhost:3737
```

### 📱 手機訪問

#### 方法一：QR Code（最簡單）
1. **雙擊「手機訪問指南.html」**
2. 點擊「自動偵測我的 IP」
3. 用手機相機掃描 QR Code
4. 自動開啟 Dashboard ✨

#### 方法二：手動輸入
1. 確保手機和電腦在**同一個 WiFi**
2. 查看電腦 IP（啟動器會顯示）
3. 在手機瀏覽器輸入：`http://你的IP:3737`

**範例：**
```
http://192.168.1.100:3737
```

---

## 🔄 切換模型

1. 點擊頂部「切換模型」按鈕
2. 查看所有可用模型及其狀態
3. 點擊「切換到此模型」按鈕
4. 等待自動重啟完成（約 3 秒）
5. 完成！Bot 立即使用新模型 ✅

**在手機上也能切換！** 📱

---

## 📋 系統需求

- **Node.js** >= 14.0.0
- **OpenClaw** 已安裝並配置
- **macOS** / Linux（理論上支援 Windows）

---

## 📁 專案結構

```
token-dashboard/
├── 啟動 Dashboard.command       # 🎯 圖形化啟動器（推薦）
├── 打包分享.command              # 📦 一鍵打包分享
├── 手機訪問指南.html            # 📱 手機訪問說明（含 QR Code）
├── 分享給朋友指南.md            # 👥 分享使用說明
├── README_FOR_FRIEND.md        # 📖 給朋友的快速指南
├── start.sh                    # 🔧 終端機啟動腳本
│
├── backend/
│   ├── server.js               # Express API 伺服器
│   ├── collector/
│   │   └── collect.js          # 數據收集腳本
│   ├── db/
│   │   └── openclaw-tokens.db  # SQLite 資料庫
│   └── utils/
│       └── pricing.js          # 成本計算工具
│
├── frontend/
│   ├── index.html              # 主頁面（含 Lucide Icons）
│   ├── css/
│   │   └── main.css            # 賽博朋克主題樣式
│   └── js/
│       └── main.js             # 前端邏輯
│
└── 文檔/
    ├── README.md               # 本文件
    ├── DEPLOYMENT_GUIDE.md     # 部署指南
    ├── UPGRADE_NOTES.md        # 詳細功能說明
    ├── CYBERPUNK_THEME.md      # 主題配色文檔
    ├── FEATURES_CHECKLIST.md   # 功能檢查清單
    └── IMPLEMENTATION_SUMMARY.md  # 實作總結
```

---

## 🔧 API 端點

### 數據查詢
- `GET /api/overview?period=today|week|month` - 用量總覽
- `GET /api/models` - 模型配額狀態
- `GET /api/rate-limits` - 速率限制
- `GET /api/history?days=7` - 歷史數據
- `GET /api/cost?period=today|week|month` - 成本分析

### 配置管理
- `GET /api/config` - 獲取當前配置
- `POST /api/switch-model` - 切換模型
- `GET /api/health` - 健康檢查

---

## 🎯 使用場景

### 場景 1：監控 Token 用量
每秒自動刷新，隨時掌握 Token 消耗狀況，避免超出預算。

### 場景 2：管理多個模型
當一個模型進入 Cooldown 或配額不足時，一鍵切換到其他可用模型。

### 場景 3：成本分析
查看各模型的成本佔比，優化使用策略，降低整體開銷。

### 場景 4：排查問題
監控 Gateway 狀態、速率限制，快速定位問題根源。

---

## 🐛 疑難排解

### Q: Gateway 狀態顯示紅色
**A:** 執行 `openclaw gateway start` 啟動服務

### Q: 切換模型後仍使用舊模型
**A:** 等待 3 秒讓 Gateway 完全重啟，或手動執行 `openclaw gateway restart`

### Q: 配額顯示 0%
**A:** 該模型可能處於 Cooldown 或已用盡，請切換到其他模型

### Q: 頁面載入慢
**A:** 檢查 OpenClaw CLI 是否回應緩慢，可能需要重啟 Gateway

---

## 📸 視覺特色

### 🌌 賽博朋克背景
- 深黑到深夜藍的漸層背景
- 淡色網格線（50px × 50px）
- 脈動粉紅色光暈（8秒循環）

### ⚡ 霓虹發光系統
- **霓虹粉** (#ff0080)：按鈕、當前模型
- **電光藍** (#00f0ff)：文字標籤、邊框
- **螢光綠** (#00ff88)：成功狀態、配額充足
- 所有元素帶發光 `box-shadow`

### 🎬 動畫特效
| 效果 | 位置 | 描述 |
|------|------|------|
| 霓虹流動線 | Header 底部 | 彩色線條 3秒循環流動 |
| 脈動呼吸燈 | Gateway 狀態 | 2秒循環，陰影擴散 |
| 旋轉光暈 | 按鈕懸停 | 徑向光暈 360度旋轉 |
| 掃描線 | 卡片懸停 | 半透明線條橫向掃過 |
| 滑入動畫 | Toast 通知 | 從右側滑入帶淡入 |

### 📱 頁面元素
- **頂部控制面板**：當前模型 + 配額圓環 + 倒數計時
- **模型切換 Modal**：霓虹邊框卡片 + Cooldown 倒數
- **數據卡片**：發光邊框 + 漸層數字 + 懸停上浮
- **Toast 通知**：毛玻璃效果 + 霓虹邊框

---

## 🎨 主題切換

### 當前主題：賽博朋克 ⚡
霓虹粉/電光藍/螢光綠配色，帶網格背景和發光特效

### 可用主題
```bash
# 當前使用中（賽博朋克）
main.css

# 備份可用
main.css.backup  # 原版紫色漸層主題
```

### 切換回舊版紫色主題
```bash
cd /Users/user/clawd/projects/token-dashboard/frontend/css
mv main.css main-cyberpunk.css
mv main.css.backup main.css
```

### 主題特色對比
| 特色 | 賽博朋克 | 紫色主題 |
|------|---------|---------|
| 配色 | 霓虹粉/電光藍/螢光綠 | 紫色漸層 |
| 背景 | 深黑 + 網格 | 淺色漸層 |
| 特效 | 霓虹發光 + 流動線 | 基礎陰影 |
| 風格 | 未來科技感 | 現代專業風 |

詳細配色說明請參考：[CYBERPUNK_THEME.md](./CYBERPUNK_THEME.md)

---

## 🔮 未來計劃

- [ ] WebSocket 即時推送
- [ ] 圖表視覺化（Chart.js）
- [ ] 更多主題選項（深空藍、黑客綠、科技藍）
- [ ] 自訂警報閾值
- [ ] 匯出報表（CSV/PDF）

---

## 📝 更新日誌

**v2.0.0** (2026-02-02)
- ✨ 新增模型切換功能
- ✨ 1 秒即時刷新
- ✨ Toast 通知系統
- ✨ Cooldown 倒數計時器
- 🎨 全面 UI/UX 優化
- ⚡ 採用賽博朋克主題設計
- 🌌 新增霓虹發光特效
- 🎬 新增多種動畫效果

**v1.0.0** (初始版本)
- 基礎 Token 監控
- 成本估算
- 歷史數據

---

## 📄 授權

MIT License

---

## 📦 分享給朋友

### 一鍵打包
**雙擊「打包分享.command」** - 自動打包到桌面

### 給朋友的說明
壓縮包中包含：
- ✅ `啟動 Dashboard.command` - 雙擊啟動
- ✅ `手機訪問指南.html` - QR Code 訪問
- ✅ `README_FOR_FRIEND.md` - 快速開始指南
- ✅ 完整原始碼和文檔

詳細說明：查看 [分享給朋友指南.md](./分享給朋友指南.md)

---

## 🙋 需要幫助？

| 文檔 | 用途 |
|------|------|
| [README_FOR_FRIEND.md](./README_FOR_FRIEND.md) | 🎯 給朋友的快速指南 |
| [分享給朋友指南.md](./分享給朋友指南.md) | 📦 打包分享說明 |
| [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) | 🚀 完整部署指南 |
| [FEATURES_CHECKLIST.md](./FEATURES_CHECKLIST.md) | ✅ 功能檢查清單 |
| [UPGRADE_NOTES.md](./UPGRADE_NOTES.md) | 📝 詳細功能說明 |
| [CYBERPUNK_THEME.md](./CYBERPUNK_THEME.md) | 🎨 主題配色文檔 |
| `手機訪問指南.html` | 📱 手機訪問圖形化說明 |

**OpenClaw 文檔**：查看 `/Users/user/Downloads/備份指南/`

---

---

**打造於 2026 年，專為 OpenClaw 使用者設計** ⚡🦞  
*Powered by Cyberpunk Theme - Neon Future Tech*
