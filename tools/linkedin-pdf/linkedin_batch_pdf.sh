#!/bin/bash
# LinkedIn PDF 批量下載 + 自動處理腳本
# 流程：下載 → 改名 → 上傳 Drive → 解析匯入 Step1ne → 刪除本地
# 防護：隨機間隔、滑鼠漂移、時間限制、分批大休息

API_BASE="https://backendstep1ne.zeabur.app"
MAPPING_FILE="/tmp/pdf_mapping.json"

# ===== 防護：只在白天跑 =====
check_time() {
    hour=$(date +%H)
    if [ "$hour" -lt 9 ] || [ "$hour" -ge 22 ]; then
        echo "⏰ 現在是 $(date '+%H:%M')，超出允許時段（09:00-22:00），停止執行"
        exit 0
    fi
}

# ===== 防護：隨機滑鼠漂移 =====
random_mouse_drift() {
    # 在目標座標附近隨機移動幾次，模擬人類手部微抖
    local target_x=$1
    local target_y=$2
    local steps=$((RANDOM % 3 + 2))  # 2-4步
    for s in $(seq 1 $steps); do
        drift_x=$((target_x + RANDOM % 30 - 15))
        drift_y=$((target_y + RANDOM % 20 - 10))
        cliclick m:${drift_x},${drift_y}
        sleep 0.$((RANDOM % 4 + 1))
    done
    # 最後移到目標
    cliclick m:${target_x},${target_y}
    sleep 0.$((RANDOM % 3 + 1))
}

# ===== 防護：隨機捲動頁面 =====
random_scroll() {
    local scroll_times=$((RANDOM % 3 + 1))
    for s in $(seq 1 $scroll_times); do
        scroll_y=$((RANDOM % 300 + 100))
        osascript -e "tell application \"Google Chrome\" to execute front window's active tab javascript \"window.scrollBy(0, $scroll_y)\"" 2>/dev/null
        sleep 0.$((RANDOM % 5 + 3))
    done
    # 稍微捲回去
    osascript -e 'tell application "Google Chrome" to execute front window'\''s active tab javascript "window.scrollTo(0, 0)"' 2>/dev/null
    sleep 0.$((RANDOM % 3 + 1))
}

download_pdf() {
    local url="$1"
    local name="$2"
    local id="$3"

    before=$(ls ~/Downloads/Profile*.pdf 2>/dev/null | wc -l | tr -d ' ')

    # 開頁面
    osascript -e "tell application \"Google Chrome\" to set URL of active tab of front window to \"$url\"" 2>/dev/null

    # 隨機等待頁面載入（3-6秒）
    sleep $((RANDOM % 4 + 3))

    # 防護：隨機捲動頁面（模擬閱讀）
    random_scroll

    # 防護：隨機等待（0.5-2秒）再點 More
    sleep 0.$((RANDOM % 15 + 5))

    # 防護：滑鼠漂移後點擊 More 按鈕
    random_mouse_drift 339 719
    cliclick c:339,719
    sleep $((RANDOM % 2 + 1)).$((RANDOM % 9))

    # 點擊 Save as PDF
    random_mouse_drift 446 508
    cliclick c:446,508

    # 等待下載（4-7秒）
    sleep $((RANDOM % 4 + 4))

    after=$(ls ~/Downloads/Profile*.pdf 2>/dev/null | wc -l | tr -d ' ')

    if [ "$after" -gt "$before" ]; then
        newest=$(ls -t ~/Downloads/Profile*.pdf | head -1)
        echo "✅ $name (ID:$id) → $newest"
        echo "$newest"
        return 0
    else
        echo "❌ $name (ID:$id) - No PDF downloaded"
        return 1
    fi
}

# ===== 主流程 =====
candidates=$(cat /tmp/li_candidates.json)
total=$(echo "$candidates" | jq length)

echo "🚀 Starting batch download of $total LinkedIn PDFs..."
echo "=================================================="

success=0
failed=0
mapping="[]"

for i in $(seq 0 $((total-1))); do
    # 防護：每個候選人前檢查時間
    check_time

    id=$(echo "$candidates" | jq -r ".[$i].id")
    name=$(echo "$candidates" | jq -r ".[$i].name")
    url=$(echo "$candidates" | jq -r ".[$i].linkedin_url")

    echo ""
    echo "[$((i+1))/$total] Processing: $name"

    output=$(download_pdf "$url" "$name" "$id" 2>&1)
    echo "$output"

    pdf_path=$(echo "$output" | grep "~/Downloads\|/Users" | tail -1 | awk '{print $NF}')

    if [ -f "$pdf_path" ]; then
        mapping=$(echo "$mapping" | jq --arg id "$id" --arg name "$name" --arg pdf "$pdf_path" '. + [{id: $id, name: $name, pdf: $pdf}]')
        ((success++))
    else
        newest=$(ls -t ~/Downloads/Profile*.pdf 2>/dev/null | head -1)
        if [ -n "$newest" ]; then
            mapping=$(echo "$mapping" | jq --arg id "$id" --arg name "$name" --arg pdf "$newest" '. + [{id: $id, name: $name, pdf: $pdf}]')
            ((success++))
        else
            ((failed++))
        fi
    fi

    # ===== 防護：隨機間隔 50-100 秒 =====
    wait_sec=$((RANDOM % 51 + 50))
    echo "  ⏱️  等待 ${wait_sec}s..."
    sleep $wait_sec

    # 每 5 人小休息 2-3 分鐘（隨機）
    pos5=$(( (i + 1) % 5 ))
    pos10=$(( (i + 1) % 10 ))
    pos20=$(( (i + 1) % 20 ))

    if [ "$pos20" -eq 0 ] && [ "$i" -lt "$((total-1))" ]; then
        # 每 20 人大休息 8-12 分鐘
        big_rest=$((RANDOM % 241 + 480))
        echo ""
        echo "⏸️  完成第 $((i+1)) 位，20人大休息 $((big_rest/60)) 分鐘..."
        sleep $big_rest
        echo "▶️  繼續..."
    elif [ "$pos10" -eq 0 ] && [ "$i" -lt "$((total-1))" ]; then
        # 每 10 人休息 3-5 分鐘
        rest=$((RANDOM % 121 + 180))
        echo ""
        echo "⏸️  完成第 $((i+1)) 位，10人休息 $((rest/60)) 分鐘..."
        sleep $rest
        echo "▶️  繼續..."
    elif [ "$pos5" -eq 0 ] && [ "$i" -lt "$((total-1))" ]; then
        # 每 5 人休息 2-3 分鐘
        rest=$((RANDOM % 61 + 120))
        echo ""
        echo "⏸️  完成第 $((i+1)) 位，5人小休息 $((rest/60)) 分鐘..."
        sleep $rest
        echo "▶️  繼續..."
    fi
done

echo ""
echo "=================================================="
echo "📊 Download: $success succeeded, $failed failed out of $total"

echo "$mapping" > "$MAPPING_FILE"
echo "💾 Mapping saved to $MAPPING_FILE"

if [ "$success" -gt 0 ]; then
    echo ""
    echo "🔍 Starting parse + upload + cleanup..."
    python3 "$(dirname "$0")/process_resume.py" "$MAPPING_FILE"
fi
