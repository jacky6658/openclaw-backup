#!/bin/bash
# 使用 OpenClaw Cron 定時搜尋

DATE=$(date +%Y%m%d)
RESULT_FILE="/Users/user/clawd/projects/headhunter-scraper/data/results_$DATE.json"

# 初始化 JSON
echo '{"timestamp": "'$(date +"%Y-%m-%d %H:%M:%S")'", "companies": [], "candidates": []}' > "$RESULT_FILE"

echo "🚀 獵頭自動化搜尋開始 - $(date)"
echo "📊 結果將儲存至：$RESULT_FILE"
echo ""
echo "✅ 系統已就緒，等待 Cron 任務執行"
echo "   每天早上 9:00 自動搜尋並通知到 Telegram"
