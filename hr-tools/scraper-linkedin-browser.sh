#!/bin/bash
# LinkedIn 公開個人檔案爬蟲（使用 agent-browser）

KEYWORD="$1"
MAX_RESULTS="${2:-10}"
OUTPUT="${3:-/tmp/linkedin-candidates.json}"

echo "🔍 搜尋 LinkedIn 個人檔案：$KEYWORD"

# 1. Google 搜尋 LinkedIn 個人檔案
ENCODED_KEYWORD=$(echo "$KEYWORD Taiwan site:linkedin.com/in" | sed 's/ /%20/g')
GOOGLE_URL="https://www.google.com/search?q=$ENCODED_KEYWORD&num=$MAX_RESULTS"

echo "📍 Google 搜尋：$GOOGLE_URL"

# 使用 curl + grep 提取 LinkedIn URLs（比 agent-browser 快）
LINKEDIN_URLS=$(curl -s -A "Mozilla/5.0" "$GOOGLE_URL" | \
  grep -oE 'https://[a-z]+\.linkedin\.com/in/[^"&<>?]+' | \
  head -n "$MAX_RESULTS" | \
  sort -u)

echo "✅ 找到 $(echo "$LINKEDIN_URLS" | wc -l) 個 LinkedIn 個人檔案"
echo ""

# 2. 訪問每個 LinkedIn 個人檔案
CANDIDATES="[]"
INDEX=0

for url in $LINKEDIN_URLS; do
  INDEX=$((INDEX + 1))
  echo "[$INDEX] 訪問：$url"
  
  # 使用 agent-browser 抓取頁面
  agent-browser navigate "$url" --wait 3000
  agent-browser snapshot > /tmp/linkedin-profile-$INDEX.txt
  
  # 提取資訊（簡單解析）
  NAME=$(cat /tmp/linkedin-profile-$INDEX.txt | grep -m1 "^[A-Z]" | head -1 | tr -d '\n')
  COMPANY=$(cat /tmp/linkedin-profile-$INDEX.txt | grep -i "company\|at " | head -1 | sed 's/.*at //' | tr -d '\n')
  
  # 組成 JSON
  CANDIDATE=$(cat <<EOF
{
  "name": "$NAME",
  "company": "$COMPANY",
  "linkedin_url": "$url",
  "source": "linkedin_public",
  "platforms": ["linkedin"]
}
EOF
)
  
  # 加入陣列
  CANDIDATES=$(echo "$CANDIDATES" | jq ". += [$CANDIDATE]")
  
  echo "  ✅ $NAME - $COMPANY"
  echo ""
  
  # 避免被擋
  sleep 3
done

# 3. 輸出結果
echo "$CANDIDATES" > "$OUTPUT"

echo "💾 結果已存至 $OUTPUT"
echo "✅ 完成：$INDEX 位候選人"
