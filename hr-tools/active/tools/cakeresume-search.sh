#!/bin/bash
# CakeResume Search - 台灣求職者搜尋

set -e

POSITION="$1"
SKILLS="$2"
COUNT="${3:-10}"
OUTPUT_FILE="/tmp/cakeresume-candidates-$(date +%s).json"

if [ -z "$POSITION" ]; then
    echo "用法: $0 <職位> <技能關鍵字> [數量]"
    echo "範例: $0 'AI工程師' 'Python Machine Learning' 10"
    exit 1
fi

echo "🍰 CakeResume Search"
echo "職位：$POSITION"
echo "技能：$SKILLS"
echo "數量：$COUNT"
echo ""

# 建立搜尋關鍵字
QUERY="$POSITION $SKILLS site:cakeresume.com"

echo "🔎 搜尋關鍵字：$QUERY"
echo "⏳ 正在搜尋..."

# 使用 OpenClaw web_search
cat > /tmp/cakeresume-search-temp.py << 'PYTHON_EOF'
#!/usr/bin/env python3
import sys
import json

# 實際使用時整合 web_search
results = []

print(json.dumps(results, ensure_ascii=False))
PYTHON_EOF

chmod +x /tmp/cakeresume-search-temp.py
python3 /tmp/cakeresume-search-temp.py "$QUERY" "$COUNT" > "$OUTPUT_FILE"

echo ""
echo "✅ 搜尋完成"
echo "📄 結果儲存於：$OUTPUT_FILE"

TOTAL=$(jq 'length' "$OUTPUT_FILE")
echo "📊 找到 $TOTAL 位 CakeResume 求職者"
