# YQ2 (HR YuQi) Commands Handler

## Bot 資訊
- **Bot**: @HRyuqi_bot
- **AccountId**: yuqi2
- **群組**: HR AI招募自動化 (-1003231629634)

## 指令列表

### /jd - 顯示職缺管理面板
**觸發條件**: 訊息內容為 `/jd`
**執行動作**: 使用 `message` tool 發送帶按鈕的面板

```json
{
  "action": "send",
  "channel": "telegram",
  "target": "-1003231629634",
  "message": "📋 **Step1ne JD 管理系統**\n\n請選擇操作：",
  "buttons": [[
    {"text":"📋 列出所有職缺","callback_data":"jd:list"}
  ],[
    {"text":"🔍 搜尋 - 工程師","callback_data":"jd:search:工程師"},
    {"text":"🔍 搜尋 - AI","callback_data":"jd:search:AI"}
  ],[
    {"text":"📊 統計報表","callback_data":"jd:stats"},
    {"text":"🔄 重新整理","callback_data":"jd:refresh"}
  ]]
}
```

---

### /list - 列出所有職缺
**觸發條件**: 訊息內容為 `/list`
**執行動作**: 執行腳本並回覆結果

```bash
bash /Users/user/clawd/hr-tools/jd-bot-handler.sh "列出職缺"
```

---

### /search [關鍵字] - 搜尋職缺
**觸發條件**: 訊息內容以 `/search` 開頭
**執行動作**: 提取關鍵字並執行搜尋

```bash
# 提取關鍵字
KEYWORD=$(echo "$MESSAGE" | sed 's/^\/search //')

# 執行搜尋
bash /Users/user/clawd/hr-tools/jd-bot-handler.sh "搜尋職缺" "$KEYWORD"
```

**範例**:
- `/search 工程師` → 搜尋包含「工程師」的職缺
- `/search AI` → 搜尋包含「AI」的職缺
- `/search Python` → 搜尋包含「Python」的職缺

**無關鍵字處理**:
如果只輸入 `/search` 沒有關鍵字，回覆：
```
🔍 **搜尋職缺**

請提供搜尋關鍵字：

**用法**：
`/search [關鍵字]`

**範例**：
• `/search 工程師`
• `/search AI`
• `/search Python`
```

---

### /stats - 職缺統計報表
**觸發條件**: 訊息內容為 `/stats`
**執行動作**: 執行腳本並回覆結果

```bash
bash /Users/user/clawd/hr-tools/jd-bot-handler.sh "JD統計"
```

---

### /help - HR 幫助資訊
**觸發條件**: 訊息內容為 `/help`
**執行動作**: 回覆 HR YuQi 的使用說明

```
🦞 **HR YuQi 使用說明**

**職缺管理**：
• `/jd` - 顯示職缺管理面板
• `/list` - 列出所有職缺
• `/search [關鍵字]` - 搜尋職缺
• `/stats` - 職缺統計報表

**履歷處理**：
• 上傳履歷到 Topic 4 → 自動匹配
• 每小時自動檢查新履歷

**BD 開發**：
• Topic 364 觸發自動開發
• 每天 09:30 + 14:30 自動發信

**需要幫助？**
@YuQi 或直接詢問問題
```

---

## Callback 處理

當用戶點擊按鈕時，會收到 callback_data：

### jd:list
執行：`bash /Users/user/clawd/hr-tools/jd-bot-handler.sh "列出職缺"`

### jd:search:[關鍵字]
提取關鍵字並執行：`bash /Users/user/clawd/hr-tools/jd-bot-handler.sh "搜尋職缺" "[關鍵字]"`

### jd:stats
執行：`bash /Users/user/clawd/hr-tools/jd-bot-handler.sh "JD統計"`

### jd:refresh
重新發送 `/jd` 面板

---

## 實作邏輯

在主 session 中監聽訊息：
1. 檢查 accountId 是否為 `yuqi2`
2. 檢查訊息是否為上述指令
3. 執行對應動作
4. 使用 `message` tool 回覆結果到群組

**偽代碼**：
```javascript
if (accountId === 'yuqi2' && chatId === '-1003231629634') {
  if (message === '/jd') {
    // 發送按鈕面板
    sendButtonPanel();
  } else if (message === '/list') {
    // 執行列出職缺
    const result = exec('bash jd-bot-handler.sh "列出職缺"');
    reply(result);
  } else if (message.startsWith('/search ')) {
    // 執行搜尋
    const keyword = message.replace('/search ', '');
    const result = exec(`bash jd-bot-handler.sh "搜尋職缺" "${keyword}"`);
    reply(result);
  } else if (message === '/stats') {
    // 執行統計
    const result = exec('bash jd-bot-handler.sh "JD統計"');
    reply(result);
  }
}
```
