#!/bin/bash
# 自動找人選系統 v2 - 整合版
# 功能：搜尋 → 去重 → AI 配對 → 匯入履歷池 → 通知

set -e  # 遇到錯誤立即停止

# ========== 設定 ==========
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="$SCRIPT_DIR/data"
TMP_DIR="/tmp/auto-sourcing-$$"

SHEET_ID="1QPaeOm-slNVFCeM8Q3gg3DawKjzp2tYwyfquvdHlZFE"  # step1ne 職缺管理
RESUME_POOL_SHEET="1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q"  # 履歷池索引
TELEGRAM_GROUP="-1003231629634"
TELEGRAM_TOPIC="304"  # #2履歷池

# ========== 初始化 ==========
mkdir -p "$DATA_DIR" "$TMP_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

# ========== 讀取職缺清單 ==========
get_active_jds() {
    log "讀取招募中職缺..."
    
    # 使用 gog sheets 讀取
    gog sheets read --sheet-id "$SHEET_ID" --format json > "$TMP_DIR/jds.json"
    
    # 篩選「招募中」職缺
    cat "$TMP_DIR/jds.json" | jq -r '.[] | select(.狀態 == "招募中") | {
        id: .職位ID,
        title: .職位,
        department: .部門,
        required_skills: (.技能 | split(",")),
        required_years: (.經驗 | tonumber),
        industry: "科技",
        role: .職位,
        location: "taipei",
        remote_ok: true
    }' > "$TMP_DIR/active_jds.json"
    
    JD_COUNT=$(cat "$TMP_DIR/active_jds.json" | jq -s 'length')
    log "找到 $JD_COUNT 個招募中職缺"
}

# ========== 搜尋候選人（多管道）==========
search_candidates() {
    local jd_file="$1"
    local output_file="$2"
    
    JD_TITLE=$(cat "$jd_file" | jq -r '.title')
    JD_SKILLS=$(cat "$jd_file" | jq -r '.required_skills | join(",")')
    
    log "搜尋職缺：$JD_TITLE"
    
    # 1. LinkedIn 搜尋
    log "  → LinkedIn 搜尋..."
    bash "$SCRIPT_DIR/google-linkedin-search.sh" "$JD_TITLE" "$JD_SKILLS" > "$TMP_DIR/linkedin.json" 2>&1 || true
    
    # 2. GitHub 搜尋
    log "  → GitHub 搜尋..."
    python3 "$SCRIPT_DIR/github-talent-search.py" --keywords "$JD_SKILLS" --location Taiwan --output "$TMP_DIR/github.json" 2>&1 || true
    
    # 3. 履歷池內部搜尋
    log "  → 履歷池內部搜尋..."
    bash "$SCRIPT_DIR/search-resume-pool.sh" "$JD_SKILLS" > "$TMP_DIR/resume_pool.json" 2>&1 || true
    
    # 合併所有來源
    log "  → 合併搜尋結果..."
    python3 -c "
import json
import sys

candidates = []

# LinkedIn
try:
    with open('$TMP_DIR/linkedin.json') as f:
        data = json.load(f)
        for c in data:
            c['platforms'] = ['linkedin']
            candidates.append(c)
except: pass

# GitHub
try:
    with open('$TMP_DIR/github.json') as f:
        data = json.load(f)
        for c in data:
            c['platforms'] = ['github']
            candidates.append(c)
except: pass

# Resume Pool
try:
    with open('$TMP_DIR/resume_pool.json') as f:
        data = json.load(f)
        for c in data:
            c['platforms'] = ['履歷池']
            candidates.append(c)
except: pass

with open('$output_file', 'w') as f:
    json.dump(candidates, f, ensure_ascii=False, indent=2)

print(f'合併完成：{len(candidates)} 位候選人', file=sys.stderr)
"
}

# ========== 去重 ==========
dedup_candidates() {
    local input_file="$1"
    local output_file="$2"
    local jd_id="$3"
    
    log "執行去重..."
    
    python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from dedup_engine import DedupEngine
import json

# 讀取候選人
with open('$input_file') as f:
    candidates = json.load(f)

print(f'去重前：{len(candidates)} 位', file=sys.stderr)

# 初始化引擎
engine = DedupEngine()

# 合併重複候選人
merged = engine.merge_candidates(candidates)
print(f'合併後：{len(merged)} 位', file=sys.stderr)

# 過濾已推薦
filtered = engine.filter_already_recommended(merged, jd_id='$jd_id')
print(f'過濾後：{len(filtered)} 位新候選人', file=sys.stderr)

# 輸出
with open('$output_file', 'w') as f:
    json.dump(filtered, f, ensure_ascii=False, indent=2)
"
}

