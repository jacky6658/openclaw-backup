#!/usr/bin/env python3
"""
Unified Talent Scraper v4 Enhanced - Industry-Aware Parallel Search

核心功能：
1. 产业识别（客户 + JD → 产业标签）
2. 行业感知搜尋（GitHub + LinkedIn）
3. 分层爬蟲策略（Layer 1: P0 职缺 vs Layer 2: P1 职缺）
4. 智能并行执行（ThreadPoolExecutor）
5. 增量缓存 + 去重
"""

import json
import subprocess
import sqlite3
import time
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import hashlib

# ==================== 产业类型 ====================

class IndustryType(Enum):
    GAMING = "gaming"
    FINTECH = "fintech"
    HEALTHCARE = "healthcare"
    MANUFACTURING = "manufacturing"
    INTERNET = "internet"
    LEGAL_TECH = "legal_tech"
    DEVOPS = "devops"
    UNKNOWN = "unknown"

class SearchLayer(Enum):
    LAYER_1 = "layer_1"  # P0 职缺，立即爬蟲
    LAYER_2 = "layer_2"  # P1 职缺，本周爬蟲

# ==================== 客户产业映射 ====================

CUSTOMER_TO_INDUSTRY = {
    'AIJob内部': IndustryType.INTERNET,
    'AIJob內部': IndustryType.INTERNET,
    '美德医疗': IndustryType.HEALTHCARE,
    '律准科技股份有限公司': IndustryType.LEGAL_TECH,
    '士芃科技股份有限公司': IndustryType.MANUFACTURING,
    '志邦企业': IndustryType.MANUFACTURING,
    '创乐科技有限公司': IndustryType.INTERNET,
    '遊戲橘子集團': IndustryType.GAMING,
    '台灣遊戲橘子': IndustryType.GAMING,
}

# ==================== 产业搜尋关键字库 ====================

INDUSTRY_SEARCH_KEYWORDS = {
    IndustryType.GAMING: {
        'github': ['language:cpp OR language:csharp', 'game server', 'multiplayer', 'unity', 'unreal'],
        'linkedin': ['Game Server Engineer', 'Gaming Backend', 'Multiplayer Programmer'],
        'priority': ['networking', 'real-time', 'latency', 'physics']
    },
    
    IndustryType.HEALTHCARE: {
        'github': ['healthcare', 'medical', 'clinical', 'python OR java'],
        'linkedin': ['Healthcare', 'Medical', 'Clinical', 'Pharmaceutical'],
        'priority': ['patient', 'diagnosis', 'hipaa']
    },
    
    IndustryType.MANUFACTURING: {
        'github': ['BIM', 'Revit', 'AutoCAD', 'IoT', 'python OR c++'],
        'linkedin': ['Manufacturing', 'BIM', 'Industrial', 'Supply Chain'],
        'priority': ['automation', 'robotics', 'erp']
    },
    
    IndustryType.FINTECH: {
        'github': ['trading', 'quantitative', 'python OR cpp', 'high-frequency'],
        'linkedin': ['Trading', 'Fintech', 'Quantitative', 'Risk Management'],
        'priority': ['hft', 'derivatives', 'compliance']
    },
    
    IndustryType.DEVOPS: {
        'github': ['kubernetes', 'docker', 'terraform', 'devops'],
        'linkedin': ['DevOps', 'Infrastructure', 'Cloud', 'Kubernetes'],
        'priority': ['ci/cd', 'monitoring', 'aws', 'gcp']
    },
    
    IndustryType.INTERNET: {
        'github': ['backend', 'web', 'api', 'python OR javascript OR java'],
        'linkedin': ['Backend Engineer', 'Frontend Engineer', 'Web Developer', 'Software Engineer'],
        'priority': ['microservices', 'scalability', 'database']
    },
    
    IndustryType.LEGAL_TECH: {
        'github': ['compliance', 'legal', 'contract'],
        'linkedin': ['Legal Tech', 'Compliance', 'Legal'],
        'priority': ['regulation', 'contracts']
    }
}

# ==================== 数据类 ====================

@dataclass
class JobRequirement:
    """职缺需求"""
    job_title: str
    customer_name: str
    industry: IndustryType
    sub_industry: Optional[str]
    headcount: int
    salary_range: str
    skills: List[str]
    experience_years: int
    location: str
    search_layer: SearchLayer
    priority: str  # P0, P1, P2
    
    def get_search_keywords(self) -> Dict:
        """获取搜尋关键字"""
        keywords = INDUSTRY_SEARCH_KEYWORDS.get(self.industry, {})
        return {
            'github': keywords.get('github', []),
            'linkedin': keywords.get('linkedin', []),
            'priority': keywords.get('priority', [])
        }

