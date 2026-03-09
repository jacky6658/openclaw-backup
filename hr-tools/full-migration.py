#!/usr/bin/env python3
"""完整遷移腳本"""

import subprocess
import re
import time

SHEET_ID = "1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q"
ACCOUNT = "aiagentg888@gmail.com"
START_ROW = 2
END_ROW = 230  # 含緩衝

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
    if 'drive.google.com' in l: return "Gmail"
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

def process_row(row_num):
    cols = ['A','B','C','D','E','F','G','H','I','J','K','L']
    d = [get_cell(row_num, c) for c in cols]
    
    name = clean(d[0])
    if not name: return None
    
    email, phone = parse_contact(d[1])
    position = clean(d[2])
    skills = clean(d[3])
    years = parse_years(d[4])
    edu = clean(d[5])
    source = parse_source(d[6])
    status = clean(d[7])
    consultant = clean(d[8])
    note = clean(d[9])
    stability = calc_stability(years)
    
    return "|".join([
        name, email, phone, "", position,
        str(years) if years > 0 else "", "", "", "",
        skills, edu, source, "", "",
        str(stability) if stability > 0 else "",
        "", "", status, consultant, note
    ])

print("="*60)
print("🚀 開始完整遷移")
print("="*60)

batch = []
success = 0
errors = 0

for row in range(START_ROW, END_ROW):
    try:
        data = process_row(row)
        if data:
            batch.append(data)
            success += 1
            
            if success % 20 == 0:
                # 批量寫入
                values = ",".join(batch)
                result = subprocess.run(
                    ["gog", "sheets", "append", SHEET_ID, "履歷池v2!A:T", values, "--account", ACCOUNT],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    print(f"✅ 已遷移 {success} 筆")
                    batch = []
                else:
                    print(f"⚠️ 批量寫入失敗，改用單筆...")
                    for single in batch:
                        subprocess.run(
                            ["gog", "sheets", "append", SHEET_ID, "履歷池v2!A:T", single, "--account", ACCOUNT],
                            capture_output=True, text=True
                        )
                    batch = []
            
            time.sleep(0.1)  # 避免API限流
        else:
            break  # 遇到空行就停止
    except Exception as e:
        errors += 1
        print(f"❌ 第 {row} 行錯誤: {e}")

# 寫入剩餘資料
if batch:
    values = ",".join(batch)
    subprocess.run(
        ["gog", "sheets", "append", SHEET_ID, "履歷池v2!A:T", values, "--account", ACCOUNT],
        capture_output=True, text=True
    )

print("="*60)
print(f"🎉 遷移完成！成功 {success} 筆，錯誤 {errors} 筆")
print("="*60)
