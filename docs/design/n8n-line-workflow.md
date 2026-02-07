# n8n LINE ↔ Clawdbot Workflow

## 架構
```
LINE App → LINE Platform → n8n Webhook → Clawdbot API → n8n → LINE Reply API
```

## n8n Workflow 設定

### Node 1: Webhook (觸發器)
- **Type**: Webhook
- **HTTP Method**: POST
- **Path**: `39333e40-ceb1-4c5a-9bb5-08deb87e29a3`（你現有的）

---

### Node 2: 解析 LINE 訊息
- **Type**: Code (JavaScript)
```javascript
// 取得 LINE 訊息內容
const body = $input.first().json.body || $input.first().json;
const events = body.events || [];

if (events.length === 0) {
  return [{ json: { skip: true } }];
}

const event = events[0];
const messageType = event.type;

if (messageType !== 'message' || event.message.type !== 'text') {
  return [{ json: { skip: true } }];
}

return [{
  json: {
    replyToken: event.replyToken,
    userId: event.source.userId,
    groupId: event.source.groupId || null,
    text: event.message.text,
    timestamp: event.timestamp
  }
}];
```

---

### Node 3: IF (過濾非文字訊息)
- **Type**: IF
- **Condition**: `{{ $json.skip }}` is not true

---

### Node 4: HTTP Request (呼叫 Clawdbot)
- **Type**: HTTP Request
- **Method**: POST
- **URL**: `https://listed-footwear-marina-george.trycloudflare.com/v1/chat/completions`
- **Authentication**: None (用 Header)
- **Headers**:
  - `Authorization`: `Bearer b2a08c1a3e70e75f03ecb1404e41da32b5eca2e51545e380`
  - `Content-Type`: `application/json`
- **Body (JSON)**:
```json
{
  "model": "sonnet",
  "messages": [
    {
      "role": "user",
      "content": "{{ $json.text }}"
    }
  ]
}
```

---

### Node 5: 解析 Clawdbot 回覆
- **Type**: Code (JavaScript)
```javascript
const response = $input.first().json;
const replyToken = $('解析 LINE 訊息').first().json.replyToken;

let replyText = '';
if (response.choices && response.choices[0]) {
  replyText = response.choices[0].message.content;
} else {
  replyText = '抱歉，我暫時無法回覆。';
}

return [{
  json: {
    replyToken: replyToken,
    replyText: replyText
  }
}];
```

---

### Node 6: HTTP Request (回覆 LINE)
- **Type**: HTTP Request
- **Method**: POST
- **URL**: `https://api.line.me/v2/bot/message/reply`
- **Headers**:
  - `Authorization`: `Bearer iQ6SFlF0D/gqU+/Kop1R9A+ylVtNffReVaxqV7Ca5IHydykYcBPFSKbOFyyTS05Ttrl4UyFgLd0qbiIQTJMRu//LCda6UnZbDYDKriRPfxzCZgybDSDustr2fa347u+b3KF2BPYqtd6/zF1VKULG9wdB04t89/1O/w1cDnyilFU=`
  - `Content-Type`: `application/json`
- **Body (JSON)**:
```json
{
  "replyToken": "{{ $json.replyToken }}",
  "messages": [
    {
      "type": "text",
      "text": "{{ $json.replyText }}"
    }
  ]
}
```

---

## 注意事項

1. **Cloudflare Tunnel URL 會變**：每次重啟 `cloudflared tunnel` URL 都會換，需要更新 n8n
2. **LINE Webhook 驗證**：目前沒做簽名驗證，正式環境應加上
3. **群組訊息**：`groupId` 有值時代表是群組訊息

---

## 測試步驟

1. 在 n8n 建立並啟用 workflow
2. 在 LINE 加 Bot 好友（掃 QR code）
3. 發一則訊息給 Bot
4. 看 n8n 執行紀錄確認流程

---

*Created: 2026-02-02*
