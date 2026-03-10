#!/bin/bash
# LinkedIn PDF Batch Download Script
# Uses fixed coordinates: More button (339,719), Save PDF (446,508)

API_BASE="https://backendstep1ne.zeabur.app"

download_pdf() {
    local url="$1"
    local name="$2"
    local id="$3"
    
    # Get current PDF count
    before=$(ls ~/Downloads/Profile*.pdf 2>/dev/null | wc -l | tr -d ' ')
    
    # Navigate to profile
    osascript -e "tell application \"Google Chrome\" to set URL of active tab of front window to \"$url\"" 2>/dev/null
    sleep 4
    
    # Open More menu
    cliclick c:339,719
    sleep 0.8
    
    # Click Save as PDF
    cliclick c:446,508
    sleep 5
    
    # Check for new PDF
    after=$(ls ~/Downloads/Profile*.pdf 2>/dev/null | wc -l | tr -d ' ')
    
    if [ "$after" -gt "$before" ]; then
        # Get the newest PDF
        newest=$(ls -t ~/Downloads/Profile*.pdf | head -1)
        echo "✅ $name (ID:$id) → $newest"
        return 0
    else
        echo "❌ $name (ID:$id) - No PDF downloaded"
        return 1
    fi
}

# Read candidates from JSON
candidates=$(cat /tmp/li_candidates.json)

# Process each candidate
total=$(echo "$candidates" | jq length)
success=0
failed=0

echo "🚀 Starting batch download of $total LinkedIn PDFs..."
echo "=================================================="

for i in $(seq 0 $((total-1))); do
    id=$(echo "$candidates" | jq -r ".[$i].id")
    name=$(echo "$candidates" | jq -r ".[$i].name")
    url=$(echo "$candidates" | jq -r ".[$i].linkedin_url")
    
    echo ""
    echo "[$((i+1))/$total] Processing: $name"
    
    if download_pdf "$url" "$name" "$id"; then
        ((success++))
    else
        ((failed++))
    fi
    
    # Brief pause between candidates
    sleep 2
done

echo ""
echo "=================================================="
echo "📊 Complete: $success succeeded, $failed failed out of $total"
