#!/usr/bin/env python3
"""生成完美格式的CSV"""
import re
import csv

def parse_contact(s):
    email, phone = "", ""
    if not s: return email, phone
    
    # Email
    em = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', s)
    if em: email = em.group(0)
    
    # 電話
    ph = re.search(r'09\d{2}[-\s]?\d{3}[-\s]?\d{3}', s)
    if ph: phone = ph.group(0)
    
    # LinkedIn
    if 'linkedin' in s.lower() and not email and not phone:
        email = s.strip()
    
    return email, phone

def parse_years(s):
    if not s or s.strip() == "": return ""
    s = str(s).strip()
    
    # 純數字
    if s.isdigit(): return s
    
    # 範圍
    m = re.search(r'(\d+)[-~](\d+)', s)
    if m:
        avg = (int(m.group(1)) + int(m.group(2))) / 2
        return str(avg)
    
    # 提取數字
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
    if not link or link.strip() == "": return "未知"
    l = link.lower()
    
    if 'drive.google' in l: return "Gmail"
    if 'github' in l: return "GitHub"
    if 'linkedin' in l: return "LinkedIn"
    if 'telegram' in l or '直接上傳' in link: return "Telegram"
    return "其他"

def clean(text):
    if not text: return ""
    # 移除換行、多餘空白
    return text.replace('\n', ' ').replace('\r', ' ').strip()

# 讀取舊資料
print("📥 讀取舊履歷池...")
with open('data/old-resume-pool.tsv', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"✅ 讀取 {len(lines)-1} 筆（含標題）")

# CSV 標題
headers = [
    "姓名", "Email", "電話", "地點", "目前職位", 
    "總年資(年)", "轉職次數", "平均任職(月)", "最近gap(月)", 
    "技能", "學歷", "來源", "工作經歷JSON", "離職原因", 
    "穩定性評分", "學歷JSON", "DISC/Big Five", "狀態", "獵頭顧問", "備註"
]

rows = []
errors = []

for i, line in enumerate(lines[1:], start=2):  # 跳過標題
    try:
        fields = line.strip().split('\t')
        
        # 補足12欄
        while len(fields) < 12:
            fields.append("")
        
        # 解析舊12欄
        name = clean(fields[0])
        contact = fields[1]
        position = clean(fields[2])
        skills = clean(fields[3])
        years_raw = fields[4]
        edu = clean(fields[5])
        file_link = fields[6]
        status = clean(fields[7])
        consultant = clean(fields[8])
        note = clean(fields[9])
        
        # 如果沒有姓名，跳過
        if not name:
            continue
        
        # 解析處理
        email, phone = parse_contact(contact)
        years = parse_years(years_raw)
        stability = calc_stability(years)
        source = parse_source(file_link)
        
        # 組成新20欄
        row = [
            name,           # A
            email,          # B
            phone,          # C
            "",             # D: 地點（空白）
            position,       # E
            years,          # F
            "",             # G: 轉職次數（空白）
            "",             # H: 平均任職（空白）
            "",             # I: gap（空白）
            skills,         # J
            edu,            # K
            source,         # L
            "",             # M: 工作經歷JSON（空白）
            "",             # N: 離職原因（空白）
            stability,      # O
            "",             # P: 學歷JSON（空白）
            "",             # Q: DISC（空白）
            status,         # R
            consultant,     # S
            note            # T
        ]
        
        rows.append(row)
        
    except Exception as e:
        errors.append(f"第 {i} 行錯誤: {e}")

print(f"✅ 轉換完成：{len(rows)} 筆")

if errors:
    print(f"⚠️ {len(errors)} 筆錯誤：")
    for err in errors[:3]:
        print(f"  {err}")

# 寫入CSV（UTF-8 BOM for Excel相容）
csv_path = 'data/履歷池v2-完整版.csv'
with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(headers)  # 標題
    writer.writerows(rows)    # 資料

print(f"\n✅ CSV已生成：{csv_path}")
print(f"📊 總計：{len(rows)} 筆資料 + 1 標題行")

# 顯示前3筆預覽
print("\n📋 前3筆預覽：")
for i, row in enumerate(rows[:3], start=2):
    print(f"\n第 {i} 行：")
    print(f"  姓名: {row[0]}")
    print(f"  Email: {row[1]}")
    print(f"  電話: {row[2]}")
    print(f"  職位: {row[4][:30]}")
    print(f"  年資: {row[5]}")
    print(f"  穩定性: {row[14]}")
    print(f"  來源: {row[11]}")
