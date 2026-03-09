#!/usr/bin/env python3
"""生成完美CSV（逐格讀取）"""
import subprocess
import re
import csv
import time

SHEET_ID = "1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q"
ACCOUNT = "aiagentg888@gmail.com"

def get_cell(row, col):
    result = subprocess.run(
        ["gog", "sheets", "get", SHEET_ID, f"{col}{row}", "--account", ACCOUNT],
        capture_output=True, text=True
    )
    return result.stdout.strip() if result.returncode == 0 else ""

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

print("🚀 生成完美CSV（逐格讀取）...")

headers = [
    "姓名", "Email", "電話", "地點", "目前職位", 
    "總年資(年)", "轉職次數", "平均任職(月)", "最近gap(月)", 
    "技能", "學歷", "來源", "工作經歷JSON", "離職原因", 
    "穩定性評分", "學歷JSON", "DISC/Big Five", "狀態", "獵頭顧問", "備註"
]

rows = []

for row_num in range(2, 250):
    # 讀取舊12欄
    cols = ['A','B','C','D','E','F','G','H','I','J','K','L']
    old = [get_cell(row_num, c) for c in cols]
    
    name = clean(old[0])
    if not name:
        print(f"  第 {row_num} 行為空，停止讀取")
        break
    
    email, phone = parse_contact(old[1])
    years = parse_years(old[4])
    
    row = [
        name, email, phone, "",
        clean(old[2]), years, "", "", "",
        clean(old[3]), clean(old[5]), parse_source(old[6]),
        "", "", calc_stability(years), "", "",
        clean(old[7]), clean(old[8]), clean(old[9])
    ]
    
    rows.append(row)
    
    if len(rows) % 20 == 0:
        print(f"  已處理 {len(rows)} 筆...")
    
    time.sleep(0.1)

print(f"\n✅ 讀取完成：{len(rows)} 筆")

# 寫入CSV
csv_file = 'data/履歷池v2-最終版.csv'
with open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(rows)

print(f"✅ 已生成：{csv_file}")
print(f"📊 總計：{len(rows)} 筆資料")

# 預覽
print("\n📋 前3筆預覽：")
for i, row in enumerate(rows[:3], start=2):
    print(f"\n第 {i} 行：")
    print(f"  姓名: {row[0][:40]}")
    print(f"  Email: {row[1]}")
    print(f"  電話: {row[2]}")
    print(f"  職位: {row[4][:30]}")
    print(f"  年資: {row[5]}")
    print(f"  穩定性: {row[14]}")
