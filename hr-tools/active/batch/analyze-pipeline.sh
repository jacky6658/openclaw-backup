#!/bin/bash
# Pipeline 數據分析腳本
# 讀取各顧問的 Pipeline Sheet 並統計數據

set -e

ACCOUNT="aiagentg888@gmail.com"

# 顏色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 讀取 pipeline-sheets.md 中的 Sheet ID
JACKY_SHEET="1j9zl3Fk-X1DS4iDAFQjAldaLWJDcqybAWIjiDpYCR4M"
PHOBE_SHEET="1Fh6S5tSpCIacuDrCHs3mewWWqAEhTAPaNXSuQHt6Phk"

echo -e "${BLUE}📊 分析 Pipeline 數據...${NC}"

# 建立分析腳本
cat > /tmp/analyze-pipeline.py << 'EOFPY'
#!/usr/bin/env python3
import json
import sys

def analyze_pipeline(sheet_data):
    """分析 Pipeline 數據"""
    values = sheet_data.get('values', [])
    
    # 處理空 Sheet
    if not values or values is None:
        return {
            "本週新增": 0,
            "舊有累計": 0,
            "stages": {
                "CV send": 0,
                "1st interview": 0,
                "final interview": 0,
                "reference check/offer": 0,
                "offer": 0
            }
        }
    
    stats = {
        "本週新增": 0,
        "舊有累計": 0,
        "stages": {
            "CV send": 0,
            "1st interview": 0,
            "final interview": 0,
            "reference check/offer": 0,
            "offer": 0
        }
    }
    
    current_section = None
    
    for i, row in enumerate(values):
        if not row:
            continue
        
        # 檢查是否為區塊標題
        first_cell = str(row[0]).strip()
        if "本周" in first_cell or "本週" in first_cell:
            current_section = "本週新增"
            continue
        elif "舊有" in first_cell:
            current_section = "舊有累計"
            continue
        
        # 跳過標題行
        if len(row) > 1 and "Open date" in str(row[1]):
            continue
        
        # 統計候選人
        if current_section and len(row) >= 5:
            # 檢查是否有 Candidate 名字（第5欄，index 4）
            if len(row) > 4 and row[4] and str(row[4]).strip():
                candidate = str(row[4]).strip()
                
                # 只統計有名字的候選人
                if candidate and candidate not in ["Candidate", ""]:
                    stats[current_section] += 1
                    
                    # 統計階段（F-J 欄，index 5-9）
                    for stage_idx, stage_name in enumerate([
                        "CV send",
                        "1st interview", 
                        "final interview",
                        "reference check/offer",
                        "offer"
                    ]):
                        col_idx = 5 + stage_idx
                        if len(row) > col_idx and row[col_idx]:
                            # 有填日期就算該階段
                            stage_value = str(row[col_idx]).strip()
                            if stage_value and stage_value != "":
                                stats["stages"][stage_name] += 1
    
    return stats

# 讀取 JSON
data = json.load(sys.stdin)
result = analyze_pipeline(data)
print(json.dumps(result, ensure_ascii=False, indent=2))
EOFPY

chmod +x /tmp/analyze-pipeline.py

# 分析 Jacky 的 Pipeline
echo -e "${YELLOW}📋 Jacky 的 Pipeline${NC}"
gog sheets get "$JACKY_SHEET" 'A1:J50' --json --account "$ACCOUNT" > /tmp/jacky-pipeline.json
JACKY_STATS=$(python3 /tmp/analyze-pipeline.py < /tmp/jacky-pipeline.json)
echo "$JACKY_STATS" | jq '.'

# 分析 Phobe 的 Pipeline（如果有數據）
echo -e "${YELLOW}📋 Phobe 的 Pipeline${NC}"
gog sheets get "$PHOBE_SHEET" 'A1:J50' --json --account "$ACCOUNT" > /tmp/phobe-pipeline.json
PHOBE_STATS=$(python3 /tmp/analyze-pipeline.py < /tmp/phobe-pipeline.json)
echo "$PHOBE_STATS" | jq '.'

# 彙總
echo -e "${GREEN}📊 總計${NC}"
cat > /tmp/summarize-pipeline.py << 'EOFSUM'
#!/usr/bin/env python3
import json
import sys

jacky = json.load(open('/tmp/jacky-pipeline.json'))
phobe = json.load(open('/tmp/phobe-pipeline.json'))

def analyze(data):
    values = data.get('values', [])
    
    # 處理空 Sheet
    if not values or values is None:
        return {
            "本週新增": 0,
            "舊有累計": 0,
            "stages": {
                "CV send": 0,
                "1st interview": 0,
                "final interview": 0,
                "reference check/offer": 0,
                "offer": 0
            }
        }
    
    stats = {
        "本週新增": 0,
        "舊有累計": 0,
        "stages": {
            "CV send": 0,
            "1st interview": 0,
            "final interview": 0,
            "reference check/offer": 0,
            "offer": 0
        }
    }
    
    current_section = None
    for row in values:
        if not row:
            continue
        first = str(row[0]).strip()
        if "本周" in first or "本週" in first:
            current_section = "本週新增"
        elif "舊有" in first:
            current_section = "舊有累計"
        elif "Open date" in str(row[1] if len(row) > 1 else ""):
            continue
        elif current_section and len(row) >= 5:
            if len(row) > 4 and row[4] and str(row[4]).strip():
                candidate = str(row[4]).strip()
                if candidate and candidate not in ["Candidate", ""]:
                    stats[current_section] += 1
                    for idx, stage in enumerate(["CV send", "1st interview", "final interview", "reference check/offer", "offer"]):
                        col = 5 + idx
                        if len(row) > col and row[col] and str(row[col]).strip():
                            stats["stages"][stage] += 1
    return stats

j_stats = analyze(jacky)
p_stats = analyze(phobe)

total = {
    "本週新增": j_stats["本週新增"] + p_stats["本週新增"],
    "舊有累計": j_stats["舊有累計"] + p_stats["舊有累計"],
    "stages": {
        k: j_stats["stages"][k] + p_stats["stages"][k]
        for k in j_stats["stages"]
    }
}

print(json.dumps(total, ensure_ascii=False, indent=2))
EOFSUM

python3 /tmp/summarize-pipeline.py

echo -e "${GREEN}✅ 分析完成${NC}"
