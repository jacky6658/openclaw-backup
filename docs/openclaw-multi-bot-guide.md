# 🦞 OpenClaw 多 Bot 分身設定指南

在同一台機器上運行多個 Telegram Bot，共用同一個 OpenClaw Gateway。

## 目錄

- [前置條件](#前置條件)
- [步驟一：創建額外的 Bot](#步驟一創建額外的-bot)
- [步驟二：修改 OpenClaw 配置](#步驟二修改-openclaw-配置)
- [步驟三：重啟 Gateway](#步驟三重啟-gateway)
- [步驟四：確認狀態](#步驟四確認狀態)
- [步驟五：設定身份判斷（可選）](#步驟五設定身份判斷可選)
- [架構說明](#架構說明)
- [注意事項](#注意事項)
- [常見問題](#常見問題)

---

## 前置條件

- ✅ 已安裝 OpenClaw 並有一個運作中的 Telegram bot
- ✅ 擁有 Telegram 帳號
- ✅ 了解基本的 JSON 配置編輯

## 步驟一：創建額外的 Bot

1. 在 Telegram 開啟 [@BotFather](https://t.me/BotFather)
2. 發送 `/newbot`
3. 依照指示設定 bot 名稱和 username
4. 複製取得的 **Bot Token**（格式如：`1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`）

## 步驟二：修改 OpenClaw 配置

編輯 `~/.openclaw/openclaw.json`，在 `channels.telegram.accounts` 區塊加入新的 bot：

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": "主要bot的token（可選，作為預設）",
      "allowFrom": ["你的telegram_user_id"],
      "accounts": {
        "bot1": {
          "dmPolicy": "allowlist",
          "botToken": "第一個bot的token",
          "allowFrom": ["你的telegram_user_id"],
          "groupPolicy": "allowlist",
          "streamMode": "partial"
        },
        "bot2": {
          "dmPolicy": "allowlist",
          "botToken": "第二個bot的token",
          "allowFrom": ["你的telegram_user_id"],
          "groupPolicy": "allowlist",
          "streamMode": "partial"
        }
      }
    }
  }
}
```

### 配置說明

| 欄位 | 說明 |
|------|------|
| `botToken` | 從 BotFather 取得的 token |
| `dmPolicy` | DM 政策：`allowlist`（白名單）、`open`（開放） |
| `allowFrom` | 允許的 Telegram user ID 列表 |
| `groupPolicy` | 群組政策：`allowlist`、`open` |
| `streamMode` | 串流模式：`partial`、`full`、`off` |

### 取得你的 Telegram User ID

1. 在 Telegram 開啟 [@userinfobot](https://t.me/userinfobot)
2. 發送任意訊息
3. 複製回覆中的 `Id` 數字

## 步驟三：重啟 Gateway

```bash
openclaw gateway restart
```

或者如果需要完全重啟：

```bash
openclaw gateway stop
openclaw gateway start
```

## 步驟四：確認狀態

```bash
openclaw status
```

成功的話會看到：

```
│ Telegram │ ON │ OK │ token config×2 (...) · accounts 2/2 │
```

`accounts 2/2` 表示配置了 2 個 bot，2 個都成功連接。

## 步驟五：設定身份判斷（可選）

如果希望每個 bot 有不同的身份認知，可以在 workspace 的 `IDENTITY.md` 或 `SOUL.md` 加入判斷邏輯：

```markdown
## 身份判斷規則

根據 accountId 判斷身份：

| accountId | Bot | 身份 |
|-----------|-----|------|
| `bot1` | @YourBot1 | 主要助理 |
| `bot2` | @YourBot2 | HR 助理 |

查看 Runtime 資訊中的 `accountId` 來判斷當前身份。
```

Bot 可以在回覆時檢查 `deliveryContext.accountId` 來知道自己是哪個分身。

---

## 架構說明

```
┌─────────────────────────────────────────────────┐
│                 OpenClaw Gateway                │
│                   (單一實例)                     │
├─────────────────────────────────────────────────┤
│  ┌─────────────┐        ┌─────────────┐        │
│  │   Bot 1     │        │   Bot 2     │        │
│  │ @YourBot1   │        │ @YourBot2   │        │
│  │ accountId:  │        │ accountId:  │        │
│  │   "bot1"    │        │   "bot2"    │        │
│  └──────┬──────┘        └──────┬──────┘        │
│         │                      │               │
│         └──────────┬───────────┘               │
│                    │                           │
│         ┌──────────▼──────────┐               │
│         │   共用資源           │               │
│         │  • Workspace        │               │
│         │  • Memory files     │               │
│         │  • API 額度         │               │
│         │  • Skills           │               │
│         └─────────────────────┘               │
└─────────────────────────────────────────────────┘
```

## 注意事項

| 項目 | 說明 |
|------|------|
| **共用** | 同一個 Gateway、workspace、API 額度、記憶檔案 |
| **獨立** | 各自的對話 session、對話歷史 |
| **排隊** | 訊息會排隊處理（預設 maxConcurrent: 4） |
| **成本** | 多 bot 不會增加額外費用，只看實際 API 用量 |
| **同群組** | 兩個 bot 在同一群組可能會同時回覆，需注意設定 |

### 效能考量

- 輕量任務（聊天、簡單查詢）：幾乎不影響
- 重度任務（長時間腳本、大量 API 調用）：可能需要排隊等待

### 群組使用建議

如果要將多個 bot 加入同一個群組：

1. **分工明確** - 設定只有被 @mention 才回覆
2. **避免衝突** - 不同 bot 負責不同類型的問題
3. **或分開群組** - 各自管理不同的群組

## 常見問題

### Q: 為什麼只有一個 bot 連接成功？

檢查：
1. Bot token 是否正確
2. Bot token 是否被其他程序使用（409 Conflict）
3. 使用 `openclaw logs` 查看錯誤訊息

### Q: 兩個 bot 都說自己是同一個身份？

因為共用 workspace，需要在 `IDENTITY.md` 設定身份判斷邏輯，讓 bot 根據 `accountId` 判斷自己是誰。

### Q: 可以加幾個 bot？

技術上沒有限制，但建議：
- 考慮 API 額度分配
- 考慮處理能力（maxConcurrent 設定）
- 每個 bot 有明確分工

### Q: 如何讓不同 bot 用不同模型？

在各自的對話 session 中使用 `/model` 指令設定，或在對話開頭指定模型。

---

## 相關資源

- [OpenClaw 官方文檔](https://docs.openclaw.ai)
- [OpenClaw GitHub](https://github.com/anthropics/openclaw)
- [Telegram BotFather](https://t.me/BotFather)

---

*最後更新：2026-02-09*
