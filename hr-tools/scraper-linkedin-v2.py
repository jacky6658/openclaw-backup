#!/usr/bin/env python3
"""
LinkedIn 人才搜尋 v2 - 使用 agent-browser 繞過 Google 反爬蟲
策略：agent-browser Google 搜尋 → 提取 LinkedIn URLs → 抓公開資料
"""

import sys
import json
import subprocess
import time
import re

def agent_browser_google_search(keywords, location="Taiwan", max_results=10):
    """使用 agent-browser 搜尋 LinkedIn 個人檔案"""
    
    query = f"{keywords} {location} site:linkedin.com/in"
    google_url = f"https://www.google.com/search?q={query.replace(' ', '+')}&num={max_results}"
    
    print(f"🔍 Google 搜尋（agent-browser）：{query}", file=sys.stderr)
    print(f"  → URL: {google_url}", file=sys.stderr)
    
    try:
        # 使用 agent-browser 訪問 Google
        subprocess.run(['agent-browser', 'navigate', google_url], 
                      check=True, capture_output=True, timeout=15)
        
        # 等待頁面載入
        time.sleep(3)
        
        # 抓取頁面內容
        result = subprocess.run(['agent-browser', 'snapshot'],
                               capture_output=True, text=True, timeout=10)
        
        page_text = result.stdout
        
        # 從頁面文字中提取 LinkedIn URLs
        # agent-browser snapshot 會給出可讀文字，我們找 linkedin.com/in/ 的連結
        linkedin_urls = []
        
        # 方法 1：直接搜尋 URL 格式
        urls = re.findall(r'https?://[a-z]{2,3}\.linkedin\.com/in/[a-zA-Z0-9\-_]+', page_text)
        linkedin_urls.extend(urls)
        
        # 方法 2：搜尋「linkedin.com/in/username」格式
        usernames = re.findall(r'linkedin\.com/in/([a-zA-Z0-9\-_]+)', page_text)
        for username in usernames:
            linkedin_urls.append(f"https://www.linkedin.com/in/{username}")
        
        # 去重並清理
        linkedin_urls = list(set(linkedin_urls))
        linkedin_urls = [u.split('?')[0] for u in linkedin_urls]  # 移除查詢參數
        linkedin_urls = linkedin_urls[:max_results]
        
        print(f"  ✓ 找到 {len(linkedin_urls)} 個 LinkedIn 個人檔案", file=sys.stderr)
        
        return linkedin_urls
        
    except subprocess.TimeoutExpired:
        print(f"  ⚠️  超時（Google 反爬蟲？）", file=sys.stderr)
        return []
    except Exception as e:
        print(f"  ❌ 失敗：{e}", file=sys.stderr)
        return []

def extract_linkedin_name_browser(url):
    """使用 agent-browser 訪問 LinkedIn 公開頁面並提取姓名"""
    
    username = url.split('/in/')[-1].split('?')[0].strip('/')
    
    try:
        # 訪問 LinkedIn 個人頁面
        subprocess.run(['agent-browser', 'navigate', url],
                      check=True, capture_output=True, timeout=15)
        
        time.sleep(2)  # 等待頁面載入
        
        # 抓取頁面文字
        result = subprocess.run(['agent-browser', 'snapshot'],
                               capture_output=True, text=True, timeout=10)
        
        page_text = result.stdout
        
        # LinkedIn 公開頁面標題格式通常是：「Name - Job Title | LinkedIn」
        lines = page_text.split('\n')
        name = None
        
        # 找第一行（通常是姓名）
        for line in lines[:10]:
            line = line.strip()
            if line and len(line) > 2 and len(line) < 100:
                # 清理 LinkedIn 後綴
                line = re.sub(r'\s*[-|]\s*(LinkedIn|Taiwan|台灣).*$', '', line)
                if line:
                    name = line
                    break
        
        return {
            'name': name or username,
            'linkedin_url': url,
            'source': 'linkedin_public_browser',
            'platforms': ['linkedin']
        }
        
    except Exception as e:
        print(f"  ⚠️  無法抓取 {url}: {e}", file=sys.stderr)
        return {
            'name': username,
            'linkedin_url': url,
            'source': 'linkedin_public_browser',
            'platforms': ['linkedin']
        }

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn 人才搜尋 v2（agent-browser）')
    parser.add_argument('--keywords', required=True, help='搜尋關鍵字')
    parser.add_argument('--location', default='Taiwan', help='地點')
    parser.add_argument('--max-results', type=int, default=10, help='最大結果數')
    
    args = parser.parse_args()
    
    print(f"🚀 LinkedIn 人才搜尋：{args.keywords} @ {args.location}", file=sys.stderr)
    print(f"⚠️  使用 agent-browser（慢但穩定，預計 {args.max_results * 5} 秒）", file=sys.stderr)
    print("", file=sys.stderr)
    
    # 步驟 1：Google 搜尋 LinkedIn URLs
    linkedin_urls = agent_browser_google_search(
        args.keywords,
        args.location,
        args.max_results
    )
    
    if not linkedin_urls:
        print("❌ 找不到 LinkedIn 個人檔案", file=sys.stderr)
        print("[]")
        return
    
    print(f"\n📋 開始抓取 {len(linkedin_urls)} 個 LinkedIn 個人檔案...\n", file=sys.stderr)
    
    # 步驟 2：訪問每個 LinkedIn 頁面
    candidates = []
    
    for i, url in enumerate(linkedin_urls):
        print(f"  [{i+1}/{len(linkedin_urls)}] {url}", file=sys.stderr)
        
        candidate = extract_linkedin_name_browser(url)
        candidates.append(candidate)
        
        print(f"    ✓ {candidate['name']}", file=sys.stderr)
        
        # 避免被擋（每個間隔 3 秒）
        if i < len(linkedin_urls) - 1:
            time.sleep(3)
    
    # 輸出 JSON
    print(json.dumps(candidates, ensure_ascii=False, indent=2))
    
    print(f"\n✅ 完成：{len(candidates)} 位候選人", file=sys.stderr)

if __name__ == '__main__':
    main()
