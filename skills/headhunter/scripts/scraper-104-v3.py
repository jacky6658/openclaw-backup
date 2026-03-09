#!/usr/bin/env python3
"""
104人力銀行職缺爬蟲 v3 - 使用 snapshot 替代 JavaScript eval
"""

import subprocess
import json
import re
import sys
from datetime import datetime

def log_debug(message):
    """寫入 debug 日誌"""
    with open("/tmp/104-scraper-v3-debug.log", 'a', encoding='utf-8') as log:
        log.write(f"[{datetime.now()}] {message}\n")

def search_104_jobs(keyword, max_results=20):
    """搜尋 104 職缺"""
    log_debug(f"🔍 搜尋: {keyword}, 數量: {max_results}")
    
    # 步驟 1：訪問首頁建立 Session
    subprocess.run(['agent-browser', 'open', 'https://www.104.com.tw'], check=True)
    subprocess.run(['agent-browser', 'wait', '--load', 'networkidle', '--timeout', '10000'], check=True)
    
    # 步驟 2：導航到搜尋頁
    url = f"https://www.104.com.tw/jobs/search/?keyword={keyword}"
    subprocess.run(['agent-browser', 'navigate', url], check=True)
    subprocess.run(['agent-browser', 'wait', '--load', 'networkidle', '--timeout', '15000'], check=True)
    
    # 等待頁面完全載入
    import time
    time.sleep(3)
    
    # 步驟 3：取得 snapshot
    result = subprocess.run(['agent-browser', 'snapshot', '-i', '--json'], capture_output=True, text=True)
    
    try:
        data = json.loads(result.stdout)
    except Exception as e:
        log_debug(f"❌ JSON 解析失敗: {e}")
        subprocess.run(['agent-browser', 'close'], check=True)
        return []
    
    refs = data.get('data', {}).get('refs', {})
    
    # 步驟 4：提取職缺資訊
    jobs = []
    seen_urls = set()
    
    # 將 refs 轉換為 list 以便按順序處理
    ref_ids = list(refs.keys())
    
    for idx, ref_id in enumerate(ref_ids):
        ref_data = refs[ref_id]
        role = ref_data.get('role', '')
        href = ref_data.get('href', '')
        name = ref_data.get('name', '').strip()
        
        # 找職缺連結（role=link + href 包含 /job/）
        if role == 'link' and '/job/' in href:
            # 標準化 URL
            if href.startswith('//'):
                job_url = f"https:{href}"
            elif href.startswith('/'):
                job_url = f"https://www.104.com.tw{href}"
            elif not href.startswith('http'):
                job_url = f"https://{href}"
            else:
                job_url = href
            
            # 去除 query string 中的 jobsource 參數，只保留 job ID
            job_url_clean = re.sub(r'\?.*', '', job_url)
            
            # 避免重複
            if job_url_clean in seen_urls:
                continue
            
            seen_urls.add(job_url_clean)
            
            # 從附近的 refs 提取公司、地點、薪資
            company_name = "N/A"
            location = "N/A"
            salary = "N/A"
            
            # 往後找 10 個 refs
            for i in range(idx+1, min(idx+15, len(ref_ids))):
                check_ref = refs[ref_ids[i]]
                check_name = check_ref.get('name', '').strip()
                check_role = check_ref.get('role', '')
                check_href = check_ref.get('href', '')
                
                # 公司名稱（第一個 link + /company/）
                if check_role == 'link' and '/company/' in check_href and company_name == "N/A":
                    company_name = check_name
                
                # 地點（第一個 link + area=）
                if check_role == 'link' and 'area=' in check_href and location == "N/A":
                    location = check_name
                
                # 薪資（第一個包含 scmin/scmax/sctp 的 link）
                if check_role == 'link' and ('scmin=' in check_href or 'scmax=' in check_href or 'sctp=' in check_href) and salary == "N/A":
                    salary = check_name
            
            jobs.append({
                "company": company_name,
                "job_title": name,
                "location": location,
                "salary": salary,
                "url": job_url_clean
            })
            
            if len(jobs) >= max_results:
                break
    
    # 關閉瀏覽器
    subprocess.run(['agent-browser', 'close'], check=True)
    
    log_debug(f"✅ 找到 {len(jobs)} 個職缺")
    for job in jobs[:3]:
        log_debug(f"  - {job['company']}: {job['job_title']}")
    
    return jobs

def main():
    """主程式"""
    keyword = sys.argv[1] if len(sys.argv) > 1 else "AI工程師"
    max_results = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    log_debug(f"開始處理: {keyword}, 數量: {max_results}")
    
    jobs = search_104_jobs(keyword, max_results)
    
    # 輸出 JSON
    print(json.dumps(jobs, ensure_ascii=False, indent=2))
    
    log_debug(f"✅ 全部完成，共處理 {len(jobs)} 家公司")

if __name__ == "__main__":
    main()
