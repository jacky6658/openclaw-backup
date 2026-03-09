#!/bin/bash
# 批次抓取 104 公司官網

SHEET_ID="1bkI7_cCh_Bs4qVa3HlXiy0CFzmItZlA-DYGHSPS4InE"
ACCOUNT="aijessie88@step1ne.com"

# 測試 5 家
companies=(
  "東豐科技股份有限公司"
  "和運租車股份有限公司"
  "詮欣股份有限公司"
  "台泥儲能科技股份有限公司"
  "緯穎科技服務股份有限公司"
)

row=2
for company in "${companies[@]}"; do
    echo "[$row] $company"
    
    # 搜尋公司
    agent-browser open "https://www.104.com.tw/company/search/?keyword=${company// /%20}" 2>/dev/null
    agent-browser wait --load networkidle --timeout 8000 2>/dev/null
    
    # 找公司連結（第一個 /company/ 連結）
    company_url=$(agent-browser eval "document.querySelector('a[href*=\"/company/\"][href*=\"10\"]')?.href || null" 2>/dev/null | tr -d '"')
    
    if [ -z "$company_url" ] || [ "$company_url" = "null" ]; then
        echo "  ✗ 找不到公司"
        ((row++))
        continue
    fi
    
    echo "  → $company_url"
    
    # 進入公司頁面
    agent-browser open "$company_url" 2>/dev/null
    agent-browser wait --load networkidle --timeout 8000 2>/dev/null
    
    # 方法1：用 snapshot 找 ref
    ref=$(agent-browser snapshot 2>/dev/null | grep -A2 "公司網址" | grep "ref=" | sed 's/.*ref=\([a-z0-9]*\).*/\1/' | head -1)
    
    if [ -n "$ref" ]; then
        website=$(agent-browser eval "document.querySelector('[data-automation-id=\"$ref\"]')?.href || document.querySelector('a[href]:has-text(\"$ref\")')?.href || null" 2>/dev/null | tr -d '"')
    fi
    
    # 方法2：直接找外部連結
    if [ -z "$website" ] || [ "$website" = "null" ]; then
        website=$(agent-browser eval "
            Array.from(document.querySelectorAll('a[href^=\"http\"]'))
                .map(a => a.href)
                .filter(href => 
                    !href.includes('104.com.tw') &&
                    !href.includes('onelink.me') &&
                    !href.includes('google.com') &&
                    !href.includes('translate') &&
                    !href.includes('facebook') &&
                    !href.includes('linkedin') &&
                    href.match(/^https?:\\/\\/www\\.[a-z0-9-]+\\.[a-z]{2,}/)
                )[0] || null
        " 2>/dev/null | tr -d '"')
    fi
    
    if [ -z "$website" ] || [ "$website" = "null" ]; then
        echo "  ✗ 找不到官網"
        website="暫不提供"
    else
        echo "  ✓ $website"
    fi
    
    # 更新到 Sheet
    gog sheets update "$SHEET_ID" "D$row" "$website" --account "$ACCOUNT" >/dev/null 2>&1
    
    ((row++))
    sleep 2
done

agent-browser close 2>/dev/null
echo "✅ 完成"
