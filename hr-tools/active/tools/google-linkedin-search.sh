#!/bin/bash
# Google + LinkedIn 公開資料搜尋
# 用法: ./google-linkedin-search.sh "Finance Manager Cambodia" 20

set -e

QUERY="$1"
MAX_RESULTS="${2:-10}"
OUTPUT_FILE="/tmp/linkedin-candidates-$(date +%s).json"

if [ -z "$QUERY" ]; then
  echo "用法: $0 \"搜尋關鍵字\" [數量]"
  exit 1
fi

echo "🔍 開始搜尋：$QUERY"
echo "📊 目標數量：$MAX_RESULTS"

# 建立 Python 腳本呼叫 OpenClaw web_search
cat > /tmp/linkedin-search-wrapper.py << 'PYTHON_EOF'
#!/usr/bin/env python3
import sys
import json
import subprocess

query = sys.argv[1]
max_results = int(sys.argv[2])
output_file = sys.argv[3]

# 構建 LinkedIn 搜尋查詢
search_query = f"{query} site:linkedin.com/in"

print(f"🔍 搜尋：{search_query}", file=sys.stderr)

# 呼叫 OpenClaw web_search（透過 CLI）
cmd = [
    "openclaw", "agent", "run",
    "--message", f"使用 web_search 工具搜尋：{search_query}，count={max_results}。只回傳 JSON 格式結果，不要其他文字。格式：[{{\"name\":\"\",\"title\":\"\",\"company\":\"\",\"location\":\"\",\"url\":\"\"}}]",
    "--model", "anthropic/claude-sonnet-4-5"
]

try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    
    if result.returncode == 0:
        # 嘗試從輸出中提取 JSON
        output = result.stdout
        
        # 簡單解析：尋找候選人資訊
        candidates = []
        
        # 這裡先輸出原始結果，讓我們看看格式
        print(f"✅ 搜尋完成", file=sys.stderr)
        
        # 暫時輸出空陣列，等待進一步整合
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(candidates, f, ensure_ascii=False, indent=2)
        
        print(f"📄 結果儲存於：{output_file}", file=sys.stderr)
    else:
        print(f"❌ 搜尋失敗：{result.stderr}", file=sys.stderr)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump([], f)
        
except Exception as e:
    print(f"❌ 執行錯誤：{e}", file=sys.stderr)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump([], f)

PYTHON_EOF

chmod +x /tmp/linkedin-search-wrapper.py

# 執行搜尋
python3 /tmp/linkedin-search-wrapper.py "$QUERY" "$MAX_RESULTS" "$OUTPUT_FILE"

# 回傳結果
if [ -f "$OUTPUT_FILE" ]; then
  COUNT=$(cat "$OUTPUT_FILE" | jq '. | length' 2>/dev/null || echo "0")
  echo "✅ 找到 $COUNT 人"
  cat "$OUTPUT_FILE"
else
  echo "❌ 搜尋失敗"
  echo "[]"
fi
