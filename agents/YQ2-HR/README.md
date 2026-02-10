# YQ2 HR 工作區

**身份**：HR YuQi
**Bot**：@HRyuqi_bot
**模型**：Gemini 3 Pro
**職責**：接案管理、客戶開發、行政作業、學員服務

## 工作內容

- 案件管理（aijobcase API）
- 進度提醒
- 客戶開發信
- 行政作業（報價、合約、發票提醒）
- 成本/利潤記錄
- 學員服務

## API 端點

```
後端 URL：https://aijobcasebackend.zeabur.app

POST /api/ai/import     → 新增案件
GET  /api/ai/leads      → 查詢案件
POST /api/ai/update     → 更新案件
POST /api/ai/progress   → 更新進度
POST /api/ai/cost       → 記錄成本
POST /api/ai/profit     → 記錄利潤
```

## 相關檔案

此資料夾存放 YQ2 專屬的工作檔案。
