#!/bin/bash
# Gmail 智慧通知系統
# 只通知重要郵件：候選人回信 + 客戶聯繫
# 過濾廣告、系統通知

set -e

ACCOUNT="aijessie88@step1ne.com"
CACHE_FILE="$HOME/clawd/hr-tools/data/gmail-notified.json"
TELEGRAM_CHAT="-1003231629634"  # HR AI招募自動化群組
TELEGRAM_TOPIC="4"  # 履歷進件 Topic

# 建立快取目錄
mkdir -p "$(dirname "$CACHE_FILE")"

# 初始化快取檔案
if [ ! -f "$CACHE_FILE" ]; then
    echo "[]" > "$CACHE_FILE"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 開始檢查 $ACCOUNT 信箱..."

# 搜尋過去 1 天的未讀郵件
THREADS=$(gog gmail search "is:unread newer_than:1d" --account "$ACCOUNT" --json 2>/dev/null || echo '{"threads":[]}')

THREAD_COUNT=$(echo "$THREADS" | jq '.threads | length')
echo "找到 $THREAD_COUNT 封未讀郵件"

if [ "$THREAD_COUNT" -eq 0 ]; then
    echo "無新郵件"
    exit 0
fi

# 逐一處理郵件
NOTIFIED_COUNT=0

for i in $(seq 0 $((THREAD_COUNT - 1))); do
    THREAD=$(echo "$THREADS" | jq -r ".threads[$i]")
    
    THREAD_ID=$(echo "$THREAD" | jq -r '.id')
    FROM=$(echo "$THREAD" | jq -r '.from')
    SUBJECT=$(echo "$THREAD" | jq -r '.subject')
    SNIPPET=$(echo "$THREAD" | jq -r '.snippet')
    DATE=$(echo "$THREAD" | jq -r '.date')
    
    echo ""
    echo "=== 郵件 #$((i+1)) ==="
    echo "From: $FROM"
    echo "Subject: $SUBJECT"
    
    # 檢查是否已通知過
    ALREADY_NOTIFIED=$(jq --arg id "$THREAD_ID" 'any(.[]; . == $id)' "$CACHE_FILE")
    
    if [ "$ALREADY_NOTIFIED" == "true" ]; then
        echo "⏭️  已通知過，跳過"
        continue
    fi
    
    # ========================================
    # 智慧篩選邏輯
    # ========================================
    
    SHOULD_NOTIFY=false
    NOTIFY_REASON=""
    
    # 排除：自己寄的信
    if echo "$FROM" | grep -qi "aijessie88@step1ne.com"; then
        echo "❌ 排除：自己寄的信"
        continue
    fi
    
    # 排除：系統通知 / 廣告信
    if echo "$FROM" | grep -qiE "(no-?reply|noreply|notification|donotreply|automated|mailer-daemon)"; then
        echo "❌ 排除：系統通知"
        continue
    fi
    
    if echo "$SUBJECT" | grep -qiE "(unsubscribe|marketing|newsletter|promotion|advertisement)"; then
        echo "❌ 排除：廣告信"
        continue
    fi
    
    # ✅ 候選人回信判斷
    # 1. 主旨包含 Re: 或 回覆: 或 回信:
    if echo "$SUBJECT" | grep -qiE "^(Re:|回覆:|回复:|回信:|RE:)"; then
        SHOULD_NOTIFY=true
        NOTIFY_REASON="候選人回信"
        echo "✅ 符合：候選人回信（Re: 開頭）"
    fi
    
    # 2. 內容包含候選人回覆關鍵字
    if echo "$SNIPPET" | grep -qiE "(履歷|resume|面試|interview|興趣|interested|詳細|detail|了解更多|learn more|應徵|apply)"; then
        SHOULD_NOTIFY=true
        NOTIFY_REASON="候選人回覆（包含關鍵字）"
        echo "✅ 符合：候選人回覆關鍵字"
    fi
    
    # ✅ 客戶聯繫判斷
    # 1. 主旨包含職缺/招聘/合作關鍵字
    if echo "$SUBJECT" | grep -qiE "(職缺|招聘|招募|人才|合作|配合|需求|job|recruit|hiring|position|vacancy)"; then
        SHOULD_NOTIFY=true
        NOTIFY_REASON="客戶聯繫（職缺相關）"
        echo "✅ 符合：客戶聯繫"
    fi
    
    # 2. 寄件人是公司 Email（有公司網域）
    # 排除免費信箱 Gmail/Yahoo/Outlook/Hotmail
    if ! echo "$FROM" | grep -qiE "@(gmail|yahoo|outlook|hotmail|163|qq|sina)\."; then
        # 可能是公司 Email
        if echo "$SNIPPET" | grep -qiE "(職缺|招聘|合作|人才|job|recruit|position)"; then
            SHOULD_NOTIFY=true
            NOTIFY_REASON="客戶聯繫（公司 Email）"
            echo "✅ 符合：客戶聯繫（公司信箱）"
        fi
    fi
    
    # ========================================
    # 發送通知
    # ========================================
    
    if [ "$SHOULD_NOTIFY" == "true" ]; then
        echo "📧 準備通知..."
        
        # 格式化通知訊息
        MESSAGE="📧 <b>aijessie88 重要郵件</b>

<b>類型</b>：$NOTIFY_REASON
<b>寄件人</b>：$(echo "$FROM" | sed 's/</\&lt;/g' | sed 's/>/\&gt;/g')
<b>主旨</b>：$SUBJECT
<b>時間</b>：$DATE

<b>內容預覽</b>：
$(echo "$SNIPPET" | head -c 200)...

<i>請至信箱查看完整內容</i>"
        
        # 發送 Telegram 通知
        openclaw message send \
            --target "$TELEGRAM_CHAT" \
            --message "$MESSAGE" \
            --channel telegram \
            --thread "$TELEGRAM_TOPIC" 2>&1 || echo "⚠️  Telegram 發送失敗"
        
        # 記錄已通知
        jq --arg id "$THREAD_ID" '. += [$id]' "$CACHE_FILE" > "$CACHE_FILE.tmp"
        mv "$CACHE_FILE.tmp" "$CACHE_FILE"
        
        NOTIFIED_COUNT=$((NOTIFIED_COUNT + 1))
        echo "✅ 已通知"
        
        # 避免發送太快被限流
        sleep 2
    else
        echo "⏭️  不符合通知條件"
    fi
done

echo ""
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 完成！共通知 $NOTIFIED_COUNT 封重要郵件"

exit 0
