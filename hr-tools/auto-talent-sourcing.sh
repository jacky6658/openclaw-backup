#!/bin/bash

# 自動人才搜尋 + 龍蝦社回報
# 每 2 小時執行一次

set -e

LOG_FILE="/tmp/talent-sourcing-$(date +%Y%m%d-%H%M%S).log"

echo "🚀 開始人才搜尋執行..." | tee "$LOG_FILE"
echo "時間：$(date)" >> "$LOG_FILE"

# 執行爬蟲（4個職位的組合）
# Jacky 的職位：51(C++), 52(Java), 15(資安), 19(.NET)
python3 /Users/user/clawd/hr-tools/talent_sourcing_pipeline.py \
  --job-ids 51,52,15,19 \
  --execute \
  2>&1 | tee -a "$LOG_FILE"

RESULT=$?

# 提取成果統計
if [ $RESULT -eq 0 ]; then
  # 從 log 中提取統計資訊
  SUMMARY=$(tail -30 "$LOG_FILE" | grep -A 20 "【成果統計】" || echo "")
  
  REPORT="✅ 人才搜尋成功完成！

時間：$(date '+%Y-%m-%d %H:%M:%S')

📊 本次搜尋職位：
• ID 51 - C++ Developer (一通數位)
• ID 52 - Java Developer (一通數位)
• ID 15 - 資安工程師 (遊戲橘子)
• ID 19 - .NET 後端 (遊戲橘子)

✅ 狀態：成功
📝 詳細日誌：$LOG_FILE

$SUMMARY"
else
  REPORT="❌ 人才搜尋執行失敗

時間：$(date '+%Y-%m-%d %H:%M:%S')

🔍 搜尋職位：ID 51,52,15,19
❌ 狀態：失敗 (Exit Code: $RESULT)
📝 詳細日誌：$LOG_FILE"
fi

# 回報到龍蝦社 (群組 -1003793194829, Topic 15)
echo "📤 正在回報到龍蝦社..."
message send --target "-1003793194829" --topic "15" --message "$REPORT"

echo "✅ 回報完成！"
