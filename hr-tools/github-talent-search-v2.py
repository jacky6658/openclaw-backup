#!/usr/bin/env python3
"""
GitHub 人才搜尋 v2 - 含技能推斷 + 待業判斷 + 活躍度判斷
功能：搜尋 GitHub 用戶 → 抓 bio + repo 推斷技能 + 判斷工作狀態 → 回傳結構化 JSON

新增功能：
1. 待業判斷（company + hireable）
2. 活躍度判斷（最後 commit 時間）
3. 履歷更新時間（updated_at）
"""

import sys
import json
import time
import urllib.parse
import os
from datetime import datetime, timezone

try:
    import requests
except ImportError:
    print("需要安裝 requests: pip3 install requests", file=sys.stderr)
    sys.exit(1)

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "HR-Talent-Search/2.0"
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

def calculate_days_ago(iso_timestamp):
    """計算距今天數"""
    if not iso_timestamp:
        return None
    try:
        dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        delta = now - dt
        return delta.days
    except:
        return None

def judge_availability(company, hireable, bio):
    """
    判斷是否可能待業/求職中
    
    判斷規則：
    1. hireable = True → 開放工作機會 ✅
    2. company = null/空/學校/自由業 → 可能待業 ⚠️
    3. bio 包含「待業」「求職」「looking for」 → 求職中 ✅
    
    回傳：
    - available: True/False/Unknown
    - reason: 判斷原因
    """
    reasons = []
    
    # 規則 1: hireable
    if hireable == True:
        reasons.append("開放工作機會(hireable)")
        return True, reasons
    
    # 規則 2: company 判斷
    company_lower = (company or "").lower()
    
    if not company:
        reasons.append("無公司資訊")
    elif any(keyword in company_lower for keyword in ["student", "university", "college", "學生", "大學"]):
        reasons.append("學生身份")
    elif any(keyword in company_lower for keyword in ["freelance", "自由", "獨立"]):
        reasons.append("自由工作者")
    
    # 規則 3: bio 關鍵字
    bio_lower = (bio or "").lower()
    if any(keyword in bio_lower for keyword in ["待業", "求職", "looking for", "open to", "seeking", "available"]):
        reasons.append("bio標示求職中")
        return True, reasons
    
    # 綜合判斷
    if reasons:
        return "Unknown", reasons  # 有跡象但不確定
    
    return False, ["在職中"]

def judge_activity(repos_data, profile_updated_at):
    """
    判斷活躍度
    
    判斷規則：
    1. 最後 commit < 1 個月 → 活躍 ✅
    2. 最後 commit 1-6 個月 → 普通 ⚠️
    3. 最後 commit > 6 個月 → 不活躍 ❌
    4. profile updated_at < 3 個月 → 最近有更新 ✅
    
    回傳：
    - activity_level: active/normal/inactive
    - last_commit_days: 最後 commit 天數
    - profile_updated_days: 個人資料更新天數
    """
    # 找最近的 commit
    last_commit_days = None
    if repos_data:
        pushed_dates = [repo.get("pushed_at") for repo in repos_data if repo.get("pushed_at")]
        if pushed_dates:
            latest_push = max(pushed_dates)
            last_commit_days = calculate_days_ago(latest_push)
    
    # 個人資料更新時間
    profile_updated_days = calculate_days_ago(profile_updated_at)
    
    # 判斷活躍度
    if last_commit_days is not None:
        if last_commit_days < 30:
            activity_level = "active"
        elif last_commit_days < 180:
            activity_level = "normal"
        else:
            activity_level = "inactive"
    else:
        activity_level = "unknown"
    
    return {
        "activity_level": activity_level,
        "last_commit_days": last_commit_days,
        "profile_updated_days": profile_updated_days
    }

