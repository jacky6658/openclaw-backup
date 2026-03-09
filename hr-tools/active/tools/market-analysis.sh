#!/bin/bash
# 104市場職缺調查 - 找出熱門職位

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}📊 開始市場職缺調查...${NC}"

cat > /tmp/market-research.py << 'EOF'
#!/usr/bin/env python3
"""
104 市場職缺調查
分析當前熱門職位、職缺數量、薪資範圍
"""

import subprocess
import re
import json
from datetime import datetime

def log_debug(message):
    with open("/tmp/market-research-debug.log", 'a', encoding='utf-8') as log:
        log.write(f"[{datetime.now()}] {message}\n")

def search_job_count(keyword):
    """搜尋特定職位的職缺數量"""
    log_debug(f"🔍 搜尋: {keyword}")
    
    url = f"https://www.104.com.tw/jobs/search/?keyword={keyword}"
    
    subprocess.run(['agent-browser', 'navigate', url], check=True, capture_output=True)
    subprocess.run(['agent-browser', 'wait', '--load', 'networkidle', '--timeout', '10000'], check=True, capture_output=True)
    
    import time
    time.sleep(2)
    
    result = subprocess.run(['agent-browser', 'snapshot'], capture_output=True, text=True)
    
    # 找「共 XXX 筆」
    count = 0
    for line in result.stdout.split('\n'):
        match = re.search(r'共\s*(\d+[\+,]?)\s*筆', line)
        if match:
            count_str = match.group(1).replace(',', '').replace('+', '')
            try:
                count = int(count_str) if count_str.isdigit() else 1000
            except:
                count = 1000
            break
    
    log_debug(f"  ✅ {keyword}: {count} 個職缺")
    return count

# 開啟瀏覽器
subprocess.run(['agent-browser', 'open', 'https://www.104.com.tw'], check=True, capture_output=True)
subprocess.run(['agent-browser', 'wait', '--load', 'networkidle', '--timeout', '10000'], check=True, capture_output=True)

log_debug("開始職缺調查")

# 熱門職位列表
job_categories = [
    # 工程類
    "AI工程師",
    "後端工程師",
    "前端工程師",
    "全端工程師",
    "數據分析師",
    "資料工程師",
    "產品經理",
    "軟體工程師",
    "DevOps工程師",
    "測試工程師",
    # 設計類
    "UI/UX設計師",
    "平面設計師",
    # 行銷類
    "數位行銷",
    "社群行銷",
    "內容行銷",
    # 業務類
    "業務",
    "客服",
    # 人資類
    "HR",
    "招募專員"
]

results = []

for job in job_categories:
    try:
        count = search_job_count(job)
        results.append({
            "job": job,
            "count": count
        })
    except Exception as e:
        log_debug(f"❌ 搜尋失敗: {job} - {e}")
        results.append({
            "job": job,
            "count": 0
        })

# 關閉瀏覽器
subprocess.run(['agent-browser', 'close'], check=True, capture_output=True)

# 排序（職缺數量由高到低）
results_sorted = sorted(results, key=lambda x: x['count'], reverse=True)

print(json.dumps(results_sorted, ensure_ascii=False, indent=2))

log_debug(f"✅ 調查完成，共 {len(results)} 個職位")
EOF

echo -e "${BLUE}🕷️  爬取職缺數量資料...${NC}"
python3 /tmp/market-research.py > /tmp/market-research-result.json

echo -e "${GREEN}✅ 調查完成！${NC}"
echo ""
echo -e "${YELLOW}====== 市場職缺分析報告 ======${NC}"
echo ""

cat > /tmp/format-report.py << 'EOFFORMAT'
#!/usr/bin/env python3
import json

with open('/tmp/market-research-result.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("📊 104 職缺數量排名（前 10 名）")
print("-" * 50)
for i, item in enumerate(data[:10], 1):
    job = item['job']
    count = item['count']
    if count >= 1000:
        count_str = f"{count:,}+"
    else:
        count_str = f"{count:,}"
    print(f"{i:2d}. {job:20s} {count_str:>10s} 個職缺")

print("\n" + "=" * 50)
print("\n📈 分類統計：")

# 工程類
eng_jobs = ["AI工程師", "後端工程師", "前端工程師", "全端工程師", "數據分析師", 
            "資料工程師", "軟體工程師", "DevOps工程師", "測試工程師"]
eng_total = sum(item['count'] for item in data if item['job'] in eng_jobs)
print(f"  工程類總計：{eng_total:,}+ 個職缺")

# 設計類
design_jobs = ["UI/UX設計師", "平面設計師"]
design_total = sum(item['count'] for item in data if item['job'] in design_jobs)
print(f"  設計類總計：{design_total:,}+ 個職缺")

# 行銷類
marketing_jobs = ["數位行銷", "社群行銷", "內容行銷"]
marketing_total = sum(item['count'] for item in data if item['job'] in marketing_jobs)
print(f"  行銷類總計：{marketing_total:,}+ 個職缺")

print("\n💡 建議：")
print("  前 3 名職位是 BD 主要目標，職缺數量最多代表市場需求最大。")
EOFFORMAT

python3 /tmp/format-report.py

# 儲存報告
cat /tmp/market-research-result.json > /tmp/market-report-$(date +%Y%m%d).json

echo ""
echo -e "${GREEN}報告已儲存: /tmp/market-report-$(date +%Y%m%d).json${NC}"
