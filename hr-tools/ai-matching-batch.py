#!/usr/bin/env python3
"""
AI 配對批量處理腳本
用途：從履歷池批量配對候選人到指定職缺
"""

import sys
import json
import argparse

# 測試職缺資料（實際應從 Google Sheets 讀取）
TEST_JOB = {
    "title": "AI工程師",
    "required_skills": ["Python", "Machine Learning", "AI"],
    "preferred_skills": ["TensorFlow", "PyTorch"],
    "min_experience": 3,
    "industry": "科技"
}

# 測試候選人資料（實際應從履歷池讀取）
TEST_CANDIDATES = [
    {
        "name": "張大明",
        "skills": ["Python", "TensorFlow", "PyTorch", "Machine Learning", "AI"],
        "experience_years": 8.7,
        "industry": "科技",
        "github_stars": 120,
        "total_experience_years": 8.7,
        "job_changes": 2,
        "avg_tenure_months": 35,
        "last_gap_months": 24
    },
    {
        "name": "李小華",
        "skills": ["Python", "SQL", "Tableau"],
        "experience_years": 3.8,
        "industry": "電商",
        "total_experience_years": 3.8,
        "job_changes": 2,
        "avg_tenure_months": 15,
        "last_gap_months": 18
    },
    {
        "name": "王小明",
        "skills": ["JavaScript", "React", "Node.js"],
        "experience_years": 2.3,
        "industry": "網路",
        "total_experience_years": 2.3,
        "job_changes": 4,
        "avg_tenure_months": 6,
        "last_gap_months": 3
    }
]

def calculate_stability_score(candidate):
    """計算穩定性分數（簡化版）"""
    score = 0
    
    # 總年資（15 分）
    years = candidate.get('total_experience_years', 0)
    if years >= 5:
        score += 15
    elif years >= 3:
        score += 10
    elif years >= 1:
        score += 5
    
    # 平均任期（35 分）
    avg_months = candidate.get('avg_tenure_months', 0)
    if avg_months >= 36:
        score += 35
    elif avg_months >= 24:
        score += 25
    elif avg_months >= 12:
        score += 15
    elif avg_months >= 6:
        score += 5
    
    # 跳槽頻率（30 分）
    job_changes = candidate.get('job_changes', 0)
    years_for_calc = max(years, 1)
    freq = job_changes / years_for_calc
    
    if freq <= 0.3:
        score += 30
    elif freq <= 0.5:
        score += 20
    elif freq <= 1:
        score += 10
    
    # 最近穩定度（20 分）
    last_gap = candidate.get('last_gap_months', 0)
    if last_gap >= 24:
        score += 20
    elif last_gap >= 12:
        score += 15
    elif last_gap >= 6:
        score += 5
    
    return min(score, 100)

def calculate_match_score(candidate, job):
    """計算配對分數（AI Matcher v3）"""
    score = 0
    
    # 技能匹配（30%）
    required_match = sum(1 for skill in job["required_skills"] 
                        if any(skill.lower() in cs.lower() for cs in candidate.get("skills", [])))
    skill_score = (required_match / len(job["required_skills"])) * 30
    score += skill_score
    
    # 經驗（20%）
    exp_years = candidate.get('experience_years', 0)
    exp_diff = exp_years - job["min_experience"]
    if exp_diff >= 0:
        exp_score = min(20, 10 + (exp_diff / 10) * 10)
    else:
        exp_score = max(0, 10 + exp_diff * 3.33)
    score += exp_score
    
    # 產業（10%）
    if candidate.get("industry") == job["industry"]:
        score += 10
    
    # 穩定性（30%）
    stability = calculate_stability_score(candidate)
    stability_contribution = (stability / 100) * 30
    score += stability_contribution
    
    # 加分項（10%）
    if candidate.get("github_stars", 0) > 100:
        score += 10
    elif candidate.get("github_stars", 0) > 50:
        score += 5
    
    return round(score, 1), stability

def get_priority(score):
    """根據分數判斷優先級"""
    if score >= 80:
        return "P0"
    elif score >= 60:
        return "P1"
    elif score >= 40:
        return "P2"
    else:
        return "REJECT"

def get_stability_grade(score):
    """穩定性評級"""
    if score >= 80:
        return "A（極穩定）"
    elif score >= 70:
        return "B（穩定）"
    elif score >= 60:
        return "C（中等）"
    elif score >= 50:
        return "D（不穩定）"
    else:
        return "F（極不穩定）"

def main():
    parser = argparse.ArgumentParser(description='AI 配對批量處理')
    parser.add_argument('job_title', help='職位名稱')
    parser.add_argument('--limit', type=int, default=5, help='Top N 推薦數量')
    
    args = parser.parse_args()
    
    # 實際應從 Google Sheets 讀取
    job = TEST_JOB
    candidates = TEST_CANDIDATES
    
    # 配對所有候選人
    results = []
    for candidate in candidates:
        match_score, stability = calculate_match_score(candidate, job)
        priority = get_priority(match_score)
        
        results.append({
            'name': candidate['name'],
            'match_score': match_score,
            'stability': stability,
            'stability_grade': get_stability_grade(stability),
            'priority': priority,
            'skills': candidate.get('skills', [])
        })
    
    # 排序：分數高到低
    results.sort(key=lambda x: x['match_score'], reverse=True)
    
    # 統計
    p0_count = sum(1 for r in results if r['priority'] == 'P0')
    p1_count = sum(1 for r in results if r['priority'] == 'P1')
    p2_count = sum(1 for r in results if r['priority'] == 'P2')
    reject_count = sum(1 for r in results if r['priority'] == 'REJECT')
    
    # 輸出結果（Telegram 格式）
    output = f"""找到 {len(results)} 位候選人

📊 配對分佈：
• P0（高度匹配）：{p0_count} 位 {'✨' if p0_count > 0 else ''}
• P1（匹配）：{p1_count} 位
• P2（需確認）：{p2_count} 位
• REJECT（不適合）：{reject_count} 位

🎯 Top {min(args.limit, len(results))} 推薦：
"""
    
    for i, r in enumerate(results[:args.limit], 1):
        output += f"""
{i}. {r['name']} - {r['match_score']} 分（{r['priority']}）
   穩定性：{r['stability']}/100 ({r['stability_grade']})
   技能：{', '.join(r['skills'][:3])}
"""
    
    print(output)
    
    # 也可輸出 JSON（供程式讀取）
    if '--json' in sys.argv:
        print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
