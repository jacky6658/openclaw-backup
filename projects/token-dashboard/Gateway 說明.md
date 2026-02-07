# 🔧 Gateway 完整說明

> OpenClaw Gateway 是什麼？需要手動啟動嗎？

---

## 🤔 Gateway 是什麼？

### 簡單理解

**Gateway 是 OpenClaw 的核心服務**，負責：

```
📡 接收來自各處的 AI 請求
   ↓
🧠 決定使用哪個 AI 模型
   ↓
🔄 處理模型切換和 Fallback
   ↓
📊 追蹤用量和配額
   ↓
💬 返回 AI 回應
```

### 類比說明

```
Gateway = 機場塔台
AI 模型 = 各家航空公司

塔台負責：
• 決定哪家航空公司執飛
• 如果一家滿載，切換到另一家
• 追蹤各航班狀況
• 協調所有請求
```

---

## ❓ Dashboard 需要 Gateway 嗎？

### 功能對照表

| 功能 | 需要 Gateway | 不需要 Gateway |
|------|--------------|----------------|
| **查看歷史數據** | ❌ | ✅ |
| **查看統計圖表** | ❌ | ✅ |
| **查看 Token 用量** | ❌ | ✅ |
| **查看成本估算** | ❌ | ✅ |
| **切換 AI 模型** | ✅ 需要 | ❌ |
| **查看即時配額** | ⚠️ 建議 | ⚠️ 有限 |
| **查看 Cooldown** | ⚠️ 建議 | ⚠️ 有限 |

### 結論

```
沒有 Gateway：
✅ Dashboard 仍可運行
✅ 可查看歷史數據和統計
❌ 無法切換模型
❌ 無法查看即時狀態

有 Gateway：
✅ 完整功能
✅ 可切換模型
✅ 即時監控
✅ 最佳體驗
```

---

## 🚀 Gateway 會自動啟動嗎？

### 當前行為（已優化）

**「啟動 Dashboard.command」現在會：**

```
1. 檢測 Gateway 是否運行
   ↓
2. 如果未運行 → 自動啟動 ✅
   ↓
3. 如果已運行 → 繼續使用 ✅
   ↓
4. 如果啟動失敗 → 提示用戶 ⚠️
```

### 三種模式

#### 模式 1：完全自動（推薦）⭐

```bash
# 啟動器會自動處理
雙擊「啟動 Dashboard.command」

結果：
✅ Gateway 自動啟動（如果未運行）
✅ Dashboard 正常運行
✅ 所有功能可用
```

#### 模式 2：開機自動啟動

```bash
# 使用 Gateway 管理工具設定
雙擊「檢查並啟動 Gateway.command」
→ 選擇「啟用開機自動啟動」

或使用命令：
openclaw gateway install

結果：
✅ 每次開機自動啟動
✅ 永久運行在背景
✅ 不需要手動啟動
```

#### 模式 3：手動控制

```bash
# 自己控制啟動和停止
openclaw gateway start    # 啟動
openclaw gateway stop     # 停止
openclaw gateway restart  # 重啟
```

---

## 🎯 推薦設定

### 給一般使用者

**使用模式 1（完全自動）**

```
每次使用：
雙擊「啟動 Dashboard.command」
→ 自動處理一切
→ 無需擔心 Gateway
```

**優點：**
- ✅ 簡單易用
- ✅ 自動管理
- ✅ 用完即關

### 給重度使用者

**使用模式 2（開機自動啟動）**

```
設定一次：
雙擊「檢查並啟動 Gateway.command」
→ 啟用開機自動啟動

之後：
開機後 Gateway 自動運行
Dashboard 隨時可用
Telegram Bot 隨時響應
```

**優點：**
- ✅ 永久運行
- ✅ 無需手動啟動
- ✅ 最佳響應速度

---

## 🔍 如何檢查 Gateway 狀態？

### 方法一：使用圖形化工具 ⭐

```bash
雙擊「檢查並啟動 Gateway.command」
```

**會顯示：**
- ✅ Gateway 運行狀態
- 📍 進程 PID
- 🔗 Control UI 連結
- ⚙️ 快速操作選項

### 方法二：Dashboard 介面

```
開啟 Dashboard
→ 查看頂部控制面板
→ 看到「Gateway 狀態」指示

🟢 綠色 = 運行中
🔴 紅色 = 未運行
```

### 方法三：終端機命令

```bash
# 檢查進程
pgrep -f "openclaw-gateway"

# 如果顯示數字 = 運行中
# 如果沒輸出 = 未運行

# 或使用 OpenClaw 命令（可能慢）
openclaw status
```

---

## 🛠️ 常見操作

### 啟動 Gateway

```bash
# 方法一：圖形化（推薦）
雙擊「檢查並啟動 Gateway.command」

# 方法二：Dashboard 自動啟動
雙擊「啟動 Dashboard.command」

# 方法三：終端機
openclaw gateway start
```

