#!/usr/bin/env python3
"""使用已下載的TSV直接生成CSV"""
import re
import csv

print("🔧 修復問題：使用本地TSV生成CSV...")

# 讀取已下載的舊資料
with open('data/old-resume-pool.tsv', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"✅ 讀取 {len(lines)-1} 行（含標題）")

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

print("🔄 轉換資料...")

for i, line in enumerate(lines[1:], start=2):  # 跳過標題
    fields = line.strip().split('\t')
    
    # 補足12欄
    while len(fields) < 12:
        fields.append("")
    
    # 檢查姓名
    name = clean(fields[0])
    if not name or len(name) > 200:  # 避免錯誤資料
        continue
    
    # 解析
    email, phone = parse_contact(fields[1])
    years = parse_years(fields[4])
    
    # 組成新20欄
    row = [
        name,                   # A
        email,                  # B
        phone,                  # C
        "",                     # D: 地點
        clean(fields[2]),       # E: 職位
        years,                  # F
        "",                     # G: 轉職次數
        "",                     # H: 平均任職
        "",                     # I: gap
        clean(fields[3]),       # J: 技能
        clean(fields[5]),       # K: 學歷
        parse_source(fields[6]), # L: 來源
        "",                     # M: 工作經歷JSON
        "",                     # N: 離職原因
        calc_stability(years),  # O: 穩定性
        "",                     # P: 學歷JSON
        "",                     # Q: DISC
        clean(fields[7]),       # R: 狀態
        clean(fields[8]),       # S: 顧問
        clean(fields[9])        # T: 備註
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
print(f"📊 大小：{len(rows)} 行資料 + 1 標題行")

# 驗證前3筆
print("\n📋 資料驗證（前3筆）：")
for i, row in enumerate(rows[:3], start=1):
    print(f"\n候選人 {i}：")
    print(f"  姓名: {row[0]}")
    print(f"  Email: {row[1]}")
    print(f"  電話: {row[2]}")
    print(f"  職位: {row[4]}")
    print(f"  年資: {row[5]} 年")
    print(f"  來源: {row[11]}")
    print(f"  穩定性: {row[14]} 分")

print("\n✅ CSV 已就緒！")
print(f"📂 檔案位置：/Users/user/clawd/hr-tools/data/履歷池v2-完成版.csv")
