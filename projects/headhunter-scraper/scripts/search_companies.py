#!/usr/bin/env python3
"""
獵頭自動化：搜尋新公司和求職者
使用 Brave Search API
"""

import json
import os
from datetime import datetime
import requests

# Brave Search API
BRAVE_API_KEY = os.getenv('BRAVE_API_KEY', 'BSAGYPKNGT7tKInGsjI9EQxO9AkHBls')
BRAVE_API_URL = 'https://api.search.brave.com/res/v1/web/search'

# 搜尋關鍵字
COMPANY_QUERIES = [
    "AI startup Taiwan 2026 hiring",
    "台灣 AI 新創 招募",
    "SaaS company Taiwan hiring",
    "數位行銷公司 徵才 台灣"
]

CANDIDATE_QUERIES = [
    "AI engineer Taiwan open to work",
    "數位行銷經理 轉職",
    "product manager 求職 台灣",
    "資料科學家 找工作"
]

def search_brave(query, count=10):
    """使用 Brave Search API 搜尋"""
    headers = {
        'Accept': 'application/json',
        'X-Subscription-Token': BRAVE_API_KEY
    }
    params = {
        'q': query,
        'count': count,
        'country': 'TW',
        'search_lang': 'zh-tw'
    }
    
    try:
        response = requests.get(BRAVE_API_URL, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ 搜尋失敗 [{query}]: {e}")
        return None

def extract_results(data):
    """提取搜尋結果"""
    if not data or 'web' not in data:
        return []
    
    results = []
    for item in data.get('web', {}).get('results', []):
        results.append({
            'title': item.get('title', ''),
            'url': item.get('url', ''),
            'description': item.get('description', ''),
            'published': item.get('age', '')
        })
    return results

def main():
    """主程式"""
    print("🚀 開始搜尋新公司和求職者...")
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    all_results = {
        'timestamp': timestamp,
        'companies': [],
        'candidates': []
    }
    
    # 搜尋公司
    print("\n📊 搜尋公司...")
    for query in COMPANY_QUERIES:
        print(f"  🔍 {query}")
        data = search_brave(query, count=5)
        if data:
            results = extract_results(data)
            all_results['companies'].extend(results)
            print(f"    ✅ 找到 {len(results)} 筆")
    
    # 搜尋求職者
    print("\n👤 搜尋求職者...")
    for query in CANDIDATE_QUERIES:
        print(f"  🔍 {query}")
        data = search_brave(query, count=5)
        if data:
            results = extract_results(data)
            all_results['candidates'].extend(results)
            print(f"    ✅ 找到 {len(results)} 筆")
    
    # 儲存結果
    output_file = f"/Users/user/clawd/projects/headhunter-scraper/data/results_{datetime.now().strftime('%Y%m%d')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 結果已儲存：{output_file}")
    print(f"📊 公司：{len(all_results['companies'])} 筆")
    print(f"👤 求職者：{len(all_results['candidates'])} 筆")
    
    return all_results

if __name__ == '__main__':
    main()
