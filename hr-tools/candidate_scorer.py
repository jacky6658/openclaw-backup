#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI 候選人評分器 - 基於 JD + 人才畫像 + 企業畫像的動態評分
版本：v1.0
用途：評分候選人，生成面試問題，生成評論
"""

import json
import sys
from typing import Dict, List, Tuple
from datetime import datetime

# 動態導入
try:
    from jd_analyzer import JDAnalyzer
except ImportError:
    # 如果無法導入，定義一個 stub
    JDAnalyzer = None


class CandidateScorer:
    """候選人評分器"""
    
    def __init__(self, jd_analysis: Dict):
        """
        初始化評分器
        
        Args:
            jd_analysis: JD 分析結果（包含人才、企業、職位畫像）
        """
        self.jd_analysis = jd_analysis
        self.job_profile = jd_analysis["job_profile"]
        self.talent_profile = jd_analysis["talent_profile"]
        self.company_profile = jd_analysis["company_profile"]
    
    def score(self, candidate: Dict) -> Dict:
        """
        評分單個候選人
        
        Args:
            candidate: {
                'name': '...',
                'github_url': '...',
                'linkedin_url': '...',
                'key_skills': [...],
                'years_experience': int,
                'recent_activity': bool,
                'github_commits_6m': int,
                'industry_background': str,
                'education': str,
            }
        
        Returns:
            {
                'name': '...',
                'score': 89,
                'grade': 'A+',
                'dimensions': {...},
                'matched_skills': [...],
                'missing_skills': [...],
                'probing_questions': [...],
                'conclusion': '...',
                'contact_method': '...',
            }
        """
        
        # 1. 計算各維度評分
        dimensions = self._calculate_dimensions(candidate)
        
        # 2. 計算綜合分數
        final_score = self._calculate_final_score(dimensions)

        # ✅ Open to Work 加分（主動求職，接觸成功率更高）
        open_to_work = candidate.get("open_to_work", False)
        has_photo = candidate.get("has_photo", False)
        if open_to_work:
            final_score = min(100, final_score + 5)

        grade = self._score_to_grade(final_score)
        
        # 3. 提取技能匹配
        matched_skills, missing_skills = self._analyze_skills(candidate)
        
        # 4. 生成面試問題
        probing_questions = self._generate_probing_questions(
            candidate, matched_skills, missing_skills
        )
        
        # 5. 識別優勢（需要 dimensions）
        strengths = self._identify_strengths(candidate, dimensions)
        
        # 6. 生成結論
        conclusion = self._generate_conclusion(
            candidate, final_score, grade, matched_skills, strengths
        )
        
        # 6. 建議聯繫方式
        contact_method = self._suggest_contact_method(candidate)
        
        return {
            "name": candidate["name"],
            "score": final_score,
            "grade": grade,
            "date": datetime.now().isoformat(),
            "position": self.job_profile["title"],
            "company": self.company_profile["name"],
            "dimensions": dimensions,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "strengths": strengths,
            "probing_questions": probing_questions,
            "salary_fit": self._assess_salary_fit(candidate),
            "conclusion": conclusion,
            "contact_method": contact_method,
            "github_url": candidate.get("github_url"),
            "linkedin_url": candidate.get("linkedin_url"),
            "open_to_work": open_to_work,      # ✅ 主動求職標記
            "has_photo": has_photo,             # ✅ 有頭像標記
            "evaluated_by": "YuQi",
            "evaluated_at": datetime.now().isoformat(),
        }
    
    def _calculate_dimensions(self, candidate: Dict) -> Dict[str, Dict]:
        """
        計算各維度評分（動態，基於 JD）
        
        維度來自 JD 分析：
        1. 核心技能匹配
        2. 經驗年資匹配
        3. 行業背景適配
        4. 成長信號
        5. 企業文化契合
        6. 可觸達性
        """
        
        dimensions = {}
        
        # 維度 1: 核心技能匹配 (35%)
        dimensions["skill_match"] = {
            "weight": 0.35,
            "score": self._calculate_skill_match(candidate),
            "description": "必備技能覆蓋度"
        }
        
        # 維度 2: 經驗年資匹配 (25%)
        dimensions["experience_match"] = {
            "weight": 0.25,
            "score": self._calculate_experience_match(candidate),
            "description": "年資與經驗對口度"
        }
        
        # 維度 3: 行業背景適配 (20%)
        dimensions["industry_fit"] = {
            "weight": 0.20,
            "score": self._calculate_industry_fit(candidate),
            "description": "行業經驗適配度"
        }
        
        # 維度 4: 成長信號 (10%)
        dimensions["growth_signal"] = {
            "weight": 0.10,
            "score": self._calculate_growth_signal(candidate),
            "description": "最近 6 月活躍度"
        }
        
        # 維度 5: 企業文化契合 (5%)
        dimensions["culture_fit"] = {
            "weight": 0.05,
            "score": self._calculate_culture_fit(candidate),
            "description": "企業文化符合度"
        }
        
        # 維度 6: 可觸達性 (5%)
        dimensions["reachability"] = {
            "weight": 0.05,
            "score": self._calculate_reachability(candidate),
            "description": "聯絡可能性"
        }
        
        return dimensions
    
    def _calculate_final_score(self, dimensions: Dict) -> int:
        """加權計算最終分數"""
        total_score = 0
        for dim_name, dim_data in dimensions.items():
            total_score += dim_data["score"] * dim_data["weight"]
        return int(total_score)
    
    def _score_to_grade(self, score: int) -> str:
        """分數轉等級"""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        else:
            return "D"
    
    # ========== 各維度評分方法 ==========
    
    def _calculate_skill_match(self, candidate: Dict) -> int:
        """核心技能匹配評分 (0-100) - 支援模糊/子字串比對"""
        candidate_skills_raw = [skill.lower().strip() for skill in candidate.get("key_skills", [])]
        core_skills = [skill.lower().strip() for skill in self.job_profile["core_skills"]]
        
        if not core_skills:
            return 50  # 無法評估
        
        def _skill_matches(candidate_token: str, core_skill: str) -> bool:
            """模糊比對：任一方是另一方的子字串，或單詞交集非空"""
            if candidate_token == core_skill:
                return True
            if candidate_token in core_skill or core_skill in candidate_token:
                return True
            # 多字詞技能的詞語交集（例 "spring boot" vs token "spring"）
            c_words = set(candidate_token.split())
            s_words = set(core_skill.split())
            if c_words & s_words:
                return True
            return False
        
        # 展開候選人技能（加入別名對應）
        candidate_skills_expanded = set(candidate_skills_raw)
        for raw_skill in candidate_skills_raw:
            for canonical, aliases in self.SKILL_ALIASES.items():
                if raw_skill in aliases or raw_skill == canonical:
                    candidate_skills_expanded.add(canonical)
                    candidate_skills_expanded.update(aliases)
        
        # 計算每個核心技能是否被匹配（含別名展開）
        matched_count = 0
        for core_skill in core_skills:
            # 取得核心技能的所有別名
            skill_all_forms = {core_skill}
            if core_skill in self.SKILL_ALIASES:
                skill_all_forms.update(self.SKILL_ALIASES[core_skill])
            for canonical, aliases in self.SKILL_ALIASES.items():
                if core_skill in aliases:
                    skill_all_forms.add(canonical)
                    skill_all_forms.update(aliases)
            
            found = False
            # 先檢查別名展開後的集合
            for sf in skill_all_forms:
                if sf in candidate_skills_expanded:
                    found = True
                    break
            
            if not found:
                # 再做模糊比對
                for c_skill in candidate_skills_raw:
                    for sf in skill_all_forms:
                        if _skill_matches(c_skill, sf):
                            found = True
                            break
                    if found:
                        break
            
            if found:
                matched_count += 1
        
        coverage = matched_count / len(core_skills)
        
        # 評分規則
        if coverage >= 0.7:
            return 95
        elif coverage >= 0.5:
            return 85
        elif coverage >= 0.3:
            return 70
        elif coverage >= 0.15:
            return 60
        else:
            return 45
    
    def _calculate_experience_match(self, candidate: Dict) -> int:
        """經驗年資匹配評分"""
        required_years = self.job_profile["required_experience"]
        candidate_years = candidate.get("years_experience", 0)
        
        if candidate_years >= required_years + 2:
            return 98  # 超過預期
        elif candidate_years >= required_years:
            return 90  # 達到要求（提高分數）
        elif candidate_years >= required_years - 1:
            return 80  # 接近要求
        else:
            return 50  # 不足
    
    def _calculate_industry_fit(self, candidate: Dict) -> int:
        """行業背景適配評分"""
        industry_background = candidate.get("industry_background", "").lower()
        target_industries = [i.lower() for i in self.talent_profile["ideal_background"]["industry_experience"]]
        
        # 檢查是否有相關行業經驗
        for target_ind in target_industries:
            if target_ind in industry_background:
                return 90
        
        # 檢查是否有相關技術經驗
        core_skills = set(skill.lower() for skill in self.job_profile["core_skills"])
        candidate_skills = set(skill.lower() for skill in candidate.get("key_skills", []))
        
        if len(candidate_skills & core_skills) >= 3:
            return 75
        else:
            return 50
    
    def _calculate_growth_signal(self, candidate: Dict) -> int:
        """成長信號評分"""
        # 檢查最近活動
        recent_activity = candidate.get("recent_activity", False)
        commits_6m = candidate.get("github_commits_6m", 0)
        
        if recent_activity and commits_6m >= 50:
            return 95
        elif recent_activity and commits_6m >= 20:
            return 80
        elif recent_activity:
            return 70
        else:
            return 40
    
    def _calculate_culture_fit(self, candidate: Dict) -> int:
        """企業文化契合評分"""
        # 簡化的文化匹配
        # 實際可以根據 GitHub bio、LinkedIn profile 的關鍵字判斷
        return 75  # 預設 75（中性）
    
    def _calculate_reachability(self, candidate: Dict) -> int:
        """可觸達性評分"""
        score = 50
        
        if candidate.get("github_url"):
            score += 25
        if candidate.get("linkedin_url"):
            score += 25
        
        return min(score, 100)
    
    # 技能別名映射（中英文共用，方便 _calculate_skill_match 和 _analyze_skills 都能用）
    SKILL_ALIASES = {
        # ── 通用 ──
        "微服務": ["microservices", "microservice", "micro-service", "micro service"],
        "訊息佇列": ["message queue", "messagequeue", "mq", "kafka", "rabbitmq"],
        "message queue": ["kafka", "rabbitmq", "mq", "amqp", "activemq", "message"],
        "ci/cd": ["cicd", "github actions", "jenkins", "gitlab ci", "devops", "cd", "ci"],
        "kubernetes": ["k8s", "kubectl", "helm", "k8"],
        "spring boot": ["spring", "springboot", "spring-boot"],
        "mongodb": ["mongo"],
        "openapi": ["swagger", "open api", "rest api", "restful", "api"],
        "金融科技": ["fintech", "finance", "financial", "trading", "securities"],
        "交易平台": ["trading platform", "trading", "brokerage"],
        # ── C++ 高效能系統 ──
        "boost.asio": ["networking", "asio", "socket", "network-programming", "network", "tcp", "libevent", "libuv"],
        "多執行緒": ["multithreading", "concurrent", "threading", "concurrency", "thread-safe", "parallelism", "pthread", "thread", "async"],
        "網路程式設計": ["networking", "socket", "tcp", "network", "network-programming", "sockets", "boost.asio", "asio"],
        "分散式系統": ["distributed", "distributed-systems", "microservice", "microservices", "cluster", "consensus", "raft", "zookeeper"],
        "效能優化": ["performance", "optimization", "low-latency", "high-performance", "profiling", "benchmark", "perf"],
        "記憶體管理": ["memory", "memory-management", "smart-pointer", "raii", "allocator", "heap"],
        "google test": ["testing", "gtest", "unit-test", "unittest", "test", "catch2", "doctest", "googletest"],
        "tcp/ip": ["tcp", "networking", "network", "socket", "protocol", "udp", "http"],
        "高效能": ["high-performance", "performance", "low-latency", "optimization"],
        "低延遲": ["low-latency", "high-performance", "performance", "real-time", "hft"],
        # ── 資安 ──
        "penetration testing": ["pentesting", "ctf", "security", "hacking", "exploit", "pentest"],
        "siem": ["security", "monitoring", "logging", "splunk", "elk", "wazuh"],
        "資安": ["security", "cybersecurity", "infosec", "soc", "ctf"],
        # ── 雲端 ──
        "雲端": ["cloud", "aws", "gcp", "azure", "cloud-native"],
        "容器化": ["docker", "kubernetes", "container", "k8s", "podman"],
        # ── .NET ──
        "c#": ["csharp", "dotnet", ".net", "asp.net", "net"],
        ".net": ["csharp", "c#", "dotnet", "asp.net"],
    }

    def _analyze_skills(self, candidate: Dict) -> Tuple[List[str], List[str]]:
        """分析技能匹配（模糊比對 + 別名）"""
        candidate_skills_raw = [s.lower().strip() for s in candidate.get("key_skills", [])]
        
        # 展開別名
        candidate_skills_expanded = set(candidate_skills_raw)
        for raw_skill in candidate_skills_raw:
            for canonical, aliases in self.SKILL_ALIASES.items():
                all_forms = [canonical] + aliases
                if raw_skill in all_forms:
                    for form in all_forms:
                        candidate_skills_expanded.add(form)
        
        matched = []
        missing = []
        for skill in self.job_profile["core_skills"]:
            skill_lower = skill.lower().strip()
            # 取得此技能的所有別名形式
            skill_all_forms = {skill_lower}
            if skill_lower in self.SKILL_ALIASES:
                skill_all_forms.update(self.SKILL_ALIASES[skill_lower])
            for canonical, aliases in self.SKILL_ALIASES.items():
                if skill_lower in aliases:
                    skill_all_forms.add(canonical)
                    skill_all_forms.update(aliases)
            
            found = False
            for c_skill in candidate_skills_expanded:
                for sf in skill_all_forms:
                    if (c_skill == sf or c_skill in sf or sf in c_skill or
                            set(c_skill.split()) & set(sf.split())):
                        found = True
                        break
                if found:
                    break
            
            if found:
                matched.append(skill)
            else:
                missing.append(skill)
        
        return matched, missing
    
    def _identify_strengths(self, candidate: Dict, dimensions: Dict) -> List[str]:
        """識別候選人優勢"""
        strengths = []
        
        # 根據評分維度識別優勢
        if dimensions["skill_match"]["score"] >= 80:
            strengths.append("技能高度匹配")
        
        if dimensions["experience_match"]["score"] >= 85:
            strengths.append("經驗年資充足")
        
        if dimensions["growth_signal"]["score"] >= 80:
            strengths.append("最近活躍，持續學習")
        
        if candidate.get("github_commits_6m", 0) >= 100:
            strengths.append("開發活躍度高")
        
        if candidate.get("education", "").lower().startswith("master"):
            strengths.append("高學歷背景")
        
        return strengths if strengths else ["基本資格符合"]
    
    def _generate_probing_questions(self, candidate: Dict, matched_skills: List[str], 
                                   missing_skills: List[str]) -> List[str]:
        """生成面試探討問題（5 題）"""
        questions = []
        
        # 問題 1: 核心技能深度
        if matched_skills:
            primary_skill = matched_skills[0]
            questions.append(
                f"請介紹你在 {primary_skill} 方面最複雜的專案架構和技術挑戰？"
            )
        else:
            questions.append(
                f"請介紹你在 {self.job_profile['core_skills'][0]} 相關領域的實務經驗？"
            )
        
        # 問題 2: 缺失技能或需確認的技能
        if missing_skills:
            questions.append(
                f"你在 {missing_skills[0]} 方面有接觸過嗎？學習曲線如何？"
            )
        else:
            questions.append(
                f"你在 {self.job_profile['core_skills'][1] if len(self.job_profile['core_skills']) > 1 else 'microservices'} "
                f"的實戰經驗中，最大的收穫是什麼？"
            )
        
        # 問題 3: 系統設計或架構
        questions.append(
            "請描述一個你設計過的系統架構，特別是在效能優化和可擴展性方面的考量？"
        )
        
        # 問題 4: 團隊協作和代碼品質
        questions.append(
            "在過去的團隊協作中，你如何進行 Code Review？遇過什麼樣的代碼品質問題？"
        )
        
        # 問題 5: 公司適配和成長動力
        industry = self.company_profile.get("industry", "")
        questions.append(
            f"你對 {industry} 領域的發展趨勢有什麼看法？為什麼想加入我們？"
        )
        
        return questions[:5]  # 確保恰好 5 題
    
    def _generate_conclusion(self, candidate: Dict, score: int, grade: str, 
                           matched_skills: List[str], strengths: List[str] = None) -> str:
        """生成 AI 評論結論（200-300 字）"""
        
        if strengths is None:
            strengths = []
        
        strengths_summary = ", ".join(strengths) if strengths else "基本資格符合"
        matched_summary = ", ".join(matched_skills[:3]) if matched_skills else "待確認"
        
        if grade in ["A+", "A"]:
            conclusion = (
                f"{candidate['name']} 是一位優秀的候選人，"
                f"核心技能（{matched_summary}）與職位需求高度對齐。"
                f"他/她具備 {candidate.get('years_experience', 0)}+ 年相關經驗，"
                f"最近的開發活躍度也顯示其持續學習和技術熱情。\n\n"
                f"主要優勢：{strengths_summary}。\n\n"
                f"建議優先聯繫和面試。"
            )
        elif grade == "B":
            conclusion = (
                f"{candidate['name']} 具備基本資格，"
                f"部分技能（{matched_summary}）符合需求，"
                f"但在某些關鍵技能上需要進一步確認。\n\n"
                f"適合作為備選候選人，"
                f"面試時重點確認缺失技能的學習潛力。"
            )
        else:
            conclusion = (
                f"{candidate['name']} 的背景與職位需求有一定差距。"
                f"雖然部分技能相關，"
                f"但在核心需求上仍需補強。\n\n"
                f"不建議此時進行深入評估，"
                f"可作為長期觀察的候選人。"
            )
        
        return conclusion
    
    def _assess_salary_fit(self, candidate: Dict) -> str:
        """評估薪資符合度"""
        # 簡化版本，實際應根據候選人過往薪資歷史判斷
        years = candidate.get("years_experience", 0)
        required_years = self.job_profile["required_experience"]
        
        if years > required_years + 2:
            return "可能期望更高薪資"
        elif years >= required_years:
            return "符合預算範圍"
        else:
            return "薪資預期應在範圍下限"
    
    def _suggest_contact_method(self, candidate: Dict) -> str:
        """建議聯繫方式"""
        methods = []
        
        if candidate.get("github_url"):
            methods.append("GitHub Issues（推薦，專業且禮貌）")
        
        if candidate.get("linkedin_url"):
            methods.append("LinkedIn InMail（次選）")
        
        return " / ".join(methods) if methods else "直接 Email（如果有）"


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="候選人評分器")
    parser.add_argument("--jd-analysis", type=str, required=True, 
                       help="JD 分析檔案（jd-analysis.json）")
    parser.add_argument("--candidate", type=str, required=True,
                       help="候選人資料（JSON）")
    parser.add_argument("--output", type=str, default="score.json",
                       help="輸出檔案")
    
    args = parser.parse_args()
    
    # 讀取 JD 分析
    with open(args.jd_analysis, 'r', encoding='utf-8') as f:
        jd_analysis = json.load(f)
    
    # 讀取候選人資料
    with open(args.candidate, 'r', encoding='utf-8') as f:
        candidate = json.load(f)
    
    # 評分
    scorer = CandidateScorer(jd_analysis)
    score_result = scorer.score(candidate)
    
    # 輸出
    print(json.dumps(score_result, indent=2, ensure_ascii=False))
    
    # 儲存
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(score_result, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 評分完成，已儲存到 {args.output}")


if __name__ == "__main__":
    main()
