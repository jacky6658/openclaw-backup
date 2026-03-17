#!/bin/bash
# ⛔ 已永久停用 — Jacky 指示：禁止碰任何 LinkedIn 帳號做自動化（2026-03-17）
echo "⛔ 此腳本已停用：禁止使用任何 LinkedIn 帳號做自動化" && exit 1

SCRIPT_DIR="$(dirname "$0")"
API_BASE="https://api-hr.step1ne.com"
DAILY_QUOTA=40
DAILY_COUNT_FILE="/tmp/li_daily_count_$(date +%Y%m%d).txt"

MORE_X=366; MORE_Y=701     # 「更多」按鈕（JS精確校正 2026-03-17）
PDF_X=468;  PDF_Y=505      # 「存為 PDF」選項（JS精確校正 2026-03-17）

check_quota() {
    count=0; [ -f "$DAILY_COUNT_FILE" ] && count=$(cat "$DAILY_COUNT_FILE")
    [ "$count" -ge "$DAILY_QUOTA" ] && echo "🚫 配額已滿" && exit 0
    echo "📊 今日：${count}/${DAILY_QUOTA}"
}
incr_quota() {
    count=0; [ -f "$DAILY_COUNT_FILE" ] && count=$(cat "$DAILY_COUNT_FILE")
    echo $((count+1)) > "$DAILY_COUNT_FILE"
}

download_one() {
    local url="$1" name="$2"
    local before=$(ls ~/Downloads/Profile*.pdf 2>/dev/null | wc -l | tr -d ' ')

    # 1. 導航
    osascript -e "tell application \"Google Chrome\" to set URL of active tab of front window to \"$url\""
    osascript -e 'tell application "Google Chrome" to activate'
    sleep $((RANDOM % 3 + 4))

    # 2. 點「更多」（用 peekaboo 更穩定）
    peekaboo click --coords ${MORE_X},${MORE_Y} --app "Google Chrome" > /dev/null 2>&1
    sleep $((RANDOM % 2 + 1))
    
    # 確認選單已打開
    local menu_status
    menu_status=$(osascript -e "tell application \"Google Chrome\" to execute active tab of front window javascript \"document.querySelector('[role=menu]') ? 'open' : 'closed'\"" 2>/dev/null)
    if [ "$menu_status" != "open" ]; then
        echo "⚠️  $name: 選單未打開，重試..."
        peekaboo click --coords ${MORE_X},${MORE_Y} --app "Google Chrome" > /dev/null 2>&1
        sleep 1.5
    fi

    # 3. 點「存為 PDF」
    peekaboo click --coords ${PDF_X},${PDF_Y} --app "Google Chrome" > /dev/null 2>&1

    # 4. 等下載（最多 120 秒）
    for s in $(seq 1 120); do
        sleep 1
        after=$(ls ~/Downloads/Profile*.pdf 2>/dev/null | wc -l | tr -d ' ')
        [ "$after" -gt "$before" ] && {
            newest=$(ls -t ~/Downloads/Profile*.pdf | head -1)
            echo "$newest"
            return 0
        }
    done
    return 1
}

# ===== 主流程 =====
candidates=$(cat /tmp/li_candidates.json)
total=$(echo "$candidates" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))")
mapping="[]"
success=0; failed=0

echo "🚀 LinkedIn PDF 批量下載 v3 — $total 人"
echo "=================================="
check_quota

for i in $(seq 0 $((total-1))); do
    s1_id=$(echo "$candidates" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d[$i]['id'])")
    name=$(echo "$candidates"  | python3 -c "import json,sys; d=json.load(sys.stdin); print(d[$i]['name'])")
    url=$(echo "$candidates"   | python3 -c "import json,sys; d=json.load(sys.stdin); print(d[$i]['linkedin_url'])")

    echo ""
    echo "[$((i+1))/$total] $name"
    check_quota

    pdf_path=$(download_one "$url" "$name")
    if [ -n "$pdf_path" ] && [ -f "$pdf_path" ]; then
        mapping=$(echo "$mapping" | python3 -c "
import json,sys
m=json.load(sys.stdin)
m.append({'id':'${s1_id}','name':'${name}','pdf':'${pdf_path}'})
print(json.dumps(m, ensure_ascii=False))
")
        ((success++))
        incr_quota
        echo "  ✅ $pdf_path"
    else
        ((failed++))
        echo "  ❌ 下載失敗，跳過"
    fi

    # 隨機間隔 180-300 秒
    if [ "$i" -lt "$((total-1))" ]; then
        wait=$((RANDOM % 121 + 180))
        echo "  ⏱️  等 ${wait}s..."
        sleep $wait
    fi
done

echo ""
echo "=================================="
echo "✅ 成功：$success  ❌ 失敗：$failed  共：$total"
echo "$mapping" > /tmp/pdf_mapping.json

[ "$success" -gt 0 ] && python3 "${SCRIPT_DIR}/process_resume.py" /tmp/pdf_mapping.json
