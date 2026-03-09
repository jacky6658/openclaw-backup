#!/usr/bin/env python3
"""
Google Form 回覆轉 JD
用途：讀取 Google Form 的回覆（存在 Google Sheets），自動生成標準化 JD
"""

import json
import sys
import argparse
from typing import Dict, List


def form_response_to_jd(response: List[str]) -> Dict:
    """
    將 Google Form 回覆轉換為結構化 JD
    
    Args:
        response: Form 回覆（12 個欄位）
        [職位名稱, 解決問題, 團隊資訊, 必備技能1, 必備技能2, 必備技能3, 
         加分技能, 年資, 學歷, 薪資, 地點+遠端, 加班, 團隊氛圍, 到職時間]
    
    Returns:
        結構化 JD 字典
    """
    
    # 假設 response 欄位順序（與問卷順序一致）
    jd = {
        "job_title": response[0] if len(response) > 0 else "",
        "purpose": response[1] if len(response) > 1 else "",
        "team_info": response[2] if len(response) > 2 else "",
        "required_skills": [
            response[3] if len(response) > 3 else "",
            response[4] if len(response) > 4 else "",
            response[5] if len(response) > 5 else ""
        ],
        "preferred_skills": response[6].split(',') if len(response) > 6 and response[6] else [],
        "experience_years": response[7] if len(response) > 7 else "",
        "education": response[8] if len(response) > 8 else "",
        "salary_range": response[9] if len(response) > 9 else "",
        "location_remote": response[10] if len(response) > 10 else "",
        "overtime": response[11] if len(response) > 11 else "",
        "team_culture": response[12] if len(response) > 12 else "",
        "onboard_urgency": response[13] if len(response) > 13 else ""
    }
    
    # 清理空白技能
    jd["required_skills"] = [s.strip() for s in jd["required_skills"] if s.strip()]
    jd["preferred_skills"] = [s.strip() for s in jd["preferred_skills"] if s.strip()]
    
    return jd


def generate_jd_text(jd: Dict) -> str:
    """生成標準化 JD 文字"""
    
    template = f"""# {jd['job_title']}

## 職位目標
{jd['purpose']}

## 團隊資訊
{jd['team_info']}

## 職位要求

### 必備條件
- 技能：{', '.join(jd['required_skills'])}
- 年資：{jd['experience_years']}
- 學歷：{jd['education']}

### 加分條件
{chr(10).join(['- ' + s for s in jd['preferred_skills']]) if jd['preferred_skills'] else '無'}

## 工作條件
- 薪資：{jd['salary_range']}
- 地點與遠端：{jd['location_remote']}
- 加班頻率：{jd['overtime']}

## 團隊文化
{jd['team_culture']}

## 到職時間
{jd['onboard_urgency']}

---
*此 JD 由需求問卷自動生成*
"""
    
    return template


def format_for_google_sheets(jd: Dict) -> Dict:
    """格式化為 Google Sheets 職缺管理表格式"""
    
    # 解析年資要求
    experience_years = 0
    if '0-1' in jd['experience_years']:
        experience_years = 0
    elif '1-3' in jd['experience_years']:
        experience_years = 1
    elif '3-5' in jd['experience_years']:
        experience_years = 3
    elif '5+' in jd['experience_years']:
        experience_years = 5
    
    # 解析地點
    location = jd['location_remote'].split('遠端')[0].strip() if '遠端' in jd['location_remote'] else jd['location_remote']
    
    return {
        '職位名稱': jd['job_title'],
        '部門': '',  # 從 team_info 提取（如果有）
        '招募人數': 1,
        '薪資範圍': jd['salary_range'],
        '必備技能': ', '.join(jd['required_skills']),
        '年資要求': experience_years,
        '學歷要求': jd['education'],
        '工作地點': location,
        '狀態': '招募中',
        '負責顧問': '',  # 需手動填寫
        '客戶公司': '',  # 需手動填寫
        '備註': f"團隊：{jd['team_info'][:50]}..."
    }


def main():
    parser = argparse.ArgumentParser(description='Google Form 回覆轉 JD')
    parser.add_argument('--sheet-id', help='Google Form 回覆 Sheet ID')
    parser.add_argument('--account', default='aijessie88@step1ne.com', help='Google 帳號')
    parser.add_argument('--output', '-o', help='輸出檔案路徑')
    parser.add_argument('--format', choices=['text', 'json', 'sheets'], default='text',
                       help='輸出格式')
    
    # 測試模式：直接輸入回覆
    parser.add_argument('--test', nargs='+', help='測試模式：直接輸入回覆')
    
    args = parser.parse_args()
    
    try:
        if args.test:
            # 測試模式
            response = args.test
        elif args.sheet_id:
            # 從 Google Sheets 讀取最新回覆
            import subprocess
            cmd = [
                'gog', 'sheets', 'get',
                '--account', args.account,
                args.sheet_id,
                'A2:N2'  # 假設第 2 行是最新回覆（第 1 行是標題）
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"讀取 Google Sheets 失敗: {result.stderr}")
            
            # 解析回覆（tab 分隔）
            response = result.stdout.strip().split('\t')
        else:
            print("❌ 請提供 --sheet-id 或 --test 參數", file=sys.stderr)
            sys.exit(1)
        
        print(f"📝 處理問卷回覆...")
        
        # 轉換為結構化 JD
        jd = form_response_to_jd(response)
        
        # 根據格式輸出
        if args.format == 'text':
            output = generate_jd_text(jd)
        elif args.format == 'json':
            output = json.dumps(jd, ensure_ascii=False, indent=2)
        elif args.format == 'sheets':
            output = json.dumps(format_for_google_sheets(jd), ensure_ascii=False, indent=2)
        
        # 輸出結果
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"✅ 已儲存至: {args.output}")
        else:
            print("\n✅ 生成的 JD:")
            print(output)
        
        print(f"\n📊 統計:")
        print(f"  職位: {jd['job_title']}")
        print(f"  必備技能: {len(jd['required_skills'])} 項")
        print(f"  加分技能: {len(jd['preferred_skills'])} 項")
        
    except Exception as e:
        print(f"❌ 錯誤: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
