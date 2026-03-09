#!/bin/bash
# GitHub Talent Search - 技術人才搜尋

set -e

POSITION="$1"
SKILLS="$2"
COUNT="${3:-10}"
OUTPUT_FILE="/tmp/github-candidates-$(date +%s).json"

if [ -z "$POSITION" ]; then
    echo "用法: $0 <職位> <技能關鍵字> [數量]"
    echo "範例: $0 'AI工程師' 'Python Machine Learning' 10"
    exit 1
fi

echo "🔍 GitHub Talent Search"
echo "職位：$POSITION"
echo "技能：$SKILLS"
echo "數量：$COUNT"
echo ""

# 建立搜尋關鍵字
QUERY="$SKILLS Taiwan site:github.com"

echo "🔎 搜尋關鍵字：$QUERY"
echo "⏳ 正在搜尋..."

# 使用 OpenClaw web_search（實際執行時會呼叫）
# 這裡先建立暫存檔案框架
cat > /tmp/github-search-temp.py << 'PYTHON_EOF'
#!/usr/bin/env python3
import sys
import json

# 這裡需要整合 OpenClaw web_search
# 暫時輸出空結果作為框架
results = []

# 實際使用時會這樣呼叫：
# results = web_search(query=sys.argv[1], count=int(sys.argv[2]))

print(json.dumps(results, ensure_ascii=False))
PYTHON_EOF

chmod +x /tmp/github-search-temp.py
python3 /tmp/github-search-temp.py "$QUERY" "$COUNT" > "$OUTPUT_FILE"

echo ""
echo "✅ 搜尋完成"
echo "📄 結果儲存於：$OUTPUT_FILE"

# 顯示結果統計
TOTAL=$(jq 'length' "$OUTPUT_FILE")
echo "📊 找到 $TOTAL 位 GitHub 開發者"
