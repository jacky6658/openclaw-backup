#!/usr/bin/env python3
"""
匯入 GitHub 搜尋結果到履歷池 Google Sheets
強制規則：欄位用 | 分隔，技能用逗號分隔，只更新單一儲存格
"""

import sys
import json
import subprocess
import os
from datetime import datetime

# 履歷池 Sheet ID
RESUME_POOL_SHEET_ID = "1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q"
RESUME_POOL_RANGE = "工作表1!A:T"
GOO_ACCOUNT = "aijessie88@step1ne.com"

def convert_github_to_resume_pool(candidates):
    """
    轉換 GitHub 搜尋結果為履歷池格式
    
    履歷池欄位（20 欄）：A-T
    """
    
    rows = []
    today = datetime.now().strftime("%Y-%m-%d")
    
    for candidate in candidates:
        # 準備欄位
        name = candidate.get('name', candidate.get('login', ''))
        email = ""
        phone = ""
        location = candidate.get('location', '')
        title = ""
        years = ""
        job_change = ""
        avg_tenure = ""
        recent_gap = ""
        skills = ", ".join(candidate.get('skills', []))
        education = ""
        source = "GitHub"
        work_history = ""
        resign_reason = ""
        stability_score = ""
        education_json = ""
        disc = ""
        status = "待聯繫"
        consultant = "Jacky"
        
        # 備註
        github_url = candidate.get('github_url', '')
        bio = candidate.get('bio', '')
        followers = candidate.get('followers', 0)
        remark = f"GitHub: {followers} followers | {bio[:50] if bio else '無自我介紹'} | {github_url}"
        
        # 組合成履歷池格式（用 | 分隔）
        row = f"{name}|{email}|{phone}|{location}|{title}|{years}|{job_change}|{avg_tenure}|{recent_gap}|{skills}|{education}|{source}|{work_history}|{resign_reason}|{stability_score}|{education_json}|{disc}|{status}|{consultant}|{remark}"
        
        rows.append(row)
    
    return rows


def append_to_sheet(rows, test_only=False):
    """
    批量匯入到 Google Sheets
    """
    
    if not rows:
        print("❌ 沒有要匯入的資料", file=sys.stderr)
        return False
    
    print(f"📊 準備匯入 {len(rows)} 位候選人", file=sys.stderr)
    print(f"📄 Sheet ID: {RESUME_POOL_SHEET_ID}", file=sys.stderr)
    print(f"📍 Account: {GOO_ACCOUNT}", file=sys.stderr)
    print("", file=sys.stderr)
    
    # Step 1: 測試 1 筆
    print(f"🧪 Step 1: 測試匯入第 1 筆...", file=sys.stderr)
    test_row = rows[0].split('|')
    
    try:
        # 用 --values-json 格式（安全）
        result = subprocess.run([
            'gog', 'sheets', 'append',
            RESUME_POOL_SHEET_ID,
            RESUME_POOL_RANGE,
            '--account', GOO_ACCOUNT,
            '--values-json', json.dumps([test_row], ensure_ascii=False)
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            print(f"  ❌ 測試失敗：{result.stderr}", file=sys.stderr)
            return False
        
        print(f"  ✅ 測試成功，第 1 筆已匯入", file=sys.stderr)
        
    except Exception as e:
        print(f"  ❌ 異常：{e}", file=sys.stderr)
        return False
    
    # 如果是測試模式，只做 1 筆
    if test_only:
        print("", file=sys.stderr)
        print("✅ 測試完成，已暫停批量匯入。請確認格式正確後再執行。", file=sys.stderr)
        return True
    
    # Step 2: 確認後批量匯入
    print("", file=sys.stderr)
    print(f"📋 Step 2: 批量匯入剩下 {len(rows) - 1} 筆...", file=sys.stderr)
    
    # 分批匯入（每批 20 筆）
    batch_size = 20
    for i in range(1, len(rows), batch_size):
        batch_end = min(i + batch_size, len(rows))
        batch = [row.split('|') for row in rows[i:batch_end]]
        
        print(f"  匯入第 {i}-{batch_end-1} 筆...", file=sys.stderr)
        
        try:
            result = subprocess.run([
                'gog', 'sheets', 'append',
                RESUME_POOL_SHEET_ID,
                RESUME_POOL_RANGE,
                '--account', GOO_ACCOUNT,
                '--values-json', json.dumps(batch, ensure_ascii=False)
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                print(f"    ⚠️  批次匯入異常：{result.stderr}", file=sys.stderr)
                continue
            
            print(f"    ✅ 第 {i}-{batch_end-1} 筆完成", file=sys.stderr)
        
        except Exception as e:
            print(f"    ⚠️  異常：{e}", file=sys.stderr)
            continue
    
    print("", file=sys.stderr)
    print(f"✅ 批量匯入完成！共 {len(rows)} 位候選人已匯入履歷池", file=sys.stderr)
    
    return True


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='匯入 GitHub 搜尋結果到履歷池')
    parser.add_argument('--json-file', required=True, help='GitHub 搜尋結果 JSON 檔案')
    parser.add_argument('--test-only', action='store_true', help='只測試 1 筆，不批量匯入')
    
    args = parser.parse_args()
    
    # 讀取 JSON 檔案
    if not os.path.exists(args.json_file):
        print(f"❌ 檔案不存在：{args.json_file}", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(args.json_file, 'r', encoding='utf-8') as f:
            candidates = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析失敗：{e}", file=sys.stderr)
        sys.exit(1)
    
    if not candidates:
        print("❌ JSON 檔案中沒有候選人", file=sys.stderr)
        sys.exit(1)
    
    print(f"📚 讀取 {len(candidates)} 位候選人", file=sys.stderr)
    print("", file=sys.stderr)
    
    # 轉換格式
    print("🔄 轉換為履歷池格式...", file=sys.stderr)
    rows = convert_github_to_resume_pool(candidates)
    print(f"✅ 轉換完成", file=sys.stderr)
    print("", file=sys.stderr)
    
    # 預覽第 1 筆
    print("📋 預覽第 1 筆資料：", file=sys.stderr)
    fields = ["姓名", "Email", "電話", "地點", "職位", "年資", "轉職", "平均任職", "gap", "技能", 
              "學歷", "來源", "工作經歷", "離職原因", "評分", "學歷JSON", "DISC", "狀態", "顧問", "備註"]
    row_data = rows[0].split('|')
    for i, (field, value) in enumerate(zip(fields, row_data)):
        print(f"  {field}: {value[:50] if len(value) > 50 else value}", file=sys.stderr)
    print("", file=sys.stderr)
    
    # 匯入
    if not append_to_sheet(rows, test_only=args.test_only):
        sys.exit(1)


if __name__ == "__main__":
    main()
