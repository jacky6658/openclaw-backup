# Step1ne Resume Generator Skill

**版本**: 1.0.0  
**用途**: 產出 Step1ne 獵頭標準格式履歷（HTML → PDF）  
**適用場景**: 當需要產出專業的獵頭履歷給客戶時

---

## 何時使用此技能

- 需要產出 **Step1ne 標準格式履歷**
- 將候選人資料轉換成專業履歷 PDF
- 客戶要求履歷格式符合獵頭規範
- 匿名履歷製作（隱藏個人敏感資訊）

---

## Step1ne 履歷標準格式特色

1. **品牌識別**
   - Step1ne Logo (◈ STEP1NE)
   - 專業配色（藍色主題 #0066cc）
   - 保密條款聲明

2. **結構化內容**
   - 企業 / 職位 / 人選 三欄標題
   - Personal Particulars 表格
   - Summary 及個人特質
   - Career Background（工作經歷）
   - Remuneration Package（薪資結構）
   - 備註說明（給客戶 HR）

3. **匿名化處理**
   - 姓名可用代號（如 PM-2026-001）或英文名
   - 中文姓名用 ⚪⚪⚪ 隱藏
   - 公司名稱可匿名（如「某遊戲科技公司」）

---

## 快速開始

### 1. 準備候選人資料

建立候選人資料 JSON：

```json
{
  "企業": "目標公司名稱",
  "職位": "Product Manager",
  "人選": "Abeni",
  "推薦日期": "2026-02-13",
  "candidate_name": "Abeni",
  "date_of_birth": "1990",
  "age": "34",
  "language": "Chinese: Native speaker，English: IELTS 5.0",
  "marital_status": "⚪⚪⚪",
  "nationality": "Taiwan Citizen",
  "residence": "Taipei City",
  "education": "東南科技大學 / 工業工程與管理系 / 2013/6",
  "summary": [
    "遊戲產業 PM 經驗 2+ 年，目前負責撲克 APP 產品規劃",
    "熟悉產品從 0-1 完整流程，曾獨立交付 9-10 個包網平台專案"
  ],
  "work_experience": [
    {
      "company": "某遊戲科技公司",
      "period": "2025 年 10 月 ~ 現在（在職中）",
      "title": "PM（專案經理）",
      "responsibilities": [
        "負責撲克 APP 產品規劃（含 X-Poker、GGClub 等產品研究）",
        "規劃功能設計：大廳功能、桌檯功能、俱樂部系統"
      ],
      "achievements": "完成 X-Poker APP 完整產品規劃",
      "reason": "仍在職（尋求更好的發展機會）"
    }
  ],
  "current_salary": "60,000",
  "expected_salary": "月薪 7.5 萬 up，年薪 120~150 萬",
  "notice_period": "One month"
}
```

### 2. 使用 HTML 範本產出履歷

**方法 A：使用內建範本**

```bash
# 1. 讀取範本
template=$(cat /Users/user/clawd/skills/step1ne-resume-generator/templates/resume-template.html)

# 2. 替換變數（簡單版本）
# 在 HTML 中用 {{變數名}} 標記，然後用 sed 替換

# 3. 產出 PDF
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless --disable-gpu \
  --print-to-pdf=/path/to/output.pdf \
  --print-to-pdf-no-header \
  /path/to/filled-template.html
```

**方法 B：用 Python 產出（推薦）**

```python
#!/usr/bin/env python3
import json

# 讀取候選人資料
with open('candidate-data.json') as f:
    data = json.load(f)

# 讀取範本
with open('templates/resume-template.html') as f:
    template = f.read()

# 填入資料（建議用 Jinja2 或類似工具）
# 這裡示範簡單的字串替換
html = template.replace('{{企業}}', data['企業'])
html = html.replace('{{職位}}', data['職位'])
# ... 替換所有變數

# 輸出 HTML
with open('output.html', 'w', encoding='utf-8') as f:
    f.write(html)
```

### 3. 轉換成 PDF

```bash
# 使用 Chrome headless 模式
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless --disable-gpu \
  --print-to-pdf=output.pdf \
  --print-to-pdf-no-header \
  output.html

# 等待 2 秒確保產出完成
sleep 2

# 檢查檔案
ls -lh output.pdf
```

### 4. 上傳到 Google Drive

```bash
# 上傳到指定資料夾
gog drive upload output.pdf \
  --parent 12lfoz7qwjhWMwbCJL_SfOf3icCOTCydS \
  --account aijessie88@step1ne.com \
  --json

# 設定分享權限
gog drive share <file_id> \
  --anyone --role reader \
  --account aijessie88@step1ne.com
```

---

## 完整工作流程

### 情境：為 Abeni 產出創樂科技的履歷

**Step 1：收集資料**
- 從履歷池取得候選人資訊
- 確認職缺需求（企業名稱、職位）
- 確認要匿名化的欄位

**Step 2：建立 HTML**
```python
# 使用範本產出 HTML
# 參考：/Users/user/clawd/skills/step1ne-resume-generator/scripts/generate-resume.py

python3 generate-resume.py \
  --data candidate-data.json \
  --template resume-template.html \
  --output Abeni-創樂科技-履歷.html
```

