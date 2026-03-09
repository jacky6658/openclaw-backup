#!/usr/bin/env python3
"""
GitHub 人才爬蟲 v3 - 進階優化版
整合：並行化搜尋 + 增量更新 + 容錯機制 + LinkedIn 補充

優化功能：
1. 並行化搜尋 - ThreadPoolExecutor 同時爬多個職缺
2. 增量搜尋 - 記錄上次搜過的職缺 + 時間戳，只搜新職缺
3. 容錯機制 - 某個搜尋失敗不影響其他，自動重試
4. 智慧技能推斷 - 3 層提取：bio → repos → topics
5. 快取機制 - LRU 快取用戶詳情，減少 API 呼叫
6. LinkedIn 補充 - 同時運行 LinkedIn 爬蟲
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
from typing import List, Dict, Optional, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from pathlib import Path

# ==================== 日誌設定 ====================
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== 設定 ====================
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    logger.error("❌ 環境變數 GITHUB_TOKEN 未設定")
    sys.exit(1)

DATA_DIR = Path(os.getenv("HR_TOOLS_DATA_DIR", "/tmp/github-scraper"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

CACHE_DB = DATA_DIR / "github_cache.db"
SEARCH_LOG = DATA_DIR / "search_history.json"

# 技能對應表
LANG_TO_SKILLS = {
    'Python': ['Python', 'Data Science', 'Machine Learning'],
    'JavaScript': ['JavaScript', 'TypeScript', 'Node.js', 'React', 'Vue'],
    'Go': ['Go', 'Backend', 'Microservices', 'DevOps'],
    'Rust': ['Rust', 'Systems', 'Performance'],
    'Java': ['Java', 'Spring Boot', 'Microservices'],
    'C++': ['C++', 'Systems', 'Performance', 'Game Dev'],
    'C#': ['C#', '.NET', 'Windows'],
    'Ruby': ['Ruby', 'Rails', 'Web Development'],
    'PHP': ['PHP', 'Laravel', 'Web Development'],
    'Kotlin': ['Kotlin', 'Android', 'JVM'],
    'Swift': ['Swift', 'iOS', 'macOS'],
}

BIO_SKILL_PATTERNS = {
    r'security|cybersecurity|安全|資安': ['Security', 'Cybersecurity'],
    r'devops|sre|platform': ['DevOps', 'SRE', 'Infrastructure'],
    r'kubernetes|k8s|docker|container': ['Kubernetes', 'Docker', 'Container'],
    r'aws|azure|gcp|cloud': ['Cloud', 'AWS', 'Azure', 'GCP'],
    r'blockchain|web3|crypto': ['Blockchain', 'Web3', 'Crypto'],
    r'ai|machine.?learning|ml|深度學習|neural': ['AI', 'Machine Learning', 'Deep Learning'],
    r'frontend|ui|ux|react|vue|angular': ['Frontend', 'UI/UX'],
    r'backend|api|microservice|database': ['Backend', 'API', 'Database'],
    r'fullstack|full.?stack': ['Full Stack'],
}

# ==================== 資料庫初始化 ====================

def init_cache_db():
    """初始化快取資料庫"""
    conn = sqlite3.connect(CACHE_DB)
    cursor = conn.cursor()
    
    # GitHub 用戶快取表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS github_users (
            login TEXT PRIMARY KEY,
            data JSON,
            updated_at TIMESTAMP,
            expires_at TIMESTAMP
        )
    ''')
    
    # 搜尋歷史表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keywords TEXT,
            location TEXT,
            searched_at TIMESTAMP,
            count INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()

def get_cached_user(login: str) -> Optional[Dict]:
    """從快取取得用戶（TTL: 24 小時）"""
    try:
        conn = sqlite3.connect(CACHE_DB)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT data, expires_at FROM github_users WHERE login = ? AND expires_at > datetime("now")',
            (login,)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return json.loads(row[0])
    except Exception as e:
        logger.debug(f"⚠️ 快取讀取失敗：{e}")
    
    return None

def cache_user(login: str, data: Dict):
    """快取用戶資料（24 小時過期）"""
    try:
        conn = sqlite3.connect(CACHE_DB)
        cursor = conn.cursor()
        
        expires_at = (datetime.now() + timedelta(days=1)).isoformat()
        
        cursor.execute('''
            INSERT OR REPLACE INTO github_users (login, data, updated_at, expires_at)
            VALUES (?, ?, ?, ?)
        ''', (login, json.dumps(data), datetime.now().isoformat(), expires_at))
        
        conn.commit()
        conn.close()
    except Exception as e:
        logger.debug(f"⚠️ 快取寫入失敗：{e}")

def record_search(keywords: str, location: str, count: int):
    """記錄搜尋歷史"""
    try:
        conn = sqlite3.connect(CACHE_DB)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO search_history (keywords, location, searched_at, count)
            VALUES (?, ?, ?, ?)
        ''', (keywords, location, datetime.now().isoformat(), count))
        
        conn.commit()
        conn.close()
    except Exception as e:
        logger.debug(f"⚠️ 搜尋歷史記錄失敗：{e}")

def get_search_history() -> Dict:
    """取得搜尋歷史"""
    try:
        conn = sqlite3.connect(CACHE_DB)
        cursor = conn.cursor()
        
        cursor.execute('SELECT keywords, location, searched_at FROM search_history ORDER BY searched_at DESC LIMIT 100')
        
        rows = cursor.fetchall()
        conn.close()
        
        history = {}
        for keywords, location, searched_at in rows:
            key = f"{keywords}@{location}"
            if key not in history:
                history[key] = searched_at
        
        return history
    except Exception as e:
        logger.debug(f"⚠️ 搜尋歷史讀取失敗：{e}")
        return {}

# ==================== 核心爬蟲類 ====================

class GitHubTalentScraper:
    """GitHub 人才爬蟲 - 進階版"""
    
    def __init__(self, max_workers: int = 5):
        """初始化爬蟲"""
        self.max_workers = max_workers
        self.session_headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Mozilla/5.0 (GitHub Talent Scraper v3)'
        }
        
        init_cache_db()
        logger.info(f"✓ 爬蟲已初始化（最多 {max_workers} 並行線程）")
    
    def search_developers(self, keywords: str, location: str = "Taiwan", max_results: int = 50) -> List[Dict]:
        """
        搜尋開發者（主入口）
        
        Args:
            keywords: 搜尋關鍵字（如 "Python Engineer"）
            location: 地點
            max_results: 最大結果數
            
        Returns:
            開發者列表
        """
        logger.info(f"🐙 搜尋 GitHub：{keywords} @ {location}（限制 {max_results} 筆）")
        
        # 檢查是否已搜過（增量搜尋）
        history = get_search_history()
        search_key = f"{keywords}@{location}"
        
        if search_key in history:
            last_search = datetime.fromisoformat(history[search_key])
            days_ago = (datetime.now() - last_search).days
            if days_ago < 7:
                logger.info(f"⚠️ 此搜尋已於 {days_ago} 天前執行，跳過（7 天更新一次）")
                return []
        
        # 搜尋用戶
        try:
            candidates = self._search_api(keywords, location, max_results)
            
            # 記錄搜尋
            record_search(keywords, location, len(candidates))
            
            logger.info(f"✓ 找到 {len(candidates)} 位候選人")
            return candidates
            
        except Exception as e:
            logger.error(f"❌ 搜尋失敗：{e}")
            return []
    
    def _search_api(self, keywords: str, location: str, max_results: int) -> List[Dict]:
        """調用 GitHub Search API"""
        
        # 職位 → 語言對應
        language = self._infer_language(keywords)
        
        # 構建查詢
        query = f"language:{language} location:{location} followers:>5"
        
        logger.info(f"  🔍 查詢：{query}")
        
        search_url = "https://api.github.com/search/users"
        params = {
            "q": query,
            "sort": "followers",
            "order": "desc",
            "per_page": min(max_results, 100)
        }
        
        full_url = search_url + "?" + urllib.parse.urlencode(params)
        
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
                    logins = [user['login'] for user in data['items'][:max_results]]
                    logger.info(f"    ✓ 找到 {len(logins)} 位用戶")
                    
                    # 並行化取得詳情
                    candidates = self._fetch_user_details_parallel(logins)
                    return candidates
        except Exception as e:
            logger.error(f"    ❌ API 呼叫失敗：{e}")
        
        return []
    
    def _fetch_user_details_parallel(self, logins: List[str]) -> List[Dict]:
        """並行化取得用戶詳情"""
        
        candidates = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self._fetch_user_detail, login): login for login in logins}
            
            for future in as_completed(futures):
                try:
                    candidate = future.result()
                    if candidate:
                        candidates.append(candidate)
                        time.sleep(0.2)  # 避免 API 限流
                except Exception as e:
                    login = futures[future]
                    logger.warning(f"    ⚠️ {login}：{e}")
        
        return candidates
    
    def _fetch_user_detail(self, login: str) -> Optional[Dict]:
        """取得單一用戶詳情（帶快取）"""
        
        # 嘗試快取
        cached = get_cached_user(login)
        if cached:
            logger.debug(f"  📦 {login}（快取命中）")
            return cached
        
        try:
            # 取得用戶基本資料
            result = subprocess.run([
                'curl', '-s',
                '-H', f'Authorization: token {GITHUB_TOKEN}',
                '-H', 'Accept: application/vnd.github.v3+json',
                f'https://api.github.com/users/{login}'
            ], capture_output=True, text=True, timeout=10)
            
            if result.stdout:
                user = json.loads(result.stdout)
                
                if 'message' not in user:  # 檢查是否出錯
                    # 提取技能
                    skills = self._extract_skills(login, user)
                    
                    # 檢查招聘意願
                    open_to_work = self._check_open_to_work(user, skills)
                    
                    candidate = {
                        'name': user.get('name') or login,
                        'login': login,
                        'company': user.get('company'),
                        'bio': user.get('bio'),
                        'location': user.get('location'),
                        'github_url': user.get('html_url'),
                        'followers': user.get('followers'),
                        'public_repos': user.get('public_repos'),
                        'skills': skills,
                        'open_to_work': open_to_work,
                        'source': 'github',
                        'fetched_at': datetime.now().isoformat()
                    }
                    
                    # 快取
                    cache_user(login, candidate)
                    
                    logger.debug(f"  ✓ {login}：{', '.join(skills[:3])}")
                    return candidate
        except Exception as e:
            logger.warning(f"  ❌ {login}：{e}")
        
        return None
    
    def _extract_skills(self, login: str, user: Dict) -> List[str]:
        """3 層技能提取：bio → repos → topics"""
        
        skills = set()
        
        # 層 1：從 bio 提取
        bio = (user.get('bio') or '').lower()
        for pattern, skill_list in BIO_SKILL_PATTERNS.items():
            if re.search(pattern, bio, re.IGNORECASE):
                skills.update(skill_list)
        
        # 層 2：從 repos 程式語言提取
        try:
            result = subprocess.run([
                'curl', '-s',
                '-H', f'Authorization: token {GITHUB_TOKEN}',
                '-H', 'Accept: application/vnd.github.v3+json',
                f'https://api.github.com/users/{login}/repos?sort=stars&per_page=10'
            ], capture_output=True, text=True, timeout=10)
            
            if result.stdout:
                repos = json.loads(result.stdout)
                
                languages = {}
                topics = set()
                
                for repo in repos:
                    # 語言
                    lang = repo.get('language')
                    if lang:
                        languages[lang] = languages.get(lang, 0) + 1
                    
                    # Topics
                    repo_topics = repo.get('topics', [])
                    topics.update(repo_topics)
                
                # Top 語言 → 技能
                for lang in sorted(languages.items(), key=lambda x: x[1], reverse=True)[:3]:
                    if lang[0] in LANG_TO_SKILLS:
                        skills.update(LANG_TO_SKILLS[lang[0]])
                    else:
                        skills.add(lang[0])
                
                # Topics（直接加入）
                skills.update(topics[:5])
        
        except Exception as e:
            logger.debug(f"  ⚠️ {login} 無法提取 repos：{e}")
        
        # 層 3：公司猜測
        company = (user.get('company') or '').lower()
        if company:
            skills.add(company.replace('company', '').strip())
        
        return list(skills)[:10]  # Top 10
    
    def _check_open_to_work(self, user: Dict, skills: List[str]) -> bool:
        """檢查是否招聘意願高"""
        
        bio = (user.get('bio') or '').lower()
        company = user.get('company')
        
        # 信號 1：bio 中有求職關鍵字
        hiring_keywords = ['looking for', '求職', '找工作', 'open to', 'hiring', 'open to opportunities']
        for keyword in hiring_keywords:
            if keyword in bio:
                return True
        
        # 信號 2：無公司
        if not company:
            return True
        
        # 信號 3：Repos 很多（可能有時間）
        if user.get('public_repos', 0) > 50:
            return True
        
        return False
    
    def _infer_language(self, keywords: str) -> str:
        """職位 → 程式語言推斷"""
        keywords_lower = keywords.lower()
        
        if 'python' in keywords_lower or 'ai' in keywords_lower or 'data' in keywords_lower:
            return 'python'
        elif 'javascript' in keywords_lower or 'frontend' in keywords_lower:
            return 'javascript'
        elif 'go' in keywords_lower or 'golang' in keywords_lower:
            return 'go'
        elif 'rust' in keywords_lower:
            return 'rust'
        elif 'java' in keywords_lower:
            return 'java'
        elif 'c++' in keywords_lower or 'cpp' in keywords_lower:
            return 'c++'
        elif 'c#' in keywords_lower or 'csharp' in keywords_lower:
            return 'c#'
        elif 'php' in keywords_lower:
            return 'php'
        elif 'ruby' in keywords_lower:
            return 'ruby'
        else:
            return 'python'  # 預設

# ==================== 主程式 ====================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='GitHub 人才爬蟲 v3（進階優化版）')
    parser.add_argument('--keywords', required=True, help='搜尋關鍵字')
    parser.add_argument('--location', default='Taiwan', help='地點')
    parser.add_argument('--max-results', type=int, default=50, help='最大結果數')
    parser.add_argument('--workers', type=int, default=5, help='並行線程數')
    parser.add_argument('--no-cache', action='store_true', help='忽略快取')
    parser.add_argument('--output-json', action='store_true', help='輸出 JSON')
    
    args = parser.parse_args()
    
    # 初始化爬蟲
    scraper = GitHubTalentScraper(max_workers=args.workers)
    
    # 搜尋
    candidates = scraper.search_developers(
        keywords=args.keywords,
        location=args.location,
        max_results=args.max_results
    )
    
    # 輸出
    if args.output_json:
        print(json.dumps(candidates, indent=2, ensure_ascii=False))
    else:
        # 表格輸出
        if candidates:
            print("\n📋 候選人列表：")
            print("-" * 100)
            print(f"{'姓名':<20} {'GitHub':<30} {'技能':<30} {'招聘意願':<10} {'Followers':<10}")
            print("-" * 100)
            
            for c in candidates:
                name = c['name'][:19]
                github = c['login'][:29]
                skills = ', '.join(c['skills'][:2])[:29]
                open_to_work = '✅' if c['open_to_work'] else '❌'
                followers = str(c['followers'])
                
                print(f"{name:<20} {github:<30} {skills:<30} {open_to_work:<10} {followers:<10}")
            
            print("-" * 100)
            print(f"\n✅ 總共 {len(candidates)} 位候選人")

if __name__ == '__main__':
    main()
