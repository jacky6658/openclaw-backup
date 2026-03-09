#!/bin/bash
# 季度歸檔腳本 - 每季度最後一天執行
# 將 aijob-presentations 中 >12 週的報告歸檔到 market-reports-archive

set -e

PRESENTATIONS_DIR="/tmp/aijob-presentations"
ARCHIVE_DIR="/Users/user/clawd/market-reports-archive"
SCRIPT_DIR="/Users/user/clawd/hr-tools"

# 顏色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}📦 開始季度歸檔...${NC}"
echo "日期：$(date '+%Y-%m-%d %H:%M:%S')"

# 計算 12 週前的日期
CUTOFF_DATE=$(date -v-12w '+%Y.%m.%d')
echo -e "${YELLOW}🗓️  保留日期：$CUTOFF_DATE 之後${NC}"

cd "$PRESENTATIONS_DIR"

# 找出所有需要歸檔的 HTML 報告
OLD_REPORTS=$(ls market-analysis-*.*.*.html 2>/dev/null | while read file; do
    FILE_DATE=$(echo "$file" | grep -oE '[0-9]{4}\.[0-9]{2}\.[0-9]{2}')
    if [[ "$FILE_DATE" < "$CUTOFF_DATE" ]]; then
        echo "$file"
    fi
done)

if [ -z "$OLD_REPORTS" ]; then
    echo -e "${GREEN}✅ 無需歸檔的舊報告${NC}"
    exit 0
fi

ARCHIVE_COUNT=0

while IFS= read -r html_file; do
    if [ -z "$html_file" ]; then
        continue
    fi
    
    echo -e "${BLUE}📄 處理：$html_file${NC}"
    
    # 轉換為 Markdown
    bash "$SCRIPT_DIR/convert-html-to-md.sh" "$PRESENTATIONS_DIR/$html_file"
    
    # 刪除原始 HTML
    rm "$PRESENTATIONS_DIR/$html_file"
    echo -e "${YELLOW}🗑️  已刪除：$html_file${NC}"
    
    ARCHIVE_COUNT=$((ARCHIVE_COUNT + 1))
done <<< "$OLD_REPORTS"

# 提交到 Git
cd "$ARCHIVE_DIR"
git add -A
git commit -m "季度歸檔：$(date '+%Y Q%q') - 歸檔 $ARCHIVE_COUNT 份報告"
git push

# 更新展示站（刪除舊 HTML）
cd "$PRESENTATIONS_DIR"
git add -A
git commit -m "季度清理：移除 >12 週的舊報告（已歸檔到 market-reports-archive）"
git push

echo -e "${GREEN}✅ 季度歸檔完成！${NC}"
echo -e "${GREEN}📊 歸檔數量：$ARCHIVE_COUNT 份${NC}"
echo -e "${GREEN}🔗 歸檔庫：https://github.com/jacky6658/market-reports-archive${NC}"
