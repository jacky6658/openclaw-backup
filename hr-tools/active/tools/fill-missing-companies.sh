#!/bin/bash
# 處理 BD客戶開發表中沒有 104 URL 的公司

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHEET_ID="1bkI7_cCh_Bs4qVa3HlXiy0CFzmItZlA-DYGHSPS4InE"
GOG_ACCOUNT="aiagentg888@gmail.com"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}📋 讀取 BD客戶開發表...${NC}"
gog sheets get "$SHEET_ID" '工作表1!A:E' --json --account "$GOG_ACCOUNT" > /tmp/bd-missing-raw.json

echo -e "${BLUE}🔍 找出沒有 104 URL 的公司...${NC}"

cat > /tmp/find-missing-companies.py << 'EOF'
#!/usr/bin/env python3
import json

with open('/tmp/bd-missing-raw.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

companies = []
rows = data.get('values', [])

for i, row in enumerate(rows[1:], 2):
    if len(row) >= 1:
        company_name = row[0].strip() if row[0] else ""
        company_url = row[4].strip() if len(row) > 4 and row[4] else ""
        
        # 只處理：有公司名稱 且 (沒有URL 或 URL="待查" 或 URL 是錯誤的搜尋頁面)
        if company_name and (not company_url or company_url == "待查" or "company/search" in company_url):
            companies.append({
                "row": i,
                "company": company_name
            })

print(json.dumps(companies, ensure_ascii=False, indent=2))
EOF

python3 /tmp/find-missing-companies.py > /tmp/missing-companies.json

count=$(cat /tmp/missing-companies.json | jq '. | length')
echo -e "${GREEN}✅ 找到 ${count} 家沒有 104 URL 的公司${NC}"

if [[ $count -eq 0 ]]; then
    echo "沒有需要處理的公司"
    exit 0
fi

echo -e "${YELLOW}要處理的公司：${NC}"
cat /tmp/missing-companies.json | jq -r '.[] | "  Row \(.row): \(.company)"'
echo ""

# 建立爬蟲腳本
cat > /tmp/search-and-fill-companies.py << 'EOFPY'
#!/usr/bin/env python3
import subprocess
import re
import json
from datetime import datetime

def log_debug(message):
    with open("/tmp/missing-companies-debug.log", 'a', encoding='utf-8') as log:
        log.write(f"[{datetime.now()}] {message}\n")

def search_104_company(company_name):
    """在 104 搜尋公司名稱，找到公司頁面 URL"""
    log_debug(f"🔍 搜尋公司: {company_name}")
    
    # 使用 104 公司搜尋
    search_url = f"https://www.104.com.tw/company/search/?keyword={company_name}"
    
    subprocess.run(['agent-browser', 'navigate', search_url], check=True, capture_output=True)
    subprocess.run(['agent-browser', 'wait', '--load', 'networkidle', '--timeout', '10000'], check=True, capture_output=True)
    
    import time
    time.sleep(2)
    
    # 取得 snapshot
    result = subprocess.run(['agent-browser', 'snapshot'], capture_output=True, text=True)
    
    # 找第一個真正的公司連結（不是搜尋頁面）
    for line in result.stdout.split('\n'):
        if '/url:' in line and '/company/' in line:
            match = re.search(r'/url:\s*((?:https?:)?//www\.104\.com\.tw/company/([a-z0-9]+))', line)
            if match:
                company_id = match.group(2)
                # 排除 search, main 等非公司ID的頁面
                if company_id not in ['search', 'main', 'list']:
                    url = match.group(1)
                    if url.startswith('//'):
                        url = f"https:{url}"
                    log_debug(f"  ✅ 找到公司頁面: {url}")
                    return url
    
    log_debug(f"  ❌ 未找到公司頁面")
    return None

def extract_company_contact(company_url):
    """從公司頁面提取聯絡資訊"""
    log_debug(f"📞 訪問: {company_url}")
    
    subprocess.run(['agent-browser', 'navigate', company_url], check=True, capture_output=True)
    subprocess.run(['agent-browser', 'wait', '--load', 'networkidle', '--timeout', '10000'], check=True, capture_output=True)
    
    import time
    time.sleep(2)
    
    result = subprocess.run(['agent-browser', 'snapshot'], capture_output=True, text=True)
    lines = result.stdout.split('\n')
    
    contact_info = {
        "contact_person": None,
        "phone": None,
        "email": None,
        "website": None
    }
    
    for i, line in enumerate(lines):
        if 'heading "聯絡人"' in line and i+1 < len(lines):
            next_line = lines[i+1].strip()
            if '- paragraph:' in next_line:
                name = next_line.replace('- paragraph:', '').strip()
                if name and name != "暫不提供":
                    contact_info['contact_person'] = name
        
        if 'heading "電話"' in line and i+1 < len(lines):
            next_line = lines[i+1].strip()
            if '- paragraph:' in next_line:
                phone = next_line.replace('- paragraph:', '').strip()
                if phone and phone != "暫不提供":
                    contact_info['phone'] = phone
        
        if 'heading "公司網址"' in line and i+2 < len(lines):
            url_line = lines[i+2].strip()
            if '- /url:' in url_line:
                url_match = re.search(r'- /url:\s*(https?://[^\s]+)', url_line)
                if url_match:
                    contact_info['website'] = url_match.group(1).strip()
        
        if '@' in line:
            email_match = re.search(r'([\w\.-]+@[\w\.-]+\.\w+)', line)
            if email_match:
                contact_info['email'] = email_match.group(1).strip()
    
    log_debug(f"  電話: {contact_info['phone']}, Email: {contact_info['email']}")
    return contact_info

# 讀取公司列表
with open('/tmp/missing-companies.json', 'r', encoding='utf-8') as f:
    companies = json.load(f)

# 開啟瀏覽器
subprocess.run(['agent-browser', 'open', 'https://www.104.com.tw'], check=True, capture_output=True)
subprocess.run(['agent-browser', 'wait', '--load', 'networkidle', '--timeout', '10000'], check=True, capture_output=True)

log_debug(f"開始處理 {len(companies)} 家公司")

results = []

for company_data in companies:
    company_name = company_data['company']
    row = company_data['row']
    
    log_debug(f"\n{'='*60}")
    log_debug(f"🏢 處理: {company_name} (Row {row})")
    
    try:
        # 步驟 1：搜尋公司找到 104 URL
        company_url = search_104_company(company_name)
        
        if not company_url:
            results.append({
                "row": row,
                "company": company_name,
                "company_url": "找不到",
                "phone": "待查",
                "email": "待查",
                "website": ""
            })
            log_debug(f"❌ 跳過: {company_name}（未找到公司頁面）")
            continue
        
        # 步驟 2：從公司頁面提取聯絡資訊
        contact_info = extract_company_contact(company_url)
        
        results.append({
            "row": row,
            "company": company_name,
            "company_url": company_url,
            "phone": contact_info['phone'] or "待查",
            "email": contact_info['email'] or "待查",
            "website": contact_info['website'] or "",
            "contact_person": contact_info['contact_person'] or ""
        })
        
        log_debug(f"✅ 完成: {company_name}")
        
    except Exception as e:
        log_debug(f"❌ 失敗: {company_name} - {e}")
        results.append({
            "row": row,
            "company": company_name,
            "company_url": "找不到",
            "phone": "待查",
            "email": "待查",
            "website": ""
        })

# 關閉瀏覽器
subprocess.run(['agent-browser', 'close'], check=True, capture_output=True)

print(json.dumps(results, ensure_ascii=False, indent=2))
log_debug(f"✅ 全部完成，共處理 {len(results)} 家公司")
EOFPY

echo -e "${BLUE}🕷️  開始搜尋並爬取聯絡資訊...${NC}"
python3 /tmp/search-and-fill-companies.py > /tmp/missing-companies-result.json

echo -e "${BLUE}📝 更新 Google Sheets...${NC}"

cat > /tmp/update-missing-sheets.py << 'EOFUPDATE'
#!/usr/bin/env python3
import json
import subprocess

with open('/tmp/missing-companies-result.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

updated = 0
for item in results:
    row = item['row']
    phone = item.get('phone', '待查')
    email = item.get('email', '待查')
    website = item.get('website', '')
    company_url = item.get('company_url', '找不到')
    
    # 更新 B 欄（電話）
    if phone and phone != "待查":
        range_phone = f"工作表1!B{row}"
        subprocess.run(['gog', 'sheets', 'update', '1bkI7_cCh_Bs4qVa3HlXiy0CFzmItZlA-DYGHSPS4InE', range_phone, phone, '--account', 'aiagentg888@gmail.com'], check=True, capture_output=True)
        updated += 1
    
    # 更新 C 欄（Email）
    if email and email != "待查":
        range_email = f"工作表1!C{row}"
        subprocess.run(['gog', 'sheets', 'update', '1bkI7_cCh_Bs4qVa3HlXiy0CFzmItZlA-DYGHSPS4InE', range_email, email, '--account', 'aiagentg888@gmail.com'], check=True, capture_output=True)
        updated += 1
    
    # 更新 D 欄（官網）
    if website and website != "":
        range_website = f"工作表1!D{row}"
        subprocess.run(['gog', 'sheets', 'update', '1bkI7_cCh_Bs4qVa3HlXiy0CFzmItZlA-DYGHSPS4InE', range_website, website, '--account', 'aiagentg888@gmail.com'], check=True, capture_output=True)
        updated += 1
    
    # 更新 E 欄（104 公司頁面）
    if company_url:
        range_company_url = f"工作表1!E{row}"
        subprocess.run(['gog', 'sheets', 'update', '1bkI7_cCh_Bs4qVa3HlXiy0CFzmItZlA-DYGHSPS4InE', range_company_url, company_url, '--account', 'aiagentg888@gmail.com'], check=True, capture_output=True)
        updated += 1

print(f"Updated {updated} cells")
EOFUPDATE

python3 /tmp/update-missing-sheets.py

echo -e "${GREEN}✅ 完成！${NC}"
echo -e "${GREEN}查看更新：https://docs.google.com/spreadsheets/d/1bkI7_cCh_Bs4qVa3HlXiy0CFzmItZlA-DYGHSPS4InE${NC}"
