#!/usr/bin/env python3
"""
104人力銀行職缺爬蟲 v2
用途：搜尋職缺，提取公司和職位資訊（使用 JavaScript eval 提取）
"""

import subprocess
import json
import re
import sys
import tempfile
from datetime import datetime

def run_browser_command(cmd):
    """執行 agent-browser 指令"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout

def run_js_in_browser(js_code):
    """在瀏覽器中執行 JavaScript 並返回結果"""
    # 直接用 subprocess.run 傳遞參數，避免 shell 解析問題
    result = subprocess.run(
        ['agent-browser', 'eval', js_code],
        capture_output=True,
        text=True
    )
    return result.stdout

def log_debug(message):
    """寫入 debug 日誌"""
    with open("/tmp/104-scraper-v2-debug.log", 'a', encoding='utf-8') as log:
        log.write(f"[{datetime.now()}] {message}\n")

def search_104_jobs(keyword, max_results=20):
    """搜尋 104 職缺"""
    log_debug(f"🔍 搜尋: {keyword}")
    
    # 開啟搜尋頁面
    url = f"https://www.104.com.tw/jobs/search/?keyword={keyword}"
    run_browser_command(f'agent-browser open "{url}"')
    
    # 等待載入
    run_browser_command('agent-browser wait --load networkidle --timeout 10000')
    
    # 使用 JavaScript 提取職缺資料
    js_code = """
    (() => {
        const jobs = [];
        const jobCards = document.querySelectorAll('article[data-job-custno]');
        
        jobCards.forEach((card, index) => {
            if (index >= """ + str(max_results) + """) return;
            
            const titleEl = card.querySelector('a[data-job-link-type="1"]');
            const companyEl = card.querySelector('a[data-job-link-type="2"]');
            const locationEl = card.querySelector('[data-v-5e3f8c9f].job-list-tag-location');
            const salaryEl = card.querySelector('[data-v-5e3f8c9f].job-list-tag-salary');
            
            jobs.push({
                title: titleEl ? titleEl.innerText.trim() : 'N/A',
                url: titleEl ? titleEl.href : '',
                company: companyEl ? companyEl.innerText.trim() : 'N/A',
                location: locationEl ? locationEl.innerText.trim() : 'N/A',
                salary: salaryEl ? salaryEl.innerText.trim() : 'N/A'
            });
        });
        
        return JSON.stringify(jobs);
    })();
    """
    
    # 執行 JavaScript
    result = run_js_in_browser(js_code)
    
    log_debug(f"JavaScript result: {result[:200]}...")
    
    # 關閉瀏覽器
    run_browser_command('agent-browser close')
    
    # 解析結果
    try:
        jobs = json.loads(result.strip())
        log_debug(f"✅ 找到 {len(jobs)} 個職缺")
        return jobs
    except Exception as e:
        log_debug(f"❌ 解析失敗: {e}, result={result[:500]}")
        return []

def get_company_contact(job_url):
    """從職缺頁面提取公司聯絡方式"""
    log_debug(f"📞 訪問職缺頁面: {job_url}")
    
    run_browser_command(f'agent-browser open "{job_url}"')
    run_browser_command('agent-browser wait --load networkidle --timeout 10000')
    
    # 提取公司資訊的 JavaScript
    js_code = """
    (() => {
        const info = {
            phone: null,
            email: null,
            website: null,
            companyUrl: null
        };
        
        // 提取電話
        const phoneEl = document.querySelector('[data-v-7e8bc2b0].company-phone a');
        if (phoneEl) {
            info.phone = phoneEl.innerText.trim();
        }
        
        // 提取 Email（如果有）
        const emailEl = document.querySelector('[data-v-7e8bc2b0].company-email a');
        if (emailEl) {
            info.email = emailEl.innerText.trim();
        }
        
        // 提取公司網址
        const websiteEl = document.querySelector('[data-v-7e8bc2b0].company-website a');
        if (websiteEl) {
            info.website = websiteEl.href;
        }
        
        // 提取公司頁面連結
        const companyLinkEl = document.querySelector('a[href*="/company/"]');
        if (companyLinkEl) {
            info.companyUrl = companyLinkEl.href;
        }
        
        return JSON.stringify(info);
    })();
    """
    
    result = run_js_in_browser(js_code)
    
    # 關閉瀏覽器
    run_browser_command('agent-browser close')
    
    try:
        contact_info = json.loads(result.strip())
        log_debug(f"✅ 提取資訊: Phone={contact_info.get('phone')}, Email={contact_info.get('email')}, Website={contact_info.get('website')}")
        return contact_info
    except Exception as e:
        log_debug(f"❌ 提取失敗: {e}")
        return {"phone": None, "email": None, "website": None, "companyUrl": None}

def scrape_company_website(website_url):
    """爬取公司官網，提取聯絡方式"""
    if not website_url or not website_url.startswith('http'):
        return {"phone": None, "email": None}
    
    log_debug(f"🌐 訪問官網: {website_url}")
    
    # 嘗試找「聯絡我們」頁面
    contact_urls = [
        website_url,
        f"{website_url.rstrip('/')}/contact",
        f"{website_url.rstrip('/')}/contact-us",
        f"{website_url.rstrip('/')}/about"
    ]
    
    for url in contact_urls:
        try:
            run_browser_command(f'agent-browser open "{url}"')
            run_browser_command('agent-browser wait --load networkidle --timeout 5000')
            
            # 提取電話和 Email
            js_code = """
            (() => {
                const text = document.body.innerText;
                
                // 提取電話（台灣格式）
                const phoneMatch = text.match(/(\\d{2,4}[-\\s]?\\d{3,4}[-\\s]?\\d{3,4})/);
                
                // 提取 Email
                const emailMatch = text.match(/[\\w\\.-]+@[\\w\\.-]+\\.\\w+/);
                
                return JSON.stringify({
                    phone: phoneMatch ? phoneMatch[0] : null,
                    email: emailMatch ? emailMatch[0] : null
                });
            })();
            """
            
            result = run_js_in_browser(js_code)
            
            # 關閉瀏覽器
            run_browser_command('agent-browser close')
            
            contact_info = json.loads(result.strip())
            
            if contact_info.get('phone') or contact_info.get('email'):
                log_debug(f"✅ 官網找到資訊: {contact_info}")
                return contact_info
        except:
            continue
    
    log_debug(f"⚠️ 官網未找到聯絡方式")
    return {"phone": None, "email": None}

def main():
    """主程式"""
    keyword = sys.argv[1] if len(sys.argv) > 1 else "backend engineer"
    max_results = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    
    log_debug(f"開始處理: {keyword}, 數量: {max_results}")
    
    # 步驟 1：搜尋職缺
    jobs = search_104_jobs(keyword, max_results)
    
    if not jobs:
        print("[]")
        return
    
    # 步驟 2：提取每個職缺的公司聯絡方式
    detailed_jobs = []
    
    for job in jobs:
        log_debug(f"處理職缺: {job.get('title')}")
        
        # 從職缺頁面提取聯絡方式
        contact_info = get_company_contact(job.get('url', ''))
        
        # 如果沒有電話或 Email，嘗試爬官網
        if (not contact_info.get('phone') or not contact_info.get('email')) and contact_info.get('website'):
            website_contact = scrape_company_website(contact_info.get('website'))
            
            if not contact_info.get('phone'):
                contact_info['phone'] = website_contact.get('phone')
            if not contact_info.get('email'):
                contact_info['email'] = website_contact.get('email')
        
        # 整合資料
        detailed_job = {
            "company": job.get('company', 'N/A'),
            "job_title": job.get('title', 'N/A'),
            "location": job.get('location', 'N/A'),
            "salary": job.get('salary', 'N/A'),
            "url": job.get('url', ''),
            "phone": contact_info.get('phone') or "待查",
            "email": contact_info.get('email') or "待查",
            "website": contact_info.get('website') or "待查",
            "contact_person": "您好",
            "status": "待聯繫"
        }
        
        detailed_jobs.append(detailed_job)
        log_debug(f"✅ 完成: {detailed_job['company']}")
    
    # 輸出 JSON
    print(json.dumps(detailed_jobs, ensure_ascii=False, indent=2))
    
    log_debug(f"✅ 全部完成，共處理 {len(detailed_jobs)} 家公司")

if __name__ == "__main__":
    main()
