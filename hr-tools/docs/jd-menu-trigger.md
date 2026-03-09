# JD 菜單觸發指令

## 觸發關鍵字
- `JD菜單`
- `/jd`
- `jd菜單`
- `職缺菜單`

## 回應內容

當檢測到上述關鍵字時，發送以下帶按鈕的訊息：

```
📋 **Step1ne JD 管理系統**

請選擇操作：
```

## 按鈕配置

```json
[
  [{"text":"📋 列出所有職缺","callback_data":"jd:list"}],
  [
    {"text":"🔍 搜尋 - 工程師","callback_data":"jd:search:工程師"},
    {"text":"🔍 搜尋 - AI","callback_data":"jd:search:AI"}
  ],
  [
    {"text":"📊 統計報表","callback_data":"jd:stats"},
    {"text":"🔄 重新整理","callback_data":"jd:refresh"}
  ]
]
```

## Callback 處理

### jd:list
執行：`bash /Users/user/clawd/hr-tools/jd-bot-handler.sh "列出職缺"`

### jd:search:[關鍵字]
執行：`bash /Users/user/clawd/hr-tools/jd-bot-handler.sh "搜尋職缺" "[關鍵字]"`

### jd:stats
執行：`bash /Users/user/clawd/hr-tools/jd-bot-handler.sh "JD統計"`

### jd:refresh
重新發送按鈕菜單

## 實作位置

在主 session 的群組訊息監聽中：
1. 檢測訊息內容是否包含觸發關鍵字
2. 若符合，使用 `message` tool 發送帶按鈕的訊息
3. 監聽 callback_data，執行對應指令並回覆