def infer_skills_and_status(username):
    """從 GitHub 用戶的 bio + repos 推斷技能 + 工作狀態"""
    skills = set()
    
    # 1. 抓用戶個人資料
    user_data = github_get(f"https://api.github.com/users/{username}")
    if not user_data:
        return None
    
    bio = (user_data.get("bio") or "")
    company = user_data.get("company") or ""
    name = user_data.get("name") or username
    hireable = user_data.get("hireable")
    updated_at = user_data.get("updated_at")
    
    # 從 bio 推斷技能
    bio_lower = bio.lower()
    for keyword, kw_skills in KEYWORD_SKILLS.items():
        if keyword in bio_lower:
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
        if pattern in bio_lower:
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
                if len(topic) > 2:
                    skills.add(topic.title())
    
    # 整理語言
    top_langs = sorted(languages_count.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # 3. 判斷待業狀態
    available, availability_reasons = judge_availability(company, hireable, bio)
    
    # 4. 判斷活躍度
    activity_info = judge_activity(repos_data, updated_at)
    
    return {
        "name": name,
        "skills": list(skills),
        "languages": dict(top_langs),
        "company": company,
        "bio": bio,
        "hireable": hireable,
        "available": available,
        "availability_reasons": availability_reasons,
        "activity_level": activity_info["activity_level"],
        "last_commit_days": activity_info["last_commit_days"],
        "profile_updated_days": activity_info["profile_updated_days"],
        "profile_updated_at": updated_at
    }

def search_github_talent(job_title_en, location="Taiwan", max_results=50):
    """搜尋 GitHub 人才並推斷技能 + 狀態"""
    
    encoded_title = urllib.parse.quote_plus(job_title_en)
    encoded_location = urllib.parse.quote_plus(location)
    
    # GitHub API per_page 最大值是 100
    per_page = min(max_results, 100)
    search_url = f"https://api.github.com/search/users?q=location:{encoded_location}+{encoded_title}&per_page={per_page}"
    
    print(f"  → 搜尋: {search_url}", file=sys.stderr)
    
    search_result = github_get(search_url)
    if not search_result or "items" not in search_result:
        print("  ⚠️  搜尋失敗或無結果", file=sys.stderr)
        return []
    
    users = search_result["items"][:max_results]
    print(f"  → 找到 {len(users)} 位用戶，開始分析...", file=sys.stderr)
    
    candidates = []
    
    for i, user in enumerate(users):
        username = user["login"]
        print(f"  [{i+1}/{len(users)}] 分析 {username}...", file=sys.stderr)
        
        user_info = infer_skills_and_status(username)
        if not user_info:
            continue
        
        candidate = {
            "name": user_info["name"],
            "github_url": user["html_url"],
            "source": "GitHub",
            "platforms": ["github"],
            "skills": user_info["skills"],
            "languages": user_info["languages"],
            "company": user_info["company"],
            "bio": user_info["bio"],
            "hireable": user_info["hireable"],
            "available": user_info["available"],
            "availability_reasons": user_info["availability_reasons"],
            "activity_level": user_info["activity_level"],
            "last_commit_days": user_info["last_commit_days"],
            "profile_updated_days": user_info["profile_updated_days"],
            "profile_updated_at": user_info["profile_updated_at"]
        }
        
        candidates.append(candidate)
        
        # 速率限制
        if i < len(users) - 1:
            time.sleep(1)
    
    return candidates

def main():
    if len(sys.argv) < 2:
        print("用法: python3 github-talent-search-v2.py <職位英文名稱> [地點] [數量]", file=sys.stderr)
        print("範例: python3 github-talent-search-v2.py 'Security Engineer' Taiwan 50", file=sys.stderr)
        sys.exit(1)
    
    job_title = sys.argv[1]
    location = sys.argv[2] if len(sys.argv) > 2 else "Taiwan"
    max_results = int(sys.argv[3]) if len(sys.argv) > 3 else 50
    
    print(f"🔍 GitHub 人才搜尋 v2: {job_title} @ {location}", file=sys.stderr)
    print(f"📊 新增：待業判斷 + 活躍度判斷 + 履歷更新時間", file=sys.stderr)
    print(f"🎯 目標數量：最多 {max_results} 人", file=sys.stderr)
    print("", file=sys.stderr)
    
    candidates = search_github_talent(job_title, location, max_results)
    
    # 統計
    available_count = sum(1 for c in candidates if c["available"] == True)
    active_count = sum(1 for c in candidates if c["activity_level"] == "active")
    
    print(f"✅ 完成，共 {len(candidates)} 位候選人", file=sys.stderr)
    print(f"  → {available_count} 位可能求職中", file=sys.stderr)
    print(f"  → {active_count} 位近期活躍", file=sys.stderr)
    
    # 輸出 JSON
    print(json.dumps(candidates, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
