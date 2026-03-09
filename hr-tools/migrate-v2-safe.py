#!/usr/bin/env python3
"""
安全版遷移：逐行讀取並處理
"""

import subprocess
import re

SHEET_ID = "1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q"
ACCOUNT = "aiagentg888@gmail.com"

def get_cell(row, col):
    """讀取單一儲存格"""
    result = subprocess.run(
        ["gog", "sheets", "get", SHEET_ID, f"{col}{row}", "--account", ACCOUNT],
        capture_output=True,
        text=True
    )
    return result.stdout.strip() if result.returncode == 0 else ""

def parse_contact(contact_str):
    """解析聯絡方式"""
    email = ""
    phone = ""
    
    if not contact_str:
        return email, phone
    
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', contact_str)
    if email_match:
        email = email_match.group(0)
    
    phone_match = re.search(r'09\d{2}[-\s]?\d{3}[-\s]?\d{3}', contact_str)
    if phone_match:
        phone = phone_match.group(0)
    
    if 'linkedin' in contact_str.lower() and not email and not phone:
        email = contact_str.strip()
    
    return email, phone

def parse_years(years_str):
    """解析年資"""
    if not years_str:
        return 0
    
    years_str = str(years_str).strip()
    
    if years_str.isdigit():
        return int(years_str)
    
    match = re.search(r'(\d+)[-~](\d+)', years_str)
    if match:
        return (int(match.group(1)) + int(match.group(2))) / 2
    
    match = re.search(r'\d+', years_str)
    if match:
        return int(match.group(0))
    
    return 0

def parse_source(file_link):
    """解析來源"""
    if not file_link:
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
    return "其他"

def calc_stability(years):
    """計算穩定性"""
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

def clean(text):
    """清理文字"""
    if not text:
        return ""
    return text.replace('\n', ' ').replace('\r', ' ').replace('|', '｜').strip()

def process_row(row_num):
    """處理一行資料"""
    # 讀取舊12欄
    old_cols = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
    old_data = [get_cell(row_num, col) for col in old_cols]
    
    name = clean(old_data[0])
    if not name:  # 空行
        return None
    
    # 解析
    email, phone = parse_contact(old_data[1])
    position = clean(old_data[2])
    skills = clean(old_data[3])
    years = parse_years(old_data[4])
    edu = clean(old_data[5])
    source = parse_source(old_data[6])
    status = clean(old_data[7])
    consultant = clean(old_data[8])
    note = clean(old_data[9])
    stability = calc_stability(years)
    
    # 組成新20欄（使用 | 分隔）
    new_row = [
        name,                                    # A
        email,                                   # B
        phone,                                   # C
        "",                                      # D: 地點
        position,                                # E
        str(years) if years > 0 else "",        # F
        "",                                      # G: 轉職次數
        "",                                      # H: 平均任職
        "",                                      # I: gap
        skills,                                  # J
        edu,                                     # K
        source,                                  # L
        "",                                      # M: 工作經歷JSON
        "",                                      # N: 離職原因
        str(stability) if stability > 0 else "", # O
        "",                                      # P: 學歷JSON
        "",                                      # Q: DISC
        status,                                  # R
        consultant,                              # S
        note                                     # T
    ]
    
    return "|".join(new_row)

# 測試前5筆
print("🧪 測試前5筆...")
for i in range(2, 7):
    row_data = process_row(i)
    if row_data:
        fields = row_data.split('|')
        print(f"\n第 {i} 行：")
        print(f"  A-姓名: {fields[0]}")
        print(f"  B-Email: {fields[1]}")
        print(f"  C-電話: {fields[2]}")
        print(f"  E-職位: {fields[4][:30]}")
        print(f"  F-年資: {fields[5]}")
        print(f"  L-來源: {fields[11]}")
        print(f"  O-穩定性: {fields[14]}")

print("\n✅ 測試完成！")
