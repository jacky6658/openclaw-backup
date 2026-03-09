# Telegram Bot Commands 設定步驟

## 📋 要設定的指令

### @YuQi0923_bot 的指令
```
jd - 顯示職缺管理面板
list - 列出所有職缺
search - 搜尋職缺
stats - 職缺統計報表
help - 顯示幫助資訊
```

---

## 🔧 設定步驟（透過 BotFather）

### 1. 打開 Telegram，找到 @BotFather

### 2. 輸入指令
```
/setcommands
```

### 3. 選擇你的 Bot
點選 `@YuQi0923_bot`

### 4. 貼上以下指令列表
```
jd - 顯示職缺管理面板
list - 列出所有職缺
search - 搜尋職缺
stats - 職缺統計報表
help - 顯示幫助資訊
```

### 5. 完成！
BotFather 會回覆：
```
Success! Command list updated.
```

---

## 📱 使用方式

設定完成後，在群組中：
1. 輸入 `/` 會自動顯示指令列表
2. 點選或輸入 `/jd` → 顯示按鈕面板
3. 點選或輸入 `/list` → 列出所有職缺
4. 點選或輸入 `/search 工程師` → 搜尋職缺
5. 點選或輸入 `/stats` → 統計報表

---

## 🎯 指令處理邏輯

在 AGENTS.md 中已設定：
- 當收到以 `/jd`, `/list`, `/search`, `/stats` 開頭的訊息
- 自動執行對應的 jd-bot-handler.sh 指令
- 回覆結果到群組

---

## 🔄 更新指令（如需修改）

1. 再次輸入 `/setcommands` 給 @BotFather
2. 選擇 Bot
3. 貼上新的指令列表
4. 舊的會被覆蓋

---

## 📝 建議的完整指令列表

```
jd - 📋 顯示職缺管理面板
list - 📋 列出所有職缺
search - 🔍 搜尋職缺
stats - 📊 職缺統計報表
help - ❓ 顯示幫助資訊
status - 📊 查看系統狀態
```

---

## ⚠️ 注意事項

- Bot Commands 只能由 Bot 管理員透過 BotFather 設定
- 設定後會在所有使用該 Bot 的群組/私聊中生效
- 指令列表會在輸入 `/` 時自動彈出
- 每個 Bot 最多可設定 100 個指令
