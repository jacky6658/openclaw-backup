#!/bin/bash
# 從 104 公司頁面抓取官網

SHEET_ID="1bkI7_cCh_Bs4qVa3HlXiy0CFzmItZlA-DYGHSPS4InE"
ACCOUNT="aijessie88@step1ne.com"

# 讀取公司名單
companies=$(gog sheets get "$SHEET_ID" "A2:A17" --account "$ACCOUNT" --json | jq -r '.values[][]')

row=2
echo "$companies" | while read -r company; do
    echo "[$row] 處理: $company"
    
    # 1. 搜尋公司
    agent-browser open "https://www.104.com.tw/company/search/?keyword=$company" 2>/dev/null
    agent-browser wait --load networkidle --timeout 8000 2>/dev/null
    
    # 2. 點擊第一個公司連結
    company_url=$(agent-browser eval "document.querySelector('a[href*=\"/company/\"]')?.href || null" 2>/dev/null | tr -d '"')
    
    if [ -z "$company_url" ] || [ "$company_url" = "null" ]; then
        echo "  ✗ 找不到公司頁面"
        ((row++))
        continue
    fi
    
    echo "  → 進入: $company_url"
    
    # 3. 進入公司頁面
    agent-browser open "$company_url" 2>/dev/null
    agent-browser wait --load networkidle --timeout 8000 2>/dev/null
    
    # 4. 抓取公司網址（從「公司網址」欄位）
    website=$(agent-browser eval "
        const label = Array.from(document.querySelectorAll('*')).find(el => el.textContent.trim() === '公司網址');
        if (label && label.nextElementSibling) {
            const link = label.nextElementSibling.querySelector('a');
            return link ? link.href : null;
        }
        return null;
    " 2>/dev/null | tr -d '"')
    
    if [ -z "$website" ] || [ "$website" = "null" ]; then
        echo "  ✗ 找不到公司網址"
        website="暫不提供"
    else
        echo "  ✓ 官網: $website"
    fi
    
    # 5. 更新到 Sheet
    gog sheets update "$SHEET_ID" "D$row" "$website" --account "$ACCOUNT" >/dev/null 2>&1
    
    ((row++))
    sleep 2
done

agent-browser close 2>/dev/null
echo "✅ 完成"
