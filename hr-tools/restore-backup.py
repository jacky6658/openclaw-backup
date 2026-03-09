#!/usr/bin/env python3
import subprocess
import re

# 讀取備份
with open('data/resume-pool-backup-20260221-1518.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"備份總行數: {len(lines)}")

# 解析每一行
rows = []
for i, line in enumerate(lines):
    if i == 0:  # 標題行
        continue
    parts = re.split(r'\s{2,}', line.strip())
    if len(parts) >= 8 and parts[0]:
        rows.append('|'.join(parts[:12]))  # 只取前 12 欄

print(f"解析資料: {len(rows)} 筆")

# 先清空 Sheet（保留標題）
print("清空舊資料...")
subprocess.run([
    "gog", "sheets", "update", "--account", "aijessie88@step1ne.com",
    "1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q",
    "A2:L1000", ""
])

# 分批上傳（每 30 筆）
print("回復備份資料...")
batch_size = 30
for i in range(0, len(rows), batch_size):
    batch = rows[i:i+batch_size]
    data = ','.join(batch)
    
    subprocess.run([
        "gog", "sheets", "append", "--account", "aijessie88@step1ne.com",
        "1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q",
        "A:L", data
    ])
    print(f"  回復第 {i+1}-{min(i+batch_size, len(rows))} 筆...")

print(f"✅ 回復完成！共 {len(rows)} 筆")
