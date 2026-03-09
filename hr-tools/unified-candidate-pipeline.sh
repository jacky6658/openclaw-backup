#!/bin/bash
# 統一候選人處理流程 - 整合被動履歷 + 主動搜尋
# 功能：Gmail 履歷 + GitHub/LinkedIn 搜尋 → 去重 → AI 配對 → 履歷池 → Pipeline

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="$SCRIPT_DIR/data"
RESUME_POOL_SHEET="1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q"

mkdir -p "$DATA_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

# 職位中英翻譯
translate_job_title() {
    local title="$1"
    
    case "$title" in
        *AI工程師*|*AI*) echo "AI Engineer" ;;
        *.NET*) echo ".NET Developer" ;;
        *資安*) echo "Security Engineer" ;;
        *自動化測試*) echo "QA Automation Engineer" ;;
        *會計*) echo "Accountant Finance" ;;
        *供應鏈*) echo "Supply Chain" ;;
        *產品經理*|*專案經理*|*PM*) echo "Project Manager" ;;
        *雲端維運*|*雲端*) echo "Cloud Engineer DevOps" ;;
        *前端*) echo "Frontend Engineer" ;;
        *後端*) echo "Backend Engineer" ;;
        *全端*) echo "Full Stack Engineer" ;;
        *) echo "$title" ;;
    esac
}

# 提取關鍵字（用於履歷池搜尋）
extract_keywords() {
    local title="$1"
    
    # 移除公司名稱（- 後面的部分）
    title=$(echo "$title" | sed 's/-.*$//')
    
    case "$title" in
        *AI*) echo "AI|Python|機器學習|深度學習|TensorFlow|PyTorch" ;;
        *.NET*) echo ".NET|C#|ASP.NET|Core|MVC" ;;
        *資安*) echo "資安|資訊安全|Security|滲透測試|防火牆" ;;
        *自動化測試*) echo "自動化|測試|Selenium|QA|Test" ;;
        *會計*) echo "會計|財務|IFRS|稅務|成本|審計" ;;
        *供應鏈*) echo "供應鏈|採購|物流|Supply|Chain" ;;
        *) echo "$title" ;;
    esac
}

# ========== 步驟 1：收集所有候選人 ==========
collect_candidates() {
    local jd_id="$1"
    local output_file="$2"
    
    log "📦 步驟 1：收集候選人來源"
    
    ALL_CANDIDATES="[]"
    
    # === 優先：外部搜尋（GitHub / LinkedIn）===
    
    # 1.1 ✅ 主動來源：GitHub 搜尋 v2（含技能推斷 + 待業判斷 + 活躍度）
    log "  → [優先] GitHub 搜尋 v2（最多 20 人）..."
    
    JD_TITLE=$(echo "$jd_id" | sed 's/-[0-9]*$//')
    ENGLISH_TITLE=$(translate_job_title "$JD_TITLE")
    
    # 呼叫 Python 腳本 v2：搜尋 20 人 + 完整判斷（無 Token 限制）
    python3 "$SCRIPT_DIR/github-talent-search-v2.py" "$ENGLISH_TITLE" "Taiwan" 20 > /tmp/github-candidates.json 2>/tmp/github-search.log || echo "[]" > /tmp/github-candidates.json
    
    GITHUB_COUNT=$(cat /tmp/github-candidates.json | jq 'length' 2>/dev/null || echo 0)
    GITHUB_AVAILABLE=$(cat /tmp/github-candidates.json | jq '[.[] | select(.available == true)] | length' 2>/dev/null || echo 0)
    GITHUB_ACTIVE=$(cat /tmp/github-candidates.json | jq '[.[] | select(.activity_level == "active")] | length' 2>/dev/null || echo 0)
    log "    ✓ GitHub v2：$GITHUB_COUNT 位（$GITHUB_AVAILABLE 位求職中，$GITHUB_ACTIVE 位活躍）"
    
    # 1.2 ✅ 主動來源：LinkedIn 搜尋（Bing + 爬蟲，有 URL 就夠）
    log "  → [優先] LinkedIn 搜尋（Bing，取 URL）..."
    
    # 使用 Bing 爬蟲（反爬蟲較寬鬆，只取 URL）
    python3 "$SCRIPT_DIR/scraper-linkedin-bing.py" \
        --keywords "$ENGLISH_TITLE" \
        --location "Taiwan" \
        --max-results 10 > /tmp/linkedin-candidates.json 2>/tmp/linkedin-scrape.log || echo "[]" > /tmp/linkedin-candidates.json
    
    LINKEDIN_COUNT=$(cat /tmp/linkedin-candidates.json | jq 'length' 2>/dev/null || echo 0)
    log "    ✓ LinkedIn：$LINKEDIN_COUNT 位（Bing，有 URL 即可用）"
    
    # === 次要：內部履歷池（2/28 起啟用）===
    
    # 1.3 ⏸️ 被動來源：履歷池現有候選人（2/28 前不使用，優先找外部新人）
    log "  → [暫停] 履歷池搜尋..."
    log "    ⏸️  2/28 前關閉（外部搜尋優先，2/28 起啟用）"
    
    echo "[]" > /tmp/pool-candidates.json
    POOL_COUNT=0
    
    # 合併所有來源（外部優先）
    jq -s 'add' /tmp/github-candidates.json /tmp/linkedin-candidates.json /tmp/pool-candidates.json > "$output_file"
    
    TOTAL=$(cat "$output_file" | jq 'length')
    log "  ✅ 總計收集：$TOTAL 位候選人"
}

