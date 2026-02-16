# Step1ne Resume Generator - 快速指南

**一鍵產出專業獵頭履歷 PDF**

---

## 🚀 快速開始（5 分鐘上手）

### 1. 準備候選人資料

建立 JSON 檔案（參考 `examples/candidate-data-example.json`）：

```json
{
  "企業": "創樂科技有限公司",
  "職位": "Product Manager",
  "人選": "Abeni",
  "candidate_name": "Abeni",
  "date_of_birth": "198X",
  "age": "34",
  "expected_salary": "月薪 7.5 萬 up，年薪 120~150 萬"
}
```

### 2. 產出履歷

**使用 HTML 範本手動產出（最簡單）**：

```bash
# 1. 複製範本
cp templates/resume-template.html /tmp/resume.html

# 2. 手動編輯 /tmp/resume.html（替換企業、職位、人選等資訊）

# 3. 轉 PDF
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless --disable-gpu \
  --print-to-pdf=output.pdf \
  --print-to-pdf-no-header \
  /tmp/resume.html 2>/dev/null

sleep 2
open output.pdf
```

### 3. 上傳分享

```bash
# 上傳到 Google Drive
gog drive upload output.pdf \
  --parent 12lfoz7qwjhWMwbCJL_SfOf3icCOTCydS \
  --account aijessie88@step1ne.com \
  --json

# 分享連結
gog drive share <file_id> --anyone --role reader --account aijessie88@step1ne.com
```

---

## 📋 檢查清單

產出履歷前，確認以下項目：

- [ ] **企業名稱**：客戶公司全名
- [ ] **職位名稱**：精確的職缺名稱
- [ ] **人選**：使用英文名（如 Abeni）
- [ ] **Candidate 欄位**：只留英文名，不含「中文：⚪⚪⚪」
- [ ] **期望薪資**：完整範圍（如「月薪 7.5 萬 up，年薪 120~150 萬」）
- [ ] **Date of Birth**：完整年份或 198X
- [ ] **聯絡方式**：已刪除底部「聯絡方式：[待提供]」

---

## 🔧 修改履歷

如果需要修改現有履歷：

```bash
# 方法 1：直接編輯 HTML 後重新產出
vim /tmp/resume.html
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless --disable-gpu \
  --print-to-pdf=updated.pdf \
  --print-to-pdf-no-header \
  /tmp/resume.html 2>/dev/null
```

---

## 📁 檔案結構

```
step1ne-resume-generator/
├── SKILL.md                    # 完整技能說明文件
├── README.md                   # 本檔案（快速指南）
├── templates/
│   └── resume-template.html   # Step1ne 標準格式 HTML 範本
├── examples/
│   └── candidate-data-example.json  # 範例資料
└── scripts/
    └── (未來可加入自動化腳本)
```

---

## ⚠️ 常見問題

### Q: PDF 產出失敗？

**A**: 檢查：
- Chrome 路徑是否正確
- 輸出目錄是否存在
- 是否有寫入權限

### Q: 格式跑掉？

**A**: 
- 在瀏覽器開啟 HTML 檢查
- 確認所有 HTML 標籤已正確閉合

### Q: Google Drive 上傳失敗？

**A**:
```bash
# 檢查授權
gog auth list

# 重新授權
gog auth add --account aijessie88@step1ne.com
```

---

## 📚 進階使用

詳細說明請參考 `SKILL.md`

---

**建立者**: YuQi 🦞  
**版本**: 1.0.0  
**更新日期**: 2026-02-13
