#!/bin/bash
# 104 完整爬蟲（純 bash 版本）

KEYWORD="${1:-後端工程師}"
LIMIT="${2:-5}"
OUTPUT="/tmp/104-result-$(date +%Y%m%d-%H%M%S).json"

echo "🔍 搜尋: $KEYWORD (限 $LIMIT 筆)" >&2

# 步驟 1：搜尋職缺
echo "📡 開啟搜尋頁面..." >&2
agent-browser open "https://www.104.com.tw/jobs/search/?keyword=$KEYWORD" >&2
agent-browser wait --load networkidle >&2

echo "📋 提取職缺列表..." >&2
JOBS=$(agent-browser eval "Array.from(document.querySelectorAll('a[href*=\"/job/\"]')).slice(0, $LIMIT).map(a => ({url: a.href, title: a.textContent.trim()})).filter(j => j.title.length > 5)")

# 解析 JSON（每個職缺）
echo "$JOBS" | jq -c '.[]' | while read -r job; do
    URL=$(echo "$job" | jq -r '.url')
    TITLE=$(echo "$job" | jq -r '.title')
    
    echo "  📄 $TITLE" >&2
    
    # 訪問職缺頁面
    agent-browser open "$URL" >&2
    agent-browser wait --load networkidle --timeout 5000 >&2
    
    # 提取公司資訊
    DETAIL=$(agent-browser eval "(function(){const get=(s)=>{const e=document.querySelector(s);return e?e.textContent.trim():null};const getHref=(s)=>{const e=document.querySelector(s);return e?e.href:null};return{company:get('a[href*=\"/company/\"]')||get('.company-name'),location:get('[data-qa=\"job-location\"]'),salary:get('[data-qa=\"job-salary\"]'),company_url:getHref('a[href*=\"/company/\"]')}})()")
    
    COMPANY=$(echo "$DETAIL" | jq -r '.company // "N/A"')
    LOCATION=$(echo "$DETAIL" | jq -r '.location // "N/A"')
    SALARY=$(echo "$DETAIL" | jq -r '.salary // "N/A"')
    COMPANY_URL=$(echo "$DETAIL" | jq -r '.company_url // ""')
    
    PHONE="待查"
    EMAIL="待查"
    WEBSITE="待查"
    
    # 如果有公司頁面，去爬取聯絡方式
    if [[ -n "$COMPANY_URL" && "$COMPANY_URL" != "null" ]]; then
        echo "    🏢 訪問公司頁面..." >&2
        agent-browser open "$COMPANY_URL" >&2
        agent-browser wait --load networkidle --timeout 5000 >&2
        
        CONTACT=$(agent-browser eval "(function(){const t=document.body.textContent;const p=t.match(/(\\d{2,4}[-\\s]?\\d{3,4}[-\\s]?\\d{3,4})/);const e=t.match(/([\\w\\.-]+@[\\w\\.-]+\\.\\w+)/);const w=document.querySelector('a[href*=\"http\"]:not([href*=\"104.com.tw\"])');return{phone:p?p[1]:null,email:e?e[1]:null,website:w?w.href:null}})()")
        
        PHONE=$(echo "$CONTACT" | jq -r '.phone // "待查"')
        EMAIL=$(echo "$CONTACT" | jq -r '.email // "待查"')
        WEBSITE=$(echo "$CONTACT" | jq -r '.website // "待查"')
        
        echo "    ✓ Phone: $PHONE | Email: $EMAIL" >&2
    fi
    
    # 輸出 JSON（一行一個）
    jq -n \
        --arg company "$COMPANY" \
        --arg job_title "$TITLE" \
        --arg location "$LOCATION" \
        --arg salary "$SALARY" \
        --arg url "$URL" \
        --arg phone "$PHONE" \
        --arg email "$EMAIL" \
        --arg website "$WEBSITE" \
        '{company: $company, job_title: $job_title, location: $location, salary: $salary, url: $url, phone: $phone, email: $email, website: $website}'
    
done | jq -s '.'  # 合併成陣列

agent-browser close >&2

echo "✅ 完成" >&2
