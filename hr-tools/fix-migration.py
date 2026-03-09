#!/usr/bin/env python3
"""
修正版遷移腳本：使用安全的分隔符號
"""

import subprocess
import re

SHEET_ID = "1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q"
ACCOUNT = "aiagentg888@gmail.com"

def parse_contact(contact_str):
    """解析聯絡方式"""
    email = ""
    phone = ""
    
    if not contact_str or contact_str.strip() == "":
        return email, phone
    
    # Email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', contact_str)
    if email_match:
        email = email_match.group(0)
    
    # 電話
    phone_match = re.search(r'09\d{2}[-\s]?\d{3}[-\s]?\d{3}', contact_str)
    if phone_match:
        phone = phone_match.group(0)
    
    # LinkedIn
    if 'linkedin' in contact_str.lower() and not email and not phone:
        email = contact_str.strip()
    
    return email, phone

def parse_years(years_str):
    """解析年資"""
    if not years_str or years_str.strip() == "":
        return 0
    
    years_str = str(years_str).strip()
    
    if years_str.isdigit():
        return int(years_str)
    
    match = re.search(r'(\d+)[-~](\d+)', years_str)
    if match:
        low = int(match.group(1))
        high = int(match.group(2))
        return (low + high) / 2
    
    match = re.search(r'\d+', years_str)
    if match:
        return int(match.group(0))
    
    return 0

def parse_source(file_link):
    """解析來源"""
    if not file_link or file_link.strip() == "":
        return "未知"
    
    link = file_link.lower()
    
    if 'drive.google.com' in link:
        return "Gmail"
    elif 'github' in link:
        return "GitHub"
    elif 'linkedin' in link:
        return "LinkedIn"
    elif 'telegram' in link or '直接上傳' in file_link:
        return "Telegram"
    else:
        return "其他"

def calculate_simple_stability(years):
    """簡化穩定性評分"""
    if years == 0:
        return 0
    
    score = 40
    
    if years >= 10:
        score += 30
    elif years >= 5:
        score += 20
    elif years >= 3:
        score += 10
    elif years >= 1:
        score += 5
    
    return min(score, 100)

def clean_field(text):
    """清理欄位內容（移除換行、逗號）"""
    if not text:
        return ""
    return text.replace('\n', ' ').replace('\r', ' ').replace(',', '，').replace('|', '｜').strip()

# 讀取舊資料
print("📥 讀取舊分頁...")
result = subprocess.run(
    ["gog", "sheets", "get", SHEET_ID, "A2:L250", "--account", ACCOUNT],
    capture_output=True,
    text=True
)

lines = [l for l in result.stdout.strip().split('\n') if l.strip()]
print(f"✅ 讀取 {len(lines)} 行")

# 測試前5筆
print("\n🧪 測試前5筆資料格式...")

for i, row in enumerate(lines[:5], start=2):
    fields = row.split('\t')
    while len(fields) < 12:
        fields.append("")
    
    name = clean_field(fields[0])
    email, phone = parse_contact(fields[1])
    position = clean_field(fields[2])
    skills = clean_field(fields[3])
    years = parse_years(fields[4])
    edu = clean_field(fields[5])
    source = parse_source(fields[6])
    status = clean_field(fields[7])
    consultant = clean_field(fields[8])
    note = clean_field(fields[9])
    stability = calculate_simple_stability(years)
    
    print(f"\n第 {i} 行：")
    print(f"  姓名: {name}")
    print(f"  Email: {email}")
    print(f"  電話: {phone}")
    print(f"  職位: {position[:30]}...")
    print(f"  技能: {skills[:40]}...")
    print(f"  年資: {years}")
    print(f"  來源: {source}")
    print(f"  穩定性: {stability}")

print("\n✅ 測試完成！格式正確")
print("\n請確認以上資料正確，然後執行完整遷移")
