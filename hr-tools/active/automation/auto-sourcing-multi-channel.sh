#!/bin/bash
# 多管道自動找人選系統
# 功能：根據職位類型智能選擇搜尋管道（LinkedIn / GitHub / CakeResume）
# 作者：YQ1 YuQi
# 日期：2026-02-13

SHEET_ID="1QPaeOm-slNVFCeM8Q3gg3DawKjzp2tYwyfquvdHlZFE"
RESUME_POOL_ID="1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q"
SCRIPTS_DIR="/Users/user/clawd/hr-tools/active/tools"
LOG_FILE="/Users/user/clawd/hr-tools/logs/auto-sourcing-$(date +%Y%m%d).log"

# 確保 log 目錄存在
mkdir -p /Users/user/clawd/hr-tools/logs

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 判斷職位類型與適用管道
determine_channels() {
    local position="$1"
    local skills="$2"
    local channels=""
    
    # 技術職位關鍵字
    tech_keywords="工程師|程式|開發|Developer|Engineer|Software|Backend|Frontend|Full Stack|DevOps|AI|Machine Learning|Data|測試|QA|架構師"
    
    # 非技術但適合 LinkedIn 的關鍵字
    linkedin_keywords="經理|主管|VP|總監|Manager|Director|Chief|VP|顧問|Consultant|分析師|Analyst|產品|Product|專案|Project|業務|Sales|行銷|Marketing|人資|HR"
    
    # CakeResume 優先職位（台灣本地、新創偏好）
    cakeresume_keywords="設計|Designer|UI|UX|創意|Creative|內容|Content|社群|Community|編輯|Editor"
    
    # 技術職 → GitHub + LinkedIn
    if echo "$position $skills" | grep -qiE "$tech_keywords"; then
        channels="github,linkedin"
        log "  🔧 技術職位 → GitHub + LinkedIn"
    
    # 設計/創意職 → CakeResume + LinkedIn
    elif echo "$position $skills" | grep -qiE "$cakeresume_keywords"; then
        channels="cakeresume,linkedin"
        log "  🎨 設計/創意職位 → CakeResume + LinkedIn"
    
    # 管理職/非技術 → LinkedIn only
    elif echo "$position $skills" | grep -qiE "$linkedin_keywords"; then
        channels="linkedin"
        log "  💼 管理/非技術職位 → LinkedIn"
    
    # 預設 LinkedIn
    else
        channels="linkedin"
        log "  ℹ️  預設 → LinkedIn"
    fi
    
    echo "$channels"
}

# 執行 LinkedIn 搜尋
search_linkedin() {
    local position="$1"
    local location="${2:-台灣}"
    local output_file="$3"
    
    log "  🔍 LinkedIn 搜尋: $position @ $location"
    
    bash "$SCRIPTS_DIR/google-linkedin-search.sh" "$position" "$location" > "$output_file" 2>&1
    
    local latest_file=$(ls -t /tmp/linkedin-candidates-*.json 2>/dev/null | head -1)
    if [ -n "$latest_file" ] && [ -f "$latest_file" ]; then
        local count=$(jq length "$latest_file" 2>/dev/null || echo 0)
        log "  ✅ LinkedIn: $count 人"
        echo "$latest_file"
    else
        log "  ⚠️  LinkedIn: 0 人"
        echo ""
    fi
}

# 執行 GitHub 搜尋
search_github() {
    local position="$1"
    local skills="$2"
    local location="${3:-taipei}"
    local output_file="$4"
    
    log "  🔍 GitHub 搜尋: $position (skills: $skills) @ $location"
    
    # 從技能提取程式語言
    local language=""
    if echo "$skills" | grep -qiE "python|django|flask"; then
        language="python"
    elif echo "$skills" | grep -qiE "javascript|react|vue|node|typescript"; then
        language="javascript"
    elif echo "$skills" | grep -qiE "java|spring|kotlin"; then
        language="java"
    elif echo "$skills" | grep -qiE "golang|go語言"; then
        language="go"
    elif echo "$skills" | grep -qiE "rust"; then
        language="rust"
    else
        language="python"  # 預設
    fi
    
    # 執行 GitHub 搜尋
    python3 "$SCRIPTS_DIR/github-talent-search.py" "$location" "$language" 15 > "$output_file" 2>&1
    
    local latest_file=$(ls -t /tmp/github-talent-*.json 2>/dev/null | head -1)
    if [ -n "$latest_file" ] && [ -f "$latest_file" ]; then
        local count=$(jq length "$latest_file" 2>/dev/null || echo 0)
        log "  ✅ GitHub: $count 人"
        echo "$latest_file"
    else
        log "  ⚠️  GitHub: 0 人"
        echo ""
    fi
}