# ========== 步驟 2：去重處理 ==========
dedup_candidates() {
    local input_file="$1"
    local output_file="$2"
    local jd_id="$3"
    
    log "🔄 步驟 2：去重處理"
    
    python3 -c "
import sys
sys.path.append('$SCRIPT_DIR')
from dedup_engine import DedupEngine
import json

with open('$input_file') as f:
    candidates = json.load(f)

log_msg = f'  → 去重前：{len(candidates)} 位'
print(log_msg, file=sys.stderr)

engine = DedupEngine()
merged = engine.merge_candidates(candidates)

log_msg = f'  → 合併後：{len(merged)} 位'
print(log_msg, file=sys.stderr)

filtered = engine.filter_already_recommended(merged, jd_id='$jd_id')

log_msg = f'  → 過濾後：{len(filtered)} 位新候選人'
print(log_msg, file=sys.stderr)

with open('$output_file', 'w') as f:
    json.dump(filtered, f, ensure_ascii=False, indent=2)

print(f'  ✅ 去重完成', file=sys.stderr)
"
}

# ========== 步驟 3：AI 配對評分 ==========
ai_matching() {
    local jd_file="$1"
    local candidates_file="$2"
    local output_file="$3"
    
    log "🤖 步驟 3：AI 配對評分"
    
    python3 -c "
import sys
sys.path.append('$SCRIPT_DIR')
from ai_matcher_v2 import CandidateMatcher
import json

with open('$jd_file') as f:
    jd = json.load(f)

with open('$candidates_file') as f:
    candidates = json.load(f)

print(f'  → 開始配對：{len(candidates)} 位候選人', file=sys.stderr)

matcher = CandidateMatcher()
results = []

for candidate in candidates:
    result = matcher.match(candidate, jd)
    results.append(result)

results.sort(key=lambda x: x['total_score'], reverse=True)

with open('$output_file', 'w') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

p0 = sum(1 for r in results if r['confidence'] == 'P0')
p1 = sum(1 for r in results if r['confidence'] == 'P1')
p2 = sum(1 for r in results if r['confidence'] == 'P2')

print(f'  ✅ 配對完成 - P0: {p0}, P1: {p1}, P2: {p2}', file=sys.stderr)
"
}

