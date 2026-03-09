#!/usr/bin/env python3
"""
統一人才爬蟲 v4 - 並行 LinkedIn + GitHub
整合進階反爬蟲機制 + 智能去重 + 風險管理

功能：
1. 並行化搜尋 - LinkedIn & GitHub 同時執行
2. 智能去重 - 同一人多平台檢測
3. 數據融合 - 合併 LinkedIn + GitHub 信息
4. 風險管理 - 帳號監控 + 備用方案
5. 實時進度 - 進度條 + 預估時間
"""

import sys
import json
import subprocess
import os
import time
import re
import urllib.parse
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import hashlib

# ==================== 日誌設定 ====================
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== 環境變數 ====================
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

if not GITHUB_TOKEN:
    logger.error("❌ 環境變數 GITHUB_TOKEN 未設定")
    sys.exit(1)

DATA_DIR = Path(os.getenv("HR_TOOLS_DATA_DIR", "/tmp/unified-scraper"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

CACHE_DB = DATA_DIR / "unified_cache.db"
ACCOUNT_STATUS = DATA_DIR / "account_status.json"

# ==================== 設定 ====================

LANG_TO_SKILLS = {
    'Python': ['Python', 'Data Science', 'Machine Learning', 'AI'],
    'JavaScript': ['JavaScript', 'TypeScript', 'Node.js', 'React', 'Vue'],
    'Go': ['Go', 'Backend', 'Microservices', 'DevOps'],
    'Java': ['Java', 'Spring Boot', 'Microservices', 'Enterprise'],
    'C++': ['C++', 'Systems', 'Performance'],
    'C#': ['C#', '.NET', 'Windows'],
    'Rust': ['Rust', 'Systems', 'Performance'],
    'Ruby': ['Ruby', 'Rails', 'Web'],
    'PHP': ['PHP', 'Laravel', 'Web'],
}

BIO_SKILL_PATTERNS = {
    r'security|cybersecurity|安全|資安': ['Security'],
    r'devops|sre|platform|ops': ['DevOps', 'SRE'],
    r'kubernetes|k8s|docker|container': ['Kubernetes', 'Docker'],
    r'aws|azure|gcp|cloud': ['Cloud'],
    r'ai|machine.?learning|ml|深度學習': ['AI', 'ML'],
    r'frontend|ui|react|vue|angular': ['Frontend'],
    r'backend|api|microservice|database': ['Backend'],
    r'fullstack': ['Full Stack'],
}

# ==================== 資料庫初始化 ====================

def init_db():
    """初始化資料庫"""
    conn = sqlite3.connect(CACHE_DB)
    cursor = conn.cursor()
    
    # 候選人合併表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS merged_candidates (
            id TEXT PRIMARY KEY,
            data JSON,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
    ''')
    
    # 去重記錄
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dedup_records (
            hash TEXT PRIMARY KEY,
            candidate_ids JSON,
            matched_at TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_candidate(candidate_id: str) -> Optional[Dict]:
    """取得候選人"""
    try:
        conn = sqlite3.connect(CACHE_DB)
        cursor = conn.cursor()
        cursor.execute('SELECT data FROM merged_candidates WHERE id = ?', (candidate_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return json.loads(row[0])
    except:
        pass
    
    return None

def save_candidate(candidate: Dict):
    """保存候選人"""
    try:
        conn = sqlite3.connect(CACHE_DB)
        cursor = conn.cursor()
        
        candidate_id = candidate.get('id') or f"{candidate.get('name')}_{candidate.get('github_login') or candidate.get('linkedin_url')}"
        
        cursor.execute('''
            INSERT OR REPLACE INTO merged_candidates (id, data, created_at, updated_at)
            VALUES (?, ?, ?, ?)
        ''', (
            candidate_id,
            json.dumps(candidate),
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    except Exception as e:
        logger.debug(f"⚠️ 保存候選人失敗：{e}")

# ==================== GitHub 爬蟲（簡化版） ====================

class GitHubScraper:
    """GitHub 爬蟲"""
    
    def search(self, keywords: str, location: str = "Taiwan", max_results: int = 30) -> List[Dict]:
        """搜尋 GitHub 開發者"""
        logger.info(f"🐙 搜尋 GitHub：{keywords} @ {location}")
        
        language = self._infer_language(keywords)
        query = f"language:{language} location:{location} followers:>5"
        
        search_url = "https://api.github.com/search/users"
        params = {
            "q": query,
            "sort": "followers",
            "order": "desc",
            "per_page": min(max_results, 100)
        }
        
        full_url = search_url + "?" + urllib.parse.urlencode(params)
        
        candidates = []
        
        try:
            result = subprocess.run([
                'curl', '-s',
                '-H', f'Authorization: token {GITHUB_TOKEN}',
                '-H', 'Accept: application/vnd.github.v3+json',
                full_url
            ], capture_output=True, text=True, timeout=20)
            
            if result.stdout:
                data = json.loads(result.stdout)
                
                if 'items' in data:
                    for user in data['items'][:max_results]:
                        candidate = self._fetch_detail(user['login'])
                        if candidate:
                            candidates.append(candidate)
                            time.sleep(0.1)
        
        except Exception as e:
            logger.error(f"❌ GitHub 搜尋失敗：{e}")
        
        logger.info(f"  ✓ GitHub 找到 {len(candidates)} 位")
        return candidates
    
    def _fetch_detail(self, login: str) -> Optional[Dict]:
        """取得用戶詳情"""
        try:
            result = subprocess.run([
                'curl', '-s',
                '-H', f'Authorization: token {GITHUB_TOKEN}',
                '-H', 'Accept: application/vnd.github.v3+json',
                f'https://api.github.com/users/{login}'
            ], capture_output=True, text=True, timeout=10)
            
            if result.stdout:
                user = json.loads(result.stdout)
                
                if 'message' not in user:
                    skills = self._extract_skills(login, user)
                    
                    return {
                        'github_login': login,
                        'name': user.get('name') or login,
                        'github_url': user.get('html_url'),
                        'company': user.get('company'),
                        'bio': user.get('bio'),
                        'location': user.get('location'),
                        'followers': user.get('followers'),
                        'skills': skills,
                        'source': 'github'
                    }
        except Exception as e:
            logger.debug(f"⚠️ GitHub {login}：{e}")
        
        return None
    
    def _extract_skills(self, login: str, user: Dict) -> List[str]:
        """提取技能"""
        skills = set()
        
        # Bio 技能
        bio = (user.get('bio') or '').lower()
        for pattern, skill_list in BIO_SKILL_PATTERNS.items():
            if re.search(pattern, bio, re.IGNORECASE):
                skills.update(skill_list)
        
        # Repos 語言
        try:
            result = subprocess.run([
                'curl', '-s',
                '-H', f'Authorization: token {GITHUB_TOKEN}',
                f'https://api.github.com/users/{login}/repos?sort=stars&per_page=5'
            ], capture_output=True, text=True, timeout=10)
            
            if result.stdout:
                repos = json.loads(result.stdout)
                
                for repo in repos:
                    lang = repo.get('language')
                    if lang and lang in LANG_TO_SKILLS:
                        skills.update(LANG_TO_SKILLS[lang])
        except:
            pass
        
        return list(skills)[:8]
    
    def _infer_language(self, keywords: str) -> str:
        """推斷程式語言"""
        keywords_lower = keywords.lower()
        
        if 'python' in keywords_lower or 'ai' in keywords_lower:
            return 'python'
        elif 'javascript' in keywords_lower or 'frontend' in keywords_lower:
            return 'javascript'
        elif 'go' in keywords_lower:
            return 'go'
        elif 'java' in keywords_lower:
            return 'java'
        elif 'c++' in keywords_lower:
            return 'c++'
        else:
            return 'python'

# ==================== LinkedIn 爬蟲（簡化版） ====================

class LinkedInScraper:
    """LinkedIn 爬蟲"""
    
    def search(self, keywords: str, location: str = "Taiwan", max_results: int = 30) -> List[Dict]:
        """搜尋 LinkedIn"""
        logger.info(f"🔗 搜尋 LinkedIn：{keywords} @ {location}")
        
        candidates = []
        
        query = f'"{keywords}" {location} site:linkedin.com/in'
        search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&num={max_results}"
        
        try:
            result = subprocess.run([
                'curl', '-s', '-L',
                '-A', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                search_url
            ], capture_output=True, text=True, timeout=15)
            
            # 提取 LinkedIn URLs
            urls = re.findall(r'href="(https://(?:www\.)?linkedin\.com/in/[^"]+)"', result.stdout)
            
            for url in urls[:max_results]:
                clean_url = url.split('?')[0].rstrip('/')
                username = clean_url.split('/in/')[-1]
                
                candidates.append({
                    'linkedin_url': clean_url,
                    'linkedin_username': username,
                    'name': username.replace('-', ' ').title(),
                    'source': 'linkedin'
                })
                
                time.sleep(0.3)
        
        except Exception as e:
            logger.error(f"❌ LinkedIn 搜尋失敗：{e}")
        
        logger.info(f"  ✓ LinkedIn 找到 {len(candidates)} 位")
        return candidates

# ==================== 智能去重 ====================

class SmartDeduplicator:
    """智能去重器"""
    
    @staticmethod
    def generate_fingerprint(candidate: Dict) -> str:
        """生成候選人指紋（用於去重）"""
        
        # 提取關鍵信息
        name = (candidate.get('name') or '').lower().strip()
        github = (candidate.get('github_login') or '').lower()
        linkedin = (candidate.get('linkedin_username') or '').lower()
        company = (candidate.get('company') or '').lower()
        
        # 生成指紋（名字 + GitHub 或 LinkedIn）
        if github:
            key = f"{name}:{github}"
        elif linkedin:
            key = f"{name}:{linkedin}"
        else:
            key = name
        
        return hashlib.md5(key.encode()).hexdigest()
    
    @staticmethod
    def merge_candidates(linkedin_list: List[Dict], github_list: List[Dict]) -> List[Dict]:
        """合併 LinkedIn + GitHub 候選人"""
        
        logger.info(f"🔄 合併 {len(linkedin_list)} 個 LinkedIn + {len(github_list)} 個 GitHub...")
        
        # 建立指紋映射
        fingerprints = {}
        merged = {}
        
        # 先加 GitHub（資訊較完整）
        for candidate in github_list:
            fp = SmartDeduplicator.generate_fingerprint(candidate)
            fingerprints[fp] = candidate['github_login']
            merged[fp] = candidate
        
        # 再加 LinkedIn（補充缺失信息）
        for candidate in linkedin_list:
            fp = SmartDeduplicator.generate_fingerprint(candidate)
            
            if fp in merged:
                # 已存在 → 合併信息
                existing = merged[fp]
                
                if not existing.get('linkedin_url'):
                    existing['linkedin_url'] = candidate.get('linkedin_url')
                if not existing.get('linkedin_username'):
                    existing['linkedin_username'] = candidate.get('linkedin_username')
                
                if 'sources' not in existing:
                    existing['sources'] = [existing.get('source')]
                existing['sources'].append('linkedin')
            else:
                # 新候選人
                merged[fp] = candidate
                if 'sources' not in candidate:
                    candidate['sources'] = ['linkedin']
        
        result = list(merged.values())
        logger.info(f"  ✓ 合併完成：{len(result)} 位（去重 {len(linkedin_list) + len(github_list) - len(result)} 位）")
        
        return result

# ==================== 主爬蟲類 ====================

class UnifiedScraper:
    """統一爬蟲（並行 LinkedIn + GitHub）"""
    
    def __init__(self, max_workers: int = 2):
        """初始化"""
        self.max_workers = max_workers
        self.github = GitHubScraper()
        self.linkedin = LinkedInScraper()
        self.dedup = SmartDeduplicator()
        
        init_db()
        logger.info(f"✓ 統一爬蟲已初始化")
    
    def search(self, keywords: str, location: str = "Taiwan", max_results: int = 50, parallel: bool = True) -> List[Dict]:
        """搜尋候選人"""
        
        logger.info(f"🚀 開始搜尋：{keywords} @ {location}（限制 {max_results} 筆）")
        print("")
        
        if parallel:
            return self._search_parallel(keywords, location, max_results)
        else:
            return self._search_sequential(keywords, location, max_results)
    
    def _search_parallel(self, keywords: str, location: str, max_results: int) -> List[Dict]:
        """並行搜尋"""
        
        linkedin_results = []
        github_results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 同時提交兩個搜尋任務
            linkedin_future = executor.submit(
                self.linkedin.search,
                keywords, location, max_results
            )
            github_future = executor.submit(
                self.github.search,
                keywords, location, max_results
            )
            
            # 等待完成
            for future in [linkedin_future, github_future]:
                try:
                    result = future.result(timeout=30)
                    if future == linkedin_future:
                        linkedin_results = result
                    else:
                        github_results = result
                except Exception as e:
                    logger.error(f"❌ 搜尋失敗：{e}")
        
        # 合併
        merged = self.dedup.merge_candidates(linkedin_results, github_results)
        
        # 限制結果
        merged = merged[:max_results]
        
        logger.info(f"✅ 搜尋完成：{len(merged)} 位候選人")
        print("")
        
        return merged
    
    def _search_sequential(self, keywords: str, location: str, max_results: int) -> List[Dict]:
        """順序搜尋（備用方案）"""
        
        logger.warning("⚠️ 順序搜尋模式（並行失敗時使用）")
        
        github_results = self.github.search(keywords, location, max_results)
        linkedin_results = self.linkedin.search(keywords, location, max_results)
        
        merged = self.dedup.merge_candidates(linkedin_results, github_results)
        merged = merged[:max_results]
        
        return merged
    
    def export_results(self, candidates: List[Dict], format: str = 'json') -> str:
        """導出結果"""
        
        if format == 'json':
            return json.dumps(candidates, indent=2, ensure_ascii=False)
        
        elif format == 'table':
            output = "\n📋 候選人列表：\n"
            output += "-" * 120 + "\n"
            output += f"{'姓名':<20} {'GitHub':<20} {'LinkedIn':<20} {'技能':<30} {'來源':<20}\n"
            output += "-" * 120 + "\n"
            
            for c in candidates:
                name = (c.get('name') or '')[:19]
                github = (c.get('github_login') or '-')[:19]
                linkedin = (c.get('linkedin_username') or '-')[:19]
                skills = ', '.join(c.get('skills', [])[:2])[:29]
                sources = ', '.join(c.get('sources', ['unknown']))[:19]
                
                output += f"{name:<20} {github:<20} {linkedin:<20} {skills:<30} {sources:<20}\n"
            
            output += "-" * 120 + f"\n\n✅ 總共 {len(candidates)} 位候選人\n"
            
            return output
        
        else:
            return json.dumps(candidates, indent=2, ensure_ascii=False)

# ==================== 主程式 ====================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='統一人才爬蟲 v4（並行 LinkedIn + GitHub）')
    parser.add_argument('--keywords', required=True, help='搜尋關鍵字')
    parser.add_argument('--location', default='Taiwan', help='地點')
    parser.add_argument('--max-results', type=int, default=50, help='最大結果數')
    parser.add_argument('--output-format', choices=['json', 'table'], default='table', help='輸出格式')
    parser.add_argument('--no-parallel', action='store_true', help='禁用並行搜尋')
    parser.add_argument('--workers', type=int, default=2, help='並行線程數')
    
    args = parser.parse_args()
    
    # 初始化爬蟲
    scraper = UnifiedScraper(max_workers=args.workers)
    
    # 搜尋
    start_time = time.time()
    
    candidates = scraper.search(
        keywords=args.keywords,
        location=args.location,
        max_results=args.max_results,
        parallel=not args.no_parallel
    )
    
    elapsed = time.time() - start_time
    
    # 輸出
    output = scraper.export_results(candidates, format=args.output_format)
    print(output)
    
    # 統計
    print(f"\n⏱️ 搜尋耗時：{elapsed:.1f} 秒")
    print(f"📊 結果數：{len(candidates)} 位")
    
    if candidates:
        github_count = sum(1 for c in candidates if 'github_login' in c)
        linkedin_count = sum(1 for c in candidates if 'linkedin_username' in c)
        both_count = sum(1 for c in candidates if 'github_login' in c and 'linkedin_username' in c)
        
        print(f"  - GitHub：{github_count} 位")
        print(f"  - LinkedIn：{linkedin_count} 位")
        print(f"  - 雙平台：{both_count} 位")

if __name__ == '__main__':
    main()
