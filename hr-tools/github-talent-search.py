#!/usr/bin/env python3
"""
GitHub 人才搜尋 - 含技能推斷
功能：搜尋 GitHub 用戶 → 抓 bio + repo 推斷技能 → 回傳結構化 JSON
"""

import sys
import json
import time
import urllib.parse
import os

try:
    import requests
except ImportError:
    print("需要安裝 requests: pip3 install requests", file=sys.stderr)
    sys.exit(1)

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")  # 從環境變數讀取，沒有也行（但 rate limit 較低）
HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "HR-Talent-Search/1.0"
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"

SESSION = requests.Session()
SESSION.headers.update(HEADERS)

# 語言 → 技能對應
LANG_TO_SKILLS = {
    "Python": ["Python"],
    "JavaScript": ["JavaScript", "Node.js"],
    "TypeScript": ["TypeScript"],
    "Java": ["Java"],
    "C#": ["C#", ".NET"],
    "C++": ["C++"],
    "Go": ["Go", "Golang"],
    "Rust": ["Rust"],
    "PHP": ["PHP"],
    "Ruby": ["Ruby"],
    "Swift": ["Swift", "iOS"],
    "Kotlin": ["Kotlin", "Android"],
    "Shell": ["Shell", "Linux", "Bash"],
    "Dockerfile": ["Docker"],
    "HCL": ["Terraform", "Infrastructure"],
    "Jupyter Notebook": ["Python", "Machine Learning", "Data Science"],
}

# repo 名稱/描述關鍵字 → 技能推斷
KEYWORD_SKILLS = {
    "security": ["Security", "資安"],
    "ctf": ["CTF", "Security"],
    "pentest": ["滲透測試", "Security"],
    "exploit": ["Security"],
    "reverse": ["逆向工程", "Security"],
    "malware": ["Security"],
    "kubernetes": ["Kubernetes", "K8s"],
    "k8s": ["Kubernetes"],
    "docker": ["Docker"],
    "devops": ["DevOps"],
    "cicd": ["CI/CD"],
    "jenkins": ["Jenkins", "CI/CD"],
    "gitlab": ["GitLab", "CI/CD"],
    "aws": ["AWS", "雲端"],
    "gcp": ["GCP", "雲端"],
    "azure": ["Azure", "雲端"],
    "terraform": ["Terraform", "Infrastructure as Code"],
    "ansible": ["Ansible", "自動化"],
    "prometheus": ["Prometheus", "監控"],
    "grafana": ["Grafana", "監控"],
    "linux": ["Linux"],
    "nginx": ["Nginx"],
    "redis": ["Redis"],
    "mysql": ["MySQL", "資料庫"],
    "postgresql": ["PostgreSQL", "資料庫"],
    "mongodb": ["MongoDB", "資料庫"],
    "react": ["React", "前端"],
    "vue": ["Vue", "前端"],
    "angular": ["Angular", "前端"],
    "django": ["Django", "Python"],
    "flask": ["Flask", "Python"],
    "fastapi": ["FastAPI", "Python"],
    "spring": ["Spring", "Java"],
    "dotnet": [".NET", "C#"],
    "unity": ["Unity", "遊戲開發"],
    "machine-learning": ["Machine Learning", "AI"],
    "deep-learning": ["Deep Learning", "AI"],
    "tensorflow": ["TensorFlow", "AI"],
    "pytorch": ["PyTorch", "AI"],
    "selenium": ["Selenium", "自動化測試"],
    "pytest": ["pytest", "測試"],
    "automation": ["自動化"],
    "scraper": ["爬蟲"],
    "crawler": ["爬蟲"],
    "supply-chain": ["供應鏈"],
    "erp": ["ERP"],
    "accounting": ["會計"],
    "finance": ["財務"],
    "project-management": ["專案管理"],
    "ifrs": ["IFRS"],
    "network": ["網路"],
    "firewall": ["防火牆"],
    "acl": ["ACL", "網路管理"],
    "vpn": ["VPN", "網路"],
}

def github_get(url):
    """安全的 GitHub API 請求"""
    try:
        resp = SESSION.get(url, timeout=10)
        if resp.status_code == 403:
            print(f"  ⚠️  Rate limit 或需要 token: {url}", file=sys.stderr)
            return None
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"  ⚠️  請求失敗: {e}", file=sys.stderr)
        return None

