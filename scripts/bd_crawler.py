#!/usr/bin/env python3
"""
BD 開發客戶爬蟲
用法：python3 bd_crawler.py "Java 台北 100-500人"
"""

import subprocess
import json
import sys
import time
import re
from datetime import datetime

def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def search_104_companies(keyword, max_results=20):
    """用 104 搜尋有在徵才的公司"""
    print(f"🔍 搜尋 104：{keyword}")
    
    url = f"https://www.104.com.tw/jobs/search/?keyword={keyword}&jobsource=index_s"
    run(f'agent-browser open "{url}"')
    run('agent-browser wait --load networkidle --timeout 15000')
    time.sleep(2)
    
    snapshot = run('agent-browser snapshot -i --json')
    
    try:
        data = json.loads(snapshot)
        refs = data.get('data', {}).get('refs', {})
    except:
        return []
    
    companies = {}
    
    for ref_id, ref_data in refs.items():
        name = ref_data.get('name', '')
        href = ref_data.get('href', '')
        
        # 找公司連結
        if 'company' in href and href not in companies:
            companies[href] = name
        
        if len(companies) >= max_results:
            break
    
    return [{"name": v, "url": k} for k, v in companies.items() if v]

def get_company_info(company_name):
    """用 Brave Search 補充公司聯絡資訊"""
    import os
    api_key = "BSAGYPKNGT7tKInGsjI9EQxO9AkHBls"
    
    try:
        import requests
        resp = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            params={"q": f"{company_name} 台灣 HR 人資 聯絡"},
            headers={"Accept": "application/json", "X-Subscription-Token": api_key},
            timeout=10
        )
        results = resp.json().get('web', {}).get('results', [])
        
        # 找官網
        website = next((r.get('url') for r in results 
                       if not any(x in r.get('url','') for x in ['104.com','1111','linkedin','facebook'])), "待查")
        
        return {"website": website}
    except:
        return {"website": "待查"}

def main():
    keyword = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    
    if not keyword:
        print("❌ 請輸入關鍵字")
        sys.exit(1)
    
    print(f"\n{'='*50}")
    print(f"🚀 BD 開發客戶爬蟲啟動")
    print(f"🔑 關鍵字：{keyword}")
    print(f"⏰ 開始時間：{datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*50}\n")
    
    companies = search_104_companies(keyword)
    
    if not companies:
        print("❌ 找不到相關公司")
        sys.exit(1)
    
    print(f"✅ 找到 {len(companies)} 間公司\n")
    
    results = []
    for i, co in enumerate(companies, 1):
        print(f"[{i}/{len(companies)}] {co['name']}")
        info = get_company_info(co['name'])
        co.update(info)
        results.append(co)
        time.sleep(1)  # 避免被封
    
    # 輸出結果
    print(f"\n{'='*50}")
    print(f"📊 BD 開發名單 — {keyword}")
    print(f"{'='*50}")
    
    for i, co in enumerate(results, 1):
        print(f"\n{i}. {co['name']}")
        print(f"   104：{co['url']}")
        print(f"   官網：{co.get('website', '待查')}")
    
    print(f"\n{'='*50}")
    print(f"✅ 完成！共 {len(results)} 間公司")
    print(f"⏰ 完成時間：{datetime.now().strftime('%H:%M:%S')}")
    
    # 儲存 JSON
    output_file = f"/tmp/bd_result_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"💾 結果已存：{output_file}")

if __name__ == "__main__":
    main()
