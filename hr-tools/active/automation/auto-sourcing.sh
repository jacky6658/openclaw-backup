#!/bin/bash
# 自動找人選系統 v1.0
# 用法: ./auto-sourcing.sh <JD_ID>
# 範例: ./auto-sourcing.sh 7  (志邦企業財會主管)

set -e

JD_ID="$1"

if [ -z "$JD_ID" ]; then
  echo "❌ 請提供 JD ID"
  echo "用法: ./auto-sourcing.sh <JD_ID>"
  exit 1
fi

echo "🔍 自動找人選系統啟動"
echo "📋 JD ID: $JD_ID"
echo ""

# 讀取 JD 資訊（從 Google Sheets）
echo "⏳ 讀取職缺資訊..."
JD_DATA=$(gog sheets get \
  --sheet-id "1QPaeOm-slNVFCeM8Q3gg3DawKjzp2tYwyfquvdHlZFE" \
  --range "A$JD_ID:K$JD_ID" \
  --account aijessie88@step1ne.com)

# 解析 JD 資料（簡化版，實際需要更複雜的解析）
JOB_TITLE=$(echo "$JD_DATA" | cut -d'|' -f1)
COMPANY=$(echo "$JD_DATA" | cut -d'|' -f2)
SKILLS=$(echo "$JD_DATA" | cut -d'|' -f6)
LOCATION=$(echo "$JD_DATA" | cut -d'|' -f9)

echo "✅ 職缺資訊："
echo "   職位: $JOB_TITLE"
echo "   公司: $COMPANY"
echo "   技能: $SKILLS"
echo "   地點: $LOCATION"
echo ""

# 建立搜尋關鍵字
SEARCH_QUERY="$JOB_TITLE $LOCATION"
echo "🔎 搜尋關鍵字: $SEARCH_QUERY"
echo ""

# 呼叫 Python 腳本執行搜尋（使用 OpenClaw web_search）
python3 /Users/user/clawd/hr-tools/auto-sourcing-search.py \
  --query "$SEARCH_QUERY" \
  --jd-id "$JD_ID" \
  --max-results 20

echo ""
echo "✅ 搜尋完成！"
echo "📊 結果已儲存並發送 Telegram 通知"
