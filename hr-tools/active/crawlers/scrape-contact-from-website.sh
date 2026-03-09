#!/bin/bash
# 從公司官網抓取聯絡資訊

SHEET="1bkI7_cCh_Bs4qVa3HlXiy0CFzmItZlA-DYGHSPS4InE"
ACC="aijessie88@step1ne.com"

# 讀取公司名稱和官網
data=$(gog sheets get "$SHEET" "A2:D17" --account "$ACC" --json)

row=2
echo "$data" | jq -r '.values[] | @json' | while read line; do
    company=$(echo "$line" | jq -r '.[0]')
    website=$(echo "$line" | jq -r '.[3]')  # D 欄
    
    echo "[$row] $company"
    
    # 跳過無效官網
    if [[ -z "$website" ]] || [[ "$website" == "null" ]] || [[ "$website" =~ ^(待查|找不到|暫不提供)$ ]]; then
        echo "  ✗ 無官網"
        ((row++))
        continue
    fi
    
    echo "  → $website"
    
    # 開啟官網
    agent-browser open "$website" 2>/dev/null
    agent-browser wait --load networkidle --timeout 8000 2>/dev/null
    
    # 找「聯絡我們」或「Contact」連結
    contact_url=$(agent-browser eval "
        const links = Array.from(document.querySelectorAll('a'));
        const contactLink = links.find(a => 
            a.textContent.match(/(聯絡|聯繫|Contact|contact-us|關於我們|About)/i) ||
            a.href.match(/(contact|about|company)/i)
        );
        contactLink ? contactLink.href : null;
    " 2>/dev/null | tr -d '"')
    
    if [[ "$contact_url" == "null" ]] || [[ -z "$contact_url" ]]; then
        echo "  → 在首頁直接抓"
        contact_url="$website"
    else
        echo "  → 進入 Contact: $contact_url"
        agent-browser open "$contact_url" 2>/dev/null
        agent-browser wait --load networkidle --timeout 8000 2>/dev/null
    fi
    
    # 抓取頁面文字內容
    text=$(agent-browser eval "document.body.innerText" 2>/dev/null)
    
    # 用正則提取電話（台灣格式）
    phone=$(echo "$text" | grep -oE '(\+886|02|03|04|05|06|07|08|09)[- ]?[0-9]{3,4}[- ]?[0-9]{4}' | head -1)
    
    # 提取 Email（優先業務相關）
    email=$(echo "$text" | grep -oE '[a-zA-Z0-9._+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' | grep -vE '(example|privacy|unsubscribe)' | head -1)
    
    # 如果沒找到，標記為待查
    [ -z "$phone" ] && phone="待查"
    [ -z "$email" ] && email="待查"
    
    echo "  ✓ 電話: $phone"
    echo "  ✓ Email: $email"
    
    # 更新到 Sheet
    gog sheets update "$SHEET" "B$row" "$phone" --account "$ACC" >/dev/null 2>&1
    gog sheets update "$SHEET" "C$row" "$email" --account "$ACC" >/dev/null 2>&1
    
    ((row++))
    sleep 2
done

agent-browser close 2>/dev/null
echo "✅ 完成"