**Step 3：轉 PDF**
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless --disable-gpu \
  --print-to-pdf=Abeni-創樂科技-履歷.pdf \
  --print-to-pdf-no-header \
  Abeni-創樂科技-履歷.html 2>/dev/null

sleep 2
```

**Step 4：上傳分享**
```bash
# 上傳
FILE_ID=$(gog drive upload Abeni-創樂科技-履歷.pdf \
  --parent 12lfoz7qwjhWMwbCJL_SfOf3icCOTCydS \
  --account aijessie88@step1ne.com \
  --json | jq -r '.file.id')

# 分享
gog drive share $FILE_ID \
  --anyone --role reader \
  --account aijessie88@step1ne.com

# 取得連結
echo "https://drive.google.com/file/d/$FILE_ID/view"
```

**Step 5：開啟預覽**
```bash
open Abeni-創樂科技-履歷.pdf
```

---

## 履歷修改流程

### 修改現有履歷

**情境：需要修改履歷內容（如薪資、姓名）**

1. **修改 HTML 原檔**：
   ```bash
   # 使用 Edit tool 修改指定內容
   # 例如：改期望薪資
   ```

2. **重新產出 PDF**：
   ```bash
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
     --headless --disable-gpu \
     --print-to-pdf=updated.pdf \
     --print-to-pdf-no-header \
     updated.html 2>/dev/null
   ```

3. **上傳新版本**

---

## 重要提醒

### ✅ 必須確認的資訊

產出履歷前，務必確認：

1. **企業名稱** - 客戶公司全名
2. **職位名稱** - 精確的職缺名稱
3. **人選姓名** - 英文名或代號（PM-2026-001）
4. **Candidate 欄位** - 只留英文名（不含中文⚪⚪⚪）
5. **期望薪資** - 完整的薪資範圍（月薪 + 年薪）
6. **Date of Birth** - 完整年份或 198X（如果沒有完整資料）
7. **聯絡方式** - 是否需要保留（通常刪除）

### ❌ 常見錯誤

1. **忘記刪除聯絡方式**
   - 底部「聯絡方式：[待提供]」要刪除

2. **Candidate 欄位格式錯誤**
   - ❌ 錯誤：`中文：⚪⚪⚪  英文：⚪⚪⚪`
   - ✅ 正確：`Abeni`

3. **人選欄位用代號**
   - ❌ 錯誤：`人 選: PM-2026-001`
   - ✅ 正確：`人 選: Abeni`（使用英文名）

4. **期望薪資不完整**
   - ❌ 錯誤：`待議`
   - ✅ 正確：`月薪 7.5 萬 up，年薪 120~150 萬`

5. **PDF 產出失敗**
   - Chrome headless 有時會卡住
   - 建議加上 `2>/dev/null` 忽略錯誤訊息
   - 加上 `sleep 2` 等待產出完成

---

## 範本檔案位置

- **HTML 範本**：`templates/resume-template.html`
- **範例資料**：`examples/candidate-data.json`
- **產出腳本**：`scripts/generate-resume.py`
- **說明文件**：本檔案 (`SKILL.md`)

---

## 進階使用

### 批量產出履歷

```bash
# 從履歷池批量產出
for candidate in $(cat candidate-list.txt); do
  python3 generate-resume.py \
    --data "${candidate}.json" \
    --output "${candidate}-履歷.pdf"
done
```

### 自動化上傳

```bash
# 產出後自動上傳並取得連結
./scripts/auto-resume-upload.sh candidate-data.json
```

---

## 疑難排解

### Q: Chrome headless 產出失敗

**A**: 常見原因與解決方案：
- **字型問題**：確保系統有安裝中文字型
- **權限問題**：確保輸出目錄有寫入權限
- **路徑問題**：使用絕對路徑
- **檔案鎖定**：先關閉 Preview/PDF 檢視器

```bash
# 檢查 Chrome 路徑
which "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# 確認輸出目錄存在
mkdir -p /path/to/output

# 使用絕對路徑
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless --disable-gpu \
  --print-to-pdf=/absolute/path/output.pdf \
  --print-to-pdf-no-header \
  /absolute/path/input.html
```

### Q: Google Drive 上傳失敗

**A**: 檢查項目：
- gog CLI 是否已安裝
- 帳號是否已授權（`gog auth list`）
- 資料夾 ID 是否正確
- 檔案大小是否超過限制

```bash
# 檢查授權
gog auth list

# 重新授權
gog auth add --account aijessie88@step1ne.com
```

### Q: 履歷格式跑掉

**A**: 常見原因：
- CSS 樣式缺失
- HTML 標籤未閉合
- 特殊字元未轉義

**檢查方式**：
```bash
# 在瀏覽器開啟 HTML 預覽
open output.html

# 檢查 HTML 語法
tidy -q -e output.html
```

---

## 版本更新

### v1.0.0 (2026-02-13)
- ✅ 初版發布
- ✅ Step1ne 標準格式範本
- ✅ 產出腳本與說明文件
- ✅ 匿名化處理規則
- ✅ Google Drive 整合

---

**建立者**: YuQi 🦞  
**最後更新**: 2026-02-13  
**授權**: 內部使用
