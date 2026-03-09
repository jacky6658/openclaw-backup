#!/bin/bash
# 自動找人選 v2.0 - 多管道整合版本
# 包含：LinkedIn + GitHub + CakeResume + 聯絡資料搜尋 + 公司官網爬蟲

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLS_DIR="$SCRIPT_DIR/../tools"

JD_SHEET="1QPaeOm-slNVFCeM8Q3gg3DawKjzp2tYwyfquvdHlZFE"
RESUME_POOL="1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q"
ACCOUNT="aiagentg888@gmail.com"

echo "🚀 自動找人選 v2.0 - 多管道整合版"
echo "================================"
echo ""

# Step 1: 讀取職缺列表
echo "📋 Step 1: 讀取職缺列表"
gog sheets get "$JD_SHEET" "工作表1!A2:F100" \
  --account "$ACCOUNT" \
  --json > /tmp/jd-list.json

TOTAL_JDS=$(jq '.values | length' /tmp/jd-list.json)
echo "   找到 $TOTAL_JDS 個職缺"
echo ""

# Step 2: 逐個職缺執行多管道搜尋
echo "🔍 Step 2: 多管道搜尋"

python3 << 'PYTHON_EOF'
import json
import subprocess
import sys

with open('/tmp/jd-list.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

all_candidates = []

for row in data.get('values', [])[:5]:  # 先處理前 5 個職缺測試
    if len(row) < 2:
        continue
    
    position = row[0]
    company = row[1]
    skills = row[5] if len(row) > 5 else ""
    
    print(f"\n📊 處理職缺：{position}", file=sys.stderr)
    
    # 呼叫多管道搜尋
    cmd = [
        'python3',
        '/Users/user/clawd/hr-tools/active/automation/multi-channel-sourcing.py',
        position,
        skills,
        '20'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        search_result = json.loads(result.stdout)
        all_candidates.append(search_result)
    else:
        print(f"❌ 搜尋失敗：{result.stderr}", file=sys.stderr)

print(f"\n✅ 多管道搜尋完成", file=sys.stderr)
print(f"   職缺：{len(all_candidates)} 個", file=sys.stderr)

# 儲存結果
with open('/tmp/multi-channel-results.json', 'w', encoding='utf-8') as f:
    json.dump(all_candidates, f, ensure_ascii=False, indent=2)
PYTHON_EOF

echo ""

# Step 3: 聯絡資料搜尋
echo "📞 Step 3: 聯絡資料搜尋"

if [ -f /tmp/multi-channel-results.json ]; then
    python3 "$SCRIPT_DIR/contact-finder.py" /tmp/multi-channel-results.json > /tmp/contacts-found.json
    
    CONTACTS_FOUND=$(jq '[.[] | select(.contact_found == true)] | length' /tmp/contacts-found.json)
    echo "   ✅ 找到聯絡資料：$CONTACTS_FOUND 位"
else
    echo "   ⚠️  跳過（無搜尋結果）"
fi

echo ""

# Step 4: 匯入履歷池
echo "📥 Step 4: 匯入履歷池"

python3 << 'PYTHON_EOF'
import json
import subprocess
from datetime import datetime

# 讀取搜尋結果
with open('/tmp/multi-channel-results.json', 'r', encoding='utf-8') as f:
    search_results = json.load(f)

# 讀取聯絡資料
contacts = {}
try:
    with open('/tmp/contacts-found.json', 'r', encoding='utf-8') as f:
        contact_results = json.load(f)
        for contact in contact_results:
            name = contact['candidate']['name']
            contacts[name] = contact
except:
    pass

# 轉換為履歷池格式
rows = []
for job_result in search_results:
    position = job_result['position']
    
    for channel_result in job_result['search_results']:
        for candidate in channel_result.get('candidates', []):
            name = candidate.get('name', '')
            linkedin = candidate.get('url', '')
            
            # 取得聯絡資料
            contact_info = contacts.get(name, {})
            email = contact_info.get('emails', [''])[0] if contact_info.get('emails') else ""
            phone = contact_info.get('phones', [''])[0] if contact_info.get('phones') else ""
            
            # 組合聯絡方式
            contact_str = linkedin
            if email:
                contact_str = f"{email} | {linkedin}"
            elif phone:
                contact_str = f"{phone} | {linkedin}"
            
            row = [
                name,                                    # A: 姓名
                contact_str,                             # B: 聯絡方式
                position,                                # C: 應徵職位
                candidate.get('title', ''),              # D: 主要技能
                "",                                      # E: 工作經驗(年)
                "",                                      # F: 學歷
                linkedin,                                # G: 履歷檔案連結
                "待聯繫",                                 # H: 狀態
                "Jacky",                                 # I: 獵頭顧問
                f"多管道搜尋 | {channel_result['channel']}", # J: 備註
                datetime.now().strftime("%Y-%m-%d"),     # K: 新增日期
                datetime.now().strftime("%Y-%m-%d")      # L: 最後更新
            ]
            
            rows.append(row)

if rows:
    # 匯入
    cmd = [
        'gog', 'sheets', 'append',
        '1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q',
        '工作表1!A:L',
        '--account', 'aiagentg888@gmail.com',
        '--values-json', json.dumps(rows, ensure_ascii=False),
        '--insert', 'INSERT_ROWS'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ 成功匯入 {len(rows)} 位候選人")
    else:
        print(f"❌ 匯入失敗：{result.stderr}")
else:
    print("⚠️  沒有候選人可匯入")
PYTHON_EOF

echo ""
echo "🎉 自動找人選 v2.0 完成！"
echo ""
echo "📊 執行摘要："
echo "   職缺處理：$(jq 'length' /tmp/multi-channel-results.json) 個"
echo "   候選人：$(jq '[.[] | .search_results[].candidates] | flatten | length' /tmp/multi-channel-results.json 2>/dev/null || echo 0) 位"
echo "   聯絡資料：$(jq '[.[] | select(.contact_found == true)] | length' /tmp/contacts-found.json 2>/dev/null || echo 0) 位"
echo ""
echo "📄 履歷池："
echo "   https://docs.google.com/spreadsheets/d/1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q"
