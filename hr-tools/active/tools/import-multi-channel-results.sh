#!/bin/bash
# 多管道結果匯入履歷池
# 功能：將 LinkedIn、GitHub、CakeResume 的搜尋結果統一匯入履歷池
# 作者：YQ1 YuQi
# 日期：2026-02-13

RESUME_POOL_ID="1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q"
LOG_FILE="/Users/user/clawd/hr-tools/logs/import-$(date +%Y%m%d).log"

log() {
    echo "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 格式化 LinkedIn 候選人
format_linkedin() {
    local json_file="$1"
    local position="$2"
    
    jq -r --arg pos "$position" '.[] | [
        .name // "",
        .linkedin_url // "",
        .current_company // "",
        .title // "",
        "",
        "LinkedIn",
        "待聯繫",
        $pos,
        ("LinkedIn: " + (.linkedin_url // "") + "\n地點: " + (.location // ""))
    ] | @tsv' "$json_file" | sed 's/\t/|/g'
}

# 格式化 GitHub 候選人
format_github() {
    local json_file="$1"
    local position="$2"
    
    jq -r --arg pos "$position" '.[] | [
        .username,
        .email // "",
        .company // "",
        (.bio // "開發者"),
        ((.repos // "") + " repos, " + (.followers // "") + " followers"),
        "GitHub",
        "待聯繫",
        $pos,
        ("GitHub: " + .url + "\n地點: " + (.location // "") + "\n語言: " + (.language // ""))
    ] | @tsv' "$json_file" | sed 's/\t/|/g'
}

# 格式化 CakeResume 候選人
format_cakeresume() {
    local json_file="$1"
    local position="$2"
    
    jq -r --arg pos "$position" '.[] | [
        (.name // .user_id),
        .email // "",
        (.experience[0] // ""),
        .title // "",
        (.skills[:5] | join(", ")),
        "CakeResume",
        "待聯繫",
        $pos,
        ("CakeResume: " + .url + "\n地點: " + (.location // ""))
    ] | @tsv' "$json_file" | sed 's/\t/|/g'
}

# 主函數
main() {
    local merged_file="$1"
    local position="$2"
    local source_type="${3:-auto}"  # linkedin, github, cakeresume, auto
    
    if [ ! -f "$merged_file" ]; then
        log "❌ 檔案不存在: $merged_file"
        exit 1
    fi
    
    log "📥 匯入候選人到履歷池"
    log "  檔案: $merged_file"
    log "  職位: $position"
    log "  來源: $source_type"
    
    # 讀取現有履歷池（檢查重複）
    log "📋 讀取現有履歷池..."
    gog sheets get "$RESUME_POOL_ID" --range "B:B" --format json > /tmp/existing-candidates.json
    
    # 自動判斷來源類型
    if [ "$source_type" == "auto" ]; then
        if grep -q "linkedin_url" "$merged_file"; then
            source_type="linkedin"
        elif grep -q "github.com" "$merged_file"; then
            source_type="github"
        elif grep -q "cakeresume.com" "$merged_file"; then
            source_type="cakeresume"
        else
            log "⚠️  無法判斷來源類型，使用 LinkedIn 格式"
            source_type="linkedin"
        fi
    fi
    
    log "  檢測到來源: $source_type"
    
    # 格式化候選人資料
    case "$source_type" in
        "linkedin")
            formatted=$(format_linkedin "$merged_file" "$position")
            ;;
        "github")
            formatted=$(format_github "$merged_file" "$position")
            ;;
        "cakeresume")
            formatted=$(format_cakeresume "$merged_file" "$position")
            ;;
        *)
            log "❌ 不支援的來源類型: $source_type"
            exit 1
            ;;
    esac
    
    # 去重（檢查 LinkedIn URL / Email / 姓名）
    local new_count=0
    local dup_count=0
    
    while IFS='|' read -r name contact company title skills source status pos note; do
        # 檢查是否重複（比對 LinkedIn URL 或 Email）
        if echo "$contact" | grep -q "linkedin.com"; then
            # LinkedIn URL 去重
            if grep -qF "$contact" /tmp/existing-candidates.json 2>/dev/null; then
                dup_count=$((dup_count + 1))
                continue
            fi
        elif [ -n "$contact" ] && echo "$contact" | grep -q "@"; then
            # Email 去重
            if grep -qiF "$contact" /tmp/existing-candidates.json 2>/dev/null; then
                dup_count=$((dup_count + 1))
                continue
            fi
        fi
        
        # 新增到履歷池
        gog sheets append "$RESUME_POOL_ID" \
            --values "$name|$contact|$company|$title|$skills|$source|$status|$pos|$note" \
            --value-input-option USER_ENTERED > /dev/null 2>&1
        
        new_count=$((new_count + 1))
        log "  ✅ $name"
        
        sleep 0.2  # API 限速
    done <<< "$formatted"
    
    log ""
    log "========================================="
    log "✅ 匯入完成"
    log "  新增: $new_count 人"
    log "  重複: $dup_count 人"
    log "========================================="
}

# 執行
main "$@"
