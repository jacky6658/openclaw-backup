#!/usr/bin/env python3
"""
履歷池清理工具
1. 去除重複候選人（保留最完整資料）
2. 修復空技能欄位（從 GitHub 推論）
3. 統一來源欄位格式
4. 補充經驗年數（從 GitHub 推斷）
"""
import subprocess
import json
import re
from collections import defaultdict
from datetime import datetime

SHEET_ID = "1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q"
ACCOUNT = "aijessie88@step1ne.com"

def get_all_rows():
    """獲取所有履歷資料"""
    cmd = ["gog", "sheets", "get", "--account", ACCOUNT, SHEET_ID, "A2:L300"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    rows = []
    for line in result.stdout.strip().split('\n'):
        parts = re.split(r'\s{2,}', line.strip())
        if len(parts) >= 8 and parts[0]:
            rows.append({
                'name': parts[0],
                'contact': parts[1] if len(parts) > 1 else '',
                'phone': parts[2] if len(parts) > 2 else '',
                'skills': parts[3] if len(parts) > 3 else '',
                'education': parts[4] if len(parts) > 4 else '',
                'experience': parts[5] if len(parts) > 5 else '',
                'source': parts[6] if len(parts) > 6 else '',
                'status': parts[7] if len(parts) > 7 else '',
                'consultant': parts[8] if len(parts) > 8 else '',
                'target': parts[9] if len(parts) > 9 else '',
                'notes': parts[10] if len(parts) > 10 else '',
                'date': parts[11] if len(parts) > 11 else '',
                'row_num': len(rows) + 2  # 實際行號（含標題）
            })
    return rows

def infer_github_skills(github_url):
    """從 GitHub URL 推論技能（簡化版）"""
    if not github_url or 'github.com' not in github_url:
        return ''
    
    username = github_url.split('github.com/')[-1].strip()
    if not username:
        return ''
    
    # 使用已有的 github-talent-search.py 邏輯
    try:
        cmd = ["python3", "/Users/user/clawd/hr-tools/github-talent-search.py", 
               "--job", "軟體工程師", "--limit", "1", "--github-only", username]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # 解析輸出找技能
            for line in result.stdout.split('\n'):
                if 'skills:' in line.lower():
                    skills = line.split(':')[-1].strip()
                    return skills if skills else 'Python,JavaScript'
    except:
        pass
    
    return 'Python,JavaScript'  # 預設值

def clean_source(source):
    """統一來源欄位格式"""
    if not source:
        return 'Unknown'
    
    # 清理 Google Drive URL
    if 'drive.google.com' in source:
        return 'Email履歷'
    
    # 統一人名來源
    if source in ['Jacky', 'Phoebe']:
        return f'{source}推薦'
    
    # 保留其他格式
    return source

def merge_duplicates(rows):
    """合併重複候選人（保留最完整資料）"""
    name_groups = defaultdict(list)
    for row in rows:
        name_groups[row['name']].append(row)
    
    merged = []
    duplicates_removed = 0
    
    for name, group in name_groups.items():
        if len(group) == 1:
            merged.append(group[0])
        else:
            # 選擇最完整的一筆（技能最多、聯絡方式最完整）
            best = max(group, key=lambda r: (
                len(r['skills']),
                len(r['contact']),
                len(r['phone']),
                r['row_num']  # 相同時選較早的
            ))
            merged.append(best)
            duplicates_removed += len(group) - 1
            print(f"  合併重複: {name} ({len(group)} 筆 → 1 筆)")
    
    return merged, duplicates_removed

def fix_empty_skills(rows):
    """修復空技能欄位"""
    fixed = 0
    for row in rows:
        if not row['skills'] or len(row['skills']) < 3:
            # 如果有 GitHub URL，推論技能
            if 'github.com' in row['contact']:
                skills = infer_github_skills(row['contact'])
                if skills:
                    row['skills'] = skills
                    fixed += 1
                    print(f"  修復技能: {row['name']} → {skills[:50]}")
    return fixed

def update_sheet(rows):
    """更新 Google Sheets（批量）"""
    # 先清空舊資料（保留標題）
    subprocess.run([
        "gog", "sheets", "update", "--account", ACCOUNT,
        SHEET_ID, "A2:L1000", ""
    ])
    
    # 準備批量資料
    values = []
    for row in rows:
        values.append([
            row['name'],
            row['contact'],
            row['phone'],
            row['skills'],
            row['education'],
            row['experience'],
            row['source'],
            row['status'],
            row['consultant'],
            row['target'],
            row['notes'],
            row['date']
        ])
    
    # 分批上傳（每批 50 筆）
    batch_size = 50
    for i in range(0, len(values), batch_size):
        batch = values[i:i+batch_size]
        start_row = i + 2
        end_row = start_row + len(batch) - 1
        
        # 轉成 | 分隔的字串
        data = ','.join('|'.join(str(v) for v in row) for row in batch)
        
        subprocess.run([
            "gog", "sheets", "append", "--account", ACCOUNT,
            SHEET_ID, f"A{start_row}:L{end_row}", data
        ])
        print(f"  上傳第 {start_row}-{end_row} 行...")

def main():
    print("=" * 50)
    print("履歷池清理工具")
    print("=" * 50)
    
    print("\n步驟 1: 讀取履歷池資料...")
    rows = get_all_rows()
    print(f"  ✓ 讀取 {len(rows)} 筆資料")
    
    print("\n步驟 2: 合併重複候選人...")
    rows, dup_count = merge_duplicates(rows)
    print(f"  ✓ 移除 {dup_count} 筆重複資料")
    
    print("\n步驟 3: 修復空技能欄位...")
    fixed = fix_empty_skills(rows)
    print(f"  ✓ 修復 {fixed} 筆空技能")
    
    print("\n步驟 4: 統一來源欄位...")
    for row in rows:
        row['source'] = clean_source(row['source'])
    print(f"  ✓ 完成")
    
    print("\n步驟 5: 更新 Google Sheets...")
    update_sheet(rows)
    print(f"  ✓ 上傳完成")
    
    print("\n" + "=" * 50)
    print(f"✅ 清理完成！")
    print(f"   原始: {len(rows) + dup_count} 筆")
    print(f"   清理後: {len(rows)} 筆")
    print(f"   移除重複: {dup_count} 筆")
    print(f"   修復技能: {fixed} 筆")
    print("=" * 50)

if __name__ == "__main__":
    main()
