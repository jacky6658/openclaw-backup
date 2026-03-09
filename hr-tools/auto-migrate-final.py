#!/usr/bin/env python3
"""自動遷移：直接從舊Sheet讀取 → 寫入新Sheet"""
import subprocess
import re
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

def update_row(row_num, values):
    """更新一整行（A-T）"""
    # values 是 20 個元素的 list
    values_str = "|".join(values)
    result = subprocess.run(
        ["gog", "sheets", "update", SHEET_ID, f"履歷池v2!A{row_num}:T{row_num}", values_str, "--account", ACCOUNT],
        capture_output=True, text=True
    )
    return result.returncode == 0

def parse_contact(s):
    """拆分聯絡方式"""
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
    """解析年資"""
    if not s or s.strip() == "": return ""
    s = str(s).strip()
    
    if s.isdigit(): return s
    
    # 範圍（6-7年）
    m = re.search(r'(\d+)[-~](\d+)', s)
    if m:
        avg = (int(m.group(1)) + int(m.group(2))) / 2
        return str(avg)
    
    # 提取數字
    m = re.search(r'\d+', s)
    return m.group(0) if m else ""

def calc_stability(years_str):
    """計算穩定性評分"""
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
    """判斷來源"""
    if not link or link.strip() == "": return "未知"
    l = link.lower()
    
    if 'drive.google' in l: return "Gmail"
    if 'github' in l: return "GitHub"
    if 'linkedin' in l: return "LinkedIn"
    if 'telegram' in l or '直接上傳' in link: return "Telegram"
    return "其他"

def clean(t):
    """清理文字"""
    if not t: return ""
    return t.replace('\n', ' ').replace('\r', ' ').strip()

print("="*60)
print("🚀 自動遷移履歷池 v1.0")
print("="*60)

# Step 1: 讀取並轉換資料
print("\n📥 Step 1: 讀取舊履歷池資料...")

rows_to_migrate = []
errors = []

for row_num in range(2, 230):  # 第2-229行（含緩衝）
    try:
        # 讀取舊12欄
        old_cols = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
        old_data = [get_cell(row_num, col) for col in old_cols]
        
        # 檢查姓名
        name = clean(old_data[0])
        if not name:
            print(f"  第 {row_num} 行為空，停止讀取")
            break
        
        # 解析處理
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
        
        # 組成新20欄
        new_row = [
            name,           # A: 姓名
            email,          # B: Email
            phone,          # C: 電話
            "",             # D: 地點
            position,       # E: 職位
            years,          # F: 年資
            "",             # G: 轉職次數
            "",             # H: 平均任職
            "",             # I: gap
            skills,         # J: 技能
            edu,            # K: 學歷
            source,         # L: 來源
            "",             # M: 工作經歷JSON
            "",             # N: 離職原因
            stability,      # O: 穩定性
            "",             # P: 學歷JSON
            "",             # Q: DISC
            status,         # R: 狀態
            consultant,     # S: 顧問
            note            # T: 備註
        ]
        
        rows_to_migrate.append((row_num, new_row))
        
        if len(rows_to_migrate) % 20 == 0:
            print(f"  已讀取 {len(rows_to_migrate)} 筆...")
        
        time.sleep(0.1)  # 避免API限流
        
    except Exception as e:
        errors.append(f"第 {row_num} 行錯誤: {e}")

print(f"\n✅ 讀取完成：{len(rows_to_migrate)} 筆")

if errors:
    print(f"⚠️ {len(errors)} 筆錯誤：")
    for err in errors[:3]:
        print(f"  {err}")

# Step 2: 寫入新履歷池v2
print(f"\n📤 Step 2: 寫入履歷池v2...")

success = 0
failed = 0

for i, (old_row_num, new_row_data) in enumerate(rows_to_migrate, start=1):
    new_row_num = i + 1  # 從第2行開始（第1行是標題）
    
    if update_row(new_row_num, new_row_data):
        success += 1
        if success % 10 == 0:
            print(f"  ✅ 已寫入 {success}/{len(rows_to_migrate)}")
    else:
        failed += 1
        print(f"  ❌ 第 {new_row_num} 行寫入失敗")
    
    time.sleep(0.15)  # 避免API限流

print("\n" + "="*60)
print(f"🎉 遷移完成！")
print(f"  ✅ 成功：{success} 筆")
print(f"  ❌ 失敗：{failed} 筆")
print("="*60)

# Step 3: 驗證
print("\n📊 驗證前3筆資料...")
for row_num in range(2, 5):
    name = get_cell(row_num, "A")
    email = get_cell(row_num, "B")
    phone = get_cell(row_num, "C")
    print(f"\n第 {row_num} 行：")
    print(f"  姓名: {name[:40]}")
    print(f"  Email: {email}")
    print(f"  電話: {phone}")

print("\n✅ 完成！")
