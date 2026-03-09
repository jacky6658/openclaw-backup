# 履歷進件處理 SOP (Standard Operating Procedure)

## 目標
自動化履歷篩選、評分、通知流程，提升招募效率

---

## 📥 履歷來源

### 主要渠道
1. **Email** (Gmail API)
   - 監控信箱：aijessie88@step1ne.com
   - 篩選條件：subject 包含「應徵」「履歷」或附件為 PDF/DOCX
   
2. **人力銀行平台**
   - 104 人力銀行
   - 1111 人力銀行
   - LinkedIn
   
3. **手動上傳**
   - Telegram 群組直接傳送檔案

---

## 🔄 處理流程

### Step 1: 履歷接收
- [ ] 自動偵測新履歷（Email / 平台 API）
- [ ] 下載附件到本地資料夾：`/Users/user/clawd/hr-recruitment/resumes/`
- [ ] 檔案命名規則：`YYYYMMDD-HHMM_姓名_職位.pdf`

### Step 2: 履歷解析
使用 AI 提取以下資訊：
- **基本資料**：姓名、電話、Email、居住地
- **學歷**：學校、科系、畢業年份
- **工作經驗**：公司名稱、職位、年資、職責描述
- **技能**：程式語言、工具、證照
- **期望待遇 / 到職日**

### Step 3: 智能評分
根據職位需求評分（0-100 分）：
- **技能匹配度** (40%)
- **經驗相關性** (30%)
- **學歷背景** (15%)
- **其他加分項** (15%)：GitHub、作品集、證照

### Step 4: 自動通知
發送到 Telegram 群組（HR AI招募自動化 topic 4）：

**📋 標準格式（所有 Bot 必須遵循）**
```
📋 #履歷進件

👤 **姓名**：王小明
📧 **Email**：example@example.com
📞 **電話**：0912-345-678
💼 **應徵職位**：後端工程師
👔 **負責顧問**：[顧問名稱] ⚠️ **必填欄位**

---

⭐ **評分**：85 / 100

**優勢**：
- 3 年 Node.js 開發經驗
- 熟悉 PostgreSQL、Redis
- GitHub 有活躍專案

**待確認**：
- 期望薪資未填寫
- 無英文能力證明

---

🔗 [查看完整履歷](檔案連結)

**建議動作**：✅ 邀約面試 / ⏸️ 待觀察 / ❌ 不適合
```

**⚠️ 重要規則**：
- 所有履歷進件通知**必須包含「負責顧問」欄位**
- 未來新的 Bot 加入時，必須先設定自己的負責顧問名稱
- 若無法取得負責顧問資訊，填寫「待指派」

### Step 5: 後續追蹤
- [ ] HR 回覆決策（面試 / 婉拒）
- [ ] 自動發送面試邀約信（模板）
- [ ] 記錄到 `hr-recruitment/candidates.json`

---

## 📊 數據記錄

### candidates.json 格式
```json
{
  "candidates": [
    {
      "id": "20260210-001",
      "name": "王小明",
      "email": "example@example.com",
      "phone": "0912-345-678",
      "position": "後端工程師",
      "score": 85,
      "status": "pending", // pending / interviewed / rejected / hired
      "resume_path": "/Users/user/clawd/hr-recruitment/resumes/20260210-1758_王小明_後端工程師.pdf",
      "received_at": "2026-02-10T17:58:00+08:00",
      "notes": "技術背景優秀，待確認薪資期望"
    }
  ]
}
```

---

## 🤖 自動化觸發條件

### Heartbeat 檢查（每 30 分鐘）
- 檢查 Gmail 新郵件
- 掃描 `hr-recruitment/inbox/` 資料夾
- 若有新履歷 → 執行 Step 1-4

### 手動觸發
指令：`#履歷處理 [檔案路徑或 Email ID]`

---

## 🛡️ 隱私與合規

- 履歷檔案加密儲存
- 定期清理超過 6 個月的舊履歷
- 符合個資法要求（應徵者同意書）

---

## 📝 模板庫

### 面試邀約信模板
位置：`hr-recruitment/templates/interview-invite.md`

### 婉拒信模板
位置：`hr-recruitment/templates/rejection-letter.md`

---

**建立日期**：2026-02-10  
**負責人**：YuQi AI  
**版本**：v1.0
