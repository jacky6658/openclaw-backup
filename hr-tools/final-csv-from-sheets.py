#!/usr/bin/env python3
"""從Google Sheets直接讀取並生成CSV"""
import subprocess
import re
import csv
import time

SHEET_ID = "1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q"
ACCOUNT = "aiagentg888@gmail.com"

def get_cell(row, col):
    """讀取單一儲存格"""
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

def calc_stability(years_str):
    if not years_str: return ""
    try:
        y = float(years_str)
    except:
        return ""
    if y == 0: return ""
    score = 40
    if y >= 10: score += 30
    elif y >= 5: score += 20
    elif y >= 3: score += 10
    elif y >= 1: score += 5
    return str(min(score, 100))

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

print("🚀 從 Google Sheets 直接讀取前10筆測試...")

headers = [
    "姓名", "Email", "電話", "地點", "目前職位", 
    "總年資(年)", "轉職次數", "平均任職(月)", "最近gap(月)", 
    "技能", "學歷", "來源", "工作經歷JSON", "離職原因", 
    "穩定性評分", "學歷JSON", "DISC/Big Five", "狀態", "獵頭顧問", "備註"
]

rows = []

# 測試前10筆
for row_num in range(2, 12):  # 第2-11行
    print(f"  讀取第 {row_num} 行...")
    
    # 讀取舊12欄（A-L）
    old_cols = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
    old_data = [get_cell(row_num, col) for col in old_cols]
    
    name = clean(old_data[0])
    if not name:
        break
    
    email, phone = parse_contact(old_data[1])
    years = parse_years(old_data[4])
    stability = calc_stability(years)
    
    new_row = [
        name,                       # A
        email,                      # B
        phone,                      # C
        "",                         # D
        clean(old_data[2]),         # E
        years,                      # F
        "", "", "",                 # G, H, I
        clean(old_data[3]),         # J
        clean(old_data[5]),         # K
        parse_source(old_data[6]),  # L
        "", "",                     # M, N
        stability,                  # O
        "", "",                     # P, Q
        clean(old_data[7]),         # R
        clean(old_data[8]),         # S
        clean(old_data[9])          # T
    ]
    
    rows.append(new_row)
    time.sleep(0.2)  # 避免API限流

print(f"\n✅ 測試完成：讀取 {len(rows)} 筆")

# 寫入CSV
csv_path = 'data/履歷池v2-測試10筆.csv'
with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(rows)

print(f"✅ 已生成：{csv_path}")

# 顯示前3筆
print("\n📋 資料預覽：")
for i, row in enumerate(rows[:3], start=2):
    print(f"\n第 {i} 行：")
    print(f"  A-姓名: {row[0][:40]}")
    print(f"  B-Email: {row[1]}")
    print(f"  C-電話: {row[2]}")
    print(f"  E-職位: {row[4][:30]}")
    print(f"  F-年資: {row[5]}")
    print(f"  L-來源: {row[11]}")
    print(f"  O-穩定性: {row[14]}")
