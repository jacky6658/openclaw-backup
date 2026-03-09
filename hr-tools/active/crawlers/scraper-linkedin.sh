#!/bin/bash
# LinkedIn Job Search Scraper
# 使用 Chrome 已登入的 session

KEYWORD="$1"
LIMIT="${2:-10}"

echo "搜尋 LinkedIn: $KEYWORD (限制 $LIMIT 筆)"

# LinkedIn Jobs 搜尋 URL
SEARCH_URL="https://www.linkedin.com/jobs/search/?keywords=$(echo "$KEYWORD" | jq -sRr @uri)&location=台灣"

# 開啟搜尋頁面
open -a "Google Chrome" "$SEARCH_URL"

echo "✓ 已在 Chrome 開啟搜尋結果"
echo "URL: $SEARCH_URL"
echo ""
echo "請手動複製前 $LIMIT 筆職缺的公司名稱和職位"
echo "或者我可以嘗試自動化抓取（需要額外工具）"
