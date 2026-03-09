#!/usr/bin/env python3
"""
批量履歷匹配腳本
用途：將多份履歷與 JD 進行批量匹配分析
"""

import json
import os
import sys
from datetime import datetime

# 匹配度門檻
THRESHOLD_HIGH = 90    # 高匹配：建議直接推
THRESHOLD_MID = 70     # 中匹配：需顧問確認
THRESHOLD_LOW = 70     # 低於此值：放履歷池

def extract_skills(text):
    """從文本中提取技能關鍵字"""
    skills = []
    
    # 程式語言
    langs = ['Python', 'Java', 'JavaScript', 'TypeScript', 'Go', 'Golang', 
             'C++', 'C#', 'Ruby', 'PHP', 'Rust', 'Kotlin', 'Swift', 'Scala',
             'Node.js', 'NodeJS']
    
    # 框架
    frameworks = ['React', 'Vue', 'Angular', 'Express', 'FastAPI', 'Django',
                  'Flask', 'Spring', 'SpringBoot', 'Laravel', 'Rails', 'Gin',
                  'Next.js', 'Nuxt.js', 'NestJS']
    
    # 資料庫
    databases = ['MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch',
                 'Cassandra', 'DynamoDB', 'SQL Server', 'Oracle', 'SQLite']
    
    # 雲服務
    cloud = ['AWS', 'GCP', 'Azure', 'Alibaba Cloud', 'EC2', 'S3', 'RDS',
             'Lambda', 'CloudFront', 'EKS', 'ECS']
    
    # DevOps
    devops = ['Docker', 'Kubernetes', 'K8s', 'Jenkins', 'GitLab CI', 
              'GitHub Actions', 'Terraform', 'Ansible', 'Prometheus', 'Grafana']
    
    # 其他
    others = ['REST', 'RESTful', 'GraphQL', 'gRPC', 'Microservices', '微服務',
              'Agile', 'Scrum', 'TDD', 'CI/CD', 'Linux', 'Git']
    
    all_skills = langs + frameworks + databases + cloud + devops + others
    
    text_upper = text.upper()
    for skill in all_skills:
        if skill.upper() in text_upper:
            skills.append(skill)
    
    return list(set(skills))

def extract_experience_years(text):
    """從文本中提取工作年資"""
    import re
    
    # 尋找 "X年" 或 "X years" 模式
    patterns = [
        r'(\d+)\s*[+]?\s*年',
        r'(\d+)\s*[+]?\s*years?',
        r'經驗\s*[:：]?\s*(\d+)',
    ]
    
    max_years = 0
    for pattern in patterns:
        matches = re.findall(pattern, text, re.I)
        for match in matches:
            years = int(match)
            if years < 50:  # 合理範圍
                max_years = max(max_years, years)
    
    return max_years

def calculate_match_score(resume_skills, jd_skills, resume_exp, jd_exp):
    """計算匹配分數"""
    score = 0
    match_items = []
    gap_items = []
    
    # 技能匹配 (70% 權重)
    if jd_skills:
        matched_skills = set(s.upper() for s in resume_skills) & set(s.upper() for s in jd_skills)
        skill_ratio = len(matched_skills) / len(jd_skills)
        score += skill_ratio * 70
        
        for skill in jd_skills:
            if skill.upper() in [s.upper() for s in resume_skills]:
                match_items.append(f"{skill} ✓")
            else:
                gap_items.append(f"{skill}（缺少）")
    else:
        score += 35  # 若 JD 沒有明確技能需求，給基礎分
    
    # 經驗匹配 (30% 權重)
    if jd_exp > 0:
        if resume_exp >= jd_exp:
            score += 30
            match_items.append(f"{resume_exp}年經驗 ✓")
        elif resume_exp >= jd_exp - 1:
            score += 20
            gap_items.append(f"經驗略少（需{jd_exp}年，有{resume_exp}年）")
        else:
            score += 10
            gap_items.append(f"經驗不足（需{jd_exp}年，有{resume_exp}年）")
    else:
        score += 15  # 若 JD 沒有明確經驗需求
    
    return int(score), match_items, gap_items

