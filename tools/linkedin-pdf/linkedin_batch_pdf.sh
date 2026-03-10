#!/bin/bash
# LinkedIn PDF 批量下載 + 自動處理腳本
# 流程：下載 → 改名 → 上傳 Drive → 解析匯入 Step1ne → 刪除本地

API_BASE="https://backendstep1ne.zeabur.app"
MAPPING_FILE="/tmp/pdf_mapping.json"

download_pdf() {
    local url="$1"
    local name="$2"
    local id="$3"
    
    before=$(ls ~/Downloads/Profile*.pdf 2>/dev/null | wc -l | tr -d ' ')
    
    osascript -e "tell application \"Google Chrome\" to set URL of active tab of front window to \"$url\"" 2>/dev/null
    sleep 4
    
    cliclick c:339,719
    sleep 0.8
    cliclick c:446,508
    sleep 5
    
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

# Read candidates from JSON
candidates=$(cat /tmp/li_candidates.json)
total=$(echo "$candidates" | jq length)

echo "🚀 Starting batch download of $total LinkedIn PDFs..."
echo "=================================================="

success=0
failed=0
mapping="[]"

for i in $(seq 0 $((total-1))); do
    id=$(echo "$candidates" | jq -r ".[$i].id")
    name=$(echo "$candidates" | jq -r ".[$i].name")
    url=$(echo "$candidates" | jq -r ".[$i].linkedin_url")
    
    echo ""
    echo "[$((i+1))/$total] Processing: $name"
    
    output=$(download_pdf "$url" "$name" "$id" 2>&1)
    echo "$output"
    
    # Get last line (pdf path) if successful
    pdf_path=$(echo "$output" | grep "~/Downloads\|/Users" | tail -1 | awk '{print $NF}')
    
    if [ -f "$pdf_path" ]; then
        mapping=$(echo "$mapping" | jq --arg id "$id" --arg name "$name" --arg pdf "$pdf_path" '. + [{id: $id, name: $name, pdf: $pdf}]')
        ((success++))
    else
        # Try to get newest pdf path another way
        newest=$(ls -t ~/Downloads/Profile*.pdf 2>/dev/null | head -1)
        if [ -n "$newest" ]; then
            mapping=$(echo "$mapping" | jq --arg id "$id" --arg name "$name" --arg pdf "$newest" '. + [{id: $id, name: $name, pdf: $pdf}]')
            ((success++))
        else
            ((failed++))
        fi
    fi
    
    sleep 2
done

echo ""
echo "=================================================="
echo "📊 Download: $success succeeded, $failed failed out of $total"

# Save mapping
echo "$mapping" > "$MAPPING_FILE"
echo "💾 Mapping saved to $MAPPING_FILE"

# Run parse + upload + delete
if [ "$success" -gt 0 ]; then
    echo ""
    echo "🔍 Starting parse + upload + cleanup..."
    python3 "$(dirname "$0")/process_resume.py" "$MAPPING_FILE"
fi
