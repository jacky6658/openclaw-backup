#!/bin/bash

# JD 管理機器人指令處理器
# 處理群組中的 JD 相關指令

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHEET_ID="1QPaeOm-slNVFCeM8Q3gg3DawKjzp2tYwyfquvdHlZFE"
ACCOUNT="aiagentg888@gmail.com"

# 解析指令
COMMAND="$1"
shift
ARGS="$@"

case "$COMMAND" in
    "列出職缺"|"JD列表"|"職缺列表")
        LIMIT=5
        printf "📋 Step1ne 職缺列表（最新 %s 筆）\n\n" "$LIMIT"
        
        # 從 Google Sheets 讀取資料
        DATA=$(gog sheets get "$SHEET_ID" "工作表1!A2:K100" --json --account "$ACCOUNT" 2>&1)
        
        if [[ $? -ne 0 ]]; then
            echo "❌ 讀取職缺失敗"
            exit 1
        fi
        
        # 使用 jq 解析並格式化（列出「最新加入」的後 5 筆，避免刷屏）
        echo "$DATA" | jq -r --argjson limit "$LIMIT" '
            [.values[] | select(length >= 9)]
            | . as $rows
            | ($rows | length) as $n
            | (
                if $n <= $limit then $rows
                else $rows[($n-$limit):$n]
                end
              )[]
            | "\(.[0]) | \(.[1])\n   💰 \(.[4]) | 📍 \(.[8]) | 🎯 \(.[9])\n   🔧 \(.[5])\n   📅 \(.[6]) | 🎓 \(.[7])\n"' | \
        awk 'BEGIN {i=1} /^[^[:space:]]/ {printf "%d️⃣ %s", i++, $0; next} {print}'

        # 統計（總數仍顯示全量）
        COUNT=$(echo "$DATA" | jq '.values | length')
        echo "━━━━━━━━━━━━━━━━━━━━"
        echo "總計：$COUNT 個職缺"
        echo ""
        echo "🧭 想找特定職缺？"
        echo "• 直接跟我說關鍵字（例如：『我想找 Java 後端／工程師主管／台中／150k 以上』），我幫你查。"
        echo "• 或用指令：/search 關鍵字"
        ;;
        
    "搜尋職缺")
        LIMIT=5
        if [[ -z "$ARGS" ]]; then
            echo "❌ 請提供搜尋關鍵字"
            echo "用法：搜尋職缺 [關鍵字]"
            exit 1
        fi
        
        printf "🔍 搜尋：%s（最新符合 %s 筆）\n\n" "$ARGS" "$LIMIT"
        
        # 從 Google Sheets 讀取資料
        DATA=$(gog sheets get "$SHEET_ID" "工作表1!A2:K100" --json --account "$ACCOUNT" 2>&1)
        
        if [[ $? -ne 0 ]]; then
            echo "❌ 讀取職缺失敗"
            exit 1
        fi
        
        # 搜尋並格式化（只列「最新符合」的後 5 筆，避免刷屏）
        echo "$DATA" | jq -r --arg keyword "$ARGS" --argjson limit "$LIMIT" '
            [.values[] | select(length >= 9)]
            | map(select(
                (.[0] | ascii_downcase | contains($keyword | ascii_downcase)) or
                (.[1] | ascii_downcase | contains($keyword | ascii_downcase)) or
                (.[5] | ascii_downcase | contains($keyword | ascii_downcase))
            ))
            | . as $hits
            | ($hits | length) as $n
            | (
                if $n == 0 then []
                elif $n <= $limit then $hits
                else $hits[($n-$limit):$n]
                end
              )[]
            | "\(.[0]) | \(.[1])\n   💰 \(.[4]) | 📍 \(.[8]) | 🎯 \(.[9])\n   🔧 \(.[5])\n   📅 \(.[6]) | 🎓 \(.[7])\n"' | \
        awk 'BEGIN {i=1} /^[^[:space:]]/ {printf "%d️⃣ %s", i++, $0; next} {print}'

        # 使用者提示
        echo "━━━━━━━━━━━━━━━━━━━━"
        echo "🧭 想找更精準？你可以直接跟我說：職稱/關鍵技能/地點/薪資區間/年資，我幫你查。"
        echo "例：『找 台北 AI 相關 120k 以上 3 年+』"
        ;;
        
    "JD統計"|"職缺統計")
        echo "📊 職缺統計報表"
        echo ""
        
        # 從 Google Sheets 讀取資料
        DATA=$(gog sheets get "$SHEET_ID" "工作表1!A2:K100" --json --account "$ACCOUNT" 2>&1)
        
        if [[ $? -ne 0 ]]; then
            echo "❌ 讀取職缺失敗"
            exit 1
        fi
        
        # 統計
        TOTAL=$(echo "$DATA" | jq '.values | length')
        OPEN=$(echo "$DATA" | jq '[.values[] | select(length >= 10 and .[9] == "開放中")] | length')
        CLOSED=$(echo "$DATA" | jq '[.values[] | select(length >= 10 and .[9] == "已成交")] | length')
        PAUSED=$(echo "$DATA" | jq '[.values[] | select(length >= 10 and .[9] == "暫停")] | length')
        
        echo "總職缺數：$TOTAL"
        echo "🟢 開放中：$OPEN"
        echo "✅ 已成交：$CLOSED"
        echo "⏸️  暫停中：$PAUSED"
        echo ""
        
        # 客戶分布
        echo "📊 客戶分布："
        echo "$DATA" | jq -r '.values[] | select(length >= 2) | .[1]' | sort | uniq -c | \
        awk '{printf "   • %s: %d 個職缺\n", $2, $1}'
        ;;
        
    *)
        echo "❌ 未知指令：$COMMAND"
        echo ""
        echo "📋 可用指令："
        echo "• 列出職缺 / JD列表 / 職缺列表"
        echo "• 搜尋職缺 [關鍵字]"
        echo "• JD統計 / 職缺統計"
        exit 1
        ;;
esac
