#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JD 分析器 - 從職缺描述自動提取搜尋和評分策略
版本：v1.0
用途：解析職缺 JD，生成「人才畫像」「企業畫像」「搜尋策略」
"""

import json
import sys
from typing import Dict, List, Tuple

class JDAnalyzer:
    """職缺 JD 分析器"""
    
    def __init__(self):
        """初始化"""
        self.job_data = None
        self.analysis = {
            "company_profile": {},
            "job_profile": {},
            "talent_profile": {},
            "search_strategy": {},
        }
    
    def load_job_from_db(self, job_id: int) -> Dict:
        """
        從 Step1ne API 讀取職缺資訊
        連接真實 API：https://backendstep1ne.zeabur.app/api/jobs/{job_id}
        """
        import requests
        import re
        
        try:
            # 連接真實 API
            api_url = f"https://backendstep1ne.zeabur.app/api/jobs/{job_id}"
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data"):
                    job_data = data["data"]
                    
                    # 解析 experience_required（從 "1年以上" 或 "3年以上" 提取數字）
                    exp_str = job_data.get("experience_required", "0")
                    exp_match = re.search(r'(\d+)', exp_str)
                    exp_years = int(exp_match.group(1)) if exp_match else 0
                    
                    # 解析薪資範圍（從 "60,000~80,000元/月" 提取數字）
                    salary_str = job_data.get("salary_range", "")
                    salary_min, salary_max = 0, 0
                    if salary_str and "~" in salary_str:
                        parts = salary_str.split("~")
                        try:
                            salary_min = int(parts[0].replace(",", "").strip())
                            salary_max = int(parts[1].replace(",", "").split("元")[0].strip())
                        except:
                            pass
                    
                    # 標準化欄位
                    return {
                        "id": job_data.get("id"),
                        "title": job_data.get("position_name", ""),
                        "company": job_data.get("client_company", ""),
                        "description": job_data.get("job_description", ""),
                        "company_profile": job_data.get("company_profile", ""),
                        "talent_profile": job_data.get("talent_profile", ""),
                        "key_skills": job_data.get("key_skills", ""),
                        "search_primary": job_data.get("search_primary", ""),
                        "search_secondary": job_data.get("search_secondary", ""),
                        "experience_required": exp_years,
                        "location": job_data.get("location", ""),
                        "salary_range": job_data.get("salary_range", ""),
                        "salary_min": salary_min,
                        "salary_max": salary_max,
                        "industry": job_data.get("industry_background", "") or "Tech",
                        "department": job_data.get("department", ""),
                    }
            
            # 如果 API 失敗，使用 fallback mock 數據
            print(f"⚠️ API 連接失敗（狀態 {response.status_code}），使用 fallback 數據")
            
        except Exception as e:
            print(f"⚠️ API 連接錯誤：{e}，使用 fallback 數據")
        
        # Fallback: 本地 mock 數據
        fallback_jobs = {
            51: {
                "id": 51,
                "title": "C++ Developer",
                "company": "UnityTech (一通數位有限公司)",
                "description": "C++ 後端開發",
                "company_profile": "香港金融科技企業",
                "talent_profile": "C++ 開發經驗",
                "key_skills": "C++, Docker, Kubernetes, Linux",
                "experience_required": 3,
                "location": "Taiwan",
                "salary_range": "60,000~80,000",
                "salary_min": 60000,
                "salary_max": 80000,
                "industry": "Fintech",
                "department": "技術部",
            },
            52: {
                "id": 52,
                "title": "Java Developer",
                "company": "UnityTech (一通數位有限公司)",
                "description": "Java Spring Boot 後端開發",
                "company_profile": "香港金融科技企業",
                "talent_profile": "Java 開發經驗",
                "key_skills": "Java, Spring Boot, Kubernetes, Redis",
                "experience_required": 2,
                "location": "Taiwan",
                "salary_range": "60,000~80,000",
                "salary_min": 60000,
                "salary_max": 80000,
                "industry": "Fintech",
                "department": "技術部",
            },
            15: {
                "id": 15,
                "title": "資安工程師",
                "company": "遊戲橘子集團",
                "description": "具備 Web/APP 開發背景的資安工程師，負責 SDLC 各階段安全實踐、弱點掃描與滲透測試",
                "company_profile": "遊戲娛樂公司，支付系統與雲端平台，資安需求高",
                "talent_profile": "Web/APP 開發背景資安導向工程師，熟 DevSecOps、OWASP、弱點掃描、滲透測試，具 CEH/CISSP/Security+ 加分",
                "key_skills": "DevSecOps, OWASP, penetration testing, vulnerability assessment, SAST, DAST, CEH, Web security, AppSec, security testing",
                "experience_required": 2,
                "location": "Taiwan",
                "salary_range": "面議",
                "salary_min": 50000,
                "salary_max": 100000,
                "industry": "Gaming",
                "department": "雲力",
            },
            19: {
                "id": 19,
                "title": ".NET 後端開發工程師",
                "company": "遊戲橘子集團",
                "description": ".NET Core 後端開發",
                "company_profile": "遊戲娛樂公司",
                "talent_profile": ".NET 開發經驗",
                "key_skills": ".NET Core, C#, MSSQL, Docker",
                "experience_required": 2,
                "location": "Taiwan",
                "salary_range": "面議",
                "salary_min": 50000,
                "salary_max": 100000,
                "industry": "Gaming",
                "department": "技術部",
            }
        }
        
        if job_id not in fallback_jobs:
            raise ValueError(f"職缺 ID {job_id} 不存在於 API 也不存在於本地 fallback 數據")
        
        return fallback_jobs[job_id]
    
    def analyze(self, job_id: int) -> Dict:
        """
        分析職缺，生成評分策略
        
        Args:
            job_id: 職缺 ID
        
        Returns:
            分析結果
        """
        # 1. 讀取職缺資訊
        self.job_data = self.load_job_from_db(job_id)
        
        # 2. 分析企業畫像
        self._analyze_company_profile()
        
        # 3. 分析職位畫像
        self._analyze_job_profile()
        
        # 4. 合成人才畫像 & 搜尋策略
        self._synthesize_talent_profile()
        self._generate_search_strategy()
        
        return self.analysis
    
    def _analyze_company_profile(self):
        """分析企業畫像"""
        raw_company_desc = self.job_data.get("company_profile") or ""
        self.analysis["company_profile"] = {
            "name": self.job_data["company"],
            "industry": self.job_data["industry"],
            "raw_description": raw_company_desc,          # ✅ 納入公司畫像原文
            "stage": self._infer_company_stage(),
            "culture": self._infer_company_culture(),
            "tech_stack_profile": self._infer_tech_stack(),
            "growth_opportunity": self._infer_growth_opportunity(),
        }
    
    def _analyze_job_profile(self):
        """分析職位畫像"""
        skills = self._extract_skills()
        
        self.analysis["job_profile"] = {
            "title": self.job_data["title"],
            "level": self._infer_job_level(),
            "location": self.job_data["location"],
            "salary_range": {
                "min": self.job_data["salary_min"],
                "max": self.job_data["salary_max"],
                "currency": "TWD",
            },
            "required_experience": self.job_data["experience_required"],
            "core_skills": skills["core"],
            "nice_to_have_skills": skills["nice_to_have"],
            "technical_depth": self._assess_technical_depth(skills["core"]),
            "key_responsibilities": self._extract_responsibilities(),
        }
    
    def _synthesize_talent_profile(self):
        """合成人才畫像 - 什麼樣的人才適合這個職位"""
        core_skills = self.analysis["job_profile"]["core_skills"]
        raw_talent_desc = self.job_data.get("talent_profile") or ""

        # ✅ 從人才畫像原文提取產業背景關鍵字
        industry_experience = self._extract_industry_from_talent_profile(raw_talent_desc)

        # ✅ 從人才畫像原文提取額外技能（補充 key_skills 沒有的）
        extra_skills = self._extract_skills_from_talent_profile(raw_talent_desc, core_skills)
        enriched_skills = core_skills + [s for s in extra_skills if s not in core_skills]

        self.analysis["talent_profile"] = {
            "raw_description": raw_talent_desc,               # ✅ 納入人才畫像原文
            "ideal_background": {
                "primary_skills": enriched_skills,
                "industry_experience": industry_experience,
                "required_years": self.job_data["experience_required"],
            },
            "personality_traits": [
                "細節導向",
                "系統思維",
                "持續學習",
                "問題解決",
            ],
            "growth_indicators": [
                "GitHub 高活躍度",
                "最近 6 個月有 commits",
                "開源貢獻",
                "技術部落格",
            ],
            "red_flags": [
                "無最近 commit",
                "skills 與職位差異太大",
                "2+ 年無行業相關經驗",
            ],
        }

    def _extract_industry_from_talent_profile(self, text: str) -> List[str]:
        """從人才畫像原文提取產業背景關鍵字"""
        INDUSTRY_KEYWORDS = {
            "金融科技": ["金融", "fintech", "證券", "交易", "brokerage", "金融科技"],
            "遊戲開發": ["遊戲", "game", "gaming", "橘子", "gamania"],
            "資訊安全": ["資安", "security", "滲透", "ctf", "弱點", "漏洞"],
            "雲端運算": ["雲端", "cloud", "aws", "gcp", "azure", "公有雲"],
            "DevOps": ["devops", "sre", "ci/cd", "運維", "維運"],
            "電商": ["電商", "ecommerce", "零售", "物流"],
            "AI/ML": ["ai", "機器學習", "deep learning", "llm", "nlp"],
        }
        text_lower = text.lower()
        found = []
        for industry, keywords in INDUSTRY_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                found.append(industry)
        return found if found else ["Tech"]

    def _extract_skills_from_talent_profile(self, text: str, existing_skills: List[str]) -> List[str]:
        """從人才畫像原文提取額外技能（補充 key_skills 沒有的）"""
        import re
        SKILL_PATTERNS = [
            # 常見技術關鍵字（直接比對）
            "Python", "Java", "Go", "C++", "C#", ".NET", "JavaScript", "TypeScript",
            "React", "Vue", "Node.js", "Spring Boot", "Django", "FastAPI",
            "Docker", "Kubernetes", "Terraform", "Ansible",
            "AWS", "GCP", "Azure", "Aliyun",
            "MySQL", "PostgreSQL", "MongoDB", "Redis", "Kafka",
            "Linux", "Bash", "Shell",
            "Git", "CI/CD", "Jenkins", "GitLab",
            "Prometheus", "Grafana", "ELK",
            "Nginx", "TCP/IP", "HTTP", "REST", "gRPC",
            "微服務", "分散式系統", "高可用", "負載均衡",
        ]
        existing_lower = {s.lower() for s in existing_skills}
        extra = []
        for skill in SKILL_PATTERNS:
            if skill.lower() in existing_lower:
                continue
            # 用詞界限比對，避免 "Go" 匹配到 "MongoDB" 裡的 "go"
            pattern = r'(?<![A-Za-z0-9])' + re.escape(skill) + r'(?![A-Za-z0-9])'
            if re.search(pattern, text, re.IGNORECASE):
                extra.append(skill)
        return extra[:5]  # 最多補充 5 個額外技能
    
    def _generate_search_strategy(self):
        """生成搜尋策略"""
        core_skills = self.analysis["job_profile"]["core_skills"]
        location = self.analysis["job_profile"]["location"]
        
        # GitHub 搜尋關鍵字
        github_keywords = self._generate_github_keywords(core_skills, location)
        
        # LinkedIn Google 搜尋
        linkedin_query = self._generate_linkedin_query(core_skills, location)
        
        self.analysis["search_strategy"] = {
            "github": {
                "keywords": github_keywords,
                "estimated_results": 15,
                "estimated_time_sec": 60,
            },
            "linkedin_google": {
                "query": linkedin_query,
                "estimated_results": 15,
                "estimated_time_sec": 45,
            },
            "deduplication": {
                "priority": ["github_score", "recent_activity", "skill_match"],
                "final_target": 25,
            },
            "total_estimated_time_sec": 120,
        }
    
    def _extract_skills(self) -> Dict[str, List[str]]:
        """從 JD 提取技能 - 優先使用 API 回傳的 key_skills / search_primary"""
        
        # 優先從 key_skills 欄位解析（實際 API 資料）
        key_skills_str = self.job_data.get("key_skills", "")
        search_primary_str = self.job_data.get("search_primary", "")
        search_secondary_str = self.job_data.get("search_secondary", "")
        
        if key_skills_str:
            # 解析技能列表（支援逗號、頓號、斜線等分隔符）
            import re
            all_skills = [s.strip() for s in re.split(r'[,、/；;]+', key_skills_str) if s.strip()]
            
            # 用 search_primary 決定核心技能順序（如果有）
            primary_skills = []
            if search_primary_str:
                primary_skills = [s.strip() for s in re.split(r'[,、/；;]+', search_primary_str) if s.strip()]
            
            # 核心技能 = search_primary 優先 + 剩餘 key_skills
            primary_set = set(s.lower() for s in primary_skills)
            core_remainder = [s for s in all_skills if s.lower() not in primary_set]
            core_skills = (primary_skills + core_remainder)[:8]  # 最多8個核心技能
            
            # nice_to_have = search_secondary
            nice_to_have = []
            if search_secondary_str:
                nice_to_have = [s.strip() for s in re.split(r'[,、/；;]+', search_secondary_str) if s.strip()]
            else:
                nice_to_have = core_remainder[5:] if len(core_remainder) > 5 else []
            
            return {
                "core": core_skills,
                "nice_to_have": nice_to_have,
            }
        
        # Fallback：從 JD description 解析（不用硬編碼）
        description = self.job_data.get("description", "")
        title = self.job_data.get("title", "").lower()
        
        # 根據職位類型給預設技能集
        if "java" in title:
            core_skills = ["Java", "Spring Boot", "Microservices", "Docker", "Kubernetes"]
            nice_to_have = ["Redis", "MongoDB", "Message Queue", "CI/CD"]
        elif "python" in title or "data" in title:
            core_skills = ["Python", "SQL", "Pandas", "Docker"]
            nice_to_have = ["Spark", "TensorFlow", "PyTorch"]
        elif "devops" in title or "維運" in title:
            core_skills = ["Docker", "Kubernetes", "Linux", "CI/CD"]
            nice_to_have = ["Terraform", "Ansible", "Helm"]
        else:
            # 最後 fallback：用 key_skills 原始字串
            core_skills = [self.job_data.get("title", "Developer")]
            nice_to_have = []
        
        return {
            "core": core_skills,
            "nice_to_have": nice_to_have,
        }
    
    def _extract_responsibilities(self) -> List[str]:
        """提取職責"""
        return [
            "設計並實現高效能遊戲伺服器架構",
            "開發實時通訊系統",
            "優化 CPU/GPU 效能",
            "建立 CI/CD 流程",
            "Code Review 與知識分享",
        ]
    
    def _infer_job_level(self) -> str:
        """推斷職位等級"""
        years = self.job_data["experience_required"]
        if years <= 1:
            return "junior"
        elif years <= 3:
            return "mid"
        else:
            return "senior"
    
    def _assess_technical_depth(self, skills: List[str]) -> str:
        """評估技術深度"""
        # 如果要求 5+ 個專門技能 = deep
        if len(skills) >= 8:
            return "deep"
        elif len(skills) >= 5:
            return "medium"
        else:
            return "broad"
    
    def _infer_company_stage(self) -> str:
        """推斷公司階段"""
        # 基於產業和薪資推斷
        return "growth"
    
    def _infer_company_culture(self) -> str:
        """推斷公司文化"""
        return "tech-driven"
    
    def _infer_tech_stack(self) -> List[str]:
        """推斷技術棧"""
        return ["C++", "Docker", "Kubernetes", "CUDA", "Redis"]
    
    def _infer_growth_opportunity(self) -> str:
        """推斷成長機會"""
        return "high"
    
    def _normalize_location_for_github(self, location: str) -> str:
        """標準化地點為 GitHub 搜尋友善格式（台灣城市 → Taiwan）"""
        taiwan_city_patterns = ['台北', '台中', '台南', '高雄', '新北', '桃園', '新竹', '苗栗', '彰化', '嘉義', '屏東', '宜蘭', '花蓮', '台東', '澎湖', '金門', '連江']
        for city in taiwan_city_patterns:
            if city in location:
                return 'Taiwan'
        return location or 'Taiwan'

    def _github_friendly_terms(self, skills: List[str]) -> List[str]:
        """將 JD 特定技術名詞轉換為 GitHub 搜尋友善的對應詞"""
        # 只轉換非 ASCII 或 GitHub 搜不到的詞
        GITHUB_TERM_MAP = {
            '多執行緒': 'multithreading',
            '網路程式設計': 'networking',
            '分散式系統': 'distributed-systems',
            '效能優化': 'high-performance',
            '記憶體管理': 'memory-management',
            'tcp/ip': 'networking',
            'google test': 'testing',
            'boost.asio': 'networking',
            '微服務': 'microservices',
            '雲端': 'cloud',
            '資安': 'security',
            '前端': 'frontend',
            '後端': 'backend',
            '全端': 'fullstack',
            '低延遲': 'low-latency',
            '高效能': 'high-performance',
            '金融科技': 'fintech',
        }
        result = []
        for s in skills:
            key = s.lower().strip()
            mapped = GITHUB_TERM_MAP.get(key)
            if mapped:
                result.append(mapped)
            elif s.isascii() and len(s) >= 2:
                result.append(s)
            # 中文且不在 map 中 → 跳過（GitHub 搜不到）
        return result

    def _generate_github_keywords(self, skills: List[str], location: str) -> List[str]:
        """生成 GitHub 搜尋關鍵字 - 優先使用 search_primary/secondary，再依職位類型智慧選取"""
        title_lower = self.job_data['title'].lower()
        skills_lower = [s.lower() for s in skills]
        
        # 標準化地點（避免 "台北市內湖區" 這類過於精細的地點出現在 GitHub 搜尋）
        normalized_location = self._normalize_location_for_github(location)

        # 優先使用 API 提供的 search_primary/search_secondary
        sp = self.job_data.get("search_primary", "")
        ss = self.job_data.get("search_secondary", "")
        if sp:
            primary_list = [s.strip() for s in sp.split(",") if s.strip()]
            secondary_list = [s.strip() for s in ss.split(",") if s.strip()] if ss else []
            primary = primary_list[0] if primary_list else skills[0]
            # 轉換 secondary 為 GitHub 友善詞（過濾中文/niche詞）
            secondary_github = self._github_friendly_terms(secondary_list[:3])
            secondary = " ".join(secondary_github[:2]) if secondary_github else ""
            title_short = self.job_data['title'].split('(')[0].strip()
            # 避免重複（例如 "Java Java Developer" → "Java Developer"）
            keyword1 = title_short if primary.lower() in title_short.lower() else f"{primary} {title_short}"
            # 判斷是否金融科技背景
            company_info = (self.job_data.get("company_profile") or "") + (self.job_data.get("talent_profile") or "")
            is_fintech = any(k in company_info for k in ["金融", "證券", "fintech", "Fintech", "納斯達克", "trading"])
            last_keyword = f"{primary} {normalized_location} fintech" if is_fintech else f"{primary} {normalized_location}"
            return [
                keyword1,
                f"{primary} {secondary}".strip() if secondary else f"{primary} microservices",
                f"{title_short} {normalized_location}",
                last_keyword,
            ]

        # 依職位類型決定主要搜尋關鍵字（不再盲目用 skills[0]）
        if any(k in title_lower for k in ['devops', 'sre', 'site reliability', '維運', 'infrastructure', 'platform']):
            priority_skills = [s for s in skills if s.lower() in ['docker', 'kubernetes', 'k8s', 'terraform', 'ansible', 'helm', 'ci/cd', 'jenkins', 'github actions', 'linux']]
            primary = priority_skills[0] if priority_skills else 'DevOps'
            secondary = ' '.join(priority_skills[1:3]) if len(priority_skills) > 1 else 'Kubernetes Docker'
        elif any(k in title_lower for k in ['cloud', 'aws', 'gcp', 'azure', '雲端']):
            priority_skills = [s for s in skills if s.lower() in ['aws', 'gcp', 'azure', 'terraform', 'kubernetes', 'docker', 'cloud']]
            primary = priority_skills[0] if priority_skills else 'cloud'
            secondary = ' '.join(priority_skills[1:3]) if len(priority_skills) > 1 else 'Terraform Kubernetes'
        elif any(k in title_lower for k in ['security', '資安', 'cybersecurity', 'infosec', 'penetration']):
            SEC_SKILLS = ['penetration testing', 'pentesting', 'devsecops', 'owasp', 'appsec',
                          'web security', 'application security', 'sast', 'dast', 'vulnerability',
                          'siem', 'soc', 'ctf', 'security', 'cybersecurity', 'firewall',
                          'burp suite', 'nessus', 'metasploit', 'python', 'linux']
            priority_skills = [s for s in skills if s.lower() in SEC_SKILLS or
                               any(sec in s.lower() for sec in ['security', 'pentest', 'owasp', 'vuln', 'devsec', 'appsec', 'sast', 'dast'])]
            primary = 'devsecops' if any('devsec' in s.lower() for s in skills) else (priority_skills[0].lower().replace(' ', '-') if priority_skills else 'web-security')
            secondary = ' '.join(s.lower().replace(' ', '-') for s in priority_skills[1:3]) if len(priority_skills) > 1 else 'owasp penetration-testing'
        elif any(k in title_lower for k in ['data', 'ml', 'ai', 'machine learning', '數據', '分析']):
            priority_skills = [s for s in skills if s.lower() in ['python', 'pytorch', 'tensorflow', 'spark', 'sql', 'pandas', 'scikit-learn', 'machine learning']]
            primary = priority_skills[0] if priority_skills else 'python'
            secondary = ' '.join(priority_skills[1:3]) if len(priority_skills) > 1 else 'machine-learning pytorch'
        elif any(k in title_lower for k in ['frontend', 'front-end', '前端', 'react', 'vue', 'angular']):
            priority_skills = [s for s in skills if s.lower() in ['react', 'vue', 'angular', 'typescript', 'javascript', 'next.js', 'nuxt']]
            primary = priority_skills[0] if priority_skills else 'react'
            secondary = ' '.join(priority_skills[1:3]) if len(priority_skills) > 1 else 'typescript javascript'
        elif any(k in title_lower for k in ['c++', 'cpp', 'c plus']):
            # C++ 高效能系統工程師：用 GitHub 能搜到的主題詞
            primary = 'cpp'
            secondary = 'high-performance networking'
            company_info = (self.job_data.get("company_profile") or "") + (self.job_data.get("talent_profile") or "")
            is_fintech = any(k in company_info for k in ["金融", "證券", "fintech", "Fintech", "納斯達克", "trading"])
            title_short = self.job_data['title'].split('(')[0].strip()
            return [
                f"cpp {title_short}",
                f"cpp high-performance networking",
                f"cpp multithreading distributed-systems",
                f"cpp {normalized_location} {'fintech' if is_fintech else 'systems'}",
            ]
        elif any(k in title_lower for k in ['backend', 'back-end', '後端', 'java', 'golang', 'go ', 'spring', 'node']):
            priority_skills = [s for s in skills if s.lower() in ['java', 'go', 'golang', 'python', 'spring', 'node.js', 'postgresql', 'redis', 'kafka', 'microservices']]
            primary = priority_skills[0] if priority_skills else skills[0]
            secondary = ' '.join(priority_skills[1:3]) if len(priority_skills) > 1 else ''
        else:
            # 預設：用最前面且最常在 GitHub 搜到的技術關鍵字
            searchable = self._github_friendly_terms(skills)
            primary = searchable[0] if searchable else skills[0]
            secondary = ' '.join(searchable[1:3]) if len(searchable) > 1 else ''

        title_short = self.job_data['title'].split('(')[0].strip()  # 去括號，如 "系統維運工程師 (DevOps)" → "系統維運工程師"

        return [
            f"{primary} {title_short}",
            f"{primary} {secondary}".strip(),
            f"{title_short} {normalized_location}",
            f"{primary} {normalized_location}",
        ]
    
    def _generate_linkedin_query(self, skills: List[str], location: str) -> str:
        """生成 LinkedIn Google 搜尋查詢"""
        query_parts = [
            "site:linkedin.com/in",
            self.job_data["title"],
        ] + skills[:3] + [location]
        
        return " ".join(query_parts)


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="JD 分析器")
    parser.add_argument("--job-id", type=int, required=True, help="職缺 ID")
    parser.add_argument("--output", type=str, default="jd-analysis.json", help="輸出檔案")
    
    try:
        args = parser.parse_args()
    except SystemExit:
        # 如果沒有傳入參數，不要 exit
        return None
    
    # 分析
    analyzer = JDAnalyzer()
    analysis = analyzer.analyze(args.job_id)
    
    # 輸出
    print(json.dumps(analysis, indent=2, ensure_ascii=False))
    
    # 儲存
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 分析完成，已儲存到 {args.output}")
    return analysis


if __name__ == "__main__":
    main()
