# Google Drive 資料夾組織

**版本**：v1.0  
**日期**：2026-02-13  
**用途**：記錄獵頭系統 Google Drive 資料夾結構與自動化腳本

---

## 📂 資料夾結構

```
openclaw 龍蝦工作室/
└── 獵頭系統/
    ├── 履歷池索引 (Google Sheets)
    ├── step1ne 職缺管理 (Google Sheets)
    ├── BD客戶開發表 (Google Sheets)
    ├── Pipeline追蹤 - Jacky (Google Sheets)
    ├── Pipeline追蹤 - Phoebe (Google Sheets)
    └── aiagent 資料夾 (履歷 PDF 存放)
```

---

## 🔑 資料夾與檔案 ID

### 主資料夾
- **openclaw 龍蝦工作室**：`1DwZ9LRF5D4rSvxDjNKyUVAORvhn6mhDj`
- **獵頭系統**：`12lfoz7qwjhWMwbCJL_SfOf3icCOTCydS`

### Google Sheets
- **履歷池索引**：`1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q`
- **step1ne 職缺管理**：`1QPaeOm-slNVFCeM8Q3gg3DawKjzp2tYwyfquvdHlZFE`
- **BD客戶開發表**：`1bkI7_cCh_Bs4qVa3HlXiy0CFzmItZlA-DYGHSPS4InE`
- **Pipeline追蹤 - Jacky**：`1j9zl3Fk-X1DS4iDAFQjAldaLWJDcqybAWIjiDpYCR4M`
- **Pipeline追蹤 - Phoebe**：`1Fh6S5tSpCIacuDrCHs3mewWWqAEhTAPaNXSuQHt6Phk`

### 履歷存放
- **aiagent 資料夾**：`1JkesbUFyGz51y90NWUG91n84umU33Mc5`

---

## 🔗 快速連結

| 項目 | 連結 |
|------|------|
| openclaw 龍蝦工作室 | https://drive.google.com/drive/folders/1DwZ9LRF5D4rSvxDjNKyUVAORvhn6mhDj |
| 獵頭系統 | https://drive.google.com/drive/folders/12lfoz7qwjhWMwbCJL_SfOf3icCOTCydS |
| 履歷池索引 | https://docs.google.com/spreadsheets/d/1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q |
| step1ne 職缺管理 | https://docs.google.com/spreadsheets/d/1QPaeOm-slNVFCeM8Q3gg3DawKjzp2tYwyfquvdHlZFE |
| BD客戶開發表 | https://docs.google.com/spreadsheets/d/1bkI7_cCh_Bs4qVa3HlXiy0CFzmItZlA-DYGHSPS4InE |
| Pipeline追蹤 - Jacky | https://docs.google.com/spreadsheets/d/1j9zl3Fk-X1DS4iDAFQjAldaLWJDcqybAWIjiDpYCR4M |
| Pipeline追蹤 - Phoebe | https://docs.google.com/spreadsheets/d/1Fh6S5tSpCIacuDrCHs3mewWWqAEhTAPaNXSuQHt6Phk |
| aiagent 履歷資料夾 | https://drive.google.com/drive/folders/1JkesbUFyGz51y90NWUG91n84umU33Mc5 |

---

## 🛠️ 自動化腳本

### 移動檔案到龍蝦工作室

**腳本位置**：`/Users/user/clawd/hr-tools/active/tools/move-to-lobster-workspace.sh`

**功能**：
1. 移動「獵頭系統」資料夾到「openclaw 龍蝦工作室」
2. 移動 2 個 Pipeline 追蹤表到「獵頭系統」資料夾

**使用方式**：
```bash
bash /Users/user/clawd/hr-tools/active/tools/move-to-lobster-workspace.sh
```

**執行結果**（2026-02-13）：
```
✅ 獵頭系統 → openclaw 龍蝦工作室
✅ Pipeline追蹤 - Jacky → 獵頭系統
✅ Pipeline追蹤 - Phoebe → 獵頭系統
```

---

## 📊 資料表用途說明