# ========== AI 配對評分 ==========
match_candidates() {
    local jd_file="$1"
    local candidates_file="$2"
    local output_file="$3"
    
    log "AI 配對評分..."
    
    python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from ai_matcher_v2 import CandidateMatcher
import json

# 讀取 JD
with open('$jd_file') as f:
    jd = json.load(f)

# 讀取候選人
with open('$candidates_file') as f:
    candidates = json.load(f)

print(f'開始配對：{len(candidates)} 位候選人', file=sys.stderr)

# 執行配對
matcher = CandidateMatcher()
results = []

for candidate in candidates:
    result = matcher.match(candidate, jd)
    results.append(result)

# 排序（分數由高到低）
results.sort(key=lambda x: x['total_score'], reverse=True)

# 輸出
with open('$output_file', 'w') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

# 統計
p0 = sum(1 for r in results if r['confidence'] == 'P0')
p1 = sum(1 for r in results if r['confidence'] == 'P1')
p2 = sum(1 for r in results if r['confidence'] == 'P2')

print(f'配對完成 - P0: {p0}, P1: {p1}, P2: {p2}', file=sys.stderr)
"
}

# ========== 發送通知 ==========
send_notification() {
    local jd_title="$1"
    local results_file="$2"
    
    log "發送 Telegram 通知..."
    
    # 取得 Top 3
    TOP3=$(cat "$results_file" | jq -r '.[0:3] | .[] | "• \(.candidate_name) (\(.total_score)分) - \(.confidence_label)\n  公司：\(.details.industry // "N/A") | 平台：\(.details.bonus.platforms // "linkedin")\n"')
    
    TOTAL=$(cat "$results_file" | jq 'length')
    P0_COUNT=$(cat "$results_file" | jq '[.[] | select(.confidence == "P0")] | length')
    P1_COUNT=$(cat "$results_file" | jq '[.[] | select(.confidence == "P1")] | length')
    
    MESSAGE="📋 **找人選完成：$jd_title**

✅ 找到 $TOTAL 位候選人
• P0 高度符合：$P0_COUNT 位
• P1 可能符合：$P1_COUNT 位

🏆 **Top 3 推薦：**
$TOP3

💾 詳細清單已存至：\`$results_file\`
📊 要查看完整清單請回覆：**查看 $jd_title 候選人**"
    
    openclaw message send --channel telegram --target "$TELEGRAM_GROUP" --thread-id "$TELEGRAM_TOPIC" --message "$MESSAGE"
}

# ========== 主流程 ==========
main() {
    log "=== 自動找人選系統 v2 開始 ==="
    
    # 1. 讀取職缺
    get_active_jds
    
    # 如果指定職缺 ID，只處理該職缺
    if [ -n "$1" ]; then
        JD_ID="$1"
        log "處理指定職缺：$JD_ID"
        
        # 從 active_jds.json 中篩選
        cat "$TMP_DIR/active_jds.json" | jq -s ".[] | select(.id == \"$JD_ID\")" > "$TMP_DIR/current_jd.json"
        
        if [ ! -s "$TMP_DIR/current_jd.json" ]; then
            log "錯誤：找不到職缺 $JD_ID"
            exit 1
        fi
        
        JD_FILES=("$TMP_DIR/current_jd.json")
    else
        # 處理所有職缺
        log "處理所有招募中職缺"
        
        JD_FILES=()
        cat "$TMP_DIR/active_jds.json" | jq -c '.' | while read -r line; do
            JD_ID=$(echo "$line" | jq -r '.id')
            echo "$line" > "$TMP_DIR/jd_$JD_ID.json"
            JD_FILES+=("$TMP_DIR/jd_$JD_ID.json")
        done
    fi
    
    # 處理每個職缺
    for jd_file in $TMP_DIR/jd_*.json; do
        [ -f "$jd_file" ] || continue
        
        JD_ID=$(cat "$jd_file" | jq -r '.id')
        JD_TITLE=$(cat "$jd_file" | jq -r '.title')
        
        log "========================================="
        log "處理職缺：$JD_TITLE ($JD_ID)"
        log "========================================="
        
        # 2. 搜尋候選人
        search_candidates "$jd_file" "$TMP_DIR/candidates_$JD_ID.json"
        
        # 3. 去重
        dedup_candidates "$TMP_DIR/candidates_$JD_ID.json" "$TMP_DIR/deduped_$JD_ID.json" "$JD_ID"
        
        # 4. AI 配對評分
        match_candidates "$jd_file" "$TMP_DIR/deduped_$JD_ID.json" "$TMP_DIR/results_$JD_ID.json"
        
        # 5. 儲存結果
        RESULTS_FILE="$DATA_DIR/sourcing_results_${JD_ID}_$(date +%Y%m%d).json"
        cp "$TMP_DIR/results_$JD_ID.json" "$RESULTS_FILE"
        
        # 6. 發送通知
        send_notification "$JD_TITLE" "$RESULTS_FILE"
        
        log "完成職缺：$JD_TITLE"
        log ""
    done
    
    log "=== 自動找人選系統 v2 完成 ==="
    log "結果存放於：$DATA_DIR/sourcing_results_*.json"
}

# 執行
main "$@"
