#!/bin/bash
# LinkedIn 搜尋 via OpenClaw Agent
# 直接調用 OpenClaw agent 執行 web_search

QUERY="$1"
MAX_RESULTS="${2:-10}"
OUTPUT_FILE="/tmp/linkedin-candidates-$(date +%s).json"

if [ -z "$QUERY" ]; then
  echo "用法: $0 \"搜尋關鍵字\" [數量]"
  exit 1
fi

echo "🔍 LinkedIn 搜尋: $QUERY"

# 建立臨時任務檔案
TASK_FILE="/tmp/linkedin-search-task-$$.txt"
cat > "$TASK_FILE" << EOF
使用 web_search 工具搜尋 LinkedIn 候選人：

搜尋字串：$QUERY site:linkedin.com/in
數量：$MAX_RESULTS

請提取每個結果的：
- 姓名
- 職位
- 公司
- 地點
- LinkedIn URL

將結果以 JSON 格式輸出到：$OUTPUT_FILE

格式：
[
  {
    "name": "候選人姓名",
    "title": "職位",
    "company": "公司",
    "location": "地點",
    "url": "LinkedIn URL"
  }
]

完成後回覆：DONE
EOF

# 調用 OpenClaw agent 執行任務
openclaw agent run \
  --message "$(cat $TASK_FILE)" \
  --model "anthropic/claude-sonnet-4-5" \
  --timeout 120 \
  > /tmp/agent-output-$$.txt 2>&1

# 清理
rm -f "$TASK_FILE"

# 檢查結果
if [ -f "$OUTPUT_FILE" ]; then
  COUNT=$(jq '. | length' "$OUTPUT_FILE" 2>/dev/null || echo "0")
  echo "✅ 找到 $COUNT 人"
  echo "$OUTPUT_FILE"
else
  echo "❌ 搜尋失敗"
  echo "[]" > "$OUTPUT_FILE"
  echo "$OUTPUT_FILE"
fi
