#!/bin/bash
# 每週市場調查報告自動生成腳本
# 使用方式：./weekly-report.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$SKILL_DIR/data"
OUTPUT_DIR="/tmp/aijob-presentations"
DATE=$(date +%Y-%m-%d)

echo "📊 開始製作市場調查報告（$DATE）"

# 建立資料夾
mkdir -p "$DATA_DIR"

# Step 1：收集市場數據
echo "🔍 Step 1：收集市場數據..."
"$SCRIPT_DIR/collect-market-data.sh" > "$DATA_DIR/market-data-$DATE.md"
echo "   ✅ 市場數據已收集"

# Step 2：整理內部數據
echo "📋 Step 2：整理內部數據..."
"$SCRIPT_DIR/analyze-internal-data.sh" > "$DATA_DIR/internal-stats-$DATE.json"
echo "   ✅ 內部數據已整理"

# Step 3：生成 HTML 報告
echo "📄 Step 3：生成 HTML 報告..."
"$SCRIPT_DIR/generate-report.sh" \
  --market-data "$DATA_DIR/market-data-$DATE.md" \
  --internal-data "$DATA_DIR/internal-stats-$DATE.json" \
  --output "$OUTPUT_DIR/market-analysis-$DATE.html"
echo "   ✅ HTML 報告已生成"

# Step 4：上傳 GitHub Pages
echo "🚀 Step 4：上傳 GitHub Pages..."
cd "$OUTPUT_DIR"
git add "market-analysis-$DATE.html"
git commit -m "市場調查報告 $DATE"
git push
echo "   ✅ 報告已上線"

# Step 5：發送通知（需要 message 工具）
echo "📨 Step 5：發送通知..."
REPORT_URL="https://jacky6658.github.io/aijob-presentations/market-analysis-$DATE.html"
echo "   報告連結：$REPORT_URL"

echo ""
echo "✅ 完成！報告已發布："
echo "   $REPORT_URL"