### 1. 履歷池索引
- **用途**：儲存所有候選人資料
- **欄位**：姓名、聯絡方式、應徵職位、主要技能、狀態、獵頭顧問...（共 12 欄）
- **更新頻率**：每次找到新候選人時自動新增
- **負責人**：AI 自動維護 + 獵頭顧問手動更新

### 2. step1ne 職缺管理
- **用途**：管理所有客戶職缺
- **欄位**：職位名稱、客戶公司、部門、需求人數、薪資範圍、技能要求...（共 21 欄）
- **更新頻率**：客戶新增職缺時
- **負責人**：Jacky / AI 匯入

### 3. BD客戶開發表
- **用途**：潛在客戶名單與開發進度
- **欄位**：公司名稱、聯絡電話、Email、網址、職缺、狀態、開發日期...（共 13 欄）
- **更新頻率**：每 2 天自動爬蟲新增 + 每天自動寄信
- **負責人**：AI 自動化 + Jacky 追蹤

### 4. Pipeline追蹤 - Jacky
- **用途**：追蹤 Jacky 負責的候選人招聘進度
- **欄位**：候選人、職位、公司、狀態、下一步、備註
- **更新頻率**：每次候選人狀態變更時
- **負責人**：Jacky

### 5. Pipeline追蹤 - Phoebe
- **用途**：追蹤 Phoebe 負責的候選人招聘進度
- **欄位**：候選人、職位、公司、狀態、下一步、備註
- **更新頻率**：每次候選人狀態變更時
- **負責人**：Phoebe

---

## 🔐 權限管理

### Google 帳號
- **主要帳號**：`aiagentg888@gmail.com`
- **次要帳號**：`aijessie88@step1ne.com`

### 授權範圍
```bash
gog auth list
```

輸出：
```
aiagentg888@gmail.com    gmail,calendar,drive,docs,sheets...
aijessie88@step1ne.com   gmail,calendar,drive,docs,sheets...
```

---

## 📝 維護記錄

### 2026-02-13
- ✅ 建立「openclaw 龍蝦工作室」資料夾結構
- ✅ 移動「獵頭系統」到龍蝦工作室
- ✅ 移動 2 個 Pipeline 追蹤表到獵頭系統
- ✅ 建立自動化移動腳本
- ✅ 文檔化資料夾結構與 ID

---

## 🚨 注意事項

### 重要提醒
1. **不要手動移動資料夾**：使用 `gog drive move` 或自動化腳本
2. **ID 不會變**：即使移動資料夾，Google Drive ID 保持不變
3. **共享連結**：移動後，所有共享連結仍然有效
4. **權限繼承**：子資料夾會繼承父資料夾的權限設定

### 故障排除
**Q: 移動後找不到檔案？**
- A: 用 `gog drive search "<檔案名>"` 搜尋

**Q: 權限錯誤？**
- A: 確認 `gog auth list` 有 `drive` 權限

**Q: 移動失敗？**
- A: 檢查目標資料夾 ID 是否正確

---

## 📚 相關文檔

- **自動找人選技能包**：`AUTO-SOURCING-README.md`
- **HR 工具總覽**：`README.md`
- **腳本說明**：`AUTO-SOURCING-SCRIPTS.md`

---

**最後更新**：2026-02-13 12:25 GMT+8  
**維護者**：YuQi (OpenClaw AI Assistant)

---

## 📝 更新記錄（2026-02-13 12:30）

### aiagent 履歷資料夾移動
- ✅ 將「aiagent」資料夾移動到「獵頭系統」下
- 📁 **內容**：691+ 個履歷 PDF 檔案
- 🔗 **連結**：https://drive.google.com/drive/folders/1JkesbUFyGz51y90NWUG91n84umU33Mc5
- **用途**：所有候選人履歷 PDF 統一存放位置

### 最終資料夾結構
```
openclaw 龍蝦工作室/
└── 獵頭系統/
    ├── 履歷池索引 (Google Sheets)
    ├── step1ne 職缺管理 (Google Sheets)
    ├── BD客戶開發表 (Google Sheets)
    ├── Pipeline追蹤 - Jacky (Google Sheets)
    ├── Pipeline追蹤 - Phoebe (Google Sheets)
    └── aiagent/ ← 履歷 PDF 存放（691+ 個檔案）
```