@dataclass
class CandidateMatch:
    """候选人匹配结果"""
    name: str
    github_url: Optional[str]
    linkedin_url: Optional[str]
    skills: List[str]
    years_experience: int
    industry_match: float  # 0-1，产业匹配度
    skill_match: float  # 0-1，技能匹配度
    overall_score: float  # 0-100
    source: str  # 'github' or 'linkedin'
    job_id: str
    
    def to_dict(self) -> Dict:
        return asdict(self)

# ==================== GitHub 爬蟲 ====================

class GitHubScraper:
    """GitHub API 爬蟲 + 并行搜尋"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or subprocess.run(['git', 'config', '--global', 'github.token'], 
                                            capture_output=True, text=True).stdout.strip()
        self.session = self._init_session()
    
    def _init_session(self):
        """初始化 session"""
        import requests
        from requests.auth import HTTPBasicAuth
        
        session = requests.Session()
        if self.token:
            session.headers['Authorization'] = f'token {self.token}'
        session.headers['Accept'] = 'application/vnd.github.v3+json'
        return session
    
    def search_candidates(self, job_req: JobRequirement, max_results: int = 30) -> List[CandidateMatch]:
        """搜尋候选人"""
        
        keywords = job_req.get_search_keywords()
        results = []
        
        # 搜尋关键字优先级：优先技能 > 产业关键词 > 通用关键词
        search_queries = [
            ' '.join(job_req.skills[:2]),  # 最相关的技能
        ] + keywords.get('github', [])
        
        for query in search_queries:
            if len(results) >= max_results:
                break
            
            try:
                matches = self._search_api(query, job_req, max_results - len(results))
                results.extend(matches)
                time.sleep(1)  # API 限流
            except Exception as e:
                print(f"❌ GitHub 搜尋失败 ({query}): {e}")
        
        # 去重
        unique_results = {}
        for r in results:
            key = f"{r.name}:{r.github_url}"
            if key not in unique_results:
                unique_results[key] = r
        
        return list(unique_results.values())[:max_results]
    
    def _search_api(self, query: str, job_req: JobRequirement, max_results: int) -> List[CandidateMatch]:
        """调用 GitHub Search API"""
        
        import requests
        
        # 按地点和语言过滤
        search_query = f"{query} language:python OR language:go OR language:cpp location:Taiwan type:user"
        
        try:
            resp = self.session.get(
                'https://api.github.com/search/users',
                params={'q': search_query, 'per_page': max_results}
            )
            resp.raise_for_status()
            
            results = []
            for user in resp.json().get('items', []):
                match = self._extract_candidate(user, job_req)
                if match:
                    results.append(match)
            
            return results
        except requests.exceptions.RequestException as e:
            print(f"API 错误: {e}")
            return []
    
    def _extract_candidate(self, user: Dict, job_req: JobRequirement) -> Optional[CandidateMatch]:
        """提取候选人信息"""
        
        github_url = user.get('html_url')
        name = user.get('login') or user.get('name', 'Unknown')
        
        # 从 bio 推断技能
        bio = user.get('bio', '').lower()
        skills = []
        for skill in job_req.skills:
            if skill.lower() in bio:
                skills.append(skill)
        
        # 产业匹配度：检查 bio 中是否有产业关键词
        industry_keywords = INDUSTRY_SEARCH_KEYWORDS.get(job_req.industry, {}).get('priority', [])
        industry_match = sum(1 for kw in industry_keywords if kw in bio) / max(len(industry_keywords), 1)
        
        # 技能匹配度
        skill_match = len(skills) / max(len(job_req.skills), 1) if job_req.skills else 0.5
        
        # 综合分数
        overall_score = (industry_match * 0.3 + skill_match * 0.7) * 100
        
        if overall_score > 30:  # 最低阈值
            return CandidateMatch(
                name=name,
                github_url=github_url,
                linkedin_url=None,
                skills=skills,
                years_experience=0,  # GitHub API 无直接信息
                industry_match=industry_match,
                skill_match=skill_match,
                overall_score=overall_score,
                source='github',
                job_id=job_req.job_title
            )
        
        return None

# ==================== 搜尋计划执行器 ====================

class SearchPlanExecutor:
    """整合产业识别 + 爬蟲 + 缓存"""
    
    def __init__(self, cache_db: str = '/tmp/search-cache.db'):
        self.cache_db = cache_db
        self._init_cache()
        self.github = GitHubScraper()
    
    def _init_cache(self):
        """初始化缓存数据库"""
        conn = sqlite3.connect(self.cache_db)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS search_results (
                id INTEGER PRIMARY KEY,
                job_title TEXT,
                candidate_name TEXT,
                github_url TEXT,
                linkedin_url TEXT,
                overall_score REAL,
                created_at TIMESTAMP,
                UNIQUE(job_title, candidate_name, github_url)
            )
        ''')
        conn.commit()
        conn.close()
    
    def execute_search_plan(self, 
                           job_requirements: List[JobRequirement],
                           parallel_workers: int = 2,
                           layer_filter: Optional[SearchLayer] = None) -> Dict:
        """执行分层搜尋计划"""
        
        # 按 layer 过滤
        if layer_filter:
            jobs = [j for j in job_requirements if j.search_layer == layer_filter]
        else:
            jobs = job_requirements
        
        # 按优先级排序
        jobs_sorted = sorted(jobs, key=lambda j: (j.search_layer.value, j.priority))
        
        # 并行执行
        results = {}
        with ThreadPoolExecutor(max_workers=parallel_workers) as executor:
            futures = {
                executor.submit(self._search_for_job, job): job 
                for job in jobs_sorted
            }
            
            for future in as_completed(futures):
                job = futures[future]
                try:
                    matches = future.result()
                    results[job.job_title] = matches
                    print(f"✅ {job.job_title}: 找到 {len(matches)} 位候选人")
                except Exception as e:
                    print(f"❌ {job.job_title}: {e}")
                    results[job.job_title] = []
        
        return results
    
    def _search_for_job(self, job: JobRequirement) -> List[CandidateMatch]:
        """搜尋单个职缺"""
        
        print(f"🔍 搜尋 {job.job_title} @ {job.customer_name} ({job.industry.value})...")
        
        # GitHub 搜尋
        candidates = self.github.search_candidates(job, max_results=30)
        
        # 缓存结果
        self._cache_results(candidates)
        
        return candidates
    
    def _cache_results(self, candidates: List[CandidateMatch]):
        """保存结果到缓存"""
        conn = sqlite3.connect(self.cache_db)
        for c in candidates:
            conn.execute('''
                INSERT OR IGNORE INTO search_results 
                (job_title, candidate_name, github_url, linkedin_url, overall_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (c.job_id, c.name, c.github_url, c.linkedin_url, c.overall_score, datetime.now()))
        conn.commit()
        conn.close()

# ==================== 主程序 ====================

def main():
    """示例：从职缺表读取并执行搜尋计划"""
    
    # 示例职缺（从 TOOLS.md 提取）
    job_requirements = [
        # Layer 1: Gaming jobs (P0)
        JobRequirement(
            job_title='資安工程師',
            customer_name='遊戲橘子集團',
            industry=IndustryType.GAMING,
            sub_industry='game_server',
            headcount=1,
            salary_range='面議',
            skills=['DevOps', 'Linux', 'Security'],
            experience_years=2,
            location='台北',
            search_layer=SearchLayer.LAYER_1,
            priority='P0'
        ),
        JobRequirement(
            job_title='雲端維運工程師',
            customer_name='遊戲橘子集團',
            industry=IndustryType.GAMING,
            sub_industry='devops',
            headcount=1,
            salary_range='面議',
            skills=['Kubernetes', 'Docker', 'AWS', 'Linux'],
            experience_years=3,
            location='台北',
            search_layer=SearchLayer.LAYER_1,
            priority='P0'
        ),
        
        # Layer 2: Other jobs (P1)
        JobRequirement(
            job_title='AI工程師',
            customer_name='AIJob內部',
            industry=IndustryType.INTERNET,
            sub_industry='backend',
            headcount=2,
            salary_range='80k-120k',
            skills=['Python', 'AI', 'Machine Learning'],
            experience_years=3,
            location='台北',
            search_layer=SearchLayer.LAYER_2,
            priority='P1'
        ),
    ]
    
    # 执行搜尋计划
    executor = SearchPlanExecutor()
    
    print("\n" + "="*80)
    print("🔍 Layer 1 搜尋（P0 職缺，立即執行）")
    print("="*80 + "\n")
    
    layer1_results = executor.execute_search_plan(
        job_requirements,
        parallel_workers=2,
        layer_filter=SearchLayer.LAYER_1
    )
    
    # 输出结果
    print("\n" + "="*80)
    print("📊 搜尋結果摘要")
    print("="*80 + "\n")
    
    total_candidates = 0
    for job_title, candidates in layer1_results.items():
        print(f"\n📌 {job_title}: {len(candidates)} 位候選人")
        for c in candidates[:5]:  # 显示 Top 5
            print(f"  • {c.name} ({c.source})")
            print(f"    └─ 综合分数：{c.overall_score:.0f}, 产业匹配：{c.industry_match:.0%}")
        total_candidates += len(candidates)
    
    print(f"\n✅ 總計：{total_candidates} 位候選人找到")
    
    # 保存为 JSON
    output = {
        'timestamp': datetime.now().isoformat(),
        'layer': 'layer_1',
        'total_candidates': total_candidates,
        'results': {
            job: [c.to_dict() for c in candidates]
            for job, candidates in layer1_results.items()
        }
    }
    
    with open('/tmp/search-results-layer1.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 結果已保存：/tmp/search-results-layer1.json")

if __name__ == '__main__':
    main()
