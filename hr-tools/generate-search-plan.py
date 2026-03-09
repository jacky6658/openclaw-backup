#!/usr/bin/env python3
"""
快速生成搜尋计划（基于现有职缺数据）
"""

import json
from enum import Enum
from typing import Dict, List

class IndustryType(Enum):
    GAMING = "gaming"
    HEALTHCARE = "healthcare"
    MANUFACTURING = "manufacturing"
    INTERNET = "internet"
    LEGAL_TECH = "legal_tech"

# 现有職缺（从 Google Sheets 复制）
EXISTING_JOBS = [
    {'title': 'AI工程師', 'customer': 'AIJob內部', 'skills': ['Python', 'AI']},
    {'title': '數據分析師', 'customer': 'AIJob內部', 'skills': ['Python', 'SQL']},
    {'title': '產品經理', 'customer': 'AIJob內部', 'skills': ['產品']},
    {'title': '全端工程師', 'customer': 'AIJob內部', 'skills': ['React', 'Node.js']},
    {'title': 'HR 招募專員', 'customer': 'AIJob內部', 'skills': ['HR']},
    {'title': '會計經理', 'customer': '美德醫療', 'skills': ['財務', '會計']},
    {'title': '文件管理師', 'customer': '律准科技股份有限公司', 'skills': ['文件']},
    {'title': 'BIM工程師', 'customer': '士芃科技股份有限公司', 'skills': ['Revit', 'BIM']},
    {'title': '供應鏈管理協理', 'customer': '美德醫療', 'skills': ['供應鏈']},
    {'title': '財會主管', 'customer': '志邦企業', 'skills': ['會計']},
    {'title': '專案經理', 'customer': '創樂科技有限公司', 'skills': ['PM']},
    {'title': '自動化測試工程師', 'customer': '遊戲橘子集團', 'skills': ['Python', 'QA']},
    {'title': '資深前端工程師', 'customer': '遊戲橘子集團', 'skills': ['Vue.js', 'React']},
    {'title': '產品測試專員', 'customer': '遊戲橘子集團', 'skills': ['QA']},
    {'title': '資安工程師', 'customer': '遊戲橘子集團', 'skills': ['Security', 'DevOps']},
    {'title': '雲端維運工程師', 'customer': '遊戲橘子集團', 'skills': ['Kubernetes', 'DevOps']},
    {'title': '公有雲工程師', 'customer': '遊戲橘子集團', 'skills': ['AWS', 'GCP']},
    {'title': '機房維運工程師', 'customer': '遊戲橘子集團', 'skills': ['Linux', '網路']},
    {'title': '後端開發工程師', 'customer': '遊戲橘子集團', 'skills': ['.NET', 'C#']},
    {'title': '技術產品經理', 'customer': '遊戲橘子集團', 'skills': ['PM', '產品']},
]

# 客户 → 产业映射
CUSTOMER_INDUSTRY = {
    'AIJob內部': IndustryType.INTERNET,
    'AIJob内部': IndustryType.INTERNET,
    '美德醫療': IndustryType.HEALTHCARE,
    '律准科技股份有限公司': IndustryType.LEGAL_TECH,
    '士芃科技股份有限公司': IndustryType.MANUFACTURING,
    '志邦企業': IndustryType.MANUFACTURING,
    '創樂科技有限公司': IndustryType.INTERNET,
    '遊戲橘子集團': IndustryType.GAMING,
    '台灣遊戲橘子': IndustryType.GAMING,
}

# 产业 → 搜尋关键字
INDUSTRY_KEYWORDS = {
    IndustryType.GAMING: ['game', 'gaming', 'server', 'multiplayer', 'unity', 'unreal'],
    IndustryType.HEALTHCARE: ['healthcare', 'medical', 'clinical'],
    IndustryType.MANUFACTURING: ['manufacturing', 'bim', 'revit', 'automation'],
    IndustryType.LEGAL_TECH: ['legal', 'compliance', 'sharepoint'],
    IndustryType.INTERNET: ['backend', 'frontend', 'web', 'api', 'python', 'javascript'],
}

def generate_search_plan() -> Dict:
    """生成搜尋计划"""
    
    plan = {
        'total_jobs': len(EXISTING_JOBS),
        'by_industry': {},
        'by_customer': {},
        'search_layers': {
            'layer_1': [],  # P0 职缺
            'layer_2': [],  # P1 职缺
        }
    }
    
    for job in EXISTING_JOBS:
        customer = job['customer']
        industry = CUSTOMER_INDUSTRY.get(customer, IndustryType.INTERNET)
        keywords = INDUSTRY_KEYWORDS.get(industry, [])
        
        # 统计产业
        if industry.value not in plan['by_industry']:
            plan['by_industry'][industry.value] = {'count': 0, 'jobs': []}
        plan['by_industry'][industry.value]['count'] += 1
        plan['by_industry'][industry.value]['jobs'].append(job['title'])
        
        # 统计客户
        if customer not in plan['by_customer']:
            plan['by_customer'][customer] = {'count': 0, 'industry': industry.value}
        plan['by_customer'][customer]['count'] += 1
        
        # 确定层级
        layer = 'layer_1' if industry == IndustryType.GAMING else 'layer_2'
        
        job_plan = {
            'title': job['title'],
            'customer': customer,
            'industry': industry.value,
            'confidence': 99,
            'github_keywords': keywords,
            'estimated_candidates': 30 if industry == IndustryType.GAMING else 20,
            'search_priority': 'P0' if industry == IndustryType.GAMING else 'P1',
            'layer': layer
        }
        
        plan['search_layers'][layer].append(job_plan)
    
    return plan

def print_plan(plan: Dict):
    """打印搜尋计划"""
    
    print("\n" + "="*100)
    print("📊 职缺 → 产业 → 搜尋计划")
    print("="*100 + "\n")
    
    print(f"📋 总职缺数：{plan['total_jobs']} 个\n")
    
    print("🏭 按产业分布：")
    for industry, data in sorted(plan['by_industry'].items()):
        print(f"  • {industry.upper()}: {data['count']} 个职缺")
        for job in data['jobs'][:3]:  # 最多显示3个
            print(f"    - {job}")
        if len(data['jobs']) > 3:
            print(f"    ... 以及 {len(data['jobs']) - 3} 个职缺")
    
    print("\n🏢 按客户分布：")
    for customer, data in sorted(plan['by_customer'].items()):
        print(f"  • {customer} ({data['industry']}): {data['count']} 个职缺")
    
    print("\n")
    print("🔍 搜尋计划：\n")
    
    for layer, jobs in plan['search_layers'].items():
        if jobs:
            print(f"  {layer.upper()} （即时执行，{len(jobs)} 个职缺）")
            for job in jobs:
                print(f"    • {job['title']} @ {job['customer']}")
                print(f"      💡 搜尋关键字：{', '.join(job['github_keywords'][:3])}")
                print(f"      👥 预估：~{job['estimated_candidates']} 人，优先级 {job['search_priority']}")
            print("")
    
    print("="*100 + "\n")

def main():
    plan = generate_search_plan()
    print_plan(plan)
    
    # 保存为 JSON
    with open('/tmp/search-plan.json', 'w', encoding='utf-8') as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 搜尋计划已保存：/tmp/search-plan.json")

if __name__ == '__main__':
    main()
