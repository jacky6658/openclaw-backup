#!/usr/bin/env python3
"""
從履歷池搜尋候選人（關鍵字匹配）
"""

import sys
import json
import subprocess

RESUME_POOL_SHEET = "1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q"
ACCOUNT = "aijessie88@step1ne.com"

def get_resume_pool_data():
    """讀取履歷池資料"""
    cmd = f"gog sheets get {RESUME_POOL_SHEET} 'A2:L500' --account {ACCOUNT} --json"
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        return []
    
    try:
        data = json.loads(result.stdout)
        return data.get('values', [])
    except json.JSONDecodeError:
        return []

def search_candidates(keywords, limit=20):
    """搜尋候選人（關鍵字匹配）"""
    rows = get_resume_pool_data()
    
    results = []
    
    for row in rows:
        # 跳過空行
        if len(row) < 4:
            continue
        
        # 欄位對應
        name = row[0] if len(row) > 0 else ""
        contact = row[1] if len(row) > 1 else ""
        role = row[2] if len(row) > 2 else ""
        skills = row[3] if len(row) > 3 else ""
        exp = row[4] if len(row) > 4 else ""
        edu = row[5] if len(row) > 5 else ""
        file_url = row[6] if len(row) > 6 else ""
        
        # 關鍵字匹配（職稱 or 技能）
        text = f"{role} {skills}".lower()
        
        if any(kw.lower() in text for kw in keywords.split('|')):
            # 清理技能字串
            skills_list = [s.strip() for s in skills.split(',') if s.strip()]
            
            # 將經驗字串轉換成數字（簡單推斷）
            years_of_exp = 0
            exp_str = exp.strip()
            if exp_str.isdigit():
                years_of_exp = int(exp_str)
            elif '-' in exp_str:  # 如 "3-5年"
                try:
                    years_of_exp = int(exp_str.split('-')[0])
                except:
                    years_of_exp = 0
            
            # 推斷產業（根據技能和職稱）
            industry = "科技"  # 預設科技業
            if any(keyword in role.lower() + ' '.join(skills_list).lower() for keyword in ['finance', '財務', '會計']):
                industry = "金融"
            elif any(keyword in role.lower() for keyword in ['hr', '人資', '人力資源']):
                industry = "人力資源"
            
            candidate = {
                "id": name.strip(),  # 用名字當 ID
                "name": name.strip(),
                "contact": contact.strip(),
                "role": role.strip(),
                "current_role": role.strip(),  # AI matcher 期待的 key
                "skills": skills_list,
                "experience": exp.strip(),
                "years_of_experience": years_of_exp,  # AI matcher 期待的 key
                "education": edu.strip(),
                "industry": industry,  # AI matcher 期待的 key
                "file_url": file_url.strip(),
                "source": "履歷池",
                "platforms": ["履歷池"]
            }
            
            results.append(candidate)
            
            if len(results) >= limit:
                break
    
    return results

if __name__ == "__main__":
    keywords = sys.argv[1] if len(sys.argv) > 1 else ""
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    
    candidates = search_candidates(keywords, limit)
    print(json.dumps(candidates, ensure_ascii=False, indent=2))
