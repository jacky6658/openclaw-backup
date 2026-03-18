# 歷史教訓與已完成任務存檔

> 從 MEMORY.md 搬移過來，保留查閱用途，不每次載入。

---

## GitHub 人選搜尋系統完成（2026-02-25）✅

- GitHub 搜尋正常（Token：ghp_U4p9...）
- 統一搜尋腳本：`/Users/user/clawd/hr-tools/unified-talent-search-v3.py`
- LinkedIn 暫時跳過（反爬蟲困難）

---

## Step1ne AI 配對修復（2026-02-24）✅

- 問題：Zeabur 找不到 Python 腳本
- 解決：複製到專案內 `server/persona-matching/`
- Commit：380ee23

---

## Step1ne Zeabur 部署修復（2026-02-24）✅

- 問題：Zeabur 沒有 gog CLI
- 解決：新增 sheetsService-csv.js（公開 CSV export）
- Commit：7f3cdbe

---

## Step1ne API 開發完成（2026-02-24）✅

- 完成：匿名履歷 API + Jobs/Candidates CRUD（共 6 個新端點）
- API 總數：19 個端點
- Commits：6dd9901, 8bcc7ea, 199ca1f, bb9955e

---

## Step1ne 系統架構修復（2026-02-24）✅

- 修復前端 localhost 硬編碼 → 自動偵測環境
- 修復後端 CSV export 失敗
- Commits：134b744, c5c66d7

---

## GitHub 技能推論系統設計（2026-02-17）

**實現檔案**：`/Users/user/clawd/hr-tools/github-talent-search.py`

核心邏輯（3層技能提取）：
1. 生物訊息層：從 bio 抽取技能關鍵字
2. 代碼語言層：Top 10 repos languages → 技能映射
3. 元資訊層：Repo description + topics 關鍵字搜尋

API 速率：60 req/hr 免認證；用 GitHub PAT 升至 5000/hr

---

## 災難性資料損壞事件（2026-02-14）

- 事件：履歷池 240 行資料格式全壞（newline 字元未清理）
- 教訓：匯入前必清理 `\n`、測試 1 筆、驗證欄位數、確認後才批量

---

## Sub-agent 資料遺失風險（2026-02-13）

- 問題：sub-agent 回報「完成」但不存檔
- 強制規則：大任務完成後必須驗證檔案存在

---

## Google Sheets 換行符號問題（2026-02-13）

- `\n` 會被 gog sheets append 當成新一行 → 欄位錯位
- 解決：匯入前 `.replace('\n', ' ')`、批量前測試 1 筆

---

## 合約撰寫教訓（2026-02-12）

1. **永遠不要編造內容** — 先讀所有相關資料，不確定就問
2. **風險評估** — 法律/財務/執行/客戶接受度都要檢查
3. **服務聲明真實性** — 只列實際提供的服務
4. **費率細節** — 外派 ≠ 便宜（外派更貴），每個數字都要確認
5. **語氣** — 平等呈現選項，不推銷

---

## BD 客戶開發實戰經驗（2026-02-11）

- BIM 工程師市場：246 家新公司，BD表從 69 → 316 行
- 聯絡資訊抓取瓶頸：120 秒/家，需改進
- LinkedIn 自動化失敗（DevTools/Bookmarklet/Puppeteer 都被擋）→ 暫時擱置

---

## LinkedIn PDF 批量下載工作流程（2026-03-10）

### 固定座標點擊法
- More 按鈕：`cliclick c:339,719`
- 存為 PDF：`cliclick c:446,508`

### 批量腳本
- `/tmp/linkedin_batch_pdf.sh`
- 候選人列表：`/tmp/li_candidates.json`
- 成功率：約 75%

### PDF 解析
- `pdftotext {pdf}.pdf -` 提取文字
- PATCH 到 Step1ne API，actor 帶 `Jacky-aibot`

---

## 人資 AI 導入商業模式探討（2026-02-17）

核心策略：顧問案優先變現（銷售→執行→交付→收款）

三大支撐體系：教育訓練、輔導員機制、TTQS 認證

企業 AI 化選育用留導入：
- 選：智能招聘自動化
- 育：個性化發展路徑
- 用：人崗最優匹配
- 留：離職風險防控

---

## 老闆AI助理 SaaS 化考量

關鍵面向：
- 市場定位、定價策略、競爭分析
- 多租戶架構、數據安全、成本控制
- UI/UX 設計、定制化、客戶支援

---

## 長假期間獨立運作規劃（2026-02-12）

四大自動化系統：
1. 自動開發客戶（每 2 天凌晨，auto-bd-crawler.sh）
2. 自動發 BD 信（每天 09:30/14:30，auto-bd-send.sh）
3. 自動找人選（每週一 10:00，auto-sourcing-final.sh）
4. 自動履歷歸檔（每 1 小時，auto-resume-filing.sh）

---

## Phoebe AI 教育訓練（2026-02-11）

- 單一入口文檔降低學習門檻
- GitHub Raw 連結方便 AI 讀取
- 明確學習路徑提升執行效率

---

## 模型版本管理（2026-02-17）

- Claude Sonnet 4.5 → 4.6 升級完成
- 歷史：修正 Cron jobs 錯誤模型 → 最終升級至 4.6
