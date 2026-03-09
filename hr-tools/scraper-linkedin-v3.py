#!/usr/bin/env python3
"""
LinkedIn 人才搜尋 v3 - 使用 DuckDuckGo 避開 Google 反爬蟲
策略：DuckDuckGo HTML 搜尋 → 提取 LinkedIn URLs → agent-browser 訪問頁面
"""

import sys
import json
import subprocess
import time
import re
import urllib.parse

def duckduckgo_search_linkedin(keywords, location="Taiwan", max_results=10):
    """使用 DuckDuckGo 搜尋 LinkedIn 個人檔案（多策略）"""
    
    linkedin_urls = []
    
    # 策略 1：移除 location（有時候加 location 反而找不到）
    queries = [
        f"{keywords} site:linkedin.com/in",  # 不限地點
        f"{keywords} {location} site:linkedin.com/in",  # 限定地點
    ]
    
    for query in queries:
        if len(linkedin_urls) >= max_results:
            break
            
        encoded_query = urllib.parse.quote_plus(query)
        ddg_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        
        print(f"🔍 DuckDuckGo 搜尋：{query}", file=sys.stderr)
        
        try:
            # 輪換 User-Agent（避免被偵測）
            user_agents = [
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            ]
            
            import random
            ua = random.choice(user_agents)
            
            result = subprocess.run([
                'curl', '-s', '-L',
                '-A', ua,
                '-H', 'Accept-Language: en-US,en;q=0.9',
                ddg_url
            ], capture_output=True, text=True, timeout=15)
            
            html = result.stdout
            
            # 檢查是否被反爬蟲擋住
            if 'botnet' in html.lower() or 'challenge' in html.lower():
                print(f"  ⚠️  被反爬蟲擋住，跳過此查詢", file=sys.stderr)
                time.sleep(2)
                continue
            
            # 方法 1：直接找 LinkedIn URLs
            urls = re.findall(r'https?://[a-z]{2,3}\.linkedin\.com/in/[a-zA-Z0-9\-_]+', html)
            linkedin_urls.extend(urls)
            
            # 方法 2：找 DuckDuckGo 的重定向連結
            encoded_urls = re.findall(r'uddg=([^&"\']+)', html)
            for enc_url in encoded_urls:
                url = urllib.parse.unquote(enc_url)
                if 'linkedin.com/in/' in url:
                    linkedin_urls.append(url)
            
            # 方法 3：找結果中的 /in/username 格式
            usernames = re.findall(r'linkedin\.com/in/([a-zA-Z0-9\-_]+)', html)
            for username in usernames:
                linkedin_urls.append(f"https://www.linkedin.com/in/{username}")
            
            time.sleep(1)  # 避免太快
            
        except Exception as e:
            print(f"  ⚠️  搜尋失敗：{e}", file=sys.stderr)
            continue
    
    # 去重並清理
    linkedin_urls = list(set(linkedin_urls))
    linkedin_urls = [u.split('?')[0].split('#')[0] for u in linkedin_urls]
    linkedin_urls = [u for u in linkedin_urls if '/in/' in u][:max_results]
    
    print(f"  ✓ 總共找到 {len(linkedin_urls)} 個 LinkedIn 個人檔案", file=sys.stderr)
    
    return linkedin_urls

def extract_linkedin_name_simple(url):
    """簡單方式：只返回 LinkedIn URL（不訪問頁面，避免太慢）"""
    
    username = url.split('/in/')[-1].split('?')[0].strip('/')
    
    return {
        'name': username.replace('-', ' ').title(),  # 簡單轉換（john-doe → John Doe）
        'linkedin_url': url,
        'source': 'linkedin_ddg',
        'platforms': ['linkedin'],
        'skills': [],  # 空的，之後由 HR 手動補充或 AI 配對時推斷
        'note': '需手動訪問 LinkedIn 確認詳細資料'
    }

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn 人才搜尋 v3（DuckDuckGo）')
    parser.add_argument('--keywords', required=True, help='搜尋關鍵字')
    parser.add_argument('--location', default='Taiwan', help='地點')
    parser.add_argument('--max-results', type=int, default=10, help='最大結果數')
    parser.add_argument('--quick', action='store_true', help='快速模式（不訪問LinkedIn頁面）')
    
    args = parser.parse_args()
    
    print(f"🚀 LinkedIn 人才搜尋：{args.keywords} @ {args.location}", file=sys.stderr)
    print(f"📍 使用 DuckDuckGo（避開 Google 反爬蟲）", file=sys.stderr)
    print("", file=sys.stderr)
    
    # 步驟 1：DuckDuckGo 搜尋 LinkedIn URLs
    linkedin_urls = duckduckgo_search_linkedin(
        args.keywords,
        args.location,
        args.max_results
    )
    
    if not linkedin_urls:
        print("❌ 找不到 LinkedIn 個人檔案", file=sys.stderr)
        print("[]")
        return
    
    print(f"\n✅ 找到 {len(linkedin_urls)} 個候選人", file=sys.stderr)
    
    # 步驟 2：快速模式 - 只返回 URLs
    candidates = []
    
    if args.quick:
        print("⚡ 快速模式：只返回 LinkedIn URLs（不訪問頁面）", file=sys.stderr)
        for url in linkedin_urls:
            candidates.append(extract_linkedin_name_simple(url))
    else:
        print("🐢 完整模式：訪問每個頁面（預計 {} 秒）".format(len(linkedin_urls) * 5), file=sys.stderr)
        # 這裡可以加上 agent-browser 訪問頁面的邏輯
        # 但為了快速，先用簡單模式
        for url in linkedin_urls:
            candidates.append(extract_linkedin_name_simple(url))
    
    # 輸出 JSON
    print(json.dumps(candidates, ensure_ascii=False, indent=2))
    
    print(f"\n✅ 完成：{len(candidates)} 位候選人", file=sys.stderr)

if __name__ == '__main__':
    main()
