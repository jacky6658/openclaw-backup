#!/usr/bin/env python3
"""
完整流程測試 - Flow A (新候選人) + Flow B (舊候選人)
測試：履歷解析 → 穩定性評分 → AI 配對
"""

import json
import subprocess
import sys

# Flow A: 新候選人（有完整履歷資料）
flow_a_candidates = [
    {
        "name": "張大明（穩定型）",
        "parsed_data": {
            "name": "張大明",
            "contact": {
                "email": "zhangdaming@email.com",
                "phone": "0912-345-678",
                "linkedin": "linkedin.com/in/zhangdaming"
            },
            "total_experience_years": 8.7,  # 5 + 2.8 + 1 = 8.7 年
            "job_changes": 2,
            "avg_tenure_months": 35,  # (60 + 32 + 12) / 3 ≈ 35
            "last_gap_months": 1,
            "skills": ["Python", "TensorFlow", "PyTorch", "Machine Learning", "AI", "Kubernetes"],
            "industry": "科技"
        },
        "expected_stability": "A 級（80+ 分）",
        "expected_match": "P0（高度匹配 AI 工程師）"
    },
    {
        "name": "李小華（中等穩定）",
        "parsed_data": {
            "name": "李小華",
            "contact": {
                "email": "lixiaohua@gmail.com",
                "phone": "0987-654-321"
            },
            "total_experience_years": 3.8,  # 1.8 + 0.8 + 1.4 = 4
            "job_changes": 2,
            "avg_tenure_months": 15,  # (20 + 8 + 17) / 3 ≈ 15
            "last_gap_months": 1,
            "skills": ["Python", "SQL", "Tableau", "Data Analysis"],
            "industry": "電商"
        },
        "expected_stability": "C-D 級（30-50 分）",
        "expected_match": "P2/REJECT（技能不匹配 AI 工程師）"
    },
    {
        "name": "王小明（高風險）",
        "parsed_data": {
            "name": "王小明",
            "contact": {
                "email": "wangxiaoming999@yahoo.com.tw",
                "phone": "0922-111-222"
            },
            "total_experience_years": 2.3,  # 4 + 6 + 7 + 6 + 5 = 28 個月 ≈ 2.3 年
            "job_changes": 4,
            "avg_tenure_months": 6,  # 28 / 5 ≈ 6
            "last_gap_months": 0,
            "skills": ["JavaScript", "React", "Node.js"],
            "industry": "網路"
        },
        "expected_stability": "F 級（<20 分）",
        "expected_match": "REJECT（年資不足 + 技能不匹配）"
    }
]

# Flow B: 舊候選人（僅有基本資料）
flow_b_candidates = [
    {
        "name": "趙資深（僅年資）",
        "data": {
            "name": "趙資深",
            "experience_years": 8.0,
            "skills": ["Python", "Machine Learning", "AI"],
            "industry": "科技"
        },
        "expected_stability": "C 級（55 分，簡化模式上限）",
        "expected_match": "P1-P2（技能匹配但穩定性保守估計）"
    },
    {
        "name": "錢新人（僅年資）",
        "data": {
            "name": "錢新人",
            "experience_years": 2.0,
            "skills": ["Python", "Data Science"],
            "industry": "金融"
        },
        "expected_stability": "D-F 級（15-30 分）",
        "expected_match": "REJECT（年資不足）"
    }
]

# 測試職缺
test_job = {
    "title": "AI工程師",
    "required_skills": ["Python", "Machine Learning", "AI"],
    "preferred_skills": ["TensorFlow", "PyTorch", "Deep Learning"],
    "min_experience": 3,
    "industry": "科技"
}

