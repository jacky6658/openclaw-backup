#!/usr/bin/env python3
"""
104 公司聯絡方式爬蟲
用途：從 104 公司頁面或官網提取電話、Email、網址
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

def extract_company_id_from_url(url):
    """從 104 職缺 URL 提取公司 ID"""
    # URL 格式：https://www.104.com.tw/job/xxxxx
    # 需要訪問該頁面，從中提取公司連結
    match = re.search(r'/job/([a-z0-9]+)', url)
    if match:
        return match.group(1)
    return None

def scrape_104_company_page(job_url):
    """訪問 104 職缺頁面，提取公司資訊"""
    log_debug(f"訪問職缺頁面: {job_url}")
    
    # 開啟職缺頁面
    run_browser_command(f'agent-browser open "{job_url}"')
    run_browser_command('agent-browser wait --load networkidle')
    
    # 取得快照
    snapshot_json = run_browser_command('agent-browser snapshot -i --json')
    
    try:
        data = json.loads(snapshot_json)
        refs = data.get('data', {}).get('refs', {})
    except:
        log_debug("❌ 無法解析職缺頁面")
        return None
    
    # 解析公司資訊
    company_info = {
        "phone": None,
        "email": None,
        "website": None,
        "company_url": None
    }
    
    for ref_id, ref_data in refs.items():
        name = ref_data.get('name', '')
        role = ref_data.get('role', '')
        href = ref_data.get('href', '')
        
        # 電話號碼
        if not company_info['phone']:
            phone_match = re.search(r'(\d{2,4}[-\s]?\d{3,4}[-\s]?\d{3,4})', name)
            if phone_match:
                company_info['phone'] = phone_match.group(1)
        
        # Email
        if not company_info['email']:
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', name)
            if email_match:
                company_info['email'] = email_match.group(0)
        
        # 公司頁面連結
        if role == 'link' and '/company/' in href:
            company_info['company_url'] = href if href.startswith('http') else f"https://www.104.com.tw{href}"
        
        # 官網連結
        if role == 'link' and ('公司網址' in name or '官方網站' in name or '官網' in name):
            if href and not href.startswith('/'):
                company_info['website'] = href if href.startswith('http') else f"https://{href}"
    
    return company_info

def scrape_company_website(website_url):
    """爬取公司官網，提取聯絡方式"""
    if not website_url:
        return {"phone": None, "email": None}
    
    log_debug(f"訪問官網: {website_url}")
    
    # 嘗試找「聯絡我們」頁面
    contact_urls = [
        website_url,
        f"{website_url.rstrip('/')}/contact",
        f"{website_url.rstrip('/')}/contact-us",
        f"{website_url.rstrip('/')}/about",
        f"{website_url.rstrip('/')}/about-us"
    ]
    
    for url in contact_urls:
        try:
            run_browser_command(f'agent-browser open "{url}"')
            run_browser_command('agent-browser wait --load networkidle --timeout 5000')
            
            snapshot_json = run_browser_command('agent-browser snapshot -i --json')
            data = json.loads(snapshot_json)
            text = data.get('data', {}).get('text', '')
            
            # 提取電話
            phone_match = re.search(r'(\d{2,4}[-\s]?\d{3,4}[-\s]?\d{3,4})', text)
            phone = phone_match.group(1) if phone_match else None
            
            # 提取 Email
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
            email = email_match.group(0) if email_match else None
            
            if phone or email:
                return {"phone": phone, "email": email}
        except:
            continue
    
    return {"phone": None, "email": None}

def log_debug(message):
    """寫入 debug 日誌"""
    with open("/tmp/104-contact-scraper-debug.log", 'a', encoding='utf-8') as log:
        log.write(f"[{datetime.now()}] {message}\n")

def scrape_company_contact(company_data):
    """爬取公司聯絡方式（主函數）"""
    job_url = company_data.get('url', '')
    company_name = company_data.get('company', 'Unknown')
    
    log_debug(f"開始爬取: {company_name}")
    
    # 步驟 1：從 104 職缺頁面提取資訊
    company_info = scrape_104_company_page(job_url)
    
    if not company_info:
        log_debug(f"❌ 無法提取公司資訊: {company_name}")
        return {**company_data, "phone": "待查", "email": "待查", "website": "待查"}
    
    # 步驟 2：如果沒有電話或 Email，嘗試爬官網
    if (not company_info['phone'] or not company_info['email']) and company_info['website']:
        log_debug(f"📡 嘗試爬取官網: {company_info['website']}")
        website_contact = scrape_company_website(company_info['website'])
        
        if not company_info['phone']:
            company_info['phone'] = website_contact['phone']
        if not company_info['email']:
            company_info['email'] = website_contact['email']
    
    # 整合結果
    result = {
        **company_data,
        "phone": company_info['phone'] or "待查",
        "email": company_info['email'] or "待查",
        "website": company_info['website'] or "待查",
        "contact_person": "您好",
        "status": "待聯繫"
    }
    
    log_debug(f"✅ 完成: {company_name} | Phone: {result['phone']} | Email: {result['email']}")
    return result

def main():
    """主程式"""
    if len(sys.argv) < 2:
        print("用法: python3 scraper-company-contact.py <companies.json>", file=sys.stderr)
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # 讀取公司列表
    with open(input_file, 'r', encoding='utf-8') as f:
        companies = json.load(f)
    
    log_debug(f"開始處理 {len(companies)} 家公司")
    
    # 處理每家公司
    detailed_companies = []
    for company in companies:
        detailed = scrape_company_contact(company)
        detailed_companies.append(detailed)
    
    # 輸出 JSON
    print(json.dumps(detailed_companies, ensure_ascii=False, indent=2))
    
    # 關閉瀏覽器
    run_browser_command('agent-browser close')
    
    log_debug(f"✅ 全部完成，共處理 {len(detailed_companies)} 家公司")

if __name__ == "__main__":
    main()
