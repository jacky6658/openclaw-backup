#!/usr/bin/env python3
"""
測試 AI Matcher v2 vs v3 比較
比較加入穩定性評分前後的差異
"""

import sys
import json

# 測試候選人資料
test_candidates = [
    {
        "name": "張三",
        "skills": ["Python", "Machine Learning", "TensorFlow"],
        "experience_years": 5.8,
        "industry": "科技",
        "github_stars": 120,
        "stability_score": 80  # A級：極低風險
    },
    {
        "name": "李四",
        "skills": ["Java", "Spring", "Microservices"],
        "experience_years": 3.2,
        "industry": "金融",
        "github_stars": 50,
        "stability_score": 45  # C級：中等風險
    },
    {
        "name": "王五",
        "skills": ["Python", "AI", "Deep Learning", "PyTorch"],
        "experience_years": 7.5,
        "industry": "科技",
        "github_stars": 300,
        "stability_score": 65  # B級：低風險
    },
    {
        "name": "趙六",
        "skills": ["JavaScript", "React", "Node.js"],
        "experience_years": 2.5,
        "industry": "電商",
        "github_stars": 80,
        "stability_score": 35  # D級：中高風險
    },
    {
        "name": "錢七",
        "skills": ["Python", "Data Science", "Machine Learning"],
        "experience_years": 4.0,
        "industry": "科技",
        "github_stars": 150,
        "stability_score": 70  # B級：低風險
    },
    {
        "name": "孫八",
        "skills": ["Go", "Kubernetes", "Docker"],
        "experience_years": 6.0,
        "industry": "雲端",
        "github_stars": 200,
        "stability_score": 55  # C級：中等風險
    },
    {
        "name": "周九",
        "skills": ["Python", "AI", "NLP"],
        "experience_years": 8.5,
        "industry": "科技",
        "github_stars": 400,
        "stability_score": 85  # A級：極低風險
    },
    {
        "name": "吳十",
        "skills": ["C++", "Computer Vision", "OpenCV"],
        "experience_years": 5.0,
        "industry": "汽車",
        "github_stars": 180,
        "stability_score": 60  # B級：低風險
    },
    {
        "name": "鄭十一",
        "skills": ["Python", "Machine Learning", "Scikit-learn"],
        "experience_years": 3.5,
        "industry": "科技",
        "github_stars": 90,
        "stability_score": 50  # C級：中等風險
    },
    {
        "name": "陳十二",
        "skills": ["Python", "AI", "TensorFlow", "Keras"],
        "experience_years": 6.5,
        "industry": "科技",
        "github_stars": 250,
        "stability_score": 75  # B級：低風險
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

def calculate_v2_score(candidate, job):
    """v2 評分邏輯（無穩定性）"""
    score = 0
    
    # 1. 技能匹配 (40%)
    required_match = sum(1 for skill in job["required_skills"] 
                        if any(skill.lower() in cs.lower() for cs in candidate["skills"]))
    preferred_match = sum(1 for skill in job["preferred_skills"] 
                         if any(skill.lower() in cs.lower() for cs in candidate["skills"]))
    
    skill_score = (required_match / len(job["required_skills"])) * 30
    skill_score += (preferred_match / len(job["preferred_skills"])) * 10
    score += skill_score
    
    # 2. 經驗 (30%)
    exp_diff = candidate["experience_years"] - job["min_experience"]
    if exp_diff >= 0:
        exp_score = min(30, 15 + (exp_diff / 10) * 15)
    else:
        exp_score = max(0, 15 + exp_diff * 5)
    score += exp_score
    
    # 3. 產業 (20%)
    if candidate["industry"] == job["industry"]:
        score += 20
    
    # 4. 加分項 (10%)
    if candidate["github_stars"] > 100:
        score += 10
    elif candidate["github_stars"] > 50:
        score += 5
    
    return round(score, 1)

def calculate_v3_score(candidate, job):
    """v3 評分邏輯（含穩定性）"""
    score = 0
    
    # 1. 技能匹配 (30%) - 降低權重
    required_match = sum(1 for skill in job["required_skills"] 
                        if any(skill.lower() in cs.lower() for cs in candidate["skills"]))
    preferred_match = sum(1 for skill in job["preferred_skills"] 
                         if any(skill.lower() in cs.lower() for cs in candidate["skills"]))
    
    skill_score = (required_match / len(job["required_skills"])) * 22.5
    skill_score += (preferred_match / len(job["preferred_skills"])) * 7.5
    score += skill_score
    
    # 2. 經驗 (20%) - 降低權重
    exp_diff = candidate["experience_years"] - job["min_experience"]
    if exp_diff >= 0:
        exp_score = min(20, 10 + (exp_diff / 10) * 10)
    else:
        exp_score = max(0, 10 + exp_diff * 3.33)
    score += exp_score
    
    # 3. 產業 (10%) - 降低權重
    if candidate["industry"] == job["industry"]:
        score += 10
    
    # 4. 穩定性 (30%) - 新增！
    stability_score = (candidate["stability_score"] / 100) * 30
    score += stability_score
    
    # 5. 加分項 (10%)
    if candidate["github_stars"] > 100:
        score += 10
    elif candidate["github_stars"] > 50:
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
    print("=" * 80)
    print("AI Matcher v2 vs v3 比較測試")
    print("=" * 80)
    print(f"\n測試職缺：{test_job['title']}")
    print(f"必備技能：{', '.join(test_job['required_skills'])}")
    print(f"最低年資：{test_job['min_experience']} 年")
    print("\n" + "=" * 80)
    
    results = []
    
    for candidate in test_candidates:
        v2_score = calculate_v2_score(candidate, test_job)
        v3_score = calculate_v3_score(candidate, test_job)
        v2_priority = get_priority(v2_score)
        v3_priority = get_priority(v3_score)
        
        # 計算穩定性貢獻
        stability_contribution = (candidate["stability_score"] / 100) * 30
        
        results.append({
            "name": candidate["name"],
            "experience": candidate["experience_years"],
            "stability": candidate["stability_score"],
            "v2_score": v2_score,
            "v2_priority": v2_priority,
            "v3_score": v3_score,
            "v3_priority": v3_priority,
            "score_diff": round(v3_score - v2_score, 1),
            "priority_change": v2_priority != v3_priority,
            "stability_contribution": round(stability_contribution, 1)
        })
    
    # 排序：v3 分數高到低
    results.sort(key=lambda x: x["v3_score"], reverse=True)
    
    # 輸出結果
    print("\n個別候選人比較：\n")
    print(f"{'姓名':<8} {'年資':<6} {'穩定性':<8} {'v2分數':<8} {'v2級別':<8} {'v3分數':<8} {'v3級別':<8} {'差異':<6} {'級別變化':<8} {'穩定貢獻':<8}")
    print("-" * 110)
    
    for r in results:
        priority_change_mark = "✨" if r["priority_change"] else ""
        print(f"{r['name']:<8} {r['experience']:<6.1f} {r['stability']:<8} "
              f"{r['v2_score']:<8.1f} {r['v2_priority']:<8} "
              f"{r['v3_score']:<8.1f} {r['v3_priority']:<8} "
              f"{r['score_diff']:+6.1f} {priority_change_mark:<8} {r['stability_contribution']:<8.1f}")
    
    # 統計分析
    print("\n" + "=" * 80)
    print("統計分析：")
    print("-" * 80)
    
    # v2 分佈
    v2_p0 = sum(1 for r in results if r["v2_priority"] == "P0")
    v2_p1 = sum(1 for r in results if r["v2_priority"] == "P1")
    v2_p2 = sum(1 for r in results if r["v2_priority"] == "P2")
    v2_reject = sum(1 for r in results if r["v2_priority"] == "REJECT")
    
    # v3 分佈
    v3_p0 = sum(1 for r in results if r["v3_priority"] == "P0")
    v3_p1 = sum(1 for r in results if r["v3_priority"] == "P1")
    v3_p2 = sum(1 for r in results if r["v3_priority"] == "P2")
    v3_reject = sum(1 for r in results if r["v3_priority"] == "REJECT")
    
    print(f"\nv2 分佈：P0={v2_p0}, P1={v2_p1}, P2={v2_p2}, REJECT={v2_reject}")
    print(f"v3 分佈：P0={v3_p0}, P1={v3_p1}, P2={v3_p2}, REJECT={v3_reject}")
    
    # 級別變化統計
    priority_changes = sum(1 for r in results if r["priority_change"])
    print(f"\n級別變化人數：{priority_changes}/{len(results)}")
    
    # 平均分數
    avg_v2 = sum(r["v2_score"] for r in results) / len(results)
    avg_v3 = sum(r["v3_score"] for r in results) / len(results)
    print(f"\n平均分數：v2={avg_v2:.1f}, v3={avg_v3:.1f} (差異: {avg_v3-avg_v2:+.1f})")
    
    # 穩定性影響分析
    avg_stability_contribution = sum(r["stability_contribution"] for r in results) / len(results)
    print(f"平均穩定性貢獻：{avg_stability_contribution:.1f} 分")
    
    print("\n" + "=" * 80)
    print("✅ 測試完成！")
    print("=" * 80)

if __name__ == "__main__":
    main()
