#!/usr/bin/env python3
"""
职缺 → 产业 → 搜尋策略转换器

流程：
1. 从 Google Sheets 读取职缺
2. 产业识别（客户 → 职位 → 技能）
3. 生成搜尋策略（GitHub + LinkedIn 关键字）
4. 输出候选人搜尋计划
"""

import subprocess
import json
import sys
import re
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

# ==================== 产业类型 ====================

class IndustryType(Enum):
    GAMING = "gaming"
    FINTECH = "fintech"
    HEALTHCARE = "healthcare"
    MANUFACTURING = "manufacturing"
    INTERNET = "internet"
    DEVOPS = "devops"
    LEGAL_TECH = "legal_tech"
    UNKNOWN = "unknown"

# ==================== 客户产业映射 ====================

CUSTOMER_TO_INDUSTRY = {
    'AIJob内部': {'industry': IndustryType.INTERNET, 'confidence': 0.99},
    'AIJob內部': {'industry': IndustryType.INTERNET, 'confidence': 0.99},
    '美德医疗': {'industry': IndustryType.HEALTHCARE, 'confidence': 0.99},
    '律准科技股份有限公司': {'industry': IndustryType.LEGAL_TECH, 'confidence': 0.99},
    '士芃科技股份有限公司': {'industry': IndustryType.MANUFACTURING, 'confidence': 0.99},
    '志邦企业': {'industry': IndustryType.MANUFACTURING, 'confidence': 0.99},
    '创乐科技有限公司': {'industry': IndustryType.INTERNET, 'confidence': 0.99},
    '遊戲橘子集團': {'industry': IndustryType.GAMING, 'confidence': 0.99},
    '台灣遊戲橘子': {'industry': IndustryType.GAMING, 'confidence': 0.99},
}

# ==================== 简单的产业检测器 ====================

class SimpleIndustryDetector:
    """简化版产业识别器"""
    
    def detect(self, jd: Dict) -> Dict:
        """识别产业"""
        
        customer = jd.get('customer_name', '').strip()
        
        # 先查客户映射
        for pattern, result in CUSTOMER_TO_INDUSTRY.items():
            if pattern.lower() in customer.lower() or customer.lower() in pattern.lower():
                return {
                    'primary_industry': result['industry'].value,
                    'confidence': result['confidence'],
                    'sources': ['customer']
                }
        
        # 备选：从技能推断
        skills = jd.get('skills', [])
        skills_text = ' '.join(str(s).lower() for s in skills)
        
        if any(k in skills_text for k in ['devops', 'kubernetes', 'docker', 'aws']):
            industry = IndustryType.DEVOPS
        elif any(k in skills_text for k in ['bim', 'revit', 'autocad']):
            industry = IndustryType.MANUFACTURING
        elif any(k in skills_text for k in ['game', 'unity', 'unreal']):
            industry = IndustryType.GAMING
        else:
            industry = IndustryType.INTERNET
        
        return {
            'primary_industry': industry.value,
            'confidence': 0.7,
            'sources': ['skills'],
            'recommended_search_keywords': self._generate_keywords(industry)
        }
    
    def _generate_keywords(self, industry: IndustryType) -> List[str]:
        keywords = {
            IndustryType.GAMING: ['game', 'gaming', 'server', 'multiplayer'],
            IndustryType.HEALTHCARE: ['healthcare', 'medical'],
            IndustryType.MANUFACTURING: ['manufacturing', 'bim', 'automation'],
            IndustryType.DEVOPS: ['devops', 'kubernetes', 'cloud'],
            IndustryType.INTERNET: ['backend', 'frontend', 'web'],
            IndustryType.LEGAL_TECH: ['legal', 'compliance'],
        }
        return keywords.get(industry, ['general'])

# ==================== 从 Google Sheets 读取职缺 ====================

