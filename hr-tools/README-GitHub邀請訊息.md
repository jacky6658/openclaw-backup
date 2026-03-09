# GitHub 候選人邀請訊息生成器

自動生成專業的 GitHub Issue 邀請訊息，用於聯繫技術人才。

## 快速使用

```bash
cd /Users/user/clawd/hr-tools
./github-invite-message.sh <GitHub-username> <職缺名稱>
```

### 範例

```bash
# 邀請 jackyyuqi 應徵 AI工程師職缺
./github-invite-message.sh jackyyuqi "AI工程師"

# 邀請 torvalds 應徵資深後端工程師
./github-invite-message.sh torvalds "資深後端工程師"
```

## 互動式輸入

腳本會詢問以下資訊：

1. **💰 薪資範圍**（例：80-120k）
2. **📍 工作地點**（例：台北市/遠端）
3. **🚀 技術棧**（例：Python, TensorFlow, Docker）
4. **🏢 公司類型**（例：AI科技公司/知名遊戲公司）
5. **🎯 候選人技能**（例：Python, AI, Machine Learning）
6. **📧 聯絡 Email**
7. **🔒 是否匿名企業**（y/n）

所有欄位都可以按 Enter 使用預設值。

## 輸出

### 1. 螢幕顯示
- Issue 標題
- Issue 完整內容
- 格式化的 Markdown

### 2. 剪貼簿（macOS）
- 自動複製 Issue 內容到剪貼簿
- 可直接 Cmd+V 貼上

### 3. 檔案儲存
- 路徑：`/tmp/github-invite-<username>.md`
- 包含完整訊息 + 發送方式說明

## 發送方式

### 方法 1：手動建立 Issue（推薦）
1. 前往候選人的 GitHub repo
2. 點擊「Issues」tab
3. 點擊「New Issue」
4. 貼上標題和內容
5. 發送

### 方法 2：使用 GitHub CLI
```bash
# 安裝 GitHub CLI
brew install gh

# 登入
gh auth login

# 建立 Issue
gh issue create \
  --repo username/repo-name \
  --title "🎯 Talent Opportunity: AI工程師 at 知名AI科技公司" \
  --body "$(cat /tmp/github-invite-username.md)"
```

### 方法 3：使用 GitHub API
```bash
curl -X POST \
  -H "Authorization: token YOUR_GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/username/repo-name/issues \
  -d @/tmp/github-invite-username.md
```

## 訊息範本

### 標題格式
```
🎯 Talent Opportunity: [職位名稱] at [公司名稱/知名企業]
```

### 內容格式
```markdown
Hi @username 👋

我們在 GitHub 上發現您的專案，對您在 **技能** 方面的經驗印象深刻！

我們目前正在為一家 **公司類型** 尋找 **職位名稱** 人才，這個職缺可能很適合您：

**職位亮點：**
- 💰 薪資範圍：...
- 📍 地點：...
- 🚀 技術棧：...

如果您有興趣了解更多，歡迎：
1. 回覆這個 Issue
2. 或透過 Email 聯繫：...

我們會提供更完整的職缺資訊與公司介紹。

謝謝您的時間！🙏

---
*This is an automated talent matching message. If you're not interested, feel free to close this issue.*
```

## 使用場景

### 場景 1：從 GitHub 搜尋找到候選人
```bash
# 搜尋 AI 工程師
./github-talent-search.py "AI工程師" --limit 10

# 對每個候選人生成邀請訊息
./github-invite-message.sh candidate1 "AI工程師"
./github-invite-message.sh candidate2 "AI工程師"
```

### 場景 2：針對特定職缺批量邀請
```bash
# 創樂 PM 職缺（需要體育項目經驗）
./github-invite-message.sh username "專案經理(PM)"
# 手動補充：「過往專案類型要有體育項目相關經驗」
```

### 場景 3：匿名企業邀請
```bash
./github-invite-message.sh username "AI工程師"
# 選擇 y（匿名企業）
# 顯示：「知名AI科技公司」而非實際公司名
```

## 注意事項

1. **禁止濫發**：
   - 每個候選人最多發 1 次
   - 間隔至少 1 週以上
   - 確認候選人技能真的匹配

2. **禮貌原則**：
   - 使用專業語氣
   - 提供明確的職缺資訊
   - 尊重候選人選擇

3. **隱私保護**：
   - 匿名企業選項
   - 不透露敏感資訊
   - 只在公開 repo 發 Issue

4. **回覆追蹤**：
   - 定期檢查 Issue 回覆
   - 24 小時內回應
   - 記錄到進度追蹤（W 欄）

## 整合到履歷池

當候選人回覆後：

1. **匯入履歷池**：
   ```bash
   ./import-resume-to-pool.sh
   ```

2. **更新來源**：
   - L 欄（來源）：`GitHub - 主動邀請`

3. **新增進度**：
   - W 欄（進度追蹤）：
     ```json
     [
       {"date":"2026-02-24","event":"已聯繫","by":"Jacky","note":"透過 GitHub Issue 邀請"}
     ]
     ```

4. **記錄備註**：
   - T 欄（備註）：`應徵：AI工程師 (知名AI科技公司)`

## 疑難排解

### Q: 剪貼簿沒有自動複製？
A: 檢查是否為 macOS 系統，或手動複製輸出的內容。

### Q: 如何知道候選人的主要 repo？
A: 查看候選人的 GitHub Profile，選擇 star 最多或最近更新的 repo。

### Q: 候選人沒有回覆怎麼辦？
A: 等待 1 週，如果仍無回覆，標記為「未回應」，不再追蹤。

### Q: 如何批量發送？
A: 不建議批量自動發送，建議手動逐一確認候選人匹配度後再發送。

## 成效追蹤

建議記錄以下數據：

- **發送數量**：每週發送幾位候選人
- **回覆率**：多少候選人回覆
- **轉換率**：多少候選人進入面試
- **成功率**：多少候選人最終錄取

範例：
```
2026-02-24 週報：
- 發送：10 位 AI 工程師候選人
- 回覆：3 位（30%）
- 面試：1 位（10%）
- 錄取：0 位（0%）
```

---

**相關文件**：
- [履歷池管理](/Users/user/clawd/hr-tools/README-履歷池.md)
- [LinkedIn 履歷處理](/Users/user/clawd/projects/step1ne-headhunter-skill/docs/LINKEDIN-RESUME-PROCESSING.md)
- [GitHub 人才搜尋](/Users/user/clawd/hr-tools/github-talent-search.py)
