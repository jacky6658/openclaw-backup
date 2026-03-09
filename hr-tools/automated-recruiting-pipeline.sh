#!/bin/bash

################################################################################
# Automated Recruiting Pipeline v2
# 
# 整合：搜尋 → 評分 → 推薦 → 報告 → 通知
# 
# Cron 配置示例：
# 0 8 * * 1 /Users/user/clawd/hr-tools/automated-recruiting-pipeline.sh layer1
# 0 9 * * 1-5 /Users/user/clawd/hr-tools/automated-recruiting-pipeline.sh layer2
################################################################################

set -e

# ==================== 配置 ====================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="/Users/user/clawd"
DATA_DIR="/tmp/recruiting-pipeline"
LOG_DIR="$DATA_DIR/logs"
REPORT_DIR="$DATA_DIR/reports"
TIMESTAMP=$(date '+%Y-%m-%d_%H-%M-%S')

# Telegram 配置
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-}"

# Python 腳本
SCRAPER="$SCRIPT_DIR/unified-scraper-v4-enhanced.py"
SCORER="$SCRIPT_DIR/candidate-scoring-system-v2.py"
EXECUTOR="$SCRIPT_DIR/search-plan-executor.py"
ANALYZER="$SCRIPT_DIR/industry-migration-analyzer.py"
DASHBOARD="$SCRIPT_DIR/industry-analytics-dashboard.py"

# ==================== 初始化 ====================

init_directories() {
    mkdir -p "$DATA_DIR" "$LOG_DIR" "$REPORT_DIR"
    chmod 755 "$DATA_DIR" "$LOG_DIR" "$REPORT_DIR"
}

# ==================== 日誌函數 ====================

log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_DIR/pipeline-$TIMESTAMP.log"
}

# ==================== 主流程 ====================

execute_layer1_search() {
    # Layer 1：P0 職缺，立即執行
    
    log "INFO" "========================================="
    log "INFO" "開始 Layer 1 搜尋（P0 職缺）"
    log "INFO" "========================================="
    
    # Step 1: 生成職缺列表
    log "INFO" "步驟 1：生成職缺列表..."
    generate_jobs_list layer1 > "$DATA_DIR/jobs-layer1-$TIMESTAMP.json"
    
    # Step 2: 執行爬蟲搜尋
    log "INFO" "步驟 2：執行產業感知爬蟲..."
    python3 "$SCRAPER" \
        --jobs "$DATA_DIR/jobs-layer1-$TIMESTAMP.json" \
        --output "$REPORT_DIR/search-results-$TIMESTAMP.json" \
        --workers 3 2>&1 | tee -a "$LOG_DIR/scraper-$TIMESTAMP.log"
    
    # Step 3: 評分候選人
    log "INFO" "步驟 3：執行 6 維評分..."
    python3 "$SCORER" \
        --candidates "$REPORT_DIR/search-results-$TIMESTAMP.json" \
        --output "$REPORT_DIR/scoring-$TIMESTAMP.json" 2>&1 | tee -a "$LOG_DIR/scorer-$TIMESTAMP.log"
    
    # Step 4: 生成推薦
    log "INFO" "步驟 4：生成頂級推薦..."
    python3 "$EXECUTOR" \
        --jobs "$DATA_DIR/jobs-layer1-$TIMESTAMP.json" \
        --candidates "$REPORT_DIR/scoring-$TIMESTAMP.json" \
        --output "$REPORT_DIR/recommendations-$TIMESTAMP.json" 2>&1 | tee -a "$LOG_DIR/executor-$TIMESTAMP.log"
    
    # Step 5: 生成儀表板
    log "INFO" "步驟 5：生成分析儀表板..."
    python3 "$DASHBOARD" \
        --candidates "$REPORT_DIR/scoring-$TIMESTAMP.json" \
        --output "$REPORT_DIR" 2>&1 | tee -a "$LOG_DIR/dashboard-$TIMESTAMP.log"
    
    # Step 6: 同步到 API（履歷池）
    log "INFO" "步驟 6：同步推薦到 Step1ne 履歷池..."
    python3 "$SCRIPT_DIR/api-integration-sync.py" \
        --recommendations "$REPORT_DIR/recommendations-$TIMESTAMP.json" \
        --output "$REPORT_DIR/sync-result-$TIMESTAMP.json" 2>&1 | tee -a "$LOG_DIR/api-sync-$TIMESTAMP.log"
    
    log "INFO" "✅ Layer 1 執行完成"
    
    # 發送通知（包含同步結果）
    send_telegram_notification "layer1" "$REPORT_DIR"
}

