#!/usr/bin/env python3
import re
import csv

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
    if not s: return ""
    s = str(s).strip()
    if s.isdigit(): return s
    m = re.search(r'(\d+)[-~](\d+)', s)
    if m: return str((int(m.group(1)) + int(m.group(2))) / 2)
    m = re.search(r'\d+', s)
    return m.group(0) if m else ""

def parse_source(link):
    if not link: return "未知"
    l = link.lower()
    if 'drive.google' in l: return "Gmail"
    if 'github' in l: return "GitHub"
    if 'linkedin' in l: return "LinkedIn"
    if 'telegram' in l: return "Telegram"
    return "其他"

def calc_stability(y):
    try:
        y = float(y) if y else 0
    except:
        return ""
    if y == 0: return ""
    s = 40
    if y >= 10: s += 30
    elif y >= 5: s += 20
    elif y >= 3: s += 10
    elif y >= 1: s += 5
    return str(min(s, 100))

def clean(t):
    return t.replace('\n', ' ').replace('\r', ' ').strip() if t else ""

# 讀取TSV
with open('data/old-resume-pool.tsv', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 準備CSV
output_rows = []
headers = ["姓名","Email","電話","地點","目前職位","總年資(年)","轉職次數","平均任職(月)","最近gap(月)",
           "技能","學歷","來源","工作經歷JSON","離職原因","穩定性評分","學歷JSON","DISC/Big Five",
           "狀態","獵頭顧問","備註"]

output_rows.append(headers)

for i, line in enumerate(lines[1:], start=2):
    fields = line.strip().split('\t')
    while len(fields) < 12:
        fields.append("")
    
    name = clean(fields[0])
    if not name:
        continue
    
    email, phone = parse_contact(fields[1])
    years = parse_years(fields[4])
    stability = calc_stability(years)
    
    row = [
        name,
        email,
        phone,
        "",  # 地點
        clean(fields[2]),  # 職位
        years,
        "",  # 轉職次數
        "",  # 平均任職
        "",  # gap
        clean(fields[3]),  # 技能
        clean(fields[5]),  # 學歷
        parse_source(fields[6]),
        "",  # 工作經歷JSON
        "",  # 離職原因
        stability,
        "",  # 學歷JSON
        "",  # DISC
        clean(fields[7]),  # 狀態
        clean(fields[8]),  # 顧問
        clean(fields[9])   # 備註
    ]
    
    output_rows.append(row)

# 寫入CSV
with open('data/resume-pool-v2-final.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(output_rows)

print(f"✅ 已生成 CSV：{len(output_rows)-1} 筆資料")
print(f"📄 檔案：data/resume-pool-v2-final.csv")
