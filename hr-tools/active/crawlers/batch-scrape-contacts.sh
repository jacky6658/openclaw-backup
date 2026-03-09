#!/bin/bash
# 批量抓取 BD 公司聯絡資訊
# 策略：104 站內搜尋 → 公司頁面 → 提取電話+Email

SHEET_ID="1bkI7_cCh_Bs4qVa3HlXiy0CFzmItZlA-DYGHSPS4InE"
ACCOUNT="aijessie88@step1ne.com"

echo "📊 讀取缺資料的公司清單..."

# 使用昨天生成的 missing-contacts.json
if [ ! -f /tmp/missing-contacts.json ]; then
  echo "❌ 找不到 /tmp/missing-contacts.json"
  echo "請先執行統計腳本生成清單"
  exit 1
fi

# 讀取前 N 家公司（參數指定，預設 10）
BATCH_SIZE=${1:-10}

echo "處理前 $BATCH_SIZE 家公司..."
echo ""

python3 << 'PYEOF'
import json
import subprocess
import re
import time
import random
import sys
import urllib.parse

# 讀取清單
with open('/tmp/missing-contacts.json', 'r', encoding='utf-8') as f:
    companies = json.load(f)

# 限制數量
batch_size = int(sys.argv[1]) if len(sys.argv) > 1 else 10
companies = companies[:batch_size]

print(f"開始處理 {len(companies)} 家公司\n")

success = 0
failed = 0
updates = []

for i, company_data in enumerate(companies, 1):
    row = company_data['row']
    name = company_data['company']
    
    print(f"[{i}/{len(companies)}] 🏢 {name} (Row {row})")
    
    try:
        # 1. 104 站內搜尋
        encoded_name = urllib.parse.quote(name)
        search_url = f"https://www.104.com.tw/company/search/?keyword={encoded_name}"
        
        subprocess.run(['agent-browser', 'open', search_url], timeout=15, capture_output=True)
        time.sleep(random.uniform(3, 5))
        
        result = subprocess.run(['agent-browser', 'snapshot'], capture_output=True, text=True, timeout=10)
        
        # 找公司頁面
        match = re.search(r'/url: https://www\.104\.com\.tw/company/([a-z0-9]+)', result.stdout)
        
        if not match:
            print(f"  ❌ 未找到公司頁面")
            failed += 1
            continue
        
        company_id = match.group(1)
        company_url = f"https://www.104.com.tw/company/{company_id}"
        print(f"  ✅ 找到: {company_url}")
        
        # 2. 訪問公司頁面
        subprocess.run(['agent-browser', 'open', company_url], timeout=15, capture_output=True)
        time.sleep(random.uniform(3, 5))
        
        result = subprocess.run(['agent-browser', 'snapshot'], capture_output=True, text=True, timeout=10)
        lines = result.stdout.split('\n')
        
        # 3. 提取聯絡資訊
        phone = None
        email = None
        
        for j, line in enumerate(lines):
            if 'heading "電話"' in line and j+1 < len(lines):
                match_phone = re.search(r'paragraph: (.+)', lines[j+1])
                if match_phone:
                    phone = match_phone.group(1).strip()
            elif ('heading "Email"' in line or 'heading "E-mail"' in line) and j+1 < len(lines):
                match_email = re.search(r'paragraph: (.+)', lines[j+1])
                if match_email:
                    email = match_email.group(1).strip()
        
        # 4. 記錄結果
        phone_val = phone if phone else company_data.get('phone') or '待查'
        email_val = email if email else company_data.get('email') or '待查'
        
        print(f"  📞 電話: {phone_val}")
        print(f"  📧 Email: {email_val}")
        
        # 準備更新
        if phone or email:
            updates.append({
                'row': row,
                'phone': phone_val,
                'email': email_val
            })
            success += 1
        else:
            failed += 1
        
        # 延遲（防反爬）
        delay = random.randint(8, 15)
        print(f"  ⏳ 延遲 {delay} 秒...\n")
        time.sleep(delay)
        
    except Exception as e:
        print(f"  ❌ 錯誤: {str(e)[:50]}\n")
        failed += 1

# 5. 批量更新到 Google Sheets
print("\n" + "="*70)
print(f"📊 處理完成: 成功 {success} / 失敗 {failed}")
print("="*70)

if updates:
    print(f"\n更新 {len(updates)} 筆資料到 Google Sheets...")
    for update in updates:
        range_spec = f"工作表1!B{update['row']}:C{update['row']}"
        value = f"{update['phone']}|{update['email']}"
        
        subprocess.run([
            'gog', 'sheets', 'update',
            '1bkI7_cCh_Bs4qVa3HlXiy0CFkmItZlA-DYGHSPS4InE',
            range_spec,
            value,
            '--account', 'aijessie88@step1ne.com'
        ], capture_output=True)
        
        print(f"  ✅ Row {update['row']}: {update['phone'][:20]}...")
    
    print("\n✅ 全部更新完成！")

PYEOF $BATCH_SIZE