execute_layer2_search() {
    # Layer 2：P1 職缺，本週執行
    
    log "INFO" "========================================="
    log "INFO" "開始 Layer 2 搜尋（P1 職缺）"
    log "INFO" "========================================="
    
    # 與 Layer 1 相同流程，但限制在 P1 職缺
    generate_jobs_list layer2 > "$DATA_DIR/jobs-layer2-$TIMESTAMP.json"
    
    python3 "$SCRAPER" \
        --jobs "$DATA_DIR/jobs-layer2-$TIMESTAMP.json" \
        --output "$REPORT_DIR/search-results-l2-$TIMESTAMP.json" \
        --workers 2 2>&1 | tee -a "$LOG_DIR/scraper-l2-$TIMESTAMP.log"
    
    python3 "$SCORER" \
        --candidates "$REPORT_DIR/search-results-l2-$TIMESTAMP.json" \
        --output "$REPORT_DIR/scoring-l2-$TIMESTAMP.json" 2>&1 | tee -a "$LOG_DIR/scorer-l2-$TIMESTAMP.log"
    
    # Layer 2 推薦生成
    python3 "$EXECUTOR" \
        --jobs "$DATA_DIR/jobs-layer2-$TIMESTAMP.json" \
        --candidates "$REPORT_DIR/scoring-l2-$TIMESTAMP.json" \
        --output "$REPORT_DIR/recommendations-l2-$TIMESTAMP.json" 2>&1 | tee -a "$LOG_DIR/executor-l2-$TIMESTAMP.log"
    
    # 同步到 API
    log "INFO" "同步 Layer 2 推薦..."
    python3 "$SCRIPT_DIR/api-integration-sync.py" \
        --recommendations "$REPORT_DIR/recommendations-l2-$TIMESTAMP.json" \
        --output "$REPORT_DIR/sync-result-l2-$TIMESTAMP.json" 2>&1 | tee -a "$LOG_DIR/api-sync-l2-$TIMESTAMP.log"
    
    log "INFO" "✅ Layer 2 執行完成"
    
    send_telegram_notification "layer2" "$REPORT_DIR"
}

execute_migration_analysis() {
    # 產業遷移能力分析
    
    log "INFO" "========================================="
    log "INFO" "開始產業遷移分析"
    log "INFO" "========================================="
    
    python3 "$ANALYZER" \
        --candidates "$REPORT_DIR/scoring-$TIMESTAMP.json" \
        --output "$REPORT_DIR/migration-analysis-$TIMESTAMP.json" 2>&1 | tee -a "$LOG_DIR/migration-$TIMESTAMP.log"
    
    log "INFO" "✅ 遷移分析完成"
    
    # 注：遷移分析本身不直接導入到 API，但可用於候選人備註更新
}

# ==================== 工具函數 ====================

generate_jobs_list() {
    # 從職缺管理表生成職缺列表
    local layer=$1
    
    # 使用 gog sheets 讀取職缺
    local sheet_id="1QPaeOm-slNVFCeM8Q3gg3DawKjzp2tYwyfquvdHlZFE"
    local range="A1:H50"
    
    # 簡化示例：返回 JSON 格式職缺
    cat <<EOF
{
    "jobs": [
        {
            "job_title": "資安工程師",
            "customer_name": "遊戲橘子集團",
            "industry": "gaming",
            "experience_years": 2,
            "skills": ["DevOps", "Linux", "Security"],
            "layer": "$layer",
            "priority": "P0"
        }
    ]
}
EOF
}

send_telegram_notification() {
    # 發送 Telegram 通知
    local layer=$1
    local report_dir=$2
    
    if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ -z "$TELEGRAM_CHAT_ID" ]; then
        log "WARN" "Telegram 未配置，跳過通知"
        return
    fi
    
    local message="🎯 搜尋計畫執行完成（$layer）
    
✅ 狀態：成功
⏰ 時間：$(date '+%Y-%m-%d %H:%M:%S')
📊 報告位置：$report_dir

查看詳細報告：
${report_dir}/recommendations-${TIMESTAMP}.json
${report_dir}/analytics-dashboard.html"
    
    curl -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
        -H 'Content-Type: application/json' \
        -d "{
            \"chat_id\": ${TELEGRAM_CHAT_ID},
            \"text\": \"$message\",
            \"parse_mode\": \"Markdown\"
        }" 2>/dev/null || log "WARN" "Telegram 通知發送失敗"
}

cleanup() {
    # 清理舊日誌（保留 30 天）
    log "INFO" "清理舊日誌..."
    find "$LOG_DIR" -name "*.log" -mtime +30 -delete
    find "$DATA_DIR" -name "*.json" -mtime +30 -delete
}

# ==================== 主程序 ====================

main() {
    local mode=${1:-"layer1"}
    
    init_directories
    
    log "INFO" "管道啟動：模式=$mode"
    
    case "$mode" in
        layer1)
            execute_layer1_search
            ;;
        layer2)
            execute_layer2_search
            ;;
        migration)
            execute_migration_analysis
            ;;
        full)
            execute_layer1_search
            execute_layer2_search
            execute_migration_analysis
            ;;
        *)
            echo "用法：$0 {layer1|layer2|migration|full}"
            exit 1
            ;;
    esac
    
    cleanup
    
    log "INFO" "✅ 管道執行完成"
}

# ==================== 執行 ====================

main "$@"