# ========== 步驟 4：匯入履歷池 ==========
import_to_pool() {
    local results_file="$1"
    local jd_id="$2"
    
    log "📊 步驟 4：匯入履歷池（Top 推薦）"
    
    # 匯入 P2 以上（分數 ≥40）
    TOP_CANDIDATES=$(cat "$results_file" | jq '[.[] | select(.total_score >= 40)]')
    
    COUNT=$(echo "$TOP_CANDIDATES" | jq 'length')
    
    if [ "$COUNT" -eq 0 ]; then
        log "  ⚠️  無符合條件候選人（分數 <40）"
        return
    fi
    
    log "  → 準備匯入 $COUNT 位候選人..."
    
    # 過濾出來自外部搜尋的候選人（source = GitHub 或 LinkedIn）
    NEW_CANDIDATES=$(echo "$TOP_CANDIDATES" | python3 -c "
import json, sys
data = json.load(sys.stdin)
new = [c for c in data if c.get('source','').lower() in ('github','linkedin') or c.get('candidate_id','').lower() not in ('',)]
# 只取外部來源
new = [c for c in data if c.get('source','').lower() in ('github','linkedin')]
print(json.dumps(new, ensure_ascii=False))
")
    NEW_COUNT=$(echo "$NEW_CANDIDATES" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))")
    
    if [ "$NEW_COUNT" -eq 0 ]; then
        log "  ℹ️  所有候選人已在履歷池（無需匯入）"
        log "  📋 Top 推薦："
        echo "$TOP_CANDIDATES" | jq -r '.[:5] | .[] | "    - \(.candidate_name) (分數: \(.total_score))"' >&2
        return
    fi
    
    # 真正匯入到 Google Sheets 履歷池
    log "  → 匯入 $NEW_COUNT 位新候選人到履歷池..."
    
    python3 <<PYEOF
import sys, json, subprocess, datetime

sys.path.insert(0, '$SCRIPT_DIR')
candidates = json.loads(r"""$NEW_CANDIDATES""")
SHEET_ID = "$RESUME_POOL_SHEET"
today = datetime.date.today().isoformat()
jd_id = "$jd_id"

imported = 0
for c in candidates:
    name = c.get('candidate_name', 'unknown')
    github_url = c.get('github_url', '')
    linkedin_url = c.get('linkedin_url', '')
    contact_url = github_url or linkedin_url
    skills = ', '.join(c.get('skills', [])[:5])  # 前 5 個技能
    score = c.get('total_score', 0)
    confidence = c.get('confidence', 'P2')
    source = c.get('source', 'GitHub')

    # 履歷池格式（21 欄位）：
    # A:姓名 B:Email C:電話 D:地點 E:目前職位 F:總年資 G:轉職次數 H:平均任職 I:最近gap
    # J:技能 K:學歷 L:來源 M:工作經歷 N:離職原因 O:穩定性評分 P:學歷JSON
    # Q:DISC/Big5 R:狀態 S:獵頭顧問 T:備註 U:履歷連結
    
    # 清理技能中的換行符和特殊字元
    skills_clean = skills.replace('\n', ', ').replace('\t', ' ').replace('|', ',')
    
    # 建立 21 欄資料（用 | 分隔）
    row_data = [
        name,                          # A: 姓名
        '',                            # B: Email（待補）
        '',                            # C: 電話（待補）
        'Taiwan',                      # D: 地點
        c.get('company', ''),          # E: 目前職位/公司
        '0',                           # F: 總年資
        '0',                           # G: 轉職次數
        '0',                           # H: 平均任職
        '0',                           # I: 最近gap
        skills_clean,                  # J: 技能
        '',                            # K: 學歷
        source,                        # L: 來源
        c.get('bio', ''),              # M: 工作經歷（用bio代替）
        '',                            # N: 離職原因
        str(score),                    # O: 穩定性評分（用AI分數）
        '',                            # P: 學歷JSON
        '',                            # Q: DISC/Big5
        '待聯繫',                       # R: 狀態
        'AI自動',                       # S: 獵頭顧問
        f"{confidence} {score}分 | {jd_id} | {today}",  # T: 備註
        contact_url                     # U: 履歷連結（GitHub/LinkedIn URL）
    ]
    
    # 用 | 分隔（避免技能中的逗號導致欄位錯位）
    row = '|'.join(row_data)
    
    # 使用 gog sheets update（逐欄更新，避免分隔符問題）
    # 先用 append 佔位，再用 update 填充資料
    result = subprocess.run(
        ['gog', 'sheets', 'append', '--account', 'aijessie88@step1ne.com', SHEET_ID, 'A:U', row],
        capture_output=True, text=True
    )
    
    if result.returncode == 0:
        print(f"  ✅ 已匯入：{name} ({confidence} {score}分)", file=sys.stderr)
        imported += 1
    else:
        print(f"  ⚠️  匯入失敗：{name} - {result.stderr[:100]}", file=sys.stderr)

print(f"  📥 完成：{imported}/{len(candidates)} 位候選人已匯入履歷池", file=sys.stderr)
PYEOF
}

