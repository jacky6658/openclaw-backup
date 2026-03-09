# Step1ne HR 工具安裝指南

## 🎯 適用對象
- Step1ne 獵頭顧問的 AI 助理
- 需要使用 BD 自動化、履歷池、JD 管理工具的團隊成員

## 📧 預設信箱
**所有 BD 開發信預設使用**：`aijessie88@step1ne.com`

如需使用其他信箱，請參考「進階設定」章節。

---

## 🚀 快速安裝（AI 助理自動執行）

### 1. 下載工具
```bash
cd ~/clawd
git clone https://github.com/jacky6658/openclaw-backup.git temp
cp -r temp/hr-tools ~/clawd/hr-tools
rm -rf temp
```

### 2. 確認工具可執行
```bash
cd ~/clawd/hr-tools
chmod +x *.sh
```

### 3. 確認 gog CLI 已安裝
```bash
# 檢查是否已安裝
which gog

# 如果沒有，執行安裝
brew install steipete/tap/gogcli
```

### 4. 設定 Gmail 帳號（預設）
```bash
# 如果尚未設定 aijessie88@step1ne.com
gog auth add aijessie88@step1ne.com --services gmail
```

執行後會開啟瀏覽器，登入 Google 帳號並授權。

### 5. 測試工具
```bash
cd ~/clawd/hr-tools

# 預覽 BD 信件
./bd-outreach.sh preview "測試公司" "您好"

# 列出 JD
./jd-manager.sh list

# 查看履歷池
./resume-pool.sh stats
```

---

## 📋 工具清單

安裝完成後，你可以使用以下工具：

### 1. BD 客戶開發信自動化
```bash
# 寄送合作邀請信（附公司簡介 PDF）
./bd-outreach.sh send "公司名稱" "email@company.com" "聯絡人"

# 預覽信件
./bd-outreach.sh preview "公司名稱" "聯絡人"
```

**說明**：[README-BD自動化.md](README-BD自動化.md)

### 2. JD 管理
```bash
# 列出所有職缺
./jd-manager.sh list

# 搜尋職缺
./jd-manager.sh search "AI"

# 新增職缺
./jd-manager.sh add "職位" "部門" "人數" "薪資" "技能" "經驗" "學歷"
```

**說明**：[README-JD管理.md](README-JD管理.md)

### 3. 履歷池管理
```bash
# 新增履歷
./resume-pool.sh add "候選人姓名" "職位" "技能" "經驗" "學歷" "履歷連結"

# 搜尋履歷
./resume-pool.sh search "Python"

# 統計報表
./resume-pool.sh stats
```

**說明**：[README-履歷池.md](README-履歷池.md)

### 4. HR 總覽看板
```bash
# 啟動看板（Web UI）
./start-dashboard.sh
```

訪問：http://localhost:3000

**說明**：[README-總覽看板.md](README-總覽看板.md)

---

## 🔧 進階設定

### 使用其他 Email 帳號

如果你需要使用自己的 step1ne.com 信箱（例如 `consultant1@step1ne.com`）：

#### 方法 1：修改設定檔
編輯 `bd-outreach.sh`，找到這一行：
```bash
EMAIL_ACCOUNT="aijessie88@step1ne.com"
```

改成：
```bash
EMAIL_ACCOUNT="consultant1@step1ne.com"
```

#### 方法 2：使用環境變數
```bash
export GOG_ACCOUNT="consultant1@step1ne.com"
./bd-outreach.sh send "公司名稱" "email" "聯絡人"
```

### 自訂公司簡介 PDF

BD 信件會自動附上 `Step1ne公司簡介.pdf`。

如需替換：
```bash
cp /path/to/your/company-intro.pdf ~/clawd/hr-tools/Step1ne公司簡介.pdf
```

---

## 📊 Google Sheets 整合

部分工具需要連接 Google Sheets：
- JD 管理 → [step1ne 職缺管理](https://docs.google.com/spreadsheets/d/1QPaeOm-slNVFCeM8Q3gg3DawKjzp2tYwyfquvdHlZFE)
- 履歷池 → [履歷池索引](https://docs.google.com/spreadsheets/d/1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q)

### 設定 Google Sheets 權限
```bash
# 新增 Google Drive + Sheets 授權
gog auth add aijessie88@step1ne.com --services drive,sheets
```

或者如果已經有 Gmail 授權，可以重新授權加上 Sheets：
```bash
gog auth update aijessie88@step1ne.com --services gmail,drive,sheets
```

---

## 🐛 疑難排解

### 錯誤：找不到 gog
**解決方式**：
```bash
brew install steipete/tap/gogcli
```

### 錯誤：找不到 Google 帳號
**解決方式**：
```bash
gog auth add aijessie88@step1ne.com --services gmail,drive,sheets
```

### 錯誤：Permission denied
**解決方式**：
```bash
chmod +x ~/clawd/hr-tools/*.sh
```

### 錯誤：找不到公司簡介 PDF
**解決方式**：
確認檔案存在：
```bash
ls -lh ~/clawd/hr-tools/Step1ne公司簡介.pdf
```

如果不存在，從原始位置複製：
```bash
cp /Users/user/Downloads/Step1ne公司簡介_2026_20260105.pdf ~/clawd/hr-tools/Step1ne公司簡介.pdf
```

---

## 📞 支援

安裝或使用過程中遇到問題？

**AI 助理自動診斷**：
1. 檢查 gog 是否安裝：`which gog`
2. 檢查 Google 帳號授權：`gog auth list`
3. 檢查工具權限：`ls -l ~/clawd/hr-tools/*.sh`
4. 檢查 PDF 是否存在：`ls -lh ~/clawd/hr-tools/*.pdf`

**聯繫管理員**：
如果 AI 無法解決，請在 Telegram 群組詢問 @jackyyuqi

---

## 🔄 更新工具

當有新版本釋出時：
```bash
cd ~/clawd
git clone https://github.com/jacky6658/openclaw-backup.git temp
cp -r temp/hr-tools/* ~/clawd/hr-tools/
rm -rf temp

# 重新設定權限
chmod +x ~/clawd/hr-tools/*.sh
```

---

## 📝 完成清單

安裝完成後，確認以下項目：

- [ ] gog CLI 已安裝
- [ ] aijessie88@step1ne.com 已授權（gmail, drive, sheets）
- [ ] 所有 .sh 檔案可執行
- [ ] Step1ne公司簡介.pdf 存在
- [ ] bd-outreach.sh 預覽成功
- [ ] jd-manager.sh list 可正常執行
- [ ] resume-pool.sh stats 可正常執行

全部打勾 ✅ 就代表安裝成功！
