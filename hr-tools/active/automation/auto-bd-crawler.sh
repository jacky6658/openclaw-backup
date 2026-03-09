#!/bin/bash

# BD 自動開發爬蟲
# 每2天凌晨 01:00-06:00，每小時開發 10 家公司

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHEET_ID="1bkI7_cCh_Bs4qVa3HlXiy0CFzmItZlA-DYGHSPS4InE"
ACCOUNT="aiagentg888@gmail.com"
LOG_FILE="$SCRIPT_DIR/auto-bd-crawler.log"

# 搜尋關鍵字（輪流使用不同關鍵字）
KEYWORDS=(
    "軟體工程師"
    "後端工程師"
    "前端工程師"
    "AI工程師"
    "數據分析師"
    "產品經理"
)

# 隨機選擇一個關鍵字
KEYWORD="${KEYWORDS[$RANDOM % ${#KEYWORDS[@]}]}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "========== BD 自動開發開始 =========="
log "搜尋關鍵字：$KEYWORD"
log "目標：10 家公司"

# 執行 104 搜尋
log "🔍 搜尋 104 招聘公司..."
python3 "$SCRIPT_DIR/scraper-104.py" "$KEYWORD" 10 > "$SCRIPT_DIR/temp-companies.json"

if [[ ! -f "$SCRIPT_DIR/temp-companies.json" ]]; then
    log "❌ 搜尋失敗"
    exit 1
fi

FOUND_COUNT=$(jq 'length' "$SCRIPT_DIR/temp-companies.json")
log "✅ 找到 $FOUND_COUNT 家公司"

# 逐家處理
ADDED=0
SKIPPED=0

jq -c '.[]' "$SCRIPT_DIR/temp-companies.json" | while read -r company; do
    NAME=$(echo "$company" | jq -r '.company')
    WEBSITE=$(echo "$company" | jq -r '.website // "找不到"')
    PAGE104=$(echo "$company" | jq -r '.url')
    
    log "📝 處理：$NAME"
    
    # 檢查是否已存在
    EXISTING=$(gog sheets get "$SHEET_ID" "工作表1!A:A" --plain --account "$ACCOUNT" 2>/dev/null | grep -c "^$NAME$" || true)
    
    if [[ $EXISTING -gt 0 ]]; then
        log "   ⚠️ 已存在，跳過"
        SKIPPED=$((SKIPPED + 1))
        sleep 1
        continue
    fi
    
    # 爬取聯絡方式
    EMAIL="待查"
    PHONE="待查"
    STATUS="待顧問電話開發"
    
    if [[ "$WEBSITE" != "找不到" ]] && [[ "$WEBSITE" != "暫不提供" ]]; then
        log "   🌐 爬取網站：$WEBSITE"
        
        # 使用 scrape-contact 工具
        CONTACT_INFO=$(bash "$SCRIPT_DIR/scrape-contact-from-website.sh" "$WEBSITE" 2>/dev/null | grep -E "Email:|電話:" || true)
        
        if [[ -n "$CONTACT_INFO" ]]; then
            EMAIL=$(echo "$CONTACT_INFO" | grep "Email:" | sed 's/.*Email: //' | xargs || echo "待查")
            PHONE=$(echo "$CONTACT_INFO" | grep "電話:" | sed 's/.*電話: //' | xargs || echo "待查")
        fi
        
        # 如果找到 Email，改為「待寄信」
        if [[ "$EMAIL" != "待查" ]] && [[ "$EMAIL" != "" ]]; then
            STATUS="待寄信"
            log "   ✅ 找到 Email: $EMAIL"
        else
            log "   ⚠️ 未找到 Email"
        fi
    fi
    
    # 寫入 Google Sheets
    TODAY=$(date '+%Y-%m-%d')
    ROW_DATA='[["'$NAME'", "", "", "", "'$PHONE'", "'$EMAIL'", "'$WEBSITE'", "'$PAGE104'", "", "", "", "'$STATUS'", "'$TODAY'", "AI開發"]]'
    
    log "   💾 寫入資料庫..."
    gog sheets append "$SHEET_ID" "工作表1!A:N" \
        --values-json "$ROW_DATA" \
        --insert INSERT_ROWS \
        --account "$ACCOUNT" >> "$LOG_FILE" 2>&1
    
    ADDED=$((ADDED + 1))
    log "   ✅ 完成 ($ADDED/$FOUND_COUNT)"
    
    # 延遲 5-10 秒（反爬蟲）
    DELAY=$((5 + RANDOM % 6))
    log "   ⏳ 等待 $DELAY 秒..."
    sleep $DELAY
done

# 清理暫存
rm -f "$SCRIPT_DIR/temp-companies.json"

log "========== BD 自動開發完成 =========="
log "✅ 新增：$ADDED 家"
log "⚠️ 跳過：$SKIPPED 家（已存在）"

# 統計
TOTAL_PENDING=$(gog sheets get "$SHEET_ID" "工作表1!L:L" --plain --account "$ACCOUNT" 2>/dev/null | grep -c "待寄信" || echo "0")
TOTAL_CALL=$(gog sheets get "$SHEET_ID" "工作表1!L:L" --plain --account "$ACCOUNT" 2>/dev/null | grep -c "待顧問電話開發" || echo "0")

log "📊 目前狀態："
log "   • 待寄信：$TOTAL_PENDING"
log "   • 待顧問電話開發：$TOTAL_CALL"

# 輸出結果（會被 Cron 通知）
echo "🤖 BD 自動開發完成"
echo ""
echo "📊 本次結果："
echo "• 新增：$ADDED 家公司"
echo "• 跳過：$SKIPPED 家（已存在）"
echo ""
echo "📈 資料庫統計："
echo "• 待寄信：$TOTAL_PENDING"
echo "• 待顧問電話開發：$TOTAL_CALL"

exit 0
