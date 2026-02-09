#!/bin/bash
# 獵頭自動化每日執行腳本

set -e

SCRIPT_DIR="/Users/user/clawd/projects/headhunter-scraper/scripts"
DATA_DIR="/Users/user/clawd/projects/headhunter-scraper/data"
LOG_DIR="/Users/user/clawd/projects/headhunter-scraper/logs"
DATE=$(date +%Y%m%d)
LOG_FILE="$LOG_DIR/run_$DATE.log"

echo "🚀 獵頭自動化開始執行 - $(date)" | tee -a "$LOG_FILE"

# 1. 搜尋公司和求職者
echo "📊 步驟 1：搜尋資料..." | tee -a "$LOG_FILE"
cd "$SCRIPT_DIR"
python3 search_companies.py >> "$LOG_FILE" 2>&1

# 2. 取得最新結果檔案
RESULT_FILE="$DATA_DIR/results_$DATE.json"

if [ -f "$RESULT_FILE" ]; then
    echo "✅ 找到結果檔案：$RESULT_FILE" | tee -a "$LOG_FILE"
    
    # 3. 發送到 Telegram
    echo "📱 步驟 2：發送 Telegram 通知..." | tee -a "$LOG_FILE"
    python3 notify_telegram.py "$RESULT_FILE" >> "$LOG_FILE" 2>&1
    
    echo "✅ 執行完成 - $(date)" | tee -a "$LOG_FILE"
else
    echo "❌ 找不到結果檔案" | tee -a "$LOG_FILE"
    exit 1
fi

echo "----------------------------------------" | tee -a "$LOG_FILE"
