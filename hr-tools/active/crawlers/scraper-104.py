#!/usr/bin/env python3
"""
104人力銀行職缺爬蟲
用途：搜尋職缺，提取公司和職位資訊
"""

import subprocess
import json
import re
import sys
from datetime import datetime

def run_browser_command(cmd):
    """執行 agent-browser 指令"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout

def search_104_jobs(keyword, max_results=20):
    """搜尋 104 職缺"""
    # Debug 訊息改為寫入日誌（不輸出到 stdout/stderr）
    with open(f"/tmp/104-scraper-debug.log", 'a', encoding='utf-8') as log:
        log.write(f"[{datetime.now()}] 🔍 搜尋: {keyword}\n")
    
    # 開啟搜尋頁面
    url = f"https://www.104.com.tw/jobs/search/?keyword={keyword}"
    run_browser_command(f'agent-browser open "{url}"')
    
    # 等待載入
    run_browser_command('agent-browser wait --load networkidle')
    
    # 取得快照
    snapshot_json = run_browser_command('agent-browser snapshot -i --json')
    
    try:
        data = json.loads(snapshot_json)
        refs = data.get('data', {}).get('refs', {})
    except:
        print("❌ 無法解析結果")
        return []
    
    # 解析職缺
    jobs = []
    current_job = {}
    
    for ref_id, ref_data in refs.items():
        name = ref_data.get('name', '')
        role = ref_data.get('role', '')
        href = ref_data.get('href', '')
        
        if role != 'link':
            continue
            
        # 職位名稱（包含 Engineer, 工程師, Developer 等）
        if re.search(r'Engineer|工程師|Developer|Backend|Frontend|Full.?Stack|Manager|主管', name, re.I):
            if current_job:
                jobs.append(current_job)
            # 提取真實的職缺 URL
            job_url = href if href.startswith('http') else f"https://www.104.com.tw{href}"
            current_job = {'title': name, 'ref': ref_id, 'url': job_url}
            
        # 公司名稱（通常在職位後面）
        elif current_job and 'company' not in current_job:
            if '股份有限公司' in name or '有限公司' in name or '科技' in name:
                current_job['company'] = name
                
        # 產業
        elif current_job and 'industry' not in current_job:
            if '業' in name and len(name) < 20:
                current_job['industry'] = name
                
        # 地點
        elif current_job and 'location' not in current_job:
            if re.match(r'^(台北|新北|桃園|新竹|台中|台南|高雄)', name):
                current_job['location'] = name
                
        # 薪資
        elif current_job and 'salary' not in current_job:
            if '月薪' in name or '年薪' in name or '待遇' in name:
                current_job['salary'] = name
                
        # 經驗
        elif current_job and 'experience' not in current_job:
            if '年以上' in name or '經歷不拘' in name:
                current_job['experience'] = name
        
        if len(jobs) >= max_results:
            break
    
    # 加入最後一個
    if current_job and len(jobs) < max_results:
        jobs.append(current_job)
    
    # 關閉瀏覽器
    run_browser_command('agent-browser close')
    
    return jobs

def main():
    keyword = sys.argv[1] if len(sys.argv) > 1 else "backend engineer"
    max_results = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    
    jobs = search_104_jobs(keyword, max_results)
    
    # 轉換為符合 bd-automation.sh 期望的格式
    formatted_jobs = []
    for job in jobs:
        formatted_jobs.append({
            "company": job.get('company', 'N/A'),
            "job_title": job.get('title', 'N/A'),
            "location": job.get('location', 'N/A'),
            "salary": job.get('salary', 'N/A'),
            "url": job.get('url', f"https://www.104.com.tw/job/{job.get('ref', '')}")
        })
    
    # 輸出 JSON 到標準輸出（供 bd-automation.sh 使用）
    print(json.dumps(formatted_jobs, ensure_ascii=False, indent=2))
    
    # 同時存一份到 /tmp 供查看（debug 用）
    output_file = f"/tmp/104-jobs-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(formatted_jobs, f, ensure_ascii=False, indent=2)
    
    # Debug info 寫入日誌檔（不輸出到 stderr，避免干擾 bash 腳本的 JSON 解析）
    log_file = f"/tmp/104-scraper-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
    with open(log_file, 'w', encoding='utf-8') as log:
        log.write(f"📊 找到 {len(jobs)} 個職缺\n")
        log.write(f"✅ JSON 結果已輸出到標準輸出\n")
        log.write(f"✅ 備份已存至: {output_file}\n")

if __name__ == "__main__":
    main()
