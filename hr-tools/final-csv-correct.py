#!/usr/bin/env python3
"""正確處理：用多空格分隔"""
import re
import csv

print("🔧 最終修正：處理空格分隔資料...")

with open('data/old-resume-pool.tsv', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"✅ 讀取 {len(lines)-1} 行")

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
    if not s or s.strip() == "": return ""
    s = str(s).strip()
    if s.isdigit(): return s
    m = re.search(r'(\d+)[-~](\d+)', s)
    if m: return str((int(m.group(1)) + int(m.group(2))) / 2)
    m = re.search(r'\d+', s)
    return m.group(0) if m else ""

def calc_stability(y):
    if not y: return ""
    try: y = float(y)
    except: return ""
    if y == 0: return ""
    s = 40
    if y >= 10: s += 30
    elif y >= 5: s += 20
    elif y >= 3: s += 10
    elif y >= 1: s += 5
    return str(min(s, 100))

def parse_source(link):
    if not link: return "未知"
    l = link.lower()
    if 'drive.google' in l: return "Gmail"
    if 'github' in l: return "GitHub"
    if 'linkedin' in l: return "LinkedIn"
    if 'telegram' in l: return "Telegram"
    return "其他"

def clean(t):
    return t.replace('\n', ' ').replace('\r', ' ').strip() if t else ""

headers = [
    "姓名", "Email", "電話", "地點", "目前職位", 
    "總年資(年)", "轉職次數", "平均任職(月)", "最近gap(月)", 
    "技能", "學歷", "來源", "工作經歷JSON", "離職原因", 
    "穩定性評分", "學歷JSON", "DISC/Big Five", "狀態", "獵頭顧問", "備註"
]

rows = []

print("🔄 轉換資料（正則分割）...")

for i, line in enumerate(lines[1:], start=2):
    # 用2個以上空格分隔
    fields = re.split(r'\s{2,}', line.strip())
    
    # 補足12欄
    while len(fields) < 12:
        fields.append("")
    
    name = clean(fields[0])
    if not name or len(name) > 150:
        continue
    
    email, phone = parse_contact(fields[1])
    years = parse_years(fields[4])
    
    row = [
        name, email, phone, "",
        clean(fields[2]), years, "", "", "",
        clean(fields[3]), clean(fields[5]), parse_source(fields[6]),
        "", "", calc_stability(years), "", "",
        clean(fields[7]), clean(fields[8]), clean(fields[9])
    ]
    
    rows.append(row)
    
    if len(rows) % 50 == 0:
        print(f"  已處理 {len(rows)} 筆...")

print(f"\n✅ 轉換完成：{len(rows)} 筆")

# 寫入CSV
csv_file = 'data/履歷池v2-完成版.csv'
with open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(rows)

print(f"✅ 已生成：{csv_file}")

# 驗證
print("\n📋 驗證前5筆：")
for i, row in enumerate(rows[:5], start=1):
    print(f"\n{i}. {row[0]}")
    print(f"   Email: {row[1]}")
    print(f"   電話: {row[2]}")
    print(f"   職位: {row[4][:30]}")
    print(f"   年資: {row[5]} | 穩定性: {row[14]}")

print(f"\n✅ 完成！檔案：{csv_file}")