def match_resume_to_jd(resume_text, jd_text):
    """單份履歷與 JD 匹配"""
    # 提取技能
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)
    
    # 提取年資
    resume_exp = extract_experience_years(resume_text)
    jd_exp = extract_experience_years(jd_text)
    
    # 計算匹配度
    score, match_items, gap_items = calculate_match_score(
        resume_skills, jd_skills, resume_exp, jd_exp
    )
    
    # 判斷狀態
    if score >= THRESHOLD_HIGH:
        status = "🟢 高匹配 - 建議直接推"
    elif score >= THRESHOLD_MID:
        status = "🟡 中匹配 - 需顧問確認"
    else:
        status = "⚪ 低匹配 - 放履歷池"
    
    return {
        'score': score,
        'status': status,
        'resume_skills': resume_skills,
        'jd_skills': jd_skills,
        'resume_exp': resume_exp,
        'jd_exp': jd_exp,
        'match_items': match_items,
        'gap_items': gap_items
    }

def batch_match(resumes, jd_text):
    """批量匹配多份履歷"""
    results = []
    
    for i, resume in enumerate(resumes):
        result = match_resume_to_jd(resume['text'], jd_text)
        result['id'] = resume.get('id', f'Resume-{i+1}')
        result['name'] = resume.get('name', f'候選人 {i+1}')
        results.append(result)
    
    # 按分數排序
    results.sort(key=lambda x: x['score'], reverse=True)
    
    return results

def main():
    """主函數 - 範例使用"""
    
    # 範例 JD
    jd = """
    Senior Backend Engineer
    
    Requirements:
    - 5+ years of backend development experience
    - Proficient in Node.js or Python
    - Experience with PostgreSQL and Redis
    - AWS cloud experience (EC2, RDS, S3)
    - Docker and Kubernetes experience preferred
    - Microservices architecture experience
    """
    
    # 範例履歷
    resumes = [
        {
            'id': 'BE-001',
            'name': '王小明',
            'text': '''
            Senior Software Engineer, 6 years experience
            Skills: Node.js, Python, PostgreSQL, MongoDB, Redis
            AWS (EC2, S3, Lambda), Docker, basic Kubernetes
            Experience in microservices architecture
            '''
        },
        {
            'id': 'BE-002', 
            'name': '李大華',
            'text': '''
            Software Engineer, 3 years experience
            Skills: Java, Spring Boot, MySQL
            GCP experience, Docker
            '''
        },
        {
            'id': 'BE-003',
            'name': '張小芬',
            'text': '''
            Backend Developer, 5 years experience
            Skills: Python, Django, FastAPI, PostgreSQL
            AWS (EC2, RDS), Docker, Kubernetes
            Microservices design experience
            '''
        }
    ]
    
    print("=" * 60)
    print("📊 批量履歷匹配結果")
    print("=" * 60)
    
    results = batch_match(resumes, jd)
    
    for result in results:
        print(f"\n{result['id']} - {result['name']}")
        print(f"匹配度: {result['score']}% {result['status']}")
        print(f"經驗: {result['resume_exp']}年 (JD要求: {result['jd_exp']}年)")
        print(f"符合: {', '.join(result['match_items'][:5])}")
        if result['gap_items']:
            print(f"缺口: {', '.join(result['gap_items'][:3])}")
    
    print("\n" + "=" * 60)
    
    # 分類統計
    high = [r for r in results if r['score'] >= THRESHOLD_HIGH]
    mid = [r for r in results if THRESHOLD_MID <= r['score'] < THRESHOLD_HIGH]
    low = [r for r in results if r['score'] < THRESHOLD_LOW]
    
    print(f"🟢 高匹配 (≥{THRESHOLD_HIGH}%): {len(high)} 人")
    print(f"🟡 中匹配 ({THRESHOLD_MID}-{THRESHOLD_HIGH-1}%): {len(mid)} 人")
    print(f"⚪ 低匹配 (<{THRESHOLD_LOW}%): {len(low)} 人")

if __name__ == "__main__":
    main()
