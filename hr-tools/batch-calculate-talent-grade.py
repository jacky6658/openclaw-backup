#!/usr/bin/env python3
"""
Step1ne 人才等級批量評級系統
使用方案A權重計算綜合評分並轉換成等級（S/A/B/C/D/F）
"""

import subprocess
import json
import time

SHEET_ID = "1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q"
ACCOUNT = "aijessie88@step1ne.com"

def calculate_grade(stability, years, education, job_changes, last_gap):
    """計算人才等級"""
    
    # 1. 穩定性評分（25%）
    stability_score = int(stability) if stability and stability.isdigit() else 0
    
    # 2. 年資經驗（20%）
    years_val = int(years) if years and years.isdigit() else 0
    if years_val >= 10:
        years_score = 100
    elif years_val >= 7:
        years_score = 85
    elif years_val >= 5:
        years_score = 70
    elif years_val >= 3:
        years_score = 55
    elif years_val >= 1:
        years_score = 40
    else:
        years_score = 20
    
    # 3. 學歷背景（15%）
    education_score = 50  # 預設
    if any(keyword in (education or '') for keyword in ['博士', 'PhD', 'Doctor']):
        education_score = 100
    elif any(keyword in (education or '') for keyword in ['碩士', 'Master', '研究所']):
        education_score = 85
    elif any(keyword in (education or '') for keyword in ['學士', '大學', 'Bachelor']):
        education_score = 70
    elif any(keyword in (education or '') for keyword in ['專科', '大專']):
        education_score = 55
    elif any(keyword in (education or '') for keyword in ['高中', '高職']):
        education_score = 40
    
    # 4. 轉職次數（10% - 負向指標）
    changes = int(job_changes) if job_changes and job_changes.isdigit() else 0
    if changes == 0:
        job_changes_score = 100
    elif changes == 1:
        job_changes_score = 90
    elif changes == 2:
        job_changes_score = 70
    elif changes == 3:
        job_changes_score = 50
    elif changes == 4:
        job_changes_score = 30
    else:
        job_changes_score = 10
    
    # 5. 最近gap（5% - 負向指標）
    gap = int(last_gap) if last_gap and last_gap.isdigit() else 0
    if gap == 0:
        gap_score = 100
    elif gap <= 3:
        gap_score = 80
    elif gap <= 6:
        gap_score = 60
    elif gap <= 12:
        gap_score = 40
    else:
        gap_score = 20
    
    # 計算加權總分（方案A權重）
    # 技能匹配度（25%）- 暫時使用穩定性代替
    # 穩定性評分（25%）
    # 年資經驗（20%）
    # 學歷背景（15%）
    # 轉職次數（10%）
    # 最近gap（5%）
    
    total_score = (
        stability_score * 0.25 +  # 技能匹配度（暫時用穩定性）
        stability_score * 0.25 +  # 穩定性評分
        years_score * 0.20 +      # 年資經驗
        education_score * 0.15 +  # 學歷背景
        job_changes_score * 0.10 + # 轉職次數
        gap_score * 0.05          # 最近gap
    )
    
    # 四捨五入到整數
    total_score = round(total_score)
    
    # 轉換成等級
    if total_score >= 90:
        grade = 'S'
    elif total_score >= 80:
        grade = 'A'
    elif total_score >= 70:
        grade = 'B'
    elif total_score >= 60:
        grade = 'C'
    elif total_score >= 50:
        grade = 'D'
    else:
        grade = 'F'
    
    return grade, total_score

def get_cell_value(row, col):
    """讀取單一儲存格"""
    try:
        result = subprocess.run(
            ['gog', 'sheets', 'get', SHEET_ID, f'履歷池v2!{col}{row}', '--account', ACCOUNT],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout.strip() if result.returncode == 0 else ''
    except:
        return ''

def update_cell_value(row, col, value):
    """更新單一儲存格"""
    try:
        result = subprocess.run(
            ['gog', 'sheets', 'update', SHEET_ID, f'履歷池v2!{col}{row}', 
             '--values-json', json.dumps([[value]]), '--account', ACCOUNT],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except:
        return False

def main():
    print("=" * 50)
    print("Step1ne 人才等級批量評級系統（Python 版）")
    print("=" * 50)
    print()
    
    total = 0
    updated = 0
    skipped = 0
    
    print("⏳ 開始批量評級...")
    print()
    
    # 處理候選人（Row 2 開始）
    for row in range(2, 300):  # 最多 300 位
        # 讀取姓名（檢查是否有資料）
        name = get_cell_value(row, 'A')
        if not name:
            break  # 遇到空行就停止
        
        total += 1
        
        # 讀取評分相關欄位
        years = get_cell_value(row, 'F')       # 總年資
        job_changes = get_cell_value(row, 'G') # 轉職次數
        last_gap = get_cell_value(row, 'I')    # 最近gap
        education = get_cell_value(row, 'K')   # 學歷
        stability = get_cell_value(row, 'O')   # 穩定性評分
        
        # 計算等級
        grade, score = calculate_grade(stability, years, education, job_changes, last_gap)
        
        # 更新 Google Sheets V 欄
        success = update_cell_value(row, 'V', grade)
        
        if success:
            updated += 1
            print(f"✅ Row {row}: {name} → {grade} 級 ({score} 分)")
        else:
            skipped += 1
            print(f"❌ Row {row}: {name} - 更新失敗")
        
        # 每 10 筆暫停 2 秒（避免 API 限流）
        if updated % 10 == 0:
            print(f"   進度: {updated}/{total}")
            time.sleep(2)
    
    print()
    print("=" * 50)
    print("評級完成")
    print("=" * 50)
    print(f"✅ 總候選人數: {total}")
    print(f"✅ 成功更新: {updated}")
    print(f"❌ 失敗: {skipped}")
    print()

if __name__ == '__main__':
    main()
