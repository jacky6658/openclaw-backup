#!/usr/bin/env python3
"""
從 Google 搜尋補充公司聯絡資訊
"""

import json
import sys
import requests
from bs4 import BeautifulSoup
import re
from time import sleep

def search_google(company_name):
    """Google 搜尋公司"""
    query = f"{company_name} 台灣 聯絡電話 官網"
    url = f"https://www.google.com/search?q={query}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 提取文字內容
        text = soup.get_text()
        
        # 尋找電話號碼（台灣格式）
        phone_match = re.search(r'(\d{2,4}[-\s]?\d{3,4}[-\s]?\d{3,4})', text)
        phone = phone_match.group(1) if phone_match else None
        
        # 尋找 Email
        email_match = re.search(r'([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+)', text)
        email = email_match.group(1) if email_match else None
        
        # 尋找官網（第一個非 104/1111/518 的連結）
        website = None
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'http' in href and not any(x in href for x in ['104.com', '1111.com.tw', '518.com.tw', 'google.com']):
                website = href
                break
        
        return {
            "phone": phone or "待查",
            "email": email or "待查", 
            "website": website or "待查"
        }
        
    except Exception as e:
        print(f"錯誤: {company_name} - {e}", file=sys.stderr)
        return {"phone": "待查", "email": "待查", "website": "待查"}

def main():
    # 從標準輸入讀取公司列表（JSON）
    companies = json.loads(sys.stdin.read())
    
    results = []
    
    for idx, company in enumerate(companies, 1):
        print(f"[{idx}/{len(companies)}] 搜尋: {company['name']}", file=sys.stderr)
        
        contact = search_google(company['name'])
        
        results.append({
            **company,
            **contact
        })
        
        print(f"  → Phone: {contact['phone']} | Email: {contact['email']}", file=sys.stderr)
        
        # 延遲避免被 Google 封鎖
        sleep(2)
    
    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
