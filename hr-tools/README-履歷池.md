# 履歷池管理系統

## 📁 Google Drive 結構

**主資料夾**: [aiagent](https://drive.google.com/drive/folders/1JkesbUFyGz51y90NWUG91n84umU33Mc5)

```
aiagent/
├── 履歷池索引 (Google Sheets)
│   └── https://docs.google.com/spreadsheets/d/1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q
└── resumes/
    ├── pending/        # 待審核
    ├── interviewed/    # 已面試
    ├── hired/          # 已錄取
    └── rejected/       # 已拒絕
```

## 📊 履歷索引欄位

| 欄位 | 說明 |
|------|------|
| 姓名 | 應徵者姓名 |
| 聯絡方式 | 電話或 Email |
| 應徵職位 | 應徵的職位 |
| 主要技能 | 技能標籤（逗號分隔）|
| 工作經驗(年) | 工作經驗年數 |
| 學歷 | 最高學歷 |
| 履歷檔案連結 | Google Drive 連結 |
| 狀態 | 待審核 / 已面試 / 已錄取 / 已拒絕 |
| 備註 | 額外說明 |
| 新增日期 | 履歷新增日期 |
| 最後更新 | 最後更新時間 |

## 🛠 使用工具

### 1. 新增履歷

```bash
./resume-pool.sh add "張三" "0912345678" "AI工程師" "Python,AI,機器學習" "3" "碩士" "/path/to/resume.pdf"
```

**說明**：
- 自動上傳履歷到 `pending/` 資料夾
- 自動新增一筆記錄到 Google Sheets
- 初始狀態為「待審核」

### 2. 搜尋履歷

```bash
./resume-pool.sh search "Python"
```

**說明**：搜尋所有欄位，找出包含關鍵字的履歷

### 3. 更新狀態

```bash
./resume-pool.sh status 2 "已面試"
```

**說明**：
- `2` 是 Google Sheets 的行數（第 2 行）
- 自動移動履歷檔案到對應資料夾
- 更新 Google Sheets 的狀態和最後更新時間

**可用狀態**：
- `待審核`
- `已面試`
- `已錄取`
- `已拒絕`

### 4. 列出所有履歷

```bash
./resume-pool.sh list
```

### 5. 產生統計報表

```bash
./resume-pool.sh report
```

**輸出範例**：
```
📊 履歷池統計報表
====================
總履歷數: 15
待審核: 5
已面試: 4
已錄取: 3
已拒絕: 3

📊 查看完整索引: https://docs.google.com/spreadsheets/d/1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q
```

## 🔗 快速連結

- **履歷索引**: https://docs.google.com/spreadsheets/d/1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q
- **待審核**: https://drive.google.com/drive/folders/1M3jX7JbtQtEwtjfj_GG3UPnSRIcmGezu
- **已面試**: https://drive.google.com/drive/folders/1SNK01mbBXB6kTIdTE0UCfiilx6fZQiZK
- **已錄取**: https://drive.google.com/drive/folders/1m9uUt_S-9Rik3Uzzw0Kqoa-s9VJkm0fk
- **已拒絕**: https://drive.google.com/drive/folders/1lTuP8RCU4K2bpg-TNODN1xPm4EOru2RN

## 📝 注意事項

1. **帳號**: 使用 `aiagentg888@gmail.com`
2. **履歷格式**: 支援 PDF、DOCX 等常見格式
3. **批次操作**: 可以用 bash script 批次新增履歷
4. **備份**: Google Drive 自動備份，不用擔心遺失

## 🚀 進階用法

### 批次新增履歷

```bash
# 從 CSV 批次匯入
while IFS=',' read -r name contact position skills exp edu file; do
  ./resume-pool.sh add "$name" "$contact" "$position" "$skills" "$exp" "$edu" "$file"
done < resumes.csv
```

### 定期報表

```bash
# 加入 cron 每週一早上 9:00 產生報表
0 9 * * 1 /Users/user/clawd/hr-tools/resume-pool.sh report | mail -s "週報告" jackychen0615@gmail.com
```

---

**建立日期**: 2026-02-10  
**維護者**: YuQi 🦞 (HR 助理)
