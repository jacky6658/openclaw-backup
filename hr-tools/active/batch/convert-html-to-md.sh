#!/bin/bash
# HTML 市場報告轉 Markdown
# 用於季度歸檔

set -e

if [ $# -lt 1 ]; then
    echo "用法: $0 <HTML檔案路徑>"
    echo "範例: $0 /tmp/aijob-presentations/market-analysis-2026.02.11.html"
    exit 1
fi

HTML_FILE="$1"
BASENAME=$(basename "$HTML_FILE" .html)

# 提取日期（格式：market-analysis-2026.02.11.html → 2026.02.11）
DATE=$(echo "$BASENAME" | grep -oE '[0-9]{4}\.[0-9]{2}\.[0-9]{2}')

if [ -z "$DATE" ]; then
    echo "❌ 錯誤：無法從檔名提取日期"
    exit 1
fi

# 計算季度
MONTH=$(echo "$DATE" | cut -d. -f2)
if [ "$MONTH" -le 3 ]; then
    QUARTER="Q1"
elif [ "$MONTH" -le 6 ]; then
    QUARTER="Q2"
elif [ "$MONTH" -le 9 ]; then
    QUARTER="Q3"
else
    QUARTER="Q4"
fi

YEAR=$(echo "$DATE" | cut -d. -f1)
OUTPUT_DIR="$HOME/market-reports-archive/$YEAR/$QUARTER"
OUTPUT_FILE="$OUTPUT_DIR/$DATE.md"

mkdir -p "$OUTPUT_DIR"

echo "🔄 轉換中：$HTML_FILE → $OUTPUT_FILE"

# 使用 pandoc 轉換（如果有安裝）
if command -v pandoc &> /dev/null; then
    pandoc "$HTML_FILE" -f html -t markdown -o "$OUTPUT_FILE"
else
    # 簡易轉換（移除 HTML 標籤，保留文字）
    cat > "$OUTPUT_FILE" << EOF
# 市場調查分析報告

**報告日期**：$DATE  
**來源**：Step1ne 獵頭系統

---

**注意**：此為 HTML 自動轉換版本。完整排版請參考原始 HTML 檔案。

原始檔案：\`$(basename "$HTML_FILE")\`

---

EOF
    
    # 提取關鍵內容（移除 HTML 標籤）
    sed -e 's/<[^>]*>//g' \
        -e 's/&nbsp;/ /g' \
        -e 's/&lt;/</g' \
        -e 's/&gt;/>/g' \
        -e 's/&amp;/\&/g' \
        -e '/^[[:space:]]*$/d' \
        "$HTML_FILE" >> "$OUTPUT_FILE"
fi

echo "✅ 轉換完成：$OUTPUT_FILE"
echo "📊 檔案大小：$(du -h "$OUTPUT_FILE" | cut -f1)"
