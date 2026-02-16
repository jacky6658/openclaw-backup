# TOOLS.md - Local Notes

Skills define *how* tools work. This file is for *your* specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:
- Camera names and locations
- SSH hosts and aliases  
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras
- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH
- home-server → 192.168.1.100, user: admin

### TTS
- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## HR 履歷進件設定

### Gmail 監控信箱
- **監控帳號**：aijessie88@step1ne.com ✅
- **授權狀態**：已完成 OAuth（2026-02-11）
- **篩選條件**：subject 包含「應徵」「履歷」或附件為 PDF/DOCX

### 負責顧問自動標記規則（2026-02-11 更新）
- **Jacky 傳送的履歷** → 獵頭顧問標記為 "Jacky"
- **Phoebe (@behe10) 傳送的履歷** → 獵頭顧問標記為 "Phoebe"

**判斷方式**：根據 Telegram 訊息的 sender (userId 或 username) 自動判斷
- Jacky userId: 8365775688
- Phoebe username: @behe10

**說明**：所有履歷進件通知必須包含「負責顧問」欄位，系統會根據傳送者自動填寫。

---

## JD（職缺）管理

### 系統位置
- **管理工具**: `/Users/user/clawd/hr-tools/jd-manager.sh`
- **文件**: `/Users/user/clawd/hr-tools/README-JD管理.md`
- **雲端資料夾**: [獵頭系統](https://drive.google.com/drive/folders/12lfoz7qwjhWMwbCJL_SfOf3icCOTCydS)
- **Google Sheets**: [step1ne 職缺管理](https://docs.google.com/spreadsheets/d/1QPaeOm-slNVFCeM8Q3gg3DawKjzp2tYwyfquvdHlZFE/edit)

### 快速指令
```bash
./jd-manager.sh list          # 列出所有職缺
./jd-manager.sh search 'AI'   # 搜尋職缺
./jd-manager.sh report         # 統計報表
./jd-manager.sh add <職位> <部門> <人數> <薪資> <技能> <經驗> <學歷>
```

### 目前職缺（2026-02-10）
- AI工程師 (技術部) — 2人，80k-120k
- 數據分析師 (數據部) — 1人，60k-90k
- 產品經理 (產品部) — 1人，90k-140k
- 全端工程師 (技術部) — 3人，70k-110k
- HR 招募專員 (人資部) — 1人，50k-70k

---

## 總覽看板（新增 2026-02-10）

### Web 介面
- **專案位置**: `/Users/user/clawd/projects/hr-dashboard`
- **啟動腳本**: `/Users/user/clawd/hr-tools/start-dashboard.sh`
- **訪問位址**: http://localhost:3000
- **說明文件**: `/Users/user/clawd/hr-tools/README-總覽看板.md`

### 功能特色
- 即時追蹤職缺與候選人狀態
- Pipeline 視覺化
- 自動提醒需跟進的案件
- 每 30 秒自動更新

### 快速啟動
```bash
~/clawd/hr-tools/start-dashboard.sh
```

---

## Pipeline 追蹤表（新增 2026-02-11）

### 各顧問獨立 Sheet
- **清單文件**: `/Users/user/clawd/hr-tools/pipeline-sheets.md`

**Jacky**
- Sheet ID: `1j9zl3Fk-X1DS4iDAFQjAldaLWJDcqybAWIjiDpYCR4M`
- 網址: https://docs.google.com/spreadsheets/d/1j9zl3Fk-X1DS4iDAFQjAldaLWJDcqybAWIjiDpYCR4M/edit

**Phobe**
- Sheet ID: `1Fh6S5tSpCIacuDrCHs3mewWWqAEhTAPaNXSuQHt6Phk`
- 網址: https://docs.google.com/spreadsheets/d/1Fh6S5tSpCIacuDrCHs3mewWWqAEhTAPaNXSuQHt6Phk/edit

### 用途
- 追蹤候選人在招聘流程中的狀態
- 每週市場報告自動彙總所有顧問的 Pipeline 數據

---

## 履歷池管理

### 群組設定
- **履歷池群組**: HR AI招募自動化 (`-1003231629634`)
- **主要 Topic**: 304（履歷相關操作的主要討論區）

### 快速操作
**在 Telegram 中可以直接：**
1. 上傳履歷檔案 → YuQi 自動處理
2. 搜尋履歷：`搜尋 [關鍵字]`
3. 更新狀態：`更新狀態 [行數] [新狀態]`
4. 查看報表：`履歷報表`

### 系統位置
- **管理工具**: `/Users/user/clawd/hr-tools/resume-pool.sh`
- **文件**: `/Users/user/clawd/hr-tools/README-履歷池.md`
- **雲端資料夾**: [獵頭系統](https://drive.google.com/drive/folders/12lfoz7qwjhWMwbCJL_SfOf3icCOTCydS)
- **履歷存放**: [aiagent 資料夾](https://drive.google.com/drive/folders/1JkesbUFyGz51y90NWUG91n84umU33Mc5)
- **索引**: [履歷池索引 (Google Sheets)](https://docs.google.com/spreadsheets/d/1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q)

---

Add whatever helps you do your job. This is your cheat sheet.

---

## BD 客戶開發自動化（新增 2026-02-10）

### 觸發位置
- **群組**：HR AI招募自動化 (`-1003231629634`)
- **Topic 364**：「開發」
- **觸發方式**：`@YuQi 開發客戶：<職位名稱>`

### 工具位置
- **腳本**：`~/clawd/hr-tools/bd-automation.sh`
- **說明**：在 `/Users/user/clawd/skills/headhunter/SKILL.md` 的最後
- **資料儲存**：`~/clawd/hr-tools/data/`
- **Google Sheet**：[BD客戶開發表](https://docs.google.com/spreadsheets/d/1bkI7_cCh_Bs4qVa3HlXiy0CFzmItZlA-DYGHSPS4InE)

### 自動執行流程
1. 搜尋 104 招聘公司
2. 爬取聯絡方式
3. 整理到 Google Sheets（BD客戶開發表）
4. 批量寄 BD 信
5. 回報結果到 Topic 364

### 表格欄位
- 公司名稱
- 聯絡電話
- Email
- 網址
- 目前職缺
- 來源（104/LinkedIn）
- 狀態（待聯繫/已寄信/已回覆/合作中）
- 開發日期
- 負責顧問
- 備註
