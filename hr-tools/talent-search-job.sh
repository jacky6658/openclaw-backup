#!/bin/bash
# talent-search-job.sh - 單一職缺人才搜尋
# 用法：bash talent-search-job.sh <job_id> <job_name>
# 範例：bash talent-search-job.sh 51 "C++ Developer"

JOB_ID="${1:-51}"
JOB_NAME="${2:-Developer}"
LOG_FILE="/tmp/talent-${JOB_ID}-$(date +%Y%m%d-%H%M%S).log"

echo "🚀 人才搜尋開始 [Job ${JOB_ID}：${JOB_NAME}]"
echo "時間：$(date '+%Y-%m-%d %H:%M:%S')"

# 執行爬蟲（單一職缺）
python3 /Users/user/clawd/hr-tools/talent_sourcing_pipeline.py \
  --job-id "$JOB_ID" \
  --execute \
  2>&1 | tee "$LOG_FILE"

EXIT_CODE=$?

# 擷取統計摘要
UPLOADED=$(grep -oE '上傳.*?位' "$LOG_FILE" | tail -1 || echo "")
TOTAL=$(grep -oE '去重後.*?位' "$LOG_FILE" | tail -1 || echo "")
GRADES=$(grep -oE '[SABCD][+]? 級.*?位' "$LOG_FILE" | tr '\n' '，' | sed 's/，$//' || echo "")
DURATION=$(grep -oE '耗時.*?秒' "$LOG_FILE" | tail -1 || echo "")

if [ "$EXIT_CODE" -eq 0 ]; then
  STATUS="✅ 完成"
  ICON="✅"
else
  STATUS="❌ 失敗 (Exit: $EXIT_CODE)"
  ICON="❌"
fi

REPORT="🤖 人才搜尋回報 | $(date '+%Y-%m-%d %H:%M')

${ICON} Job ${JOB_ID}：${JOB_NAME}
• 狀態：${STATUS}
${UPLOADED:+• ${UPLOADED}}
${TOTAL:+• ${TOTAL}}
${GRADES:+• 等級：${GRADES}}
${DURATION:+• ${DURATION}}
📝 Log：${LOG_FILE}
🔗 查看系統：https://step1ne.zeabur.app → ✨ 今日新增"

echo ""
echo "📤 回報中..."
echo "$REPORT"
