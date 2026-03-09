#!/bin/bash
# 填補 BD客戶開發表中缺少的聯絡資訊

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHEET_ID="1bkI7_cCh_Bs4qVa3HlXiy0CFzmItZlA-DYGHSPS4InE"
GOG_ACCOUNT="aiagentg888@gmail.com"

# 顏色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}📋 讀取 BD客戶開發表...${NC}"

# 讀取整個表格（JSON 格式）
gog sheets get "$SHEET_ID" '工作表1!A:E' --json --account "$GOG_ACCOUNT" > /tmp/bd-raw.json

# 提取需要處理的公司（聯絡電話=待查 且 有104公司URL）
echo -e "${BLUE}🔍 找出需要補充聯絡資訊的公司...${NC}"

cat > /tmp/process-bd-companies.py << 'EOF'
#!/usr/bin/env python3
import sys
import json

# 讀取 JSON
with open('/tmp/bd-raw.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

companies = []

# data 格式：{"range": ..., "values": [[row1], [row2], ...]}
rows = data.get('values', [])

for i, row in enumerate(rows[1:], 2):  # 跳過標題行，從第2行開始
    if len(row) >= 5:
        company_name = row[0].strip() if row[0] else ""
        phone = row[1].strip() if len(row) > 1 and row[1] else ""
        email = row[2].strip() if len(row) > 2 and row[2] else ""
        website = row[3].strip() if len(row) > 3 and row[3] else ""
        company_url = row[4].strip() if len(row) > 4 and row[4] else ""
        
        # 只處理：有公司URL 且 (電話=待查 或 email=待查)
        if company_url and company_url.startswith('https://www.104.com.tw/company/'):
            if phone == "待查" or email == "待查" or not phone or not email:
                companies.append({
                    "row": i,
                    "company": company_name,
                    "company_url": company_url,
                    "current_phone": phone,
                    "current_email": email,
                    "current_website": website
                })

print(json.dumps(companies, ensure_ascii=False, indent=2))
EOF

python3 /tmp/process-bd-companies.py > /tmp/companies-to-process.json

count=$(cat /tmp/companies-to-process.json | jq '. | length')
echo -e "${GREEN}✅ 找到 ${count} 家公司需要補充聯絡資訊${NC}"

if [[ $count -eq 0 ]]; then
    echo "沒有需要處理的公司"
    exit 0
fi

# 顯示要處理的公司
echo -e "${YELLOW}要處理的公司（共 ${count} 家）：${NC}"
cat /tmp/companies-to-process.json | jq -r '.[] | "  - \(.company) (Row \(.row))"'
echo ""

# 建立爬蟲腳本
cat > /tmp/scrape-bd-contacts.py << 'EOFPY'
#!/usr/bin/env python3
import subprocess
import re
import json
import sys
import time
import random
from datetime import datetime

# 請求頻率限制：每小時 ≤30 次 = 每次間隔 ≥120 秒
REQUEST_INTERVAL = 120  # 秒

def log_debug(message):
    with open("/tmp/bd-contact-fill-debug.log", 'a', encoding='utf-8') as log:
        log.write(f"[{datetime.now()}] {message}\n")

def extract_company_contact(company_url):
    """從公司頁面提取聯絡資訊"""
    log_debug(f"📞 訪問: {company_url}")
    
    subprocess.run(['agent-browser', 'navigate', company_url], check=True, capture_output=True)
    subprocess.run(['agent-browser', 'wait', '--load', 'networkidle', '--timeout', '10000'], check=True, capture_output=True)
    
    # 隨機延遲 2-5 秒（防反爬蟲）
    delay = random.uniform(2, 5)
    log_debug(f"  ⏳ 延遲 {delay:.1f} 秒")
    time.sleep(delay)
    
    result = subprocess.run(['agent-browser', 'snapshot'], capture_output=True, text=True)
    lines = result.stdout.split('\n')
    
    contact_info = {
        "contact_person": None,
        "phone": None,
        "fax": None,
        "email": None,
        "address": None,
        "website": None
    }
    
    for i, line in enumerate(lines):
        # 聯絡人
        if 'heading "聯絡人"' in line and i+1 < len(lines):
            next_line = lines[i+1].strip()
            if '- paragraph:' in next_line:
                name = next_line.replace('- paragraph:', '').strip()
                if name and name != "暫不提供":
                    contact_info['contact_person'] = name
        
        # 電話
        if 'heading "電話"' in line and i+1 < len(lines):
            next_line = lines[i+1].strip()
            if '- paragraph:' in next_line:
                phone = next_line.replace('- paragraph:', '').strip()
                if phone and phone != "暫不提供":
                    contact_info['phone'] = phone
        
        # 傳真
        if 'heading "傳真"' in line and i+1 < len(lines):
            next_line = lines[i+1].strip()
            if '- paragraph:' in next_line:
                fax = next_line.replace('- paragraph:', '').strip()
                if fax and fax != "暫不提供":
                    contact_info['fax'] = fax
        
        # 地址
        if 'heading "地址"' in line and i+1 < len(lines):
            next_line = lines[i+1].strip()
            if '- paragraph:' in next_line:
                addr = next_line.replace('- paragraph:', '').strip()
                if addr and addr != "暫不提供":
                    contact_info['address'] = addr
        
        # 公司網址
        if 'heading "公司網址"' in line and i+2 < len(lines):
            url_line = lines[i+2].strip()
            if '- /url:' in url_line:
                url_match = re.search(r'- /url:\s*(https?://[^\s]+)', url_line)
                if url_match:
                    contact_info['website'] = url_match.group(1).strip()
        
        # Email
        if '@' in line:
            email_match = re.search(r'([\w\.-]+@[\w\.-]+\.\w+)', line)
            if email_match:
                contact_info['email'] = email_match.group(1).strip()
    
    log_debug(f"  電話: {contact_info['phone']}, Email: {contact_info['email']}")
    return contact_info

def search_email_from_website(website_url):
    """從公司官網搜尋 Email"""
    if not website_url or not website_url.startswith('http'):
        return None
    
    log_debug(f"🌐 搜尋官網 Email: {website_url}")
    
    contact_pages = [
        website_url,
        f"{website_url.rstrip('/')}/contact",
        f"{website_url.rstrip('/')}/contact-us",
        f"{website_url.rstrip('/')}/about"
    ]
    
    for url in contact_pages:
        try:
            subprocess.run(['agent-browser', 'navigate', url], check=True, capture_output=True, timeout=10)
            subprocess.run(['agent-browser', 'wait', '--load', 'networkidle', '--timeout', '5000'], check=True, capture_output=True, timeout=10)
            
            # 隨機延遲 2-5 秒（防反爬蟲）
            delay = random.uniform(2, 5)
            time.sleep(delay)
            
            result = subprocess.run(['agent-browser', 'snapshot'], capture_output=True, text=True, timeout=5)
            
            email_match = re.search(r'([\w\.-]+@[\w\.-]+\.\w+)', result.stdout)
            if email_match:
                email = email_match.group(1)
                log_debug(f"  ✅ 找到 Email: {email}")
                return email
        except:
            continue
    
    return None

# 讀取公司列表
with open('/tmp/companies-to-process.json', 'r', encoding='utf-8') as f:
    companies = json.load(f)

# 開啟瀏覽器
subprocess.run(['agent-browser', 'open', 'https://www.104.com.tw'], check=True, capture_output=True)
subprocess.run(['agent-browser', 'wait', '--load', 'networkidle', '--timeout', '10000'], check=True, capture_output=True)

log_debug(f"開始處理 {len(companies)} 家公司")

results = []
processed_count = 0

for company_data in companies:
    company_name = company_data['company']
    company_url = company_data['company_url']
    row = company_data['row']
    
    log_debug(f"\n{'='*60}")
    log_debug(f"🏢 處理: {company_name} (Row {row})")
    
    try:
        # 從公司頁面提取聯絡資訊
        contact_info = extract_company_contact(company_url)
        
        # 如果沒有 Email，嘗試從官網找
        if not contact_info['email'] and contact_info['website']:
            contact_info['email'] = search_email_from_website(contact_info['website'])
        
        results.append({
            "row": row,
            "company": company_name,
            "phone": contact_info['phone'] or company_data['current_phone'],
            "email": contact_info['email'] or company_data['current_email'],
            "website": contact_info['website'] or company_data['current_website'],
            "fax": contact_info['fax'] or "",
            "address": contact_info['address'] or "",
            "contact_person": contact_info['contact_person'] or ""
        })
        
        log_debug(f"✅ 完成: {company_name}")
        
        processed_count += 1
        
        # 每處理一家公司，等待 120 秒（每小時 ≤30 次）
        if processed_count < len(companies):
            log_debug(f"⏸️  等待 {REQUEST_INTERVAL} 秒（防反爬蟲，每小時 ≤30 次）...")
            time.sleep(REQUEST_INTERVAL)
        
    except Exception as e:
        log_debug(f"❌ 失敗: {company_name} - {e}")
        results.append({
            "row": row,
            "company": company_name,
            "phone": company_data['current_phone'],
            "email": company_data['current_email'],
            "website": company_data['current_website']
        })

# 關閉瀏覽器
subprocess.run(['agent-browser', 'close'], check=True, capture_output=True)

# 輸出結果
print(json.dumps(results, ensure_ascii=False, indent=2))

log_debug(f"✅ 全部完成，共處理 {len(results)} 家公司")
EOFPY

echo -e "${BLUE}🕷️  開始爬取聯絡資訊...${NC}"
python3 /tmp/scrape-bd-contacts.py > /tmp/bd-contacts-result.json

# 更新 Google Sheets
echo -e "${BLUE}📝 更新 Google Sheets...${NC}"

cat > /tmp/update-sheets.py << 'EOFUPDATE'
#!/usr/bin/env python3
import json
import subprocess

with open('/tmp/bd-contacts-result.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

updated = 0
for item in results:
    row = item['row']
    phone = item.get('phone', '待查')
    email = item.get('email', '待查')
    website = item.get('website', '')
    
    # 只更新有新資訊的欄位
    if phone and phone != "待查":
        # 更新 B 欄（聯絡電話）
        range_phone = f"工作表1!B{row}"
        subprocess.run(['gog', 'sheets', 'update', '1bkI7_cCh_Bs4qVa3HlXiy0CFzmItZlA-DYGHSPS4InE', range_phone, phone, '--account', 'aiagentg888@gmail.com'], check=True, capture_output=True)
        updated += 1
    
    if email and email != "待查":
        # 更新 C 欄（Email）
        range_email = f"工作表1!C{row}"
        subprocess.run(['gog', 'sheets', 'update', '1bkI7_cCh_Bs4qVa3HlXiy0CFzmItZlA-DYGHSPS4InE', range_email, email, '--account', 'aiagentg888@gmail.com'], check=True, capture_output=True)
        updated += 1
    
    if website and website != "" and website != "找不到":
        # 更新 D 欄（公司官網）
        range_website = f"工作表1!D{row}"
        subprocess.run(['gog', 'sheets', 'update', '1bkI7_cCh_Bs4qVa3HlXiy0CFzmItZlA-DYGHSPS4InE', range_website, website, '--account', 'aiagentg888@gmail.com'], check=True, capture_output=True)
        updated += 1

print(f"Updated {updated} cells")
EOFUPDATE

python3 /tmp/update-sheets.py

echo -e "${GREEN}✅ 完成！${NC}"
echo -e "${GREEN}查看更新：https://docs.google.com/spreadsheets/d/$SHEET_ID${NC}"