### 停止 Gateway

```bash
# 方法一：終端機
openclaw gateway stop

# 方法二：強制終止
pkill -f "openclaw-gateway"
```

### 重啟 Gateway

```bash
# 方法一：圖形化
雙擊「檢查並啟動 Gateway.command」
→ 選擇「重啟」

# 方法二：終端機
openclaw gateway restart

# 方法三：手動
openclaw gateway stop
sleep 2
openclaw gateway start
```

### 查看日誌

```bash
openclaw logs

# 或即時監控
openclaw logs --follow
```

---

## ⚙️ Gateway 設定

### 配置文件位置

```
~/.openclaw/openclaw.json
```

### 重要設定

```json
{
  "gateway": {
    "port": 18788,           // WebSocket 端口
    "controlUi": {
      "enabled": true,       // 啟用 Control UI
      "port": 18789         // Control UI 端口
    }
  }
}
```

### Control UI 訪問

```
http://localhost:18789
```

**功能：**
- 📊 即時監控
- 🔄 模型切換
- 📝 查看日誌
- ⚙️ 配置設定

---

## 🐛 常見問題

### Q1: Gateway 啟動失敗？

**可能原因：**
```
1. 端口被佔用
2. OpenClaw 配置不完整
3. 權限問題
```

**解決方案：**
```bash
# 1. 檢查端口
lsof -i :18788
lsof -i :18789

# 2. 重新配置
openclaw configure

# 3. 查看詳細錯誤
openclaw logs
```

### Q2: Gateway 運行但 Dashboard 偵測不到？

**檢查步驟：**
```bash
# 1. 確認進程存在
pgrep -f "openclaw-gateway"

# 2. 確認端口監聽
lsof -i :18788

# 3. 測試連接
curl http://localhost:18789
```

### Q3: Dashboard 不啟動 Gateway？

**原因：**
```
啟動器可能遇到錯誤
```

**解決：**
```bash
# 手動啟動 Gateway
openclaw gateway start

# 或使用管理工具
雙擊「檢查並啟動 Gateway.command」
```

### Q4: 要不要設定開機自動啟動？

**建議：**

```
如果您：
✅ 經常使用 OpenClaw
✅ 想要 Telegram Bot 隨時響應
✅ 不在意背景常駐

→ 建議啟用開機自動啟動

如果您：
✅ 偶爾使用
✅ 想節省系統資源
✅ 喜歡手動控制

→ 使用 Dashboard 自動啟動即可
```

---

## 📊 資源佔用

### Gateway 運行時

```
記憶體：~50-100 MB
CPU：<1%（閒置時）
端口：18788, 18789
```

**影響：**
- ✅ 資源佔用極低
- ✅ 幾乎無感
- ✅ 可放心常駐

---

## 🎯 最佳實踐

### 日常使用

```
1. 雙擊「啟動 Dashboard.command」
   → Gateway 自動啟動（如需要）

2. 使用 Dashboard 監控和切換模型

3. 用完關閉 Dashboard
   → Gateway 保持運行（不影響）

4. 如需停止 Gateway：
   openclaw gateway stop
```

### 重度使用

```
1. 一次性設定：
   雙擊「檢查並啟動 Gateway.command」
   → 啟用開機自動啟動

2. 重啟電腦
   → Gateway 自動運行

3. 隨時使用 Dashboard
   → 無需等待啟動

4. 如需停用：
   雙擊「檢查並啟動 Gateway.command」
   → 停用開機自動啟動
```

---

## 📋 快速參考

### 常用命令

```bash
# 啟動
openclaw gateway start

# 停止
openclaw gateway stop

# 重啟
openclaw gateway restart

# 狀態
openclaw status

# 日誌
openclaw logs

# 安裝為系統服務
openclaw gateway install

# 卸載系統服務
openclaw gateway uninstall
```

### 檢查命令

```bash
# 檢查進程
pgrep -f "openclaw-gateway"

# 檢查端口
lsof -i :18788
lsof -i :18789

# 檢查配置
cat ~/.openclaw/openclaw.json | grep gateway
```

---

## 🎉 總結

### Dashboard 會自動處理 Gateway ✅

```
現在的行為：
1. 雙擊「啟動 Dashboard.command」
2. 自動檢測 Gateway
3. 如果未運行 → 自動啟動
4. 如果已運行 → 繼續使用
5. ✅ 無需手動管理
```

### 您可以選擇

```
✅ 完全交給 Dashboard 自動處理（推薦）
✅ 設定開機自動啟動（重度使用）
✅ 手動控制啟動停止（進階使用）
```

### 工具一覽

```
📱 啟動 Dashboard.command
   → 自動啟動 Gateway（如需要）

🔧 檢查並啟動 Gateway.command
   → 完整 Gateway 管理工具

🐛 故障排除.command
   → 診斷和修復所有問題
```

---

**現在您不用擔心 Gateway 了！Dashboard 會自動處理一切！** ✨🚀