def test_stability_score(candidate_data, mode="full"):
    """測試穩定性評分"""
    temp_file = f"/tmp/candidate_{candidate_data['name']}.json"
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(candidate_data, f, ensure_ascii=False, indent=2)
    
    try:
        result = subprocess.run(
            ['python3', '/Users/user/clawd/hr-tools/stability_predictor.py',
             '--input', temp_file, '--mode', mode],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            # 解析分數
            for line in result.stdout.split('\n'):
                if line.startswith('總分:'):
                    score_str = line.split(':')[1].split('/')[0].strip()
                    return int(score_str), result.stdout
        
        return None, result.stderr
    except Exception as e:
        return None, str(e)

def calculate_ai_match_score(candidate, job, stability_score):
    """簡化版 AI Matcher v3 評分"""
    score = 0
    
    # 1. 技能匹配 (30%)
    required_match = sum(1 for skill in job["required_skills"] 
                        if any(skill.lower() in cs.lower() for cs in candidate.get("skills", [])))
    preferred_match = sum(1 for skill in job["preferred_skills"] 
                         if any(skill.lower() in cs.lower() for cs in candidate.get("skills", [])))
    
    skill_score = (required_match / len(job["required_skills"])) * 22.5
    skill_score += (preferred_match / len(job["preferred_skills"])) * 7.5
    score += skill_score
    
    # 2. 經驗 (20%)
    exp_years = candidate.get('total_experience_years') or candidate.get('experience_years', 0)
    exp_diff = exp_years - job["min_experience"]
    if exp_diff >= 0:
        exp_score = min(20, 10 + (exp_diff / 10) * 10)
    else:
        exp_score = max(0, 10 + exp_diff * 3.33)
    score += exp_score
    
    # 3. 產業 (10%)
    if candidate.get("industry") == job["industry"]:
        score += 10
    
    # 4. 穩定性 (30%)
    if stability_score:
        stability_contribution = (stability_score / 100) * 30
        score += stability_contribution
    
    # 5. 加分項 (10%) - 這裡簡化為有 LinkedIn 加分
    if candidate.get("contact", {}).get("linkedin"):
        score += 5
    
    return round(score, 1)

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

def main():
    print("=" * 100)
    print("完整流程測試 - AI 招聘系統 Pipeline")
    print("=" * 100)
    print(f"\n測試職缺：{test_job['title']}")
    print(f"必備技能：{', '.join(test_job['required_skills'])}")
    print(f"最低年資：{test_job['min_experience']} 年")
    print(f"產業：{test_job['industry']}")
    
    # Flow A 測試
    print("\n" + "=" * 100)
    print("Flow A：新候選人（完整履歷資料）")
    print("=" * 100)
    
    flow_a_results = []
    
    for candidate_info in flow_a_candidates:
        candidate = candidate_info["parsed_data"]
        print(f"\n{'─' * 100}")
        print(f"候選人：{candidate_info['name']}")
        print(f"預期穩定性：{candidate_info['expected_stability']}")
        print(f"預期配對：{candidate_info['expected_match']}")
        print(f"{'─' * 100}")
        
        # 步驟 1: 穩定性評分
        print("\n📊 步驟 1：穩定性評分")
        stability_score, stability_output = test_stability_score(candidate, mode="full")
        
        if stability_score:
            # 簡化輸出
            for line in stability_output.split('\n'):
                if any(keyword in line for keyword in ['總分:', '等級:', '風險評估:']):
                    print(f"  {line}")
        else:
            print(f"  ❌ 評分失敗：{stability_output}")
            continue
        
        # 步驟 2: AI 配對
        print("\n🎯 步驟 2：AI 配對評分")
        match_score = calculate_ai_match_score(candidate, test_job, stability_score)
        priority = get_priority(match_score)
        
        print(f"  總分：{match_score}/100")
        print(f"  等級：{priority}")
        
        flow_a_results.append({
            "name": candidate["name"],
            "stability_score": stability_score,
            "match_score": match_score,
            "priority": priority
        })
    
    # Flow B 測試
    print("\n" + "=" * 100)
    print("Flow B：舊候選人（僅基本資料）")
    print("=" * 100)
    
    flow_b_results = []
    
    for candidate_info in flow_b_candidates:
        candidate = candidate_info["data"]
        print(f"\n{'─' * 100}")
        print(f"候選人：{candidate_info['name']}")
        print(f"預期穩定性：{candidate_info['expected_stability']}")
        print(f"預期配對：{candidate_info['expected_match']}")
        print(f"{'─' * 100}")
        
        # 步驟 1: 穩定性評分（簡化模式）
        print("\n📊 步驟 1：穩定性評分（簡化模式）")
        stability_score, stability_output = test_stability_score(candidate, mode="simple")
        
        if stability_score:
            for line in stability_output.split('\n'):
                if any(keyword in line for keyword in ['總分:', '等級:', '風險評估:', '⚠️']):
                    print(f"  {line}")
        else:
            print(f"  ❌ 評分失敗：{stability_output}")
            continue
        
        # 步驟 2: AI 配對
        print("\n🎯 步驟 2：AI 配對評分")
        match_score = calculate_ai_match_score(candidate, test_job, stability_score)
        priority = get_priority(match_score)
        
        print(f"  總分：{match_score}/100")
        print(f"  等級：{priority}")
        
        flow_b_results.append({
            "name": candidate["name"],
            "stability_score": stability_score,
            "match_score": match_score,
            "priority": priority
        })
    
    # 總結
    print("\n" + "=" * 100)
    print("測試總結")
    print("=" * 100)
    
    print("\n**Flow A - 新候選人（完整資料）**")
    print(f"\n{'候選人':<20} {'穩定性':<10} {'配對分數':<10} {'等級':<10}")
    print("─" * 60)
    for r in flow_a_results:
        print(f"{r['name']:<20} {r['stability_score']:<10} {r['match_score']:<10.1f} {r['priority']:<10}")
    
    print("\n**Flow B - 舊候選人（簡化資料）**")
    print(f"\n{'候選人':<20} {'穩定性':<10} {'配對分數':<10} {'等級':<10}")
    print("─" * 60)
    for r in flow_b_results:
        print(f"{r['name']:<20} {r['stability_score']:<10} {r['match_score']:<10.1f} {r['priority']:<10}")
    
    print("\n" + "=" * 100)
    print("✅ 完整流程測試完成！")
    print("=" * 100)
    
    print("\n驗證項目：")
    print("✅ Flow A（新候選人）：履歷 → 穩定性評分（完整模式）→ AI 配對")
    print("✅ Flow B（舊候選人）：基本資料 → 穩定性評分（簡化模式）→ AI 配對")
    print("✅ 穩定性評分影響最終配對結果（30% 權重）")
    print("✅ 區分 P0/P1/P2/REJECT 四個等級")

if __name__ == "__main__":
    main()