def fetch_jds_from_sheets(sheet_id: str) -> List[Dict]:
    """从 Google Sheets 读取职缺数据"""
    
    try:
        result = subprocess.run([
            'gog', 'sheets', 'get',
            sheet_id, 'A1:H100',
            '--account', 'aiagentg888@gmail.com'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            print(f"❌ 读取 Google Sheets 失败：{result.stderr}", file=sys.stderr)
            return []
        
        # 解析输出
        lines = result.stdout.strip().split('\n')
        if len(lines) < 2:
            return []
        
        # 第一行是表头
        headers = lines[0].split('\t')
        
        jds = []
        for line in lines[1:]:
            if not line.strip():
                continue
            
            values = line.split('\t')
            
            # 简单的列映射
            jd = {
                'job_title': values[0] if len(values) > 0 else '',
                'customer_name': values[1] if len(values) > 1 else '',
                'department': values[2] if len(values) > 2 else '',
                'headcount': values[3] if len(values) > 3 else '',
                'salary_range': values[4] if len(values) > 4 else '',
                'skills': values[5].split('、') if len(values) > 5 else [],
                'experience': values[6] if len(values) > 6 else '',
                'education': values[7] if len(values) > 7 else '',
            }
            
            if jd['job_title'] and jd['customer_name']:
                jds.append(jd)
        
        return jds
    
    except Exception as e:
        print(f"❌ 错误：{e}", file=sys.stderr)
        return []

# ==================== 产业识别 ====================

def detect_industry_for_jds(jds: List[Dict]) -> List[Dict]:
    """为所有职缺识别产业"""
    
    detector = SimpleIndustryDetector()
    
    for jd in jds:
        result = detector.detect(jd)
        jd['industry'] = result
    
    return jds

# ==================== 生成搜尋策略 ====================

def generate_search_strategy(jds: List[Dict]) -> Dict:
    """生成完整的搜尋策略"""
    
    strategy = {
        'total_jobs': len(jds),
        'by_industry': {},
        'by_customer': {},
        'search_plan': []
    }
    
    for jd in jds:
        industry = jd['industry']['primary_industry']
        customer = jd['customer_name']
        
        # 统计产业分布
        if industry not in strategy['by_industry']:
            strategy['by_industry'][industry] = {
                'count': 0,
                'jobs': []
            }
        strategy['by_industry'][industry]['count'] += 1
        strategy['by_industry'][industry]['jobs'].append(jd['job_title'])
        
        # 统计客户分布
        if customer not in strategy['by_customer']:
            strategy['by_customer'][customer] = {
                'count': 0,
                'industry': industry,
                'jobs': []
            }
        strategy['by_customer'][customer]['count'] += 1
        strategy['by_customer'][customer]['jobs'].append(jd['job_title'])
        
        # 搜尋计划
        keywords = jd['industry'].get('recommended_search_keywords', [])
        if not keywords:
            keywords = SimpleIndustryDetector()._generate_keywords(IndustryType[industry.upper().replace('-', '_')])
        
        search_plan = {
            'job_title': jd['job_title'],
            'customer': customer,
            'industry': industry,
            'sub_industry': jd['industry'].get('sub_industry', 'general'),
            'confidence': jd['industry']['confidence'],
            'github_keywords': keywords,
            'linkedin_keywords': keywords,
            'estimated_candidates': estimate_candidate_count(industry),
            'search_priority': calculate_priority(jd),
            'layer': determine_search_layer(jd)
        }
        
        strategy['search_plan'].append(search_plan)
    
    return strategy

def estimate_candidate_count(industry: str) -> int:
    """估计可找到的候选人数量"""
    
    estimates = {
        'gaming': 40,  # 游戏产业候选人较少
        'healthcare': 20,
        'manufacturing': 25,
        'fintech': 50,  # 金融科技候选人较多
        'internet': 60,
        'legal_tech': 15,
        'devops': 35,
    }
    
    return estimates.get(industry, 30)

def calculate_priority(jd: Dict) -> str:
    """计算搜尋优先级"""
    
    # 优先级：recruitment count > 内部职缺 > 置信度
    headcount = jd.get('headcount', '')
    
    try:
        count = int(''.join(c for c in headcount if c.isdigit()) or '1')
        if count >= 3:
            return 'P0'
        elif count >= 2:
            return 'P1'
    except:
        pass
    
    if jd['customer_name'] == 'AIJob内部' or jd['customer_name'] == 'AIJob內部':
        return 'P1'
    
    return 'P2'

def determine_search_layer(jd: Dict) -> str:
    """确定搜尋层次"""
    
    # 层级 1：高优先级职缺（全职、多人、高置信度）
    priority = calculate_priority(jd)
    confidence = jd['industry']['confidence']
    
    if priority == 'P0' and confidence > 0.8:
        return 'layer_1'
    elif priority == 'P1':
        return 'layer_1'
    else:
        return 'layer_2'

# ==================== 输出 ====================

def print_strategy(strategy: Dict):
    """打印搜尋策略"""
    
    print("\n" + "="*80)
    print("📊 职缺 → 产业 → 搜尋策略分析")
    print("="*80 + "\n")
    
    # 统计
    print(f"📋 总职缺数：{strategy['total_jobs']} 个\n")
    
    # 产业分布
    print("🏭 按产业分布：")
    for industry, data in strategy['by_industry'].items():
        print(f"  • {industry.upper()}: {data['count']} 个职缺")
        for job in data['jobs']:
            print(f"    - {job}")
    
    print("\n")
    
    # 客户分布
    print("🏢 按客户分布：")
    for customer, data in strategy['by_customer'].items():
        print(f"  • {customer} ({data['industry']}): {data['count']} 个职缺")
    
    print("\n")
    
    # 搜尋计划
    print("🔍 搜尋计划（按优先级排序）：\n")
    
    # 按优先级排序
    sorted_plans = sorted(
        strategy['search_plan'],
        key=lambda x: (x['search_priority'], -x['confidence'])
    )
    
    current_layer = None
    for idx, plan in enumerate(sorted_plans, 1):
        if plan['layer'] != current_layer:
            print(f"\n{plan['layer'].upper()} （即时执行）")
            current_layer = plan['layer']
        
        print(f"\n  {idx}. {plan['job_title']} @ {plan['customer']}")
        print(f"     • 产业：{plan['industry']} ({plan['sub_industry']})")
        print(f"     • 优先级：{plan['search_priority']}")
        print(f"     • 置信度：{plan['confidence']:.0%}")
        print(f"     • 搜尋关键字：{', '.join(plan['github_keywords'])}")
        print(f"     • 预估候选人：~{plan['estimated_candidates']} 人")
    
    print("\n" + "="*80 + "\n")

def export_json(strategy: Dict, output_file: str = '/tmp/search-strategy.json'):
    """导出为 JSON"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(strategy, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 搜尋策略已导出：{output_file}")

# ==================== 主程序 ====================

def main():
    # Step 1: 读取职缺
    print("📖 读取职缺数据...")
    sheet_id = "1QPaeOm-slNVFCeM8Q3gg3DawKjzp2tYwyfquvdHlZFE"
    jds = fetch_jds_from_sheets(sheet_id)
    
    if not jds:
        print("❌ 无法读取职缺数据", file=sys.stderr)
        return
    
    print(f"✅ 成功读取 {len(jds)} 个职缺\n")
    
    # Step 2: 产业识别
    print("🔍 执行产业识别...")
    jds = detect_industry_for_jds(jds)
    print("✅ 产业识别完成\n")
    
    # Step 3: 生成策略
    print("🎯 生成搜尋策略...")
    strategy = generate_search_strategy(jds)
    print("✅ 搜尋策略已生成\n")
    
    # Step 4: 输出
    print_strategy(strategy)
    export_json(strategy)

if __name__ == '__main__':
    main()
