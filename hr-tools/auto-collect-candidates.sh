#!/bin/bash
# 自動收集候選人 - 每天執行多次，慢慢累積履歷池
# 執行職缺列表，輪流搜尋不同職缺

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/data/auto-collect.log"

# 職缺列表（輪流搜尋）
JOB_LIST=(
    "AI工程師"
    "資安工程師"
    ".NET工程師"
    "自動化測試工程師"
    "雲端維運工程師"
    "前端工程師"
    "後端工程師"
    "全端工程師"
)

echo "========================================" | tee -a "$LOG_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 開始自動收集候選人" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# 隨機選 2 個職缺（避免每次都搜尋同樣的）
SELECTED_JOBS=()
for i in {1..2}; do
    RANDOM_INDEX=$((RANDOM % ${#JOB_LIST[@]}))
    SELECTED_JOBS+=("${JOB_LIST[$RANDOM_INDEX]}")
done

echo "本次搜尋職缺：${SELECTED_JOBS[@]}" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 執行搜尋
for JOB in "${SELECTED_JOBS[@]}"; do
    echo "→ 搜尋：$JOB" | tee -a "$LOG_FILE"
    
    bash "$SCRIPT_DIR/unified-candidate-pipeline.sh" "$JOB" >> "$LOG_FILE" 2>&1
    
    # 每個職缺間隔 30 秒（避免太快）
    sleep 30
done

echo "" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 完成" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
