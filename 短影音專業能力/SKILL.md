---
name: short-video-pro
version: 1.0.0
description: 以短影音知識庫產出可直接拍攝的腳本、標題、Hook、CTA，並輸出結構化 JSON。適用於 Reels/TikTok/小紅書。
---

# 短影音專業能力（Skill）

## 目標
- 依目標（流量 / 轉換 / 信任）產出短影音腳本
- 產出：標題、Hook、Value（≤3 點）、CTA、拍攝/剪輯提示
- 提供「Q&A Flow」蒐集需求並輸出 JSON
- 可獨立完成「帳號定位、選題、腳本」

## 核心規則（摘要）
- 影片目的先行：流量型 vs 轉換型
- 開場 0–5 秒必須直給結論 + 大字卡 + 快切
- 結構優先：Hook → Value → CTA
- Value 段 ≤ 3 點，CTA 只給 1 個明確動作
- 口語、短句、節奏快，避免口頭禪

## 輸入
- 主題/產品
- 目標（流量/教育/信任/轉單/品牌）
- 受眾（年齡/性別/特質/痛點）
- 可用素材（Before/After/專家/素人/日常/B-roll/截圖）
- 鉤子類型（問句/反差/同理/數字）
- CTA 類型（關注/收藏/留言/私訊/購買）
- 是否允許趨勢搜尋/熱點參考（預設允許）

## 輸出（JSON）
```json
{
  "segments":[
    {"type":"hook","start_sec":0,"end_sec":5,"camera":"CU","dialog":"...","visual":"...","cta":""},
    {"type":"value","start_sec":5,"end_sec":25,"camera":"MS","dialog":"...","visual":"...","cta":""},
    {"type":"cta","start_sec":25,"end_sec":30,"camera":"WS","dialog":"...","visual":"...","cta":"..."}
  ]
}
```

## 產出格式（人類可讀）
- 標題
- Hook（0–5s）
- Value（最多三點）
- CTA（單一步驟）
- 拍攝/剪輯建議

## 平台注意
- Reels：自然生活化、強情緒
- TikTok：節奏更快、梗感強
- 小紅書：畫面乾淨、字幕精修
