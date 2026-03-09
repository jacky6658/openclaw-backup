#!/bin/bash
# 104人力銀行職缺搜尋腳本
# 用途：搜尋特定關鍵字的職缺，找出哪些公司在招人

KEYWORD="${1:-backend}"
OUTPUT_FILE="${2:-/tmp/104-jobs.json}"

echo "🔍 搜尋關鍵字: $KEYWORD"

# 開啟 104 搜尋頁面
agent-browser open "https://www.104.com.tw/jobs/search/?keyword=$KEYWORD" 2>/dev/null

# 等待頁面載入
sleep 2

# 取得搜尋結果快照
SNAPSHOT=$(agent-browser snapshot -i --json 2>/dev/null)

# 解析職缺資訊
echo "$SNAPSHOT" | jq -r '
  .data.refs | to_entries | 
  map(select(.value.role == "link")) |
  map(select(.value.name | test("Engineer|工程師|Developer|Backend|Frontend|Full.?Stack"; "i"))) |
  map({
    ref: .key,
    title: .value.name
  })
' > "$OUTPUT_FILE"

echo "✅ 結果已存至: $OUTPUT_FILE"
echo "📊 找到職缺數:"
cat "$OUTPUT_FILE" | jq 'length'

# 關閉瀏覽器
agent-browser close 2>/dev/null
