#!/usr/bin/env python3
"""
LinkedIn 人才搜尋 - 使用 Bing（反爬蟲較寬鬆）
策略：Bing 搜尋 → 提取 LinkedIn URLs
"""

import sys
import json
import subprocess
import time
import re
import urllib.parse
import random

def bing_search_linkedin(keywords, location="Taiwan", max_results=10):
    """使用 Bing 搜尋 LinkedIn 個人檔案"""
    
    # Bing 查詢
    query = f"{keywords} {location} site:linkedin.com/in"
    encoded_query = urllib.parse.quote_plus(query)
    bing_url = f"https://www.bing.com/search?q={encoded_query}&count={max_results}"
    
    print(f"🔍 Bing 搜尋：{query}", file=sys.stderr)
    print(f"  → URL: {bing_url}", file=sys.stderr)
    
    try:
        # Bing 比較友善，用 curl 就可以
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        
        result = subprocess.run([
            'curl', '-s', '-L',
            '-A', random.choice(user_agents),
            '-H', 'Accept-Language: en-US,en;q=0.9',
            '-H', 'Accept: text/html,application/xhtml+xml',
            bing_url
        ], capture_output=True, text=True, timeout=15)
        
        html = result.stdout
        
        # 提取 LinkedIn URLs
        linkedin_urls = []
        
        # 方法 1：直接找 LinkedIn URLs
        urls = re.findall(r'https?://[a-z]{2,3}\.linkedin\.com/in/[a-zA-Z0-9\-_]+', html)
        linkedin_urls.extend(urls)
        
        # 方法 2：從 Bing 的 URL 編碼中提取
        # Bing 格式：<a href="https://www.bing.com/ck/a?!&&p=...&u=https%3a%2f%2fwww.linkedin.com%2fin%2fusername
        encoded_linkedin = re.findall(r'linkedin\.com%2fin%2f([a-zA-Z0-9\-_]+)', html)
        for username in encoded_linkedin:
            linkedin_urls.append(f"https://www.linkedin.com/in/{username}")
        
        # 方法 3：純文字的 linkedin.com/in/
        usernames = re.findall(r'linkedin\.com/in/([a-zA-Z0-9\-_]+)', html)
        for username in usernames:
            linkedin_urls.append(f"https://www.linkedin.com/in/{username}")
        
        # 去重並清理
        linkedin_urls = list(set(linkedin_urls))
        linkedin_urls = [u.split('?')[0].split('#')[0] for u in linkedin_urls]
        linkedin_urls = [u for u in linkedin_urls if '/in/' in u][:max_results]
        
        print(f"  ✓ 找到 {len(linkedin_urls)} 個 LinkedIn 個人檔案", file=sys.stderr)
        
        return linkedin_urls
        
    except Exception as e:
        print(f"  ❌ 失敗：{e}", file=sys.stderr)
        return []

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
        'contact': url  # LinkedIn URL 就是聯絡方式
    }

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn 人才搜尋（Bing）')
    parser.add_argument('--keywords', required=True, help='搜尋關鍵字')
    parser.add_argument('--location', default='Taiwan', help='地點')
    parser.add_argument('--max-results', type=int, default=10, help='最大結果數')
    
    args = parser.parse_args()
    
    print(f"🚀 LinkedIn 人才搜尋：{args.keywords} @ {args.location}", file=sys.stderr)
    print(f"📍 使用 Bing 搜尋引擎", file=sys.stderr)
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
    
    # 輸出 JSON
    print(json.dumps(candidates, ensure_ascii=False, indent=2))
    
    print(f"\n✅ 完成：{len(candidates)} 位候選人", file=sys.stderr)

if __name__ == '__main__':
    main()
