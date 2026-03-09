#!/bin/bash
# 每週自動找人選（Cron Job 用）

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TELEGRAM_GROUP="-1003231629634"
TELEGRAM_TOPIC="304"  # 履歷池

echo "🔍 開始每週自動找人選..."

# 讀取所有「招募中」職缺
JD_LIST=$(gog sheets get 1QPaeOm-slNVFCeM8Q3gg3DawKjzp2tYwyfquvdHlZFE "A2:L100" \
  --account aijessie88@step1ne.com --plain 2>/dev/null | \
  grep "開放中\|招募中" | \
  awk -F'\t' '{print $1}' | \
  head -3)  # 每週最多處理 3 個職缺

if [ -z "$JD_LIST" ]; then
  echo "⚠️  沒有找到招募中職缺"
  exit 0
fi

echo "✅ 找到招募中職缺："
echo "$JD_LIST"
echo ""

# 對每個職缺執行搜尋
while IFS= read -r JD_TITLE; do
  [ -z "$JD_TITLE" ] && continue
  
  echo "========================================="
  echo "處理職缺：$JD_TITLE"
  echo "========================================="
  
  # 1. GitHub 搜尋
  echo "🔍 GitHub 搜尋..."
  GITHUB_RESULTS=$(curl -s "https://api.github.com/search/users?q=location:Taiwan+$JD_TITLE&per_page=10" | \
    jq -r '.items[] | {name: .login, github_url: .html_url}' | \
    jq -s '.')
  
  GITHUB_COUNT=$(echo "$GITHUB_RESULTS" | jq 'length')
  echo "  → 找到 $GITHUB_COUNT 位"
  
  # 2. LinkedIn 搜尋（限制數量避免過慢）
  echo "🔍 LinkedIn 搜尋..."
  
  # 使用 web_search (Brave API)
  LINKEDIN_URLS=$(openclaw web-search "$JD_TITLE Taiwan site:linkedin.com/in" --count 5 2>/dev/null | \
    jq -r '.results[].url' 2>/dev/null | \
    grep "linkedin.com/in" | \
    head -5)
  
  LINKEDIN_COUNT=$(echo "$LINKEDIN_URLS" | wc -l)
  echo "  → 找到 $LINKEDIN_COUNT 個個人檔案"
  
  # 3. 發送通知
  TOTAL_COUNT=$((GITHUB_COUNT + LINKEDIN_COUNT))
  
  MESSAGE="📋 **每週自動找人選：$JD_TITLE**

✅ 找到 $TOTAL_COUNT 位候選人
• GitHub: $GITHUB_COUNT 位
• LinkedIn: $LINKEDIN_COUNT 位

💡 下一步：
請執行完整配對分析以取得詳細推薦

指令：
\`bash /Users/user/clawd/hr-tools/auto-sourcing-v2.sh \"$JD_TITLE\"\`"
  
  openclaw message send \
    --channel telegram \
    --target "$TELEGRAM_GROUP" \
    --thread-id "$TELEGRAM_TOPIC" \
    --message "$MESSAGE"
  
  echo "✅ 通知已發送"
  echo ""
  
  # 避免過快
  sleep 5
  
done <<< "$JD_LIST"

echo "✅ 每週自動找人選完成"
