# 履歷處理自動化腳本使用說明

**版本**：1.0.0  
**日期**：2026-02-24  
**作者**：YuQi AI Assistant

---

## 📋 功能說明

自動處理收到的履歷 PDF，包含：
1. ✅ 上傳到 Google Drive（履歷庫資料夾）
2. ✅ 搜尋履歷池（用 LinkedIn 或姓名）
3. ✅ 更新履歷連結（U 欄）
4. ✅ 回報處理結果

---

## 🚀 快速開始

### **基本用法**

```bash
cd /Users/user/clawd/hr-tools
./process-resume-pdf.sh <PDF路徑>
```

### **範例**

```bash
./process-resume-pdf.sh ~/Downloads/Maggie-Chen-Resume.pdf
```

---

## 📖 操作流程

### **步驟 1：執行腳本**

```bash
./process-resume-pdf.sh ~/Downloads/resume.pdf
```

### **步驟 2：輸入候選人資訊**

腳本會提示：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 請輸入候選人基本資訊
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 候選人姓名：Maggie Chen
🔗 LinkedIn username（選填）：maggie-chen-472b79137
```

### **步驟 3：確認應徵公司**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Maggie Chen 應徵哪家公司的職缺？Pivot
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### **步驟 4：自動處理**

腳本會自動：
1. 上傳 PDF 到 Google Drive（檔名：`Maggie Chen-Pivot.pdf`）
2. 搜尋履歷池（用 LinkedIn 或姓名）
3. 更新履歷連結（U 欄）

### **步驟 5：確認結果**

```
📊 更新結果：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 候選人：Maggie Chen
🏢 應徵公司：Pivot
📍 履歷池行號：Row 2
🔗 履歷連結：已更新
📄 檔名：Maggie Chen-Pivot.pdf
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 處理完成！
```

---

## 🔍 搜尋邏輯

### **策略 1：LinkedIn username（優先）**
- 最準確，不會重複
- 例：`maggie-chen-472b79137`

### **策略 2：姓名**
- 次選，可能重複
- 找到時會要求確認是否為同一人

### **找不到**
- 顯示提示：「請手動新增」
- 履歷已上傳到 Google Drive（可直接使用連結）

---

## 📊 處理結果

### ✅ **找到現有候選人**
- 更新 U 欄（履歷連結）
- 保留其他欄位不變
- 前端 30 秒後自動同步

### ❌ **找不到候選人**
- 顯示 Google Drive 連結
- 提示手動新增
- 檔案已正確命名（`{姓名}-{公司}.pdf`）

---

## 🛠️ 技術細節

### **Google Drive 設定**
- **資料夾 ID**：`16IOJW0jR2mBgzBnc5QI_jEHcRBw3VnKj`
- **帳號**：aijessie88@step1ne.com
- **URL 格式**：`/preview`（嵌入式預覽）

### **Google Sheets 設定**
- **Sheet ID**：`1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q`
- **分頁**：履歷池v2
- **更新方式**：`--values-json`（安全模式）

### **檔案命名規則**
```
格式：{姓名}-{應徵公司}.pdf
範例：Maggie Chen-Pivot.pdf
```

---

## ⚠️ 注意事項

### **1. LinkedIn username 格式**
- ✅ 正確：`maggie-chen-472b79137`
- ❌ 錯誤：`https://www.linkedin.com/in/maggie-chen-472b79137`（腳本會自動處理）

### **2. 姓名輸入**
- 中英文皆可
- 必須與履歷池中的姓名**完全一致**（大小寫也要相同）

### **3. 公司名稱**
- 簡短清楚即可
- 例：`Pivot`、`遊戲橘子`、`美德醫療`

### **4. 重複候選人**
- 如果用姓名搜尋到多個結果，腳本會顯示第一個
- 建議使用 LinkedIn username（唯一）

---

## 🐛 常見問題

### **Q1: 找不到候選人怎麼辦？**
A: 履歷已上傳到 Google Drive，可：
- 手動新增候選人到履歷池
- 複製腳本輸出的 Google Drive 連結到 U 欄

### **Q2: LinkedIn username 在哪裡找？**
A: 從 LinkedIn 個人頁面 URL 複製：
```
https://www.linkedin.com/in/maggie-chen-472b79137
                             ↑
                    這部分就是 username
```

### **Q3: 可以批量處理嗎？**
A: 目前不支援，每次處理一個 PDF。未來可考慮增加批量模式。

### **Q4: 如何確認更新成功？**
A: 
1. 查看腳本輸出的「更新結果」
2. 前端 30 秒後自動同步
3. 打開 Step1ne 系統，查看候選人彈跳視窗（應該有「查看完整履歷」按鈕）

---

## 📝 未來改進

- [ ] 自動解析 PDF 內容（提取技能、經歷）
- [ ] 支援批量處理多個 PDF
- [ ] 新增候選人功能（目前只支援更新）
- [ ] Telegram 通知整合
- [ ] 錯誤重試機制

---

## 🔗 相關文檔

- [履歷處理完整流程（MEMORY.md）](../MEMORY.md#履歷處理完整流程2026-02-24)
- [履歷匯入標準流程（MEMORY.md）](../MEMORY.md#履歷匯入標準流程2026-02-23)
- [Google Drive 履歷庫](https://drive.google.com/drive/folders/16IOJW0jR2mBgzBnc5QI_jEHcRBw3VnKj)

---

**最後更新**：2026-02-24 15:30  
**腳本位置**：`/Users/user/clawd/hr-tools/process-resume-pdf.sh`
