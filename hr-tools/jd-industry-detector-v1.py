#!/usr/bin/env python3
"""
JD 产业识别转换器 v1（针对 Jacky 的 8 个客户优化）

支持客户：
- AIJob（互联网）
- 美德医疗（医疗/制造）
- 律准科技（法务/科技）
- 士芃科技（工程/制造）
- 志邦企业（制造）
- 创乐科技（SaaS）
- 遊戲橘子（游戏）
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# ==================== 产业分类 ====================

class IndustryType(Enum):
    """产业类型"""
    GAMING = "gaming"
    FINTECH = "fintech"
    ECOMMERCE = "ecommerce"
    MANUFACTURING = "manufacturing"
    HEALTHCARE = "healthcare"
    INTERNET = "internet"
    LEGAL_TECH = "legal_tech"
    DEVOPS = "devops"
    UNKNOWN = "unknown"

class SubIndustry(Enum):
    """子产业"""
    # Gaming
    GAME_ENGINE = "game_engine"
    GAME_SERVER = "game_server"
    GAME_QA = "game_qa"
    COMPETITIVE_GAMING = "competitive_gaming"
    
    # Manufacturing
    BIM_ENGINEERING = "bim_engineering"
    SUPPLY_CHAIN = "supply_chain"
    COST_ACCOUNTING = "cost_accounting"
    
    # Healthcare
    MEDICAL_MANAGEMENT = "medical_management"
    
    # Tech
    CLOUD_INFRA = "cloud_infra"
    BACKEND_SYSTEMS = "backend_systems"
    FRONTEND_UI = "frontend_ui"
    
    # General
    GENERAL = "general"

# ==================== 客户产业映射（硬编码，最优先） ====================

CUSTOMER_TO_INDUSTRY = {
    'AIJob内部': {
        'industry': IndustryType.INTERNET,
        'sub_industry': SubIndustry.BACKEND_SYSTEMS,
        'confidence': 0.99,
        'reason': '客户是 AI 互联网公司'
    },
    'AIJob內部': {  # 繁体版
        'industry': IndustryType.INTERNET,
        'sub_industry': SubIndustry.BACKEND_SYSTEMS,
        'confidence': 0.99,
        'reason': '客户是 AI 互联网公司'
    },
    
    '美德医疗': {
        'industry': IndustryType.HEALTHCARE,
        'sub_industry': SubIndustry.MEDICAL_MANAGEMENT,
        'confidence': 0.99,
        'reason': '医疗行业客户'
    },
    
    '律准科技股份有限公司': {
        'industry': IndustryType.LEGAL_TECH,
        'sub_industry': SubIndustry.GENERAL,
        'confidence': 0.99,
        'reason': '法务科技公司'
    },
    
    '士芃科技股份有限公司': {
        'industry': IndustryType.MANUFACTURING,
        'sub_industry': SubIndustry.BIM_ENGINEERING,
        'confidence': 0.99,
        'reason': 'BIM 工程技术公司'
    },
    
    '志邦企业': {
        'industry': IndustryType.MANUFACTURING,
        'sub_industry': SubIndustry.COST_ACCOUNTING,
        'confidence': 0.99,
        'reason': '制造业企业'
    },
    
    '创乐科技有限公司': {
        'industry': IndustryType.INTERNET,
        'sub_industry': SubIndustry.GENERAL,
        'confidence': 0.99,
        'reason': '科技公司'
    },
    
    '遊戲橘子集團': {
        'industry': IndustryType.GAMING,
        'sub_industry': SubIndustry.GAME_SERVER,
        'confidence': 0.99,
        'reason': '游戏公司'
    },
    
    '台灣遊戲橘子': {
        'industry': IndustryType.GAMING,
        'sub_industry': SubIndustry.GAME_SERVER,
        'confidence': 0.99,
        'reason': '游戏公司'
    },
}

# ==================== 职位 → 子产业推断 ====================

JOB_TITLE_TO_SUBINDUSTRY = {
    # 游戏相关
    r'自動化測試|QA|產品測試|automation.*qa|product.*test': SubIndustry.GAME_QA,
    r'前端|frontend|vue|react|ui|ux': SubIndustry.FRONTEND_UI,
    r'後端|backend|server|api|服務': SubIndustry.GAME_SERVER,
    r'雲端維運|devops|cloud|kubernetes|k8s': SubIndustry.CLOUD_INFRA,
    r'資安|security|安全': SubIndustry.GENERAL,
    r'產品經理|pm|product.*manager': SubIndustry.GENERAL,
    
    # 制造/BIM
    r'bim|revit|autocad|工程': SubIndustry.BIM_ENGINEERING,
    r'供應鏈|協理|採購|logistics': SubIndustry.SUPPLY_CHAIN,
    r'會計|財會|成本': SubIndustry.COST_ACCOUNTING,
    
    # 医疗
    r'醫療|醫師|護理|管理': SubIndustry.MEDICAL_MANAGEMENT,
    
    # IT/Dev
    r'\.net|c#|sqlserver|後端': SubIndustry.BACKEND_SYSTEMS,
}

# ==================== 技能 → 产业关键词 ====================

INDUSTRY_SKILLS = {
    IndustryType.GAMING: {
        'primary': [
            'Game Engine', 'Unity', 'Unreal', 'C#', 'C++',
            'multiplayer', 'real-time', 'latency',
            'game server', '遊戲引擎', '多人'
        ],
        'keywords': [
            'game', 'gaming', 'unreal', 'unity',
            '遊戲', '引擎', '多人'
        ]
    },
    
    IndustryType.HEALTHCARE: {
        'primary': [
            'HIPAA', 'patient', 'medical', 'diagnosis',
            'clinical', 'pharmaceutical', '患者', '醫療'
        ],
        'keywords': ['medical', 'health', 'hospital', '醫療', '患者']
    },
    
    IndustryType.MANUFACTURING: {
        'primary': [
            'BIM', 'Revit', 'AutoCAD', 'IoT', 'industrial',
            'automation', 'robotics', 'ERP', 'MES',
            'supply chain', '工業', '自動化'
        ],
        'keywords': ['manufacturing', 'industrial', 'bim', '製造', '工業']
    },
    
    IndustryType.DEVOPS: {
        'primary': [
            'Kubernetes', 'Docker', 'AWS', 'GCP', 'Azure',
            'CI/CD', 'Jenkins', 'DevOps', 'Linux', 'Cloud',
            'infrastructure', '雲端', '維運'
        ],
        'keywords': ['devops', 'kubernetes', 'cloud', 'docker', 'aws']
    },
    
    IndustryType.INTERNET: {
        'primary': [
            'Python', 'JavaScript', 'Node.js', 'React', 'Vue',
            'web', 'api', 'database', 'scaling',
            'microservices', '後端', '前端'
        ],
        'keywords': ['web', 'internet', 'saas', '網路', '互聯網']
    }
}

# ==================== 数据类 ====================

@dataclass
class IndustryResult:
    """产业识别结果"""
    primary_industry: IndustryType
    sub_industry: Optional[SubIndustry]
    confidence: float  # 0-1
    sources: List[str]  # ['customer', 'job_title', 'skills', 'jd_keywords']
    keywords_found: List[str]
    recommended_search_keywords: List[str]
    
    def to_dict(self) -> Dict:
        return {
            'primary_industry': self.primary_industry.value,
            'sub_industry': self.sub_industry.value if self.sub_industry else None,
            'confidence': self.confidence,
            'sources': self.sources,
            'keywords_found': self.keywords_found,
            'recommended_search_keywords': self.recommended_search_keywords
        }

# ==================== 识别引擎 ====================

class IndustryDetector:
    """JD 产业识别引擎"""
    
    def detect(self, jd: Dict) -> IndustryResult:
        """
        识别职缺产业
        
        输入：
        {
            'customer_name': '遊戲橘子集團',
            'job_title': '資安工程師',
            'job_description': '具備 Web 或 APP 2 年以上程式開發經驗...',
            'skills': ['DevOps', 'Linux', 'Network'],
        }
        
        输出：
        {
            'primary_industry': 'gaming',
            'sub_industry': 'general',
            'confidence': 0.95,
            'sources': ['customer', 'job_title'],
            'keywords_found': ['devops', 'security'],
            'recommended_search_keywords': ['game server', 'gaming backend', 'security']
        }
        """
        
        sources = []
        keywords_found = []
        
        # 第 1 步：客户产业识别（最优先，99% 置信度）
        customer_name = jd.get('customer_name', '').strip()
        customer_result = self._detect_by_customer(customer_name)
        
        if customer_result:
            sources.append('customer')
            primary_industry = customer_result['industry']
            sub_industry = customer_result.get('sub_industry')
            confidence = customer_result['confidence']
        else:
            # 第 2 步：职位名称推断
            job_title = jd.get('job_title', '').strip()
            job_result = self._detect_by_job_title(job_title)
            
            # 第 3 步：技能推断
            skills = jd.get('skills', [])
            skill_result = self._detect_by_skills(skills)
            
            # 第 4 步：JD 描述推断
            job_desc = jd.get('job_description', '').strip()
            desc_result = self._detect_by_description(job_desc)
            
            # 合并结果
            primary_industry, sub_industry, confidence, sources = self._merge_results(
                job_result, skill_result, desc_result
            )
            
            if job_result:
                keywords_found.extend(job_result.get('keywords', []))
        
        # 生成推荐搜尋关键字
        search_keywords = self._generate_search_keywords(
            primary_industry, sub_industry, jd.get('job_title', '')
        )
        
        return IndustryResult(
            primary_industry=primary_industry,
            sub_industry=sub_industry,
            confidence=confidence,
            sources=sources,
            keywords_found=keywords_found,
            recommended_search_keywords=search_keywords
        )
    
    def _detect_by_customer(self, customer_name: str) -> Optional[Dict]:
        """第 1 层：客户产业（硬编码映射）"""
        
        for pattern, result in CUSTOMER_TO_INDUSTRY.items():
            if pattern.lower() == customer_name.lower() or \
               re.search(re.escape(pattern), customer_name, re.IGNORECASE):
                return result
        
        return None
    
    def _detect_by_job_title(self, job_title: str) -> Dict:
        """第 2 层：职位名称推断"""
        
        for pattern, sub_industry in JOB_TITLE_TO_SUBINDUSTRY.items():
            if re.search(pattern, job_title, re.IGNORECASE):
                return {
                    'sub_industry': sub_industry,
                    'keywords': [sub_industry.value],
                    'confidence': 0.7
                }
        
        return {'confidence': 0.0}
    
    def _detect_by_skills(self, skills: List[str]) -> Dict:
        """第 3 层：技能推断"""
        
        if not skills:
            return {'confidence': 0.0}
        
        skills_text = ' '.join(str(s).lower() for s in skills)
        industry_scores = {}
        
        for industry, skill_dict in INDUSTRY_SKILLS.items():
            score = 0
            keywords = []
            
            for skill in skill_dict.get('primary', []):
                if skill.lower() in skills_text:
                    score += 1.0
                    keywords.append(skill)
            
            for keyword in skill_dict.get('keywords', []):
                if re.search(keyword, skills_text, re.IGNORECASE):
                    score += 0.5
                    keywords.append(keyword)
            
            if score > 0:
                industry_scores[industry] = {
                    'score': score,
                    'keywords': keywords,
                    'confidence': min(score / 2.0, 1.0)
                }
        
        if not industry_scores:
            return {'confidence': 0.0}
        
        best = max(industry_scores.items(), key=lambda x: x[1]['score'])
        return {
            'industry': best[0],
            'keywords': best[1]['keywords'],
            'confidence': best[1]['confidence']
        }
    
    def _detect_by_description(self, description: str) -> Dict:
        """第 4 层：JD 描述推断"""
        
        if not description:
            return {'confidence': 0.0}
        
        desc_lower = description.lower()
        industry_matches = {}
        
        for industry, skill_dict in INDUSTRY_SKILLS.items():
            matches = 0
            
            for keyword in skill_dict.get('keywords', []):
                if re.search(keyword, desc_lower, re.IGNORECASE):
                    matches += 1
            
            if matches > 0:
                industry_matches[industry] = matches
        
        if not industry_matches:
            return {'confidence': 0.0}
        
        best = max(industry_matches.items(), key=lambda x: x[1])
        return {
            'industry': best[0],
            'confidence': min(best[1] / 3.0, 0.8)
        }
    
    def _merge_results(self, job_result, skill_result, desc_result) -> Tuple:
        """融合多层结果"""
        
        # 优先级：skill > job_title > description
        results = [skill_result, job_result, desc_result]
        results = [r for r in results if r.get('confidence', 0) > 0]
        
        if not results:
            return IndustryType.UNKNOWN, None, 0.0, []
        
        best = max(results, key=lambda x: x.get('confidence', 0))
        
        return (
            best.get('industry', IndustryType.UNKNOWN),
            best.get('sub_industry'),
            best.get('confidence', 0.0),
            ['job_title' if best == job_result else 'skills' if best == skill_result else 'description']
        )
    
    def _generate_search_keywords(self, industry: IndustryType, sub_industry: Optional[SubIndustry], job_title: str) -> List[str]:
        """生成搜尋关键字（用于 GitHub/LinkedIn）"""
        
        keywords = []
        
        # 产业关键字
        industry_keywords = {
            IndustryType.GAMING: ['game', 'gaming', 'server', 'multiplayer'],
            IndustryType.HEALTHCARE: ['healthcare', 'medical', 'clinical'],
            IndustryType.MANUFACTURING: ['manufacturing', 'industrial', 'bim', 'automation'],
            IndustryType.DEVOPS: ['devops', 'kubernetes', 'cloud', 'infrastructure'],
            IndustryType.INTERNET: ['backend', 'frontend', 'web', 'api'],
        }
        
        if industry in industry_keywords:
            keywords.extend(industry_keywords[industry])
        
        # 子产业关键字
        if sub_industry:
            sub_keywords = {
                SubIndustry.GAME_ENGINE: ['unity', 'unreal', 'game engine'],
                SubIndustry.GAME_SERVER: ['game server', 'multiplayer', 'networking'],
                SubIndustry.GAME_QA: ['qa', 'testing', 'game qa'],
                SubIndustry.BIM_ENGINEERING: ['bim', 'revit', 'autocad'],
                SubIndustry.SUPPLY_CHAIN: ['supply chain', 'logistics', 'sourcing'],
                SubIndustry.CLOUD_INFRA: ['kubernetes', 'docker', 'aws', 'devops'],
            }
            
            if sub_industry in sub_keywords:
                keywords.extend(sub_keywords[sub_industry])
        
        # 技能关键字（从职位名提取）
        if job_title:
            if 'python' in job_title.lower():
                keywords.append('python')
            if 'java' in job_title.lower():
                keywords.append('java')
            if 'c++' in job_title.lower():
                keywords.append('c++')
        
        return list(dict.fromkeys(keywords))  # 去重

# ==================== 主程序 ====================

def main():
    import sys
    
    detector = IndustryDetector()
    
    # 示例职缺
    test_jds = [
        {
            'customer_name': '遊戲橘子集團',
            'job_title': '資安工程師',
            'job_description': '具備 Web 或 APP 2 年以上程式開發經驗，熟悉 DevOps',
            'skills': ['Linux', 'Security', 'DevOps']
        },
        {
            'customer_name': '美德医疗',
            'job_title': '會計經理',
            'job_description': '財務會計、IFRS、成本核算、稅務申報',
            'skills': ['會計', '財務', '税務']
        },
        {
            'customer_name': '士芃科技股份有限公司',
            'job_title': 'BIM工程師',
            'job_description': 'Revit、AutoCAD、BIM、ISO19650、Dynamo',
            'skills': ['Revit', 'AutoCAD', 'BIM']
        },
    ]
    
    for jd in test_jds:
        result = detector.detect(jd)
        print(f"\n职缺：{jd['job_title']} @ {jd['customer_name']}")
        print(f"产业：{result.primary_industry.value}")
        print(f"子产业：{result.sub_industry.value if result.sub_industry else 'N/A'}")
        print(f"置信度：{result.confidence:.1%}")
        print(f"搜尋关键字：{', '.join(result.recommended_search_keywords)}")

if __name__ == '__main__':
    main()
