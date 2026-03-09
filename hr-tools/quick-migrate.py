#!/usr/bin/env python3
import re

def parse_contact(s):
    email, phone = "", ""
    if not s: return email, phone
    em = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', s)
    if em: email = em.group(0)
    ph = re.search(r'09\d{2}[-\s]?\d{3}[-\s]?\d{3}', s)
    if ph: phone = ph.group(0)
    if 'linkedin' in s.lower() and not email and not phone:
        email = s.strip()
    return email, phone

def parse_years(s):
    if not s: return 0
    s = str(s).strip()
    if s.isdigit(): return int(s)
    m = re.search(r'(\d+)[-~](\d+)', s)
    if m: return (int(m.group(1)) + int(m.group(2))) / 2
    m = re.search(r'\d+', s)
    return int(m.group(0)) if m else 0

def parse_source(link):
    if not link: return "未知"
    l = link.lower()
    if 'drive.google' in l: return "Gmail"
    if 'github' in l: return "GitHub"
    if 'linkedin' in l: return "LinkedIn"
    if 'telegram' in l or '直接上傳' in link: return "Telegram"
    return "其他"

def calc_stability(y):
    if y == 0: return 0
    s = 40
    if y >= 10: s += 30
    elif y >= 5: s += 20
    elif y >= 3: s += 10
    elif y >= 1: s += 5
    return min(s, 100)

def clean(t):
    return t.replace('\n', ' ').replace('\r', ' ').replace('|', '｜').strip() if t else ""

# 讀取檔案
with open('data/old-resume-pool.tsv', 'r', encoding='utf-8') as f:
    lines = f.readlines()

output_rows = []
for i, line in enumerate(lines[1:], start=2):  # 跳過標題行
    fields = line.strip().split('\t')
    while len(fields) < 12:
        fields.append("")
    
    name = clean(fields[0])
    if not name:
        continue
    
    email, phone = parse_contact(fields[1])
    position = clean(fields[2])
    skills = clean(fields[3])
    years = parse_years(fields[4])
    edu = clean(fields[5])
    source = parse_source(fields[6])
    status = clean(fields[7])
    consultant = clean(fields[8])
    note = clean(fields[9])
    stability = calc_stability(years)
    
    new_row = [
        name, email, phone, "", position,
        str(years) if years > 0 else "", "", "", "",
        skills, edu, source, "", "",
        str(stability) if stability > 0 else "",
        "", "", status, consultant, note
    ]
    
    output_rows.append("|".join(new_row))
    
    if i % 50 == 0:
        print(f"處理中... {i-1}/227")

print(f"\n✅ 轉換完成：{len(output_rows)} 筆")

# 輸出到檔案
with open('data/new-resume-pool-v2.txt', 'w', encoding='utf-8') as f:
    for row in output_rows:
        f.write(row + '\n')

print(f"✅ 已儲存到 data/new-resume-pool-v2.txt")
