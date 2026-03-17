#!/bin/bash
# LinkedIn PDF 批量下載 v2 - 使用 JS 定位 + peekaboo 真實點擊
# 流程：導航 → JS找按鈕位置 → peekaboo點擊 → 等下載 → 處理

API_BASE="https://api-hr.step1ne.com"
DAILY_QUOTA=40
DAILY_COUNT_FILE="/tmp/li_daily_count_$(date +%Y%m%d).txt"
SCRIPT_DIR="$(dirname "$0")"

check_quota() {
    today_count=0
    [ -f "$DAILY_COUNT_FILE" ] && today_count=$(cat "$DAILY_COUNT_FILE")
    if [ "$today_count" -ge "$DAILY_QUOTA" ]; then
        echo "🚫 今日配額已達上限（${DAILY_QUOTA} 份）"
        exit 0
    fi
    echo "📊 今日已下載：${today_count}/${DAILY_QUOTA}"
}

increment_quota() {
    today_count=0
    [ -f "$DAILY_COUNT_FILE" ] && today_count=$(cat "$DAILY_COUNT_FILE")
    echo $((today_count + 1)) > "$DAILY_COUNT_FILE"
}

# 取得按鈕在螢幕上的實際座標（JS 找位置，轉換成螢幕座標）
get_button_screen_coords() {
    local js="$1"
    osascript << ASEOF
tell application "Google Chrome"
    set r to execute front window's active tab javascript "$js"
    return r
end tell
ASEOF
}

download_pdf() {
    local url="$1"
    local name="$2"
    local s1_id="$3"

    before_count=$(ls ~/Downloads/Profile*.pdf 2>/dev/null | wc -l | tr -d ' ')

    # 1. 導航到頁面
    osascript -e "tell application \"Google Chrome\" to set URL of active tab of front window to \"${url}\""
    osascript -e 'tell application "Google Chrome" to activate'
    echo "  ⏳ 等待頁面載入..."
    sleep $((RANDOM % 3 + 4))

    # 2. 用 JS 找「更多」按鈕的 BoundingRect
    coords=$(osascript << 'ASEOF'
tell application "Google Chrome"
    set result to execute front window's active tab javascript "
        var btns = document.querySelectorAll('button');
        for (var b of btns) {
            if (b.innerText && b.innerText.trim() === '更多') {
                var r = b.getBoundingClientRect();
                var x = Math.round(r.left + r.width/2);
                var y = Math.round(r.top + r.height/2);
                return x + ',' + y;
            }
        }
        return 'not_found';
    "
    return result
end tell
ASEOF
)

    echo "  📍 更多按鈕位置: $coords"

    if [ "$coords" = "not_found" ] || [ -z "$coords" ]; then
        echo "  ❌ 找不到「更多」按鈕"
        return 1
    fi

    btn_x=$(echo "$coords" | cut -d',' -f1)
    btn_y=$(echo "$coords" | cut -d',' -f2)

    # 3. 取得 Chrome 視窗位置，計算螢幕絕對座標
    win_info=$(osascript << 'ASEOF'
tell application "Google Chrome"
    set w to front window
    set b to bounds of w
    return (item 1 of b) & "," & (item 2 of b)
end tell
ASEOF
)
    win_x=$(echo "$win_info" | cut -d',' -f1)
    win_y=$(echo "$win_info" | cut -d',' -f2)

    # Chrome toolbar 高度約 100px（含 Tab bar + address bar + bookmarks bar）
    toolbar_h=100
    abs_x=$((win_x + btn_x))
    abs_y=$((win_y + toolbar_h + btn_y))

    echo "  🖱️  點擊更多：螢幕座標 (${abs_x}, ${abs_y})"
    peekaboo click --coords "${abs_x},${abs_y}"
    sleep $((RANDOM % 2 + 1))

    # 4. 截圖確認選單開啟
    sleep 1

    # 5. 用 JS 找「存為 PDF」的位置
    pdf_coords=$(osascript << 'ASEOF'
tell application "Google Chrome"
    set result to execute front window's active tab javascript "
        var items = document.querySelectorAll('[role=menuitem], li, a, button, div');
        for (var el of items) {
            var txt = (el.innerText || el.textContent || '').trim();
            if (txt === '存為 PDF' || txt === 'Save to PDF') {
                var r = el.getBoundingClientRect();
                if (r.width > 0 && r.height > 0) {
                    var x = Math.round(r.left + r.width/2);
                    var y = Math.round(r.top + r.height/2);
                    return x + ',' + y;
                }
            }
        }
        return 'not_found';
    "
    return result
end tell
ASEOF
)

    echo "  📍 存為PDF位置: $pdf_coords"

    if [ "$pdf_coords" = "not_found" ] || [ -z "$pdf_coords" ]; then
        echo "  ❌ 找不到「存為 PDF」選項"
        peekaboo press escape
        return 1
    fi

    pdf_x=$(echo "$pdf_coords" | cut -d',' -f1)
    pdf_y=$(echo "$pdf_coords" | cut -d',' -f2)
    abs_pdf_x=$((win_x + pdf_x))
    abs_pdf_y=$((win_y + toolbar_h + pdf_y))

    echo "  🖱️  點擊存為PDF：(${abs_pdf_x}, ${abs_pdf_y})"
    peekaboo click --coords "${abs_pdf_x},${abs_pdf_y}"

    # 6. 等待下載（LinkedIn 需要 5-15 秒準備）
    echo "  ⏳ 等待 PDF 下載..."
    max_wait=20
    for i in $(seq 1 $max_wait); do
        sleep 1
        after_count=$(ls ~/Downloads/Profile*.pdf 2>/dev/null | wc -l | tr -d ' ')
        if [ "$after_count" -gt "$before_count" ]; then
            newest=$(ls -t ~/Downloads/Profile*.pdf | head -1)
            echo "  ✅ 下載成功: $newest"
            echo "$newest"
            return 0
        fi
    done

    echo "  ❌ 等待 ${max_wait}s 後仍無新 PDF"
    return 1
}

