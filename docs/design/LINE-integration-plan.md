# LINE 平台接入規劃

## 一、使用情境 ✅ 已確認

**目標：LINE 私域社群互動**
- [x] **群組協作**：AI 參與 LINE 群組/社群討論
- [x] **雙向通訊**：接收群組訊息 + 回覆
- [ ] 個人助理：一對一（次要，可選）

### 私域社群特點
- 封閉群組，成員固定
- AI 作為群組成員之一參與討論
- 類似 Telegram 群組的 AI 互動模式

---

## 二、技術選項比較

### 方案 A：LINE Messaging API（推薦）
**適合：完整雙向對話**

| 項目 | 說明 |
|-----|------|
| 功能 | 接收/發送訊息、群組、圖片、按鈕 |
| 費用 | 免費版 500 則/月，超過要付費 |
| 需求 | LINE Developers 帳號、Webhook URL |
| 複雜度 | 中等 |

**架構：**
```
LINE App → LINE Platform → Webhook → Clawdbot Gateway → AI
                                  ← HTTP Response ←
```

### 方案 B：LINE Notify
**適合：只需要 AI → 用戶的單向通知**

| 項目 | 說明 |
|-----|------|
| 功能 | 只能發通知，不能收訊息 |
| 費用 | 免費 |
| 需求 | LINE Notify Token |
| 複雜度 | 低 |

❌ 不適合對話場景

### 方案 C：自建 LINE Bot + 外部 Webhook 服務
**適合：沒有公網 IP 的情況**

| 項目 | 說明 |
|-----|------|
| 工具 | ngrok / Cloudflare Tunnel / fly.io |
| 功能 | 完整雙向對話 |
| 費用 | 看服務（ngrok 免費版有限制） |
| 複雜度 | 較高 |

---

## 三、Clawdbot 接入方式

### 選項 1：開發 LINE Channel Plugin（推薦）
類似現有的 Telegram、Discord plugin

**需要開發：**
- `packages/channel-line/` — 新 channel plugin
- 處理 LINE Webhook 驗證（X-Line-Signature）
- 轉換 LINE 訊息格式 → Clawdbot 內部格式
- 支援文字、圖片、按鈕等

**優點：**
- 原生整合，跟 Telegram 一樣的體驗
- 支援所有 Clawdbot 功能（reactions、inline buttons...）

**缺點：**
- 需要開發時間

### 選項 2：用外部橋接服務
用 n8n / Make / 自寫腳本橋接

**架構：**
```
LINE → 外部服務 → HTTP POST → Clawdbot API
```

**優點：**
- 不用改 Clawdbot 程式碼

**缺點：**
- 多一層依賴
- 功能受限

---

## 四、LINE Bot 設定步驟（方案 A）

### 1. 建立 LINE Developers 帳號
https://developers.line.biz/

### 2. 建立 Messaging API Channel
- 進入 Console → Create Provider → Create Channel
- 選擇 Messaging API

### 3. 取得憑證
- **Channel ID**
- **Channel Secret**
- **Channel Access Token**（長期）

### 4. 設定 Webhook URL
- 需要公網可存取的 HTTPS URL
- 格式：`https://your-domain.com/webhook/line`

### 5. 關閉自動回覆
- 在 LINE Official Account Manager 關閉「自動回應訊息」
- 否則會跟 AI 回覆打架

---

## 五、執行計畫

### Phase 1：快速驗證（今天）
用 n8n 或簡單腳本橋接，驗證 LINE ↔ Clawdbot 可行性

**步驟：**
1. [ ] 註冊 LINE Developers 帳號
2. [ ] 建立 Messaging API Channel
3. [ ] 取得 Channel Secret + Access Token
4. [ ] 設定 ngrok 或 Cloudflare Tunnel 暴露本機
5. [ ] 寫簡單 Webhook 腳本接收 LINE 訊息 → 轉發給 Clawdbot
6. [ ] 測試：LINE 群組發訊息 → AI 回覆

**預估時間：1-2 小時**

---

### Phase 2：完整 Plugin 開發
開發 `channel-line` 讓 Clawdbot 原生支援 LINE

**開發項目：**
1. [ ] 建立 `packages/channel-line/` 專案結構
2. [ ] 實作 LINE Webhook 驗證（X-Line-Signature）
3. [ ] 訊息格式轉換（LINE ↔ Clawdbot）
4. [ ] 支援功能：
   - [ ] 文字訊息
   - [ ] 圖片訊息
   - [ ] 群組訊息
   - [ ] @mention 偵測
   - [ ] Reply 回覆
5. [ ] 整合到 clawdbot.json 設定
6. [ ] 測試 + 文件

**預估時間：1-2 天**

---

## 六、LINE Developers 註冊步驟

### Step 1：建立帳號
1. 前往 https://developers.line.biz/
2. 用你的 LINE 帳號登入
3. 同意開發者條款

### Step 2：建立 Provider
1. 點擊「Create」
2. 輸入 Provider 名稱（例如：AIJob）
3. 確認建立

### Step 3：建立 Messaging API Channel
1. 在 Provider 下點「Create a new channel」
2. 選擇「Messaging API」
3. 填寫：
   - Channel name：你的 Bot 名稱
   - Channel description：描述
   - Category：選一個
   - Subcategory：選一個
4. 同意條款 → Create

### Step 4：取得憑證
在 Channel 頁面找到：
- **Basic settings**：
  - Channel ID
  - Channel secret
- **Messaging API**：
  - Channel access token（點 Issue 產生）

### Step 5：設定 Webhook
1. 在 Messaging API 頁面
2. Webhook URL：填入你的公網 URL
3. 開啟「Use webhook」
4. 關閉「Auto-reply messages」
5. 關閉「Greeting messages」

### Step 6：加入群組
1. 在 LINE app 掃描 Bot 的 QR code 加好友
2. 把 Bot 邀請進你的私域群組

## 七、LINE 群組類型比較

| 類型 | 人數上限 | Bot 支援 | 適合場景 |
|-----|---------|---------|---------|
| **LINE 群組** | 500 人 | ✅ 可加入 | 小型私密社群 |
| **LINE 社群 (OpenChat)** | 5000 人 | ⚠️ 限制較多 | 大型開放社群 |
| **LINE 官方帳號** | 無限 | ✅ 完整 API | 品牌/客服 |

### 群組 Bot 注意事項
1. **加入方式**：需要群組管理員邀請 Bot 加入
2. **訊息接收**：Bot 可以收到所有群組訊息
3. **回覆策略**：需設計「什麼時候該回、什麼時候安靜」
4. **@mention**：LINE 群組支援 @提及，可用來觸發 Bot

---

*Created: 2026-02-02*
