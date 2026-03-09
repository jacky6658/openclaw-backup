#!/usr/bin/env python3
"""
履歷池資料遷移腳本：舊分頁(12欄) → 新分頁v2(20欄)
"""

import subprocess
import re
import json
import sys

SHEET_ID = "1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q"
ACCOUNT = "aiagentg888@gmail.com"
OLD_SHEET = "A2:L300"  # 舊分頁（跳過標題行）
NEW_SHEET = "履歷池v2"

def get_old_data():
    """讀取舊分頁資料"""
    print("📥 讀取舊分頁資料...")
    result = subprocess.run(
        ["gog", "sheets", "get", SHEET_ID, OLD_SHEET, "--account", ACCOUNT],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ 讀取失敗: {result.stderr}")
        return []
    
    lines = result.stdout.strip().split('\n')
    print(f"✅ 讀取 {len(lines)} 行資料")
    return lines

def parse_contact(contact_str):
    """
    解析聯絡方式欄位
    格式：LinkedIn: xxx / 0965-806-936 / rouzhen1030@gmail.com
    """
    email = ""
    phone = ""
    
    if not contact_str or contact_str.strip() == "":
        return email, phone
    
    # Email 正則
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', contact_str)
    if email_match:
        email = email_match.group(0)
    
    # 電話正則（台灣手機號碼）
    phone_match = re.search(r'09\d{2}[-\s]?\d{3}[-\s]?\d{3}', contact_str)
    if phone_match:
        phone = phone_match.group(0)
    
    # LinkedIn
    if 'linkedin' in contact_str.lower() and not email and not phone:
        email = contact_str.strip()  # 保留 LinkedIn 資訊在 email 欄
    
    return email, phone

def parse_years(years_str):
    """
    解析工作經驗欄位
    格式：30 / 6-7年 / 3-4年
    """
    if not years_str or years_str.strip() == "":
        return 0
    
    years_str = str(years_str).strip()
    
    # 數字
    if years_str.isdigit():
        return int(years_str)
    
    # 範圍（取中間值）
    match = re.search(r'(\d+)[-~](\d+)', years_str)
    if match:
        low = int(match.group(1))
        high = int(match.group(2))
        return (low + high) / 2
    
    # 提取第一個數字
    match = re.search(r'\d+', years_str)
    if match:
        return int(match.group(0))
    
    return 0

def parse_source(file_link):
    """
    解析來源（從履歷檔案連結推測）
    """
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
    """
    簡化穩定性評分（僅基於年資）
    """
    if years == 0:
        return 0
    
    # 基礎分
    score = 40
    
    # 年資分數（最多30分）
    if years >= 10:
        score += 30
    elif years >= 5:
        score += 20
    elif years >= 3:
        score += 10
    elif years >= 1:
        score += 5
    
    return min(score, 100)

def transform_row(row_data):
    """
    轉換一行資料：舊12欄 → 新20欄
    """
    fields = row_data.split('\t')
    
    # 確保至少12欄（補空白）
    while len(fields) < 12:
        fields.append("")
    
    # 舊欄位
    old_name = fields[0]          # A: 姓名
    old_contact = fields[1]       # B: 聯絡方式
    old_position = fields[2]      # C: 應徵職位
    old_skills = fields[3]        # D: 主要技能
    old_years = fields[4]         # E: 工作經驗(年)
    old_edu = fields[5]           # F: 學歷
    old_file = fields[6]          # G: 履歷檔案連結
    old_status = fields[7]        # H: 狀態
    old_consultant = fields[8]    # I: 獵頭顧問
    old_note = fields[9]          # J: 備註
    # K, L 捨棄（新增日期/最後更新）
    
    # 解析處理
    email, phone = parse_contact(old_contact)
    years = parse_years(old_years)
    source = parse_source(old_file)
    stability = calculate_simple_stability(years)
    
    # 新20欄
    new_row = [
        old_name,                  # A: 姓名
        email,                     # B: Email
        phone,                     # C: 電話
        "",                        # D: 地點（空白，未來補充）
        old_position,              # E: 目前職位
        str(years) if years > 0 else "",  # F: 總年資(年)
        "",                        # G: 轉職次數（空白）
        "",                        # H: 平均任職(月)（空白）
        "",                        # I: 最近gap(月)（空白）
        old_skills,                # J: 技能
        old_edu,                   # K: 學歷
        source,                    # L: 來源
        "",                        # M: 工作經歷JSON（空白）
        "",                        # N: 離職原因（空白）
        str(stability) if stability > 0 else "",  # O: 穩定性評分
        "",                        # P: 學歷JSON（空白）
        "",                        # Q: DISC/Big Five（空白）
        old_status,                # R: 狀態
        old_consultant,            # S: 獵頭顧問
        old_note                   # T: 備註
    ]
    
    return "|".join(new_row)

def migrate_data(old_data):
    """批量遷移資料"""
    print(f"\n🔄 開始遷移 {len(old_data)} 筆資料...")
    
    transformed = []
    errors = []
    
    for i, row in enumerate(old_data, start=2):
        try:
            new_row = transform_row(row)
            transformed.append(new_row)
            
            if i % 50 == 0:
                print(f"   處理中... {i}/{len(old_data)}")
        except Exception as e:
            errors.append(f"第 {i} 行錯誤: {e}")
    
    print(f"✅ 轉換完成：{len(transformed)} 筆成功")
    
    if errors:
        print(f"⚠️ {len(errors)} 筆錯誤：")
        for err in errors[:5]:  # 只顯示前5個
            print(f"   {err}")
    
    return transformed

def batch_append(new_data, batch_size=50):
    """批量寫入新分頁"""
    print(f"\n📤 開始寫入新分頁（每批 {batch_size} 筆）...")
    
    total = len(new_data)
    success = 0
    
    for i in range(0, total, batch_size):
        batch = new_data[i:i+batch_size]
        values = ",".join(batch)
        
        result = subprocess.run(
            ["gog", "sheets", "append", SHEET_ID, f"{NEW_SHEET}!A:T", values, "--account", ACCOUNT],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            success += len(batch)
            print(f"   ✅ 已寫入 {success}/{total}")
        else:
            print(f"   ❌ 批次 {i//batch_size + 1} 失敗: {result.stderr}")
            # 改用單筆寫入
            for single in batch:
                retry = subprocess.run(
                    ["gog", "sheets", "append", SHEET_ID, f"{NEW_SHEET}!A:T", single, "--account", ACCOUNT],
                    capture_output=True,
                    text=True
                )
                if retry.returncode == 0:
                    success += 1
    
    print(f"\n✅ 寫入完成：{success}/{total} 筆成功")
    return success

def main():
    print("="*60)
    print("📋 履歷池資料遷移 v1.0")
    print("="*60)
    
    # Step 1: 讀取舊資料
    old_data = get_old_data()
    if not old_data:
        print("❌ 無資料可遷移")
        return 1
    
    # Step 2: 轉換資料
    new_data = migrate_data(old_data)
    if not new_data:
        print("❌ 轉換失敗")
        return 1
    
    # Step 3: 寫入新分頁
    success_count = batch_append(new_data, batch_size=20)
    
    # Step 4: 驗證
    print("\n📊 驗證新分頁資料...")
    result = subprocess.run(
        ["gog", "sheets", "get", SHEET_ID, f"{NEW_SHEET}!A2:A5", "--account", ACCOUNT],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ 前幾筆資料：")
        print(result.stdout)
    
    print("\n" + "="*60)
    print(f"🎉 遷移完成！成功 {success_count}/{len(old_data)} 筆")
    print("="*60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