# ===== 主流程 =====
candidates=$(cat /tmp/li_candidates.json)
total=$(echo "$candidates" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))")

echo "🚀 LinkedIn PDF 批量下載 v2（25人）"
echo "=================================================="
check_quota

success=0
failed=0
mapping="[]"

for i in $(seq 0 $((total-1))); do
    s1_id=$(echo "$candidates" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d[$i]['id'])")
    name=$(echo "$candidates" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d[$i]['name'])")
    url=$(echo "$candidates" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d[$i]['linkedin_url'])")

    echo ""
    echo "[$((i+1))/$total] $name"

    check_quota

    output=$(download_pdf "$url" "$name" "$s1_id")
    pdf_path=$(echo "$output" | grep "Downloads" | tail -1)

    if [ -n "$pdf_path" ] && [ -f "$pdf_path" ]; then
        mapping=$(echo "$mapping" | python3 -c "
import json,sys
m = json.load(sys.stdin)
m.append({'id': '${s1_id}', 'name': '${name}', 'pdf': '${pdf_path}'})
print(json.dumps(m))
")
        ((success++))
        increment_quota
        echo "  💾 已記錄: $pdf_path"
    else
        ((failed++))
        echo "  ⚠️  跳過"
    fi

    # 隨機間隔 180-300 秒
    if [ "$i" -lt "$((total-1))" ]; then
        wait_sec=$((RANDOM % 121 + 180))
        echo "  ⏱️  等待 ${wait_sec}s..."
        sleep $wait_sec
    fi
done

echo ""
echo "=================================================="
echo "📊 完成: 成功 ${success} / 失敗 ${failed} / 共 ${total}"

echo "$mapping" > /tmp/pdf_mapping.json

if [ "$success" -gt 0 ]; then
    echo "🔍 開始解析上傳..."
    python3 "${SCRIPT_DIR}/process_resume.py" /tmp/pdf_mapping.json
fi
