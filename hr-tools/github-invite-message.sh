#!/bin/bash
# GitHub 候選人邀請訊息生成器
# 用途：為 GitHub 候選人生成職缺邀請訊息（Issue 格式）

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 顯示使用說明
show_help() {
    echo ""
    echo "GitHub 候選人邀請訊息生成器"
    echo ""
    echo "用法："
    echo "  $0 <GitHub-username> <職缺名稱>"
    echo ""
    echo "範例："
    echo "  $0 jackyyuqi \"AI工程師\""
    echo ""
    exit 1
}

# 參數檢查
if [ $# -lt 2 ]; then
    show_help
fi

GITHUB_USER="$1"
JOB_TITLE="$2"

echo -e "${BLUE}🔍 正在生成 GitHub 邀請訊息...${NC}"
echo ""
echo -e "${YELLOW}候選人：${NC}@${GITHUB_USER}"
echo -e "${YELLOW}職缺：${NC}${JOB_TITLE}"
echo ""

# 互動式輸入職缺資訊
echo -e "${GREEN}請輸入職缺資訊（按 Enter 使用預設值）：${NC}"
echo ""

read -p "💰 薪資範圍（例：80-120k）: " SALARY
SALARY=${SALARY:-"面議"}

read -p "📍 工作地點（例：台北市/遠端）: " LOCATION
LOCATION=${LOCATION:-"台北市"}

read -p "🚀 技術棧（例：Python, TensorFlow, Docker）: " TECH_STACK
TECH_STACK=${TECH_STACK:-"請參考職缺說明"}

read -p "🏢 公司類型（例：AI科技公司/知名遊戲公司）: " COMPANY_TYPE
COMPANY_TYPE=${COMPANY_TYPE:-"知名企業"}

read -p "🎯 候選人技能（例：Python, AI, Machine Learning）: " SKILLS
SKILLS=${SKILLS:-"相關技術"}

read -p "📧 聯絡 Email: " CONTACT_EMAIL
CONTACT_EMAIL=${CONTACT_EMAIL:-"hr@step1ne.com"}

# 是否匿名企業
read -p "🔒 是否匿名企業？(y/n, 預設 n): " IS_ANONYMOUS
IS_ANONYMOUS=${IS_ANONYMOUS:-"n"}

if [ "$IS_ANONYMOUS" = "y" ]; then
    COMPANY_DISPLAY="知名${COMPANY_TYPE}"
else
    read -p "🏢 公司名稱: " COMPANY_NAME
    COMPANY_DISPLAY="${COMPANY_NAME}"
fi

echo ""
echo -e "${GREEN}✅ 資料收集完成！${NC}"
echo ""

# 生成 Issue 標題
ISSUE_TITLE="🎯 Talent Opportunity: ${JOB_TITLE} at ${COMPANY_DISPLAY}"

# 生成 Issue 內容
ISSUE_BODY="Hi @${GITHUB_USER} 👋

我們在 GitHub 上發現您的專案，對您在 **${SKILLS}** 方面的經驗印象深刻！

我們目前正在為一家 **${COMPANY_TYPE}** 尋找 **${JOB_TITLE}** 人才，這個職缺可能很適合您：

**職位亮點：**
- 💰 薪資範圍：${SALARY}
- 📍 地點：${LOCATION}
- 🚀 技術棧：${TECH_STACK}

如果您有興趣了解更多，歡迎：
1. 回覆這個 Issue
2. 或透過 Email 聯繫：${CONTACT_EMAIL}

我們會提供更完整的職缺資訊與公司介紹。

謝謝您的時間！🙏

---
*This is an automated talent matching message. If you're not interested, feel free to close this issue.*"

# 顯示生成的訊息
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}📝 GitHub Issue 訊息已生成！${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}【Issue 標題】${NC}"
echo "$ISSUE_TITLE"
echo ""
echo -e "${YELLOW}【Issue 內容】${NC}"
echo "$ISSUE_BODY"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 複製到剪貼簿（macOS）
if command -v pbcopy &> /dev/null; then
    echo "$ISSUE_BODY" | pbcopy
    echo -e "${GREEN}✅ Issue 內容已複製到剪貼簿！${NC}"
    echo ""
fi

# 產生檔案
OUTPUT_FILE="/tmp/github-invite-${GITHUB_USER}.md"
cat > "$OUTPUT_FILE" << EOF
# GitHub Issue 邀請訊息

**候選人**: @${GITHUB_USER}
**職缺**: ${JOB_TITLE}
**生成時間**: $(date '+%Y-%m-%d %H:%M:%S')

---

## Issue 標題
${ISSUE_TITLE}

---

## Issue 內容
${ISSUE_BODY}

---

## 發送方式

### 方法 1：手動建立 Issue
1. 前往候選人的 GitHub repo（例：https://github.com/${GITHUB_USER}/repo-name）
2. 點擊「Issues」tab
3. 點擊「New Issue」
4. 貼上標題和內容
5. 發送

### 方法 2：使用 GitHub CLI
\`\`\`bash
# 安裝 GitHub CLI (如果尚未安裝)
brew install gh

# 登入
gh auth login

# 建立 Issue（替換 REPO_NAME）
gh issue create \\
  --repo ${GITHUB_USER}/REPO_NAME \\
  --title "${ISSUE_TITLE}" \\
  --body "${ISSUE_BODY}"
\`\`\`

### 方法 3：使用 GitHub API
\`\`\`bash
curl -X POST \\
  -H "Authorization: token YOUR_GITHUB_TOKEN" \\
  -H "Accept: application/vnd.github.v3+json" \\
  https://api.github.com/repos/${GITHUB_USER}/REPO_NAME/issues \\
  -d '{
    "title": "${ISSUE_TITLE}",
    "body": "${ISSUE_BODY}"
  }'
\`\`\`
EOF

echo -e "${GREEN}📄 完整訊息已儲存至：${NC}${OUTPUT_FILE}"
echo ""

# 詢問是否要開啟檔案
read -p "是否要開啟檔案查看？(y/n): " OPEN_FILE
if [ "$OPEN_FILE" = "y" ]; then
    if command -v open &> /dev/null; then
        open "$OUTPUT_FILE"
    elif command -v xdg-open &> /dev/null; then
        xdg-open "$OUTPUT_FILE"
    fi
fi

echo ""
echo -e "${GREEN}✨ 完成！${NC}"
echo ""
