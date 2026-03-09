#!/bin/bash
set -e

SHEET_ID="1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q"
ACCOUNT="aijessie88@step1ne.com"

echo "步驟 1: 清空履歷池（保留標題）..."
gog sheets clear --account "$ACCOUNT" "$SHEET_ID" "A2:L2000"
echo "  ✓ 清空完成"

echo ""
echo "步驟 2: 解析備份資料..."
python3 << 'PYTHON'
import re

with open('data/resume-pool-backup-20260221-1518.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

rows = []
for i, line in enumerate(lines[1:], start=2):  # 跳過標題
    parts = re.split(r'\s{2,}', line.strip())
    if len(parts) >= 8 and parts[0]:
        # 補齊到 12 欄
        while len(parts) < 12:
            parts.append('')
        rows.append(parts[:12])

print(f"  ✓ 解析 {len(rows)} 筆資料")

# 輸出為 TSV（給 gog sheets 用）
with open('/tmp/resume-pool-import.tsv', 'w', encoding='utf-8') as f:
    for row in rows:
        # 用 | 分隔每個欄位，用 , 分隔每一行
        f.write('|'.join(row) + '\n')

print(f"  ✓ 匯出到 /tmp/resume-pool-import.tsv")
PYTHON

echo ""
echo "步驟 3: 分批匯入（每 50 筆）..."
total_lines=$(wc -l < /tmp/resume-pool-import.tsv | xargs)
batch=0
current=0

while IFS= read -r line; do
    batch_rows+=("$line")
    ((current++))
    
    # 每 50 筆或最後一批
    if [ ${#batch_rows[@]} -eq 50 ] || [ $current -eq $total_lines ]; then
        ((batch++))
        
        # 合併成逗號分隔
        data=$(printf "%s," "${batch_rows[@]}")
        data="${data%,}"  # 移除最後的逗號
        
        gog sheets append --account "$ACCOUNT" "$SHEET_ID" "A:L" "$data"
        
        echo "  ✓ 第 $batch 批：已匯入 ${#batch_rows[@]} 筆"
        batch_rows=()
    fi
done < /tmp/resume-pool-import.tsv

echo ""
echo "=========================================="
echo "✅ 完成！已匯入 $total_lines 筆乾淨資料"
echo "=========================================="
