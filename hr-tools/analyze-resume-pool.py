#!/usr/bin/env python3
import subprocess
import json
import re
from collections import Counter

# 使用 gog sheets 原始命令獲取數據（row by row）
def get_all_rows():
    cmd = ["gog", "sheets", "get", "--account", "aijessie88@step1ne.com", 
           "1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q", "A1:L300"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    lines = result.stdout.strip().split('\n')
    if len(lines) < 2:
        return []
    
    # 解析表格（固定寬度格式）
    rows = []
    for line in lines[1:]:  # 跳過標題
        # 簡化：按多個空格分割
        parts = re.split(r'\s{2,}', line.strip())
        if len(parts) >= 8 and parts[0]:  # 至少有姓名
            rows.append(parts)
    
    return rows

print("正在分析履歷池...")
rows = get_all_rows()
print(f"總筆數: {len(rows)}\n")

# 分析問題
issues = []
names = []

for idx, row in enumerate(rows, start=2):
    name = row[0] if len(row) > 0 else ''
    skills = row[3] if len(row) > 3 else ''
    exp = row[5] if len(row) > 5 else ''
    source = row[6] if len(row) > 6 else ''
    
    names.append(name)
    
    # 記錄問題行
    row_issues = []
    if not skills or len(skills) < 3:
        row_issues.append('空技能')
    if exp == '0':
        row_issues.append('經驗=0')
    if not source:
        row_issues.append('無來源')
    
    if row_issues:
        issues.append(f"第 {idx} 行 ({name}): {', '.join(row_issues)}")

# 統計
print(f"發現 {len(issues)} 行有問題（前 20 行）:")
for issue in issues[:20]:
    print(f"  {issue}")

# 重複檢查
name_counts = Counter(names)
duplicates = {k: v for k, v in name_counts.items() if v > 1 and k}
if duplicates:
    print(f"\n重複姓名 ({len(duplicates)} 組):")
    for name, count in sorted(duplicates.items(), key=lambda x: -x[1])[:10]:
        print(f"  {name}: {count} 次")
else:
    print("\n✅ 無重複姓名")

# 來源分佈
sources = Counter(row[6] if len(row) > 6 else '(空)' for row in rows)
print(f"\n來源分佈:")
for src, count in sources.most_common(10):
    print(f"  {src}: {count}")