def infer_skills_from_user(username):
    """從 GitHub 用戶的 bio + repos 推斷技能"""
    skills = set()
    
    # 1. 抓用戶個人資料
    user_data = github_get(f"https://api.github.com/users/{username}")
    if not user_data:
        return [], {}, ""
    
    bio = (user_data.get("bio") or "").lower()
    company = user_data.get("company") or ""
    name = user_data.get("name") or username
    blog = user_data.get("blog") or ""
    
    # 從 bio 推斷技能
    for keyword, kw_skills in KEYWORD_SKILLS.items():
        if keyword in bio:
            skills.update(kw_skills)
    
    # bio 中直接提到的技術
    bio_tech_patterns = [
        ("python", "Python"), ("java", "Java"), ("golang", "Go"),
        ("rust", "Rust"), ("c#", "C#"), ("c++", "C++"),
        ("security", "Security"), ("devops", "DevOps"),
        ("machine learning", "Machine Learning"), ("ai", "AI"),
        ("kubernetes", "Kubernetes"), ("docker", "Docker"),
        ("react", "React"), ("vue", "Vue"),
        (".net", ".NET"), ("aws", "AWS"), ("gcp", "GCP"), ("azure", "Azure"),
        ("linux", "Linux"), ("shell", "Shell Script"),
        ("selenium", "Selenium"), ("automation", "自動化"),
    ]
    for pattern, skill in bio_tech_patterns:
        if pattern in bio:
            skills.add(skill)
    
    # 2. 抓前 10 個 repo
    time.sleep(0.5)  # 避免 rate limit
    repos_data = github_get(f"https://api.github.com/users/{username}/repos?sort=updated&per_page=10&type=owner")
    
    languages_count = {}
    
    if repos_data:
        for repo in repos_data[:10]:
            # repo 語言
            lang = repo.get("language")
            if lang and lang in LANG_TO_SKILLS:
                languages_count[lang] = languages_count.get(lang, 0) + 1
                skills.update(LANG_TO_SKILLS[lang])
            
            # repo 名稱和描述關鍵字
            repo_text = f"{repo.get('name', '')} {repo.get('description', '') or ''}".lower()
            for keyword, kw_skills in KEYWORD_SKILLS.items():
                if keyword in repo_text:
                    skills.update(kw_skills)
            
            # repo topics
            for topic in (repo.get("topics") or []):
                topic_lower = topic.lower()
                for keyword, kw_skills in KEYWORD_SKILLS.items():
                    if keyword in topic_lower:
                        skills.update(kw_skills)
                # 直接加入 topic 作為技能
                if len(topic) > 2:
                    skills.add(topic.title())
    
    # 整理語言（按出現次數排序，取前 5）
    top_langs = sorted(languages_count.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return list(skills), dict(top_langs), name

def search_github_talent(job_title_en, location="Taiwan", max_results=10):
    """搜尋 GitHub 人才並推斷技能"""
    
    # URL encode
    encoded_title = urllib.parse.quote_plus(job_title_en)
    encoded_location = urllib.parse.quote_plus(location)
    
    search_url = f"https://api.github.com/search/users?q=location:{encoded_location}+{encoded_title}&per_page={max_results}"
    
    print(f"  → 搜尋: {search_url}", file=sys.stderr)
    
    search_result = github_get(search_url)
    if not search_result or "items" not in search_result:
        print("  ⚠️  搜尋失敗或無結果", file=sys.stderr)
        return []
    
    users = search_result["items"][:max_results]
    print(f"  → 找到 {len(users)} 位用戶，開始抓取技能...", file=sys.stderr)
    
    candidates = []
    
    for i, user in enumerate(users):
        username = user["login"]
        print(f"  [{i+1}/{len(users)}] 分析 {username}...", file=sys.stderr)
        
        skills, languages, name = infer_skills_from_user(username)
        
        candidate = {
            "name": name or username,
            "github_url": user["html_url"],
            "source": "GitHub",
            "platforms": ["github"],
            "skills": skills,
            "languages": languages,
            "bio_source": "github_inference"
        }
        
        candidates.append(candidate)
        
        # 速率限制：每個用戶間隔 1 秒
        if i < len(users) - 1:
            time.sleep(1)
    
    return candidates

def main():
    if len(sys.argv) < 2:
        print("用法: python3 github-talent-search.py <職位英文名稱> [地點]", file=sys.stderr)
        print("範例: python3 github-talent-search.py 'Security Engineer' Taiwan", file=sys.stderr)
        sys.exit(1)
    
    job_title = sys.argv[1]
    location = sys.argv[2] if len(sys.argv) > 2 else "Taiwan"
    
    print(f"🔍 GitHub 人才搜尋: {job_title} @ {location}", file=sys.stderr)
    
    candidates = search_github_talent(job_title, location)
    
    print(f"✅ 完成，共 {len(candidates)} 位候選人", file=sys.stderr)
    
    # 輸出 JSON 到 stdout
    print(json.dumps(candidates, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
