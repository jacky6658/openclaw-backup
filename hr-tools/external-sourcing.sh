#!/bin/bash
# 對外搜尋候選人 - GitHub + LinkedIn
# 不使用履歷池，完全從外部搜尋

set -e

JD_ID="$1"
OUTPUT_FILE="${2:-/tmp/external-candidates.json}"

# 提取職位關鍵字（移除公司名稱）
JD_TITLE=$(echo "$JD_ID" | sed 's/-.*$//')

echo "=========================================="
echo "對外搜尋：$JD_TITLE"
echo "=========================================="

# 1. GitHub 搜尋
echo "→ GitHub 搜尋..."
# 替換職位關鍵字，保留空格
GITHUB_KEYWORDS=$(echo "$JD_TITLE" | sed 's/工程師/ engineer/g; s/專案經理/ project manager/g; s/產品經理/ product manager/g; s/測試/ test/g; s/自動化/ automation/g')

# URL encode 空格為 +
GITHUB_QUERY=$(echo "$GITHUB_KEYWORDS" | sed 's/ /+/g')

GITHUB_RESULTS=$(curl -s "https://api.github.com/search/users?q=location:Taiwan+$GITHUB_QUERY&per_page=10" 2>&1)

# 檢查是否有錯誤
if echo "$GITHUB_RESULTS" | grep -q '"login"'; then
  echo "$GITHUB_RESULTS" | jq -r '.items[] | {
    name: .login,
    github_url: .html_url,
    source: "GitHub",
    platforms: ["github"],
    skills: [],
    years_of_experience: 3,
    industry: "科技",
    location: "taipei"
  }' | jq -s '.' > /tmp/github-temp.json
  
  GITHUB_COUNT=$(cat /tmp/github-temp.json | jq 'length')
  echo "  ✓ GitHub：$GITHUB_COUNT 位"
else
  echo "[]" > /tmp/github-temp.json
  echo "  ⚠️  GitHub API 錯誤"
fi

# 2. LinkedIn 搜尋（使用 OpenClaw）
echo "→ LinkedIn 搜尋..."

# 建立搜尋關鍵字
LINKEDIN_QUERY="$JD_TITLE Taiwan site:linkedin.com/in"

# 這裡需要用 OpenClaw 的 web_search，但 bash 無法直接呼叫
# 改用 Python 呼叫
python3 << PYTHON_EOF
import json
import subprocess

# 暫時用空陣列，實際應該用 web_search
linkedin_results = []

with open('/tmp/linkedin-temp.json', 'w') as f:
    json.dump(linkedin_results, f)

print("  ⚠️  LinkedIn 搜尋待實作（需要 OpenClaw web_search）")
PYTHON_EOF

# 合併結果
jq -s 'add' /tmp/github-temp.json /tmp/linkedin-temp.json > "$OUTPUT_FILE"

TOTAL=$(cat "$OUTPUT_FILE" | jq 'length')
echo ""
echo "✅ 總計：$TOTAL 位候選人"
echo "結果：$OUTPUT_FILE"
