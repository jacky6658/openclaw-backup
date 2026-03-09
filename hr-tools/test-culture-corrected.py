#!/usr/bin/env python3
"""
測試文化適配 - 修正欄位名稱（使用正確的 culture_matcher.py 期望格式）
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stability_predictor import StabilityPredictor
from stability_predictor_v2 import StabilityPredictorV2

# 測試公司
test_company = {
    "name": "快節奏AI科技公司",
    "work_pace": "快速迭代",
    "decision_style": "扁平化",
    "team_atmosphere": "協作導向",
    "overtime_culture": "經常加班",
    "communication_style": "直接坦率",
    "growth_path": "快速晉升",
    "failure_tolerance": "高度容忍",
    "work_life_balance": "工作優先",
    "core_values": ["創新突破", "快速執行", "技術領先"]
}

# 測試候選人（修正欄位名稱）
test_candidates = [
    {
        "name": "張三（完美適配）",
        "career": {
            "total_experience_years": 5.0,
            "job_changes": 1,
            "avg_tenure_months": 30,
            "last_gap_months": 24  # ✅ 目前在職 2 年
        },
        "culture": {
            "work_pace_preference": "快速變化",
            "decision_preference": "高度自主",
            "team_atmosphere_preference": "協作型",  # ✅ 修正欄位名
            "overtime_attitude": "可以接受",  # ✅ 修正欄位名
            "communication_style": "直接坦率",
            "career_goals": ["快速晉升", "技術專家"],  # ✅ 修正為 list
            "failure_attitude": "從錯誤中學習",  # ✅ 修正欄位名
            "work_priorities": [  # ✅ 修正為 list of dict
                {"value": "Work-Life Balance", "rank": 8},  # 最不重視（適配「工作優先」公司）
                {"value": "職涯發展", "rank": 1},
                {"value": "工作挑戰", "rank": 2}
            ],
            "motivations": ["成就感", "成長機會"]
        },
        "skills": ["Python", "Machine Learning", "AI"],
        "industry": "科技"
    },
    {
        "name": "李穩定（文化衝突）",
        "career": {
            "total_experience_years": 5.0,
            "job_changes": 1,
            "avg_tenure_months": 30,
            "last_gap_months": 24  # ✅ 職涯完全相同
        },
        "culture": {
            "work_pace_preference": "穩定可預測",  # ❌ 衝突
            "decision_preference": "聽從指導",  # ❌ 衝突
            "team_atmosphere_preference": "協作型",  # ✅ 匹配
            "overtime_attitude": "完全不接受",  # ❌ 極高衝突
            "communication_style": "委婉含蓄",  # ❌ 衝突
            "career_goals": ["穩定發展", "平衡生活"],  # ❌ 衝突
            "failure_attitude": "謹慎避免犯錯",  # ❌ 衝突
            "work_priorities": [  # ❌ 重視 WLB（衝突）
                {"value": "Work-Life Balance", "rank": 1},  # 最重視（衝突「工作優先」）
                {"value": "工作穩定", "rank": 2},
                {"value": "薪資福利", "rank": 3}
            ],
            "motivations": ["工作生活平衡", "穩定收入"]  # ❌ 衝突
        },
        "skills": ["Python", "Machine Learning", "AI"],
        "industry": "科技"
    }
]

# 測試職缺
test_job = {
    "title": "AI工程師",
    "required_skills": ["Python", "Machine Learning", "AI"],
    "preferred_skills": ["TensorFlow", "PyTorch"],
    "min_experience": 3,
    "industry": "科技"
}

def calculate_match_score(candidate, job, stability_score, version="v3"):
    """計算配對分數"""
    score = 0
    
    # 技能 (30%)
    required_match = sum(1 for skill in job["required_skills"] 
                        if any(skill.lower() in cs.lower() for cs in candidate.get("skills", [])))
    skill_score = (required_match / len(job["required_skills"])) * 30
    score += skill_score
    
    # 經驗 (20%)
    exp_years = candidate["career"]["total_experience_years"]
    exp_diff = exp_years - job["min_experience"]
    exp_score = min(20, 10 + (exp_diff / 10) * 10) if exp_diff >= 0 else max(0, 10 + exp_diff * 3.33)
    score += exp_score
    
    # 產業 (10%)
    if candidate.get("industry") == job["industry"]:
        score += 10
    
    # 穩定性 (30%)
    stability_contribution = (stability_score / 100) * 30
    score += stability_contribution
    
    # 加分項 (10%)
    score += 5
    
    return round(score, 1)

def get_priority(score):
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
    print("🎯 AI Matcher v3 vs v4 對比測試（文化適配影響 - 修正版）")
    print("=" * 100)
    
    print(f"\n測試職缺：{test_job['title']}")
    print(f"公司：{test_company['name']}")
    print(f"公司文化：{test_company['work_pace']} / {test_company['overtime_culture']} / {test_company['work_life_balance']}")
    
    career_predictor = StabilityPredictor()
    career_culture_predictor = StabilityPredictorV2()
    
    results = []
    
    for candidate in test_candidates:
        print(f"\n{'=' * 100}")
        print(f"候選人：{candidate['name']}")
        print(f"職涯：{candidate['career']['total_experience_years']} 年 / {candidate['career']['job_changes']} 次跳槽 / 目前在職 {candidate['career']['last_gap_months']} 個月")
        print(f"文化偏好：{candidate['culture']['work_pace_preference']} / {candidate['culture']['overtime_attitude']} / WLB排名 {candidate['culture']['work_priorities'][0]['rank']}")
        print("=" * 100)
        
        # 合併候選人資料
        candidate_data = {
            **candidate['career'],
            **candidate['culture'],
            'skills': candidate['skills'],
            'industry': candidate.get('industry')
        }
        
        # v3: 僅職涯穩定
        print("\n📊 AI Matcher v3（僅職涯穩定）")
        career_result = career_predictor.predict(candidate_data, mode='full')
        career_score = career_result['score']
        v3_match_score = calculate_match_score(candidate, test_job, career_score, "v3")
        v3_priority = get_priority(v3_match_score)
        
        print(f"  職涯穩定性：{career_score}/100 ({career_result['grade']})")
        print(f"  配對總分：{v3_match_score}/100")
        print(f"  等級：{v3_priority}")
        
        # v4: 職涯 + 文化
        print("\n🎯 AI Matcher v4（職涯 + 文化適配）")
        v2_result = career_culture_predictor.predict(candidate_data, company=test_company, mode='full')
        v2_score = v2_result['total_score']
        v4_match_score = calculate_match_score(candidate, test_job, v2_score, "v4")
        v4_priority = get_priority(v4_match_score)
        
        culture_score_val = v2_result['breakdown']['culture_fit']['score']
        culture_detail = v2_result.get('culture_fit_detail', {})
        culture_level = culture_detail.get('fit_level', 'N/A')
        
        print(f"  文化適配：{culture_score_val:.1f}/100 ({culture_level})")
        print(f"  職涯穩定：{career_score}/100")
        print(f"  綜合穩定性：{v2_score:.1f}/100 ({v2_result['grade']})")
        print(f"  配對總分：{v4_match_score}/100")
        print(f"  等級：{v4_priority}")
        print(f"  保證期建議：{v2_result.get('guarantee_period_recommendation', 'N/A')}")
        
        if v2_result.get('risk_factors'):
            print(f"  ⚠️ 風險因素：{len(v2_result['risk_factors'])} 個")
            for risk in v2_result['risk_factors'][:5]:
                print(f"     • {risk}")
        
        # 文化適配詳細breakdown
        if 'culture_fit_detail' in v2_result and 'dimensions' in v2_result['culture_fit_detail']:
            print(f"\n  📊 文化適配細節：")
            dims = v2_result['culture_fit_detail']['dimensions']
            for dim_name, dim_data in list(dims.items())[:5]:  # 顯示前5個維度
                print(f"     {dim_name}: {dim_data['score']}/100")
        
        # 差異分析
        score_diff = v4_match_score - v3_match_score
        priority_changed = v3_priority != v4_priority
        
        print(f"\n📈 差異分析")
        print(f"  分數變化：{score_diff:+.1f} 分")
        if priority_changed:
            print(f"  等級變化：{v3_priority} → {v4_priority} ✨")
        else:
            print(f"  等級：維持 {v3_priority}")
        
        # 提取保證期天數
        guarantee_rec = v2_result.get('guarantee_period_recommendation', '90 天')
        guarantee_days = int(guarantee_rec.split()[0]) if guarantee_rec and guarantee_rec[0].isdigit() else 90
        
        results.append({
            'name': candidate['name'],
            'career_stability': career_score,
            'culture_fit': culture_score_val,
            'v3_score': v3_match_score,
            'v3_priority': v3_priority,
            'v4_score': v4_match_score,
            'v4_priority': v4_priority,
            'score_diff': score_diff,
            'priority_changed': priority_changed,
            'guarantee_days': guarantee_days,
            'risk_count': len(v2_result.get('risk_factors', []))
        })
    
    # 總結對比
    print("\n" + "=" * 100)
    print("📊 總結對比")
    print("=" * 100)
    
    print(f"\n{'候選人':<25} {'職涯':<8} {'文化':<8} {'v3分數':<10} {'v3級':<6} {'v4分數':<10} {'v4級':<6} {'差異':<8} {'保證期':<8} {'風險':<6}")
    print("-" * 100)
    
    for r in results:
        priority_mark = "✨" if r['priority_changed'] else ""
        print(f"{r['name']:<25} {r['career_stability']:<8} {r['culture_fit']:<8.1f} "
              f"{r['v3_score']:<10.1f} {r['v3_priority']:<6} "
              f"{r['v4_score']:<10.1f} {r['v4_priority']:<6} {r['score_diff']:+8.1f} "
              f"{r['guarantee_days']:<8} {r['risk_count']:<6} {priority_mark}")
    
    print("\n" + "=" * 100)
    print("✅ 測試完成！")
    print("=" * 100)
    
    if len(results) >= 2:
        print("\n🔍 核心發現：")
        print(f"• 兩位候選人職涯穩定度完全相同（都是 {results[0]['career_stability']} 分）")
        print(f"• 但文化適配度差異巨大（{results[0]['culture_fit']:.1f} vs {results[1]['culture_fit']:.1f}）")
        culture_diff = abs(results[0]['culture_fit'] - results[1]['culture_fit'])
        print(f"• 文化適配分數差異：{culture_diff:.1f} 分 {'✨ 達成目標' if culture_diff >= 40 else '⚠️ 需優化'}")
        print(f"• 最終配對分數差異：{abs(results[0]['score_diff'] - results[1]['score_diff']):.1f} 分")
        print(f"• 保證期差異：{results[0]['guarantee_days']} vs {results[1]['guarantee_days']} 天")
        print(f"• 風險因素：{results[0]['risk_count']} vs {results[1]['risk_count']} 個")
        print("\n💡 結論：文化適配是預測離職風險的關鍵因素！")

if __name__ == "__main__":
    main()