# ========== 主流程 ==========
main() {
    local jd_id="${1:-AI工程師}"
    
    log "========================================="
    log "統一候選人處理流程"
    log "職缺：$jd_id"
    log "========================================="
    
    # 建立 JD 資料（根據職缺 ID 自動生成）
    JD_FILE="/tmp/jd-${jd_id}.json"
    
    JD_TITLE=$(echo "$jd_id" | sed 's/-[0-9]*$//')
    
    # 根據職缺類型設定技能需求（簡化版：只要求核心技能）
    case "$JD_TITLE" in
        *AI工程師*|*AI*)
            REQUIRED_SKILLS='["AI", "Python"]'  # 簡化：只要求 2 個核心技能
            REQUIRED_YEARS=1  # 降低年資門檻
            ;;
        *.NET*)
            REQUIRED_SKILLS='[".NET", "C#"]'
            REQUIRED_YEARS=1
            ;;
        *資安*)
            REQUIRED_SKILLS='["資安", "Security"]'
            REQUIRED_YEARS=1
            ;;
        *自動化測試*)
            REQUIRED_SKILLS='["測試", "QA"]'
            REQUIRED_YEARS=1
            ;;
        *會計*)
            REQUIRED_SKILLS='["會計", "財務"]'
            REQUIRED_YEARS=2
            ;;
        *供應鏈*)
            REQUIRED_SKILLS='["供應鏈", "Supply"]'
            REQUIRED_YEARS=2
            ;;
        *雲端維運*|*雲端*|*Cloud*)
            REQUIRED_SKILLS='["Linux", "Shell"]'
            REQUIRED_YEARS=1
            ;;
        *專案經理*|*Project*|*PM*)
            REQUIRED_SKILLS='["專案管理", "Project"]'
            REQUIRED_YEARS=1
            ;;
        *前端*|*Frontend*)
            REQUIRED_SKILLS='["JavaScript", "React"]'
            REQUIRED_YEARS=1
            ;;
        *後端*|*Backend*)
            REQUIRED_SKILLS='["Python", "Java"]'
            REQUIRED_YEARS=1
            ;;
        *)
            REQUIRED_SKILLS='["相關"]'
            REQUIRED_YEARS=1
            ;;
    esac
    
    cat > "$JD_FILE" <<EOF
{
  "id": "$jd_id",
  "title": "$JD_TITLE",
  "required_skills": $REQUIRED_SKILLS,
  "required_years": $REQUIRED_YEARS,
  "industry": "科技",
  "role": "$JD_TITLE",
  "location": "taipei",
  "remote_ok": true
}
EOF
    
    # 步驟 1：收集候選人
    CANDIDATES_FILE="$DATA_DIR/candidates-${jd_id}.json"
    collect_candidates "$jd_id" "$CANDIDATES_FILE"
    
    # 步驟 2：去重
    DEDUPED_FILE="$DATA_DIR/deduped-${jd_id}.json"
    dedup_candidates "$CANDIDATES_FILE" "$DEDUPED_FILE" "$jd_id"
    
    # 步驟 3：AI 配對
    MATCHED_FILE="$DATA_DIR/matched.json"
    ai_matching "$JD_FILE" "$DEDUPED_FILE" "$MATCHED_FILE"
    
    # 步驟 4：匯入履歷池
    import_to_pool "$MATCHED_FILE" "$jd_id"
    
    log "========================================="
    log "✅ 流程完成"
    log "結果：$MATCHED_FILE"
    log "========================================="
}

# 執行
main "$@"
