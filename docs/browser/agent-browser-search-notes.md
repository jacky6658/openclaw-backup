# agent-browser + Google Search 限制備註

> 紀錄在這台機器上實測的結果，給未來的 AI 助理參考。

## 1. 實測結果摘要

- 使用 `agent-browser open https://www.google.com` 可以正常開啟 Google 首頁。
- 使用 `agent-browser snapshot -i --json` 可以抓到搜尋欄位（`combobox "搜尋" [ref=e7]` 等）。
- 嘗試：
  ```bash
  agent-browser fill @e7 "(G)I-DLE 台灣 KKTIX"
  agent-browser press Enter
  agent-browser wait --load networkidle
  agent-browser snapshot -i --json
  ```
  回傳的 snapshot 只有：
  ```text
  - link "Why did this happen?" [ref=e1]
  ```
  代表被 Google 的防機器人頁面擋住（常見是 ReCAPTCHA / "unusual traffic"）。

## 2. 結論

- 在目前這個環境，**直接用 agent-browser 操控 Google 搜尋結果是不穩定的**：
  - 很容易被 Google 判定為機器人流量，導到「Why did this happen?」頁面。
  - 無法保證穩定取得搜尋結果列表。

## 3. 給老闆看的說明（人話版）

> 這段是要講給老闆聽的，不是技術細節：

- 「我可以幫你在網站上自動點按鈕、填表、抓資料，但是 Google 本身會擋機器人。
   所以『找網站』這件事，會比較適合你用手機或平常的瀏覽器先查好，再把網址丟給我。
   我再幫你處理後面那些無聊的重複動作。」
- 「簡單說：
   - 找網址／找活動 → 你用平常的 Google 搜尋；
   - 進網站後要操作很多步驟 → 換我來幫你按。」

在啟用 Browser Automation（特別是訂位／訂票）技能時，要先用這種人話跟老闆說明一次，讓他知道限制和分工方式。

## 4. 建議做法

1. **把「搜尋」與「網站操作」拆開**：
   - 讓老闆用一般瀏覽器／手機上的 Google 搜尋找到目標網站（例如 KKTIX 活動頁）。
   - 老闆把該網站 URL 貼給 AI 助理。
   - AI 再用 `agent-browser open <那個 URL>` 來處理後續（看票、整理資訊、協助填表）。

2. **搜尋引擎查資料優先用 API 工具（web_search）**：
   - 若已設定 Brave API key，能用 `web_search` 做文字搜尋與摘要。  
   - `agent-browser` 則專心用在「登入／填表／操作網站」，而不是拿來當一般搜尋引擎。

3. **不要跟 Google 的風控硬拼**：
   - 避免設計需要長期依賴「agent-browser + Google Search」的流程。  
   - 對於需要穩定搜尋的場景，優先考慮：
     - Brave API / 其他搜尋 API  
     - 或讓使用者先貼目標網站 URL。

這份備註會放在 `docs/browser/agent-browser-search-notes.md`，
未來任何 AI 助理在設計 Browser Automation 流程時，都要先參考這些限制。