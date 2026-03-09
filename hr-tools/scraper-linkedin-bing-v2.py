#!/usr/bin/env python3
"""
LinkedIn 人才搜尋 v2 - 使用 Bing（反爬蟲較寬鬆）
策略：Bing 搜尋 → 提取 LinkedIn URLs

新增功能：
- 支援多頁搜尋（預設 3 頁 = 30 筆）
"""

import sys
import json
import subprocess
import time
import re
import urllib.parse
import random

def bing_search_linkedin(keywords, location="Taiwan", max_results=30):
    """使用 Bing 搜尋 LinkedIn 個人檔案（支援翻頁）"""
    
    query = f"{keywords} {location} site:linkedin.com/in"
    linkedin_urls = set()  # 用 set 去重
    
    # 計算需要幾頁（每頁 10 筆）
    pages_needed = (max_results + 9) // 10
    
    print(f"🔍 Bing 搜尋：{query}", file=sys.stderr)
    print(f"📄 搜尋頁數：{pages_needed} 頁（目標 {max_results} 筆）", file=sys.stderr)
    
    for page in range(pages_needed):
        # Bing 翻頁參數：first = (page * 10) + 1
        offset = page * 10 + 1
        
        encoded_query = urllib.parse.quote_plus(query)
        bing_url = f"https://www.bing.com/search?q={encoded_query}&count=10&first={offset}"
        
        print(f"  → 第 {page + 1} 頁: offset={offset}", file=sys.stderr)
        
        try:
            # Bing 比較友善，用 curl 就可以
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            ]
            
            result = subprocess.run([
                'curl', '-s', '-L',
                '-A', random.choice(user_agents),
                '-H', 'Accept-Language: en-US,en;q=0.9',
                '-H', 'Accept: text/html,application/xhtml+xml',
                bing_url
            ], capture_output=True, text=True, timeout=15)
            
            html = result.stdout
            
            # 檢查是否有結果（Bing 會返回 "No results found"）
            if 'no results found' in html.lower() or len(html) < 1000:
                print(f"  ⚠️  第 {page + 1} 頁無結果", file=sys.stderr)
                # 不是反爬蟲，繼續嘗試下一頁
            
            # 檢查是否被反爬蟲（真正的 captcha）
            if 'captcha' in html.lower() and 'recaptcha' in html.lower():
                print(f"  ⚠️  第 {page + 1} 頁被反爬蟲擋住，停止搜尋", file=sys.stderr)
                break
            
            # 提取 LinkedIn URLs（3 種方法）
            
            # 方法 1：直接找 LinkedIn URLs
            # 修改：Bing 搜尋結果中，LinkedIn 網址可能在 href="..." 或 cite 標籤中
            # 使用更寬鬆的正則，並解碼
            urls = re.findall(r'(https?://[a-z]{2,3}\.linkedin\.com/in/[a-zA-Z0-9\-_%]+)', html)
            # 解碼 URL (處理 %2d 等)
            decoded_urls = [urllib.parse.unquote(u) for u in urls]
            linkedin_urls.update(decoded_urls)
            
            # 方法 1.5：針對 Bing 的特定結構 href="https://www.linkedin.com/in/..."
            href_urls = re.findall(r'href="(https://[a-z]+\.linkedin\.com/in/[^"]+)"', html)
            linkedin_urls.update(href_urls)
            
            # 方法 2：從 Bing 的 URL 編碼中提取
            encoded_linkedin = re.findall(r'linkedin\.com%2fin%2f([a-zA-Z0-9\-_]+)', html)
            for username in encoded_linkedin:
                linkedin_urls.add(f"https://www.linkedin.com/in/{username}")
            
            # 方法 3：純文字的 linkedin.com/in/
            usernames = re.findall(r'linkedin\.com/in/([a-zA-Z0-9\-_]+)', html)
            for username in usernames:
                linkedin_urls.add(f"https://www.linkedin.com/in/{username}")
            
            print(f"    ✓ 累計找到 {len(linkedin_urls)} 個 LinkedIn 個人檔案", file=sys.stderr)
            
            # 如果已經足夠，提前結束
            if len(linkedin_urls) >= max_results:
                break
            
            # 翻頁間隔（避免太快被擋）
            if page < pages_needed - 1:
                time.sleep(random.uniform(2, 4))
            
        except Exception as e:
            print(f"  ❌ 第 {page + 1} 頁失敗：{e}", file=sys.stderr)
            continue
    
    # 清理並限制數量
    linkedin_urls = list(linkedin_urls)
    linkedin_urls = [u.split('?')[0].split('#')[0] for u in linkedin_urls]
    linkedin_urls = [u for u in linkedin_urls if '/in/' in u][:max_results]
    
    print(f"  ✓ 最終結果：{len(linkedin_urls)} 個 LinkedIn 個人檔案", file=sys.stderr)
    
    return linkedin_urls

def extract_linkedin_name_simple(url):
    """簡單方式：只返回 LinkedIn URL"""
    
    username = url.split('/in/')[-1].split('?')[0].strip('/')
    
    # 簡單轉換 username → 姓名（john-doe → John Doe）
    name = username.replace('-', ' ').title()
    
    return {
        'name': name,
        'linkedin_url': url,
        'source': 'linkedin_bing',
        'platforms': ['linkedin'],
        'skills': [],
        'contact': url
    }

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn 人才搜尋 v2（Bing，支援多頁）')
    parser.add_argument('--keywords', required=True, help='搜尋關鍵字')
    parser.add_argument('--location', default='Taiwan', help='地點')
    parser.add_argument('--max-results', type=int, default=30, help='最大結果數（預設 30）')
    
    args = parser.parse_args()
    
    print(f"🚀 LinkedIn 人才搜尋 v2：{args.keywords} @ {args.location}", file=sys.stderr)
    print(f"📍 使用 Bing 搜尋引擎（支援多頁）", file=sys.stderr)
    print("", file=sys.stderr)
    
    # 搜尋 LinkedIn URLs
    linkedin_urls = bing_search_linkedin(
        args.keywords,
        args.location,
        args.max_results
    )
    
    if not linkedin_urls:
        print("❌ 找不到 LinkedIn 個人檔案", file=sys.stderr)
        print("[]")
        return
    
    # 轉換成候選人格式
    candidates = []
    for url in linkedin_urls:
        candidates.append(extract_linkedin_name_simple(url))
    
    print(f"✅ 完成：{len(candidates)} 位候選人", file=sys.stderr)
    
    # 輸出 JSON
    print(json.dumps(candidates, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
