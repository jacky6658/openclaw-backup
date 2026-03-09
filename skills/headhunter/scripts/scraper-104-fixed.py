#!/usr/bin/env python3
"""
104人力銀行職缺爬蟲（修正版）
"""

import subprocess
import json
import sys
from datetime import datetime

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def log(msg):
    log_file = f"/tmp/104-scraper-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.now()}] {msg}\n")

def search_jobs(keyword, max_results=20):
    log(f"搜尋: {keyword}")
    
    # 開啟搜尋頁面
    url = f"https://www.104.com.tw/jobs/search/?keyword={keyword}"
    run_cmd(f'agent-browser open "{url}"')
    run_cmd('agent-browser wait --load networkidle')
    
    # 提取職缺 URL 和標題
    js = "Array.from(document.querySelectorAll('a[href*=\"/job/\"]')).slice(0, %d).map(a => ({url: a.href, title: a.textContent.trim()})).filter(j => j.title.length > 5)" % max_results
    result = run_cmd(f"agent-browser eval '{js}'")
    
    try:
        jobs = json.loads(result)
        log(f"找到 {len(jobs)} 個職缺")
    except:
        log("解析失敗")
        run_cmd('agent-browser close')
        return []
    
    # 抓取詳細資訊
    detailed = []
    for job in jobs[:max_results]:
        log(f"處理: {job['title'][:40]}")
        
        # 訪問職缺頁面
        run_cmd(f"agent-browser open '{job['url']}'")
        run_cmd('agent-browser wait --load networkidle --timeout 5000')
        
        # 提取資訊
        js_detail = """
(function(){
  const get = (sel) => {
    const el = document.querySelector(sel);
    return el ? el.textContent.trim() : 'N/A';
  };
  return {
    company: get('a[href*="/company/"]') || get('.company-name'),
    location: get('[data-qa="job-location"]') || get('.job-location'),
    salary: get('[data-qa="job-salary"]') || get('.job-salary')
  };
})()
"""
        detail_result = run_cmd(f"agent-browser eval '{js_detail}'")
        
        try:
            details = json.loads(detail_result)
        except:
            details = {"company": "N/A", "location": "N/A", "salary": "N/A"}
        
        detailed.append({
            "company": details.get('company', 'N/A'),
            "job_title": job['title'],
            "location": details.get('location', 'N/A'),
            "salary": details.get('salary', 'N/A'),
            "url": job['url']
        })
    
    run_cmd('agent-browser close')
    log(f"完成，共 {len(detailed)} 個")
    return detailed

def main():
    keyword = sys.argv[1] if len(sys.argv) > 1 else "backend"
    max_results = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    
    jobs = search_jobs(keyword, max_results)
    print(json.dumps(jobs, ensure_ascii=False, indent=2))
    
    # 備份
    with open(f"/tmp/104-jobs-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json", 'w', encoding='utf-8') as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