# 執行 CakeResume 搜尋
search_cakeresume() {
    local position="$1"
    local location="${2:-台灣}"
    local output_file="$3"
    
    log "  🔍 CakeResume 搜尋: $position @ $location"
    
    python3 "$SCRIPTS_DIR/cakeresume-talent-search.py" "$position" "$location" 15 > "$output_file" 2>&1
    
    local latest_file=$(ls -t /tmp/cakeresume-candidates-*.json 2>/dev/null | head -1)
    if [ -n "$latest_file" ] && [ -f "$latest_file" ]; then
        local count=$(jq length "$latest_file" 2>/dev/null || echo 0)
        log "  ✅ CakeResume: $count 人"
        echo "$latest_file"
    else
        log "  ⚠️  CakeResume: 0 人"
        echo ""
    fi
}

# 合併多管道結果
merge_results() {
    local output_file="/tmp/merged-candidates-$(date +%s).json"
    local files=("$@")
    
    log "  🔗 合併 ${#files[@]} 個管道結果..."
    
    # 合併 JSON 檔案
    jq -s 'flatten | unique_by(.linkedin_url // .url // .username)' "${files[@]}" > "$output_file"
    
    local total=$(jq length "$output_file")
    log "  ✅ 合併完成：$total 人（已去重）"
    
    echo "$output_file"
}

# 主流程
main() {
    local start_row="${1:-2}"  # 預設從第 2 行開始
    local priority_position="${2:-}"  # 優先職位關鍵字
    
    log "========================================="
    log "🚀 多管道自動找人選系統 啟動"
    log "========================================="
    
    # 讀取所有「招募中」職缺
    log "📋 讀取 step1ne 職缺管理..."
    
    gog sheets get "$SHEET_ID" A2:L100 --json --account aijessie88@step1ne.com > /tmp/jd-list.json 2>/dev/null
    
    local total_jds=$(jq '.values | length' /tmp/jd-list.json)
    log "📊 總計 $total_jds 個職缺"
    
    # 篩選「開放中」職缺（原本是「招募中」，實際欄位是「開放中」）
    local recruiting_jds=$(jq '.values | [.[] | select(.[9] == "開放中" or .[9] == "招募中")]' /tmp/jd-list.json)
    local recruiting_count=$(echo "$recruiting_jds" | jq 'length')
    log "✅ 招募中：$recruiting_count 個職缺"
    
    if [ "$recruiting_count" -eq 0 ]; then
        log "⚠️  沒有招募中的職缺，結束"
        exit 0
    fi
    
    # 處理每個職缺
    local processed=0
    local total_candidates=0
    
    echo "$recruiting_jds" | jq -c '.[]' | while read -r jd; do
        local position=$(echo "$jd" | jq -r '.[0]')
        local department=$(echo "$jd" | jq -r '.[2]')
        local skills=$(echo "$jd" | jq -r '.[5]')
        local location=$(echo "$jd" | jq -r '.[8] // "台灣"')
        
        # 優先處理指定職位
        if [ -n "$priority_position" ] && ! echo "$position" | grep -qi "$priority_position"; then
            log "⏭️  跳過：$position（不符合優先條件）"
            continue
        fi
        
        processed=$((processed + 1))
        
        log ""
        log "[$processed/$recruiting_count] 處理：$position"
        log "  部門：$department"
        log "  技能：$skills"
        log "  地點：$location"
        
        # 判斷適用管道
        local channels=$(determine_channels "$position" "$skills")
        
        # 執行各管道搜尋
        local result_files=()
        
        if echo "$channels" | grep -q "linkedin"; then
            local linkedin_file=$(search_linkedin "$position" "$location" "/tmp/linkedin-$processed.log")
            [ -n "$linkedin_file" ] && result_files+=("$linkedin_file")
            sleep 3  # 避免頻繁請求
        fi
        
        if echo "$channels" | grep -q "github"; then
            local github_file=$(search_github "$position" "$skills" "$location" "/tmp/github-$processed.log")
            [ -n "$github_file" ] && result_files+=("$github_file")
            sleep 3
        fi
        
        if echo "$channels" | grep -q "cakeresume"; then
            local cakeresume_file=$(search_cakeresume "$position" "$location" "/tmp/cakeresume-$processed.log")
            [ -n "$cakeresume_file" ] && result_files+=("$cakeresume_file")
            sleep 3
        fi
        
        # 合併結果
        if [ ${#result_files[@]} -gt 0 ]; then
            local merged_file=$(merge_results "${result_files[@]}")
            local count=$(jq length "$merged_file")
            total_candidates=$((total_candidates + count))
            
            log "  📊 $position 共找到 $count 人"
            
            # 匯入履歷池
            bash "$SCRIPTS_DIR/import-multi-channel-results.sh" "$merged_file" "$position" "auto"
        else
            log "  ⚠️  $position 未找到候選人"
        fi
        
        # 間隔時間
        sleep 5
    done
    
    log ""
    log "========================================="
    log "✅ 完成！"
    log "📊 處理 $processed 個職缺，找到 $total_candidates 人"
    log "========================================="
}

# 執行
if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    echo "用法："
    echo "  $0                    # 處理所有招募中職缺"
    echo "  $0 2                  # 從第 2 行開始處理"
    echo "  $0 2 '工程師'         # 優先處理「工程師」職缺"
    exit 0
fi

main "$@"
