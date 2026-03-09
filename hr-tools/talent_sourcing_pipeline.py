#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智慧人才搜尋閉環系統 - 主編排器
版本：v1.0
功能：JD 分析 → 雙管道搜尋 → 去重 → AI 評分 → 批量上傳
"""

import os
import sys
import json
import argparse
import time
import random
from typing import Dict, List, Tuple
from datetime import datetime
import subprocess
import requests

# 導入自建模組
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from jd_analyzer import JDAnalyzer
    from candidate_scorer import CandidateScorer
    from human_behavior import CrawlLogger, HumanBehavior
    from deduplication_handler import DeduplicationHandler, UploadReporter
except ImportError as e:
    print(f"❌ 導入失敗: {e}")
    print(f"   嘗試路徑: {current_dir}")
    print(f"   可用文件: {os.listdir(current_dir)[:10]}")
    sys.exit(1)


class TalentSourcingPipeline:
    """人才搜尋閉環系統"""
    
    def __init__(self, job_id: int, dry_run=False, test_zero_dedup=False):
        """
        初始化
        
        Args:
            job_id: 職缺 ID
            dry_run: 是否為 dry-run 模式
            test_zero_dedup: 測試模式 - 讓去重後為 0 人，驗證智慧回退邏輯
        """
        self.job_id = job_id
        self.dry_run = dry_run
        self.test_zero_dedup = test_zero_dedup  # 測試模式
        self.api_base = "https://backendstep1ne.zeabur.app/api"
        
        # 初始化日誌
        self.logger = None
        
        # 分析結果存儲
        self.jd_analysis = None
        self.github_candidates = []
        self.linkedin_candidates = []
        self.final_candidates = []
        self.scored_candidates = []
        
        # 去重和回報機制
        self.dedup_handler = DeduplicationHandler(self.api_base)
        self.upload_reporter = None

        # 🛡️ 反爬蟲機制 - API 速率追蹤
        self._github_requests = []    # 每次請求時間（秒）
        self._brave_requests = []     # Brave API 請求時間
        self._GITHUB_SEARCH_LIMIT = 20  # 安全門檻（實際 30/min，留緩衝）
        self._BRAVE_LIMIT = 4           # Brave 安全門檻（/sec，更保守）

        # 🔴 Circuit Breaker（連續錯誤自動熔斷）
        self._github_consecutive_errors = 0
        self._brave_consecutive_errors = 0
        self._MAX_CONSECUTIVE_ERRORS = 3   # 連續 3 次 429/error → 暫停

        # 📊 每日請求計數器（防止累積超標）
        self._github_daily_count = 0
        self._brave_daily_count = 0
        self._GITHUB_DAILY_LIMIT = 300   # GitHub API 每日安全上限
        self._BRAVE_DAILY_LIMIT = 150    # Brave API 每日安全上限

        # 🚫 禁止直接存取的域名（不走任何直連爬蟲）
        self._BLOCKED_DIRECT_DOMAINS = [
            'linkedin.com', 'www.linkedin.com',
            'facebook.com', 'instagram.com',
        ]

        # 🎭 User-Agent 輪換池（模擬不同瀏覽器）
        self._USER_AGENTS = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        self._ua_index = 0  # 輪流使用
    
    def run(self):
        """執行完整流程"""
        
        print("=" * 60)
        print("🚀 智慧人才搜尋閉環系統")
        print(f"   職缺 ID: {self.job_id}")
        print(f"   模式: {'DRY-RUN' if self.dry_run else 'EXECUTE'}")
        print("=" * 60)
        
        # 階段 1: JD 分析
        print("\n📋 【第一階段】JD 深度分析...")
        self._stage_jd_analysis()
        
        if self.dry_run:
            print("\n✅ DRY-RUN 模式 - 分析完成，未執行搜尋")
            self._print_dry_run_summary()
            return
        
        # 階段 2: 搜尋
        print("\n🔍 【第二階段】雙管道智慧搜尋...")
        self._stage_search()
        
        # 階段 3: 去重
        print("\n🧹 【第三階段】智慧去重...")
        self._stage_deduplication()
        
        # 階段 4: 評分
        print("\n🤖 【第四階段】AI 配對評分...")
        self._stage_scoring()
        
        # 階段 5: 上傳
        print("\n📤 【第五階段】批量上傳系統...")
        self._stage_upload()
        
        # 完成
        print("\n" + "=" * 60)
        print("✅ 完整流程執行完成！")
        print("=" * 60)
        self._print_final_summary()
    
    def _stage_jd_analysis(self):
        """JD 分析"""
        try:
            analyzer = JDAnalyzer()
            self.jd_analysis = analyzer.analyze(self.job_id)
            
            print(f"  ✅ 企業: {self.jd_analysis['company_profile']['name']}")
            print(f"  ✅ 職位: {self.jd_analysis['job_profile']['title']}")
            print(f"  ✅ 必備技能: {', '.join(self.jd_analysis['job_profile']['core_skills'][:5])}")
            print(f"  ✅ 搜尋策略已生成")
            
            # 儲存分析結果
            with open('/tmp/jd-analysis.json', 'w', encoding='utf-8') as f:
                json.dump(self.jd_analysis, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            print(f"  ❌ 分析失敗: {e}")
            raise
    
    def _stage_search(self):
        """搜尋（GitHub + LinkedIn Google）"""
        import signal

        def _search_timeout_handler(signum, frame):
            raise TimeoutError("搜尋階段超時（180s），強制跳過剩餘搜尋")

        search_start_time = time.time()

        # 🛡️ 整體搜尋 180 秒 hard limit
        signal.signal(signal.SIGALRM, _search_timeout_handler)
        signal.alarm(180)

        try:
            # GitHub 搜尋
            print("\n  📍 GitHub 搜尋...")
            github_start = time.time()
            self._search_github()
            github_duration = time.time() - github_start
            print(f"     ✅ 找到 {len(self.github_candidates)} 位候選人 ({github_duration:.1f}s)")

            # 搜尋間隔
            print(f"\n  ⏸️ 搜尋間隔中... ", end='', flush=True)
            HumanBehavior.batch_pause(2, 3)  # 縮短：3-5s → 2-3s
            print("✅")

            # LinkedIn Google 搜尋
            print(f"\n  💼 LinkedIn Google 搜尋...")
            linkedin_start = time.time()
            self._search_linkedin_google()
            linkedin_duration = time.time() - linkedin_start
            print(f"     ✅ 找到 {len(self.linkedin_candidates)} 位候選人 ({linkedin_duration:.1f}s)")

        except TimeoutError as e:
            elapsed = time.time() - search_start_time
            print(f"\n  ⏱️ {e}（已用 {elapsed:.0f}s）")
            print(f"     GitHub: {len(self.github_candidates)} 位 / LinkedIn: {len(self.linkedin_candidates)} 位（部分結果）")
        finally:
            signal.alarm(0)

        search_duration = time.time() - search_start_time
        print(f"\n  【搜尋階段耗時】{search_duration:.1f} 秒")
    
    def _extract_all_keywords(self) -> dict:
        """從 jd_analysis 提取完整中英文關鍵字集合
        
        Returns:
            {
                'all': [所有關鍵字],
                'english': [英文技術詞],
                'chinese': [中文詞],
                'job_title': '職位名稱',
                'github_list': [GitHub搜尋用列表],
                'linkedin_query': '完整 LinkedIn 查詢字串',
            }
        """
        strategy = self.jd_analysis.get('search_strategy', {})
        job_profile = self.jd_analysis.get('job_profile', {})

        # GitHub 關鍵字（完整列表）
        github_kws_raw = strategy.get('github', {}).get('keywords', [])
        if isinstance(github_kws_raw, list):
            github_list = github_kws_raw  # 保留全部
        else:
            github_list = [str(github_kws_raw)]

        # LinkedIn 查詢（完整字串）
        linkedin_query = strategy.get('linkedin_google', {}).get('query', '')
        if isinstance(linkedin_query, list):
            linkedin_query = ' '.join(linkedin_query)

        # 彙整所有詞（去重）
        all_kws = []
        for kw in github_list:
            all_kws.extend(kw.split())
        all_kws.extend(linkedin_query.split())
        all_kws.extend(job_profile.get('core_skills', []))

        # 分中/英
        english_kws = list(dict.fromkeys(
            w for w in all_kws if w.isascii() and len(w) >= 2 and w.lower() not in (
                'in', 'on', 'at', 'the', 'and', 'or', 'for', 'with', 'site:linkedin.com/in',
                'taiwan', 'engineer', 'developer', 'site:github.com'
            )
        ))
        chinese_kws = list(dict.fromkeys(
            w for w in all_kws if not w.isascii() and len(w) >= 2
        ))

        job_title = job_profile.get('title', '')

        return {
            'all': list(dict.fromkeys(all_kws)),
            'english': english_kws,
            'chinese': chinese_kws,
            'job_title': job_title,
            'github_list': github_list,
            'linkedin_query': linkedin_query,
        }

    def _search_github(self, relax=False):
        """GitHub 真實搜尋（全關鍵字 + Brave fallback）
        
        改進：
        - 遍歷所有 GitHub 關鍵字（不再只用前 2 個）
        - GitHub 失敗/無結果 → Brave fallback（含中英文搜尋）
        """
        try:
            kws = self._extract_all_keywords()
            max_results = 30 if relax else 20
            seen = set()
            total_found = 0
            github_ok = False

            print(f"     🔑 GitHub 關鍵字組: {kws['github_list']}")

            # 遍歷所有 GitHub 關鍵字（全部使用，不截斷）
            for kw in kws['github_list']:
                if total_found >= max_results:
                    break
                results = self._real_github_search(kw, max_results=10)
                new_results = []
                for r in results:
                    uid = r.get('github_url', r.get('name', ''))
                    if uid not in seen:
                        seen.add(uid)
                        new_results.append(r)
                if new_results:
                    github_ok = True
                    self.github_candidates.extend(new_results)
                    total_found += len(new_results)
                    print(f"       ✅ [{kw[:40]}] 找到 {len(new_results)} 位")
                else:
                    print(f"       ⚠️  [{kw[:40]}] 無結果")
                time.sleep(1)  # GitHub API 速率控制

            print(f"     ✅ GitHub 共找到 {total_found} 位候選人")

            # Brave fallback：GitHub 找到 < 5 人或全部失敗
            if total_found < 5:
                print(f"     🔄 GitHub 結果不足，啟動 Brave 全關鍵字搜尋...")
                # 傳入完整關鍵字（中 + 英）
                all_kw_str = ' '.join(kws['english'][:5] + kws['chinese'][:3])
                brave_results = self._search_brave_github_fallback(
                    all_kw_str, max_results, kws=kws
                )
                new_brave = []
                for r in brave_results:
                    uid = r.get('github_url', r.get('name', ''))
                    if uid not in seen:
                        seen.add(uid)
                        new_brave.append(r)
                if new_brave:
                    self.github_candidates.extend(new_brave)
                    print(f"     ✅ Brave fallback 補充 {len(new_brave)} 位候選人")
                else:
                    print(f"     ⚠️  Brave fallback 也無結果")

        except Exception as e:
            print(f"     ❌ GitHub 搜尋失敗: {e}，嘗試 Brave fallback...")
            try:
                kws = self._extract_all_keywords()
                all_kw_str = ' '.join(kws['english'][:5] + kws['chinese'][:3])
                brave_results = self._search_brave_github_fallback(all_kw_str, 20, kws=kws)
                if brave_results:
                    self.github_candidates.extend(brave_results)
                    print(f"     ✅ Brave fallback 找到 {len(brave_results)} 位候選人")
            except Exception as e2:
                print(f"     ❌ Brave fallback 也失敗: {e2}")

    def _search_linkedin_google(self, relax=False):
        """LinkedIn 真實搜尋（全關鍵字：中文職稱 + 英文技術詞）
        
        改進：
        - 使用完整 LinkedIn 查詢字串（不再截斷）
        - 額外生成中文職稱查詢 + 英文技術詞查詢
        - 搜尋範圍擴大到 104/CakeResume 等台灣平台
        - ⏱️ 限制最多 2 個 query，防止超時（資安/.NET 問題修復）
        """
        import signal

        def _timeout_handler(signum, frame):
            raise TimeoutError("LinkedIn 搜尋超時（90s）")

        try:
            # 🛡️ 整體 90 秒 timeout 保護（防止 cron 被卡住）
            signal.signal(signal.SIGALRM, _timeout_handler)
            signal.alarm(90)

            kws = self._extract_all_keywords()
            max_results = 20 if relax else 10

            # 建立多語言查詢清單（最多 2 個，防超時）
            queries = []

            # 1. 原始 LinkedIn 查詢（最有效，優先）
            if kws['linkedin_query']:
                queries.append(kws['linkedin_query'])

            # 2. 中文職稱搜尋（第二優先）
            if kws['job_title'] and len(queries) < 2:
                queries.append(f'site:linkedin.com/in "{kws["job_title"]}" 台灣')

            # 備用：英文技術詞組合（若前兩個未設定）
            if len(queries) < 2 and kws['english']:
                eng_combo = ' '.join(kws['english'][:3])
                queries.append(f'site:linkedin.com/in {eng_combo} Taiwan')

            print(f"     🔑 LinkedIn 查詢數: {len(queries)}（限制最多 2，避免超時）")
            seen = set()
            total_found = 0

            for query in queries:
                if total_found >= max_results:
                    break
                print(f"       🔍 [{query[:60]}]")
                results = self._real_linkedin_search(query, max_results=10)
                new_results = []
                for r in results:
                    uid = r.get('linkedin_url', r.get('name', ''))
                    if uid not in seen:
                        seen.add(uid)
                        new_results.append(r)
                if new_results:
                    self.linkedin_candidates.extend(new_results)
                    total_found += len(new_results)
                    print(f"         ✅ 找到 {len(new_results)} 位")
                else:
                    print(f"         ⚠️  無結果")
                time.sleep(0.8)  # Brave API 速率控制（從 1.5s 縮短）

            if total_found > 0:
                print(f"     ✅ LinkedIn 共找到 {total_found} 位候選人")
            else:
                print(f"     ⚠️  LinkedIn 無結果")

        except TimeoutError:
            print(f"     ⏱️  LinkedIn 搜尋超時（90s），已找到 {len(self.linkedin_candidates)} 位，繼續下一階段")
        except Exception as e:
            print(f"     ❌ LinkedIn 搜尋失敗: {e}")
        finally:
            signal.alarm(0)  # 確保 alarm 一定被取消
    
    def _mock_github_results(self) -> List[Dict]:
        """模擬 GitHub 搜尋結果（示例 - 包含 A、B、C 級）"""
        return [
            # A 級候選人
            {
                "name": "charkchalk",
                "github_url": "https://github.com/charkchalk",
                "key_skills": ["C++", "CMake", "Docker", "Kubernetes", "Linux", "CUDA", "gRPC"],
                "years_experience": 6,
                "recent_activity": True,
                "github_commits_6m": 250,
                "industry_background": "遊戲開發伺服器",
                "education": "Master",
            },
            # B 級候選人
            {
                "name": "James Wong",
                "github_url": "https://github.com/jameswong",
                "key_skills": ["C++", "CMake", "Linux"],  # 只有 3 個必備技能
                "years_experience": 2,  # 低於要求的 3 年
                "recent_activity": True,
                "github_commits_6m": 40,  # 活躍度低
                "industry_background": "一般軟體開發",
                "education": "Bachelor",
            },
        ]
    
    def _mock_linkedin_results(self) -> List[Dict]:
        """模擬 LinkedIn 搜尋結果（示例 - 包含 A、C 級）"""
        return [
            # A 級候選人
            {
                "name": "Magic Len",
                "linkedin_url": "https://linkedin.com/in/magiclen",
                "key_skills": ["C++", "CMake", "Linux", "Redis", "CI/CD", "Docker", "Protocol Buffers"],
                "years_experience": 7,
                "recent_activity": True,
                "github_commits_6m": 150,
                "industry_background": "遊戲伺服器開發 + 金融系統",
                "education": "Master",
            },
            # C 級候選人
            {
                "name": "David Chen",
                "linkedin_url": "https://linkedin.com/in/davidchen",
                "key_skills": ["C", "Java"],  # 只有 C，沒有 C++
                "years_experience": 1,  # 遠低於要求
                "recent_activity": False,  # 沒有最近活動
                "github_commits_6m": 5,  # 幾乎沒活動
                "industry_background": "CRUD 開發",
                "education": "High School",
            },
        ]
    
    def _mock_github_results_relaxed(self) -> List[Dict]:
        """模擬 GitHub 放寬搜尋結果（更多 B、C 級）"""
        return [
            # B 級候選人（相關技能但經驗較少）
            {
                "name": "Tom Lee",
                "github_url": "https://github.com/tomlee",
                "key_skills": ["C++", "Linux", "Docker"],  # 有基礎但缺少高級技能
                "years_experience": 2,
                "recent_activity": True,
                "github_commits_6m": 60,
                "industry_background": "後端開發",
                "education": "Bachelor",
            },
            # C 級候選人（相關但距離較遠）
            {
                "name": "Sophie Wang",
                "github_url": "https://github.com/sophiewang",
                "key_skills": ["Python", "C++"],  # 有 C++ 但主要是 Python
                "years_experience": 3,
                "recent_activity": False,
                "github_commits_6m": 20,
                "industry_background": "資料分析",
                "education": "Bachelor",
            },
        ]
    
    def _mock_linkedin_results_relaxed(self) -> List[Dict]:
        """模擬 LinkedIn 放寬搜尋結果（更多 B、C 級）"""
        return [
            # B 級候選人（相關背景但技能略差）
            {
                "name": "Alex Liu",
                "linkedin_url": "https://linkedin.com/in/alexliu",
                "key_skills": ["C++", "Java", "Linux"],  # 會 C++ 但也做 Java
                "years_experience": 4,
                "recent_activity": True,
                "github_commits_6m": 80,
                "industry_background": "應用開發",
                "education": "Master",
            },
            # C 級候選人（邊際相關）
            {
                "name": "Emma Zhang",
                "linkedin_url": "https://linkedin.com/in/emmazhang",
                "key_skills": ["C++", "Python"],  # 有 C++ 經驗但很基礎
                "years_experience": 1,
                "recent_activity": True,
                "github_commits_6m": 15,
                "industry_background": "剛畢業，科系相關",
                "education": "Bachelor",
            },
        ]
    
    def _load_github_token(self) -> str:
        """載入 GitHub Token（env > .zshrc）"""
        token = os.getenv('GITHUB_TOKEN', '')
        if not token:
            try:
                import re
                with open(os.path.expanduser('~/.zshrc'), 'r') as f:
                    match = re.search(r'export GITHUB_TOKEN="([^"]+)"', f.read())
                    if match:
                        token = match.group(1)
                        os.environ['GITHUB_TOKEN'] = token  # 載入 env 供後續使用
            except:
                pass
        return token

    def _get_ua(self) -> str:
        """🎭 輪換 User-Agent"""
        ua = self._USER_AGENTS[self._ua_index % len(self._USER_AGENTS)]
        self._ua_index += 1
        return ua

    def _check_blocked_domain(self, url: str):
        """🚫 禁止直接存取特定域名（LinkedIn 等）"""
        for domain in self._BLOCKED_DIRECT_DOMAINS:
            if domain in url:
                raise RuntimeError(
                    f"🚫 安全阻擋：禁止直接爬取 {domain}（必須透過 Brave API 間接存取）"
                )

    def _github_rate_wait(self, is_error: bool = False):
        """🛡️ GitHub API 速率控制（含熔斷 + 每日限額）"""
        now = time.time()

        # 🔴 Circuit Breaker
        if is_error:
            self._github_consecutive_errors += 1
        else:
            self._github_consecutive_errors = 0

        if self._github_consecutive_errors >= self._MAX_CONSECUTIVE_ERRORS:
            wait = 60 * self._github_consecutive_errors  # 遞增等待
            print(f"     🔴 GitHub Circuit Breaker！連續 {self._github_consecutive_errors} 次錯誤，暫停 {wait}s...")
            time.sleep(wait)
            self._github_consecutive_errors = 0

        # 📊 每日限額檢查
        self._github_daily_count += 1
        if self._github_daily_count > self._GITHUB_DAILY_LIMIT:
            raise RuntimeError(f"🛑 GitHub 每日請求上限（{self._GITHUB_DAILY_LIMIT}）已達，停止搜尋")

        # 🕐 每次隨機延遲（2.5~5s，模擬人工節奏）
        delay = round(random.uniform(2.5, 5.0), 1)
        time.sleep(delay)

        # ⏱️ 分鐘限額保護
        self._github_requests = [t for t in self._github_requests if now - t < 60]
        if len(self._github_requests) >= self._GITHUB_SEARCH_LIMIT:
            wait = 60 - (now - self._github_requests[0]) + 5
            print(f"     ⏳ GitHub 分鐘上限，等待 {wait:.0f}s...")
            time.sleep(wait)
            self._github_requests = []
        self._github_requests.append(time.time())

    def _brave_rate_wait(self, is_error: bool = False):
        """🛡️ Brave Search API 速率控制（含熔斷 + 每日限額）"""
        now = time.time()

        # 🔴 Circuit Breaker
        if is_error:
            self._brave_consecutive_errors += 1
        else:
            self._brave_consecutive_errors = 0

        if self._brave_consecutive_errors >= self._MAX_CONSECUTIVE_ERRORS:
            wait = 120 * self._brave_consecutive_errors
            print(f"     🔴 Brave Circuit Breaker！連續 {self._brave_consecutive_errors} 次錯誤，暫停 {wait}s...")
            time.sleep(wait)
            self._brave_consecutive_errors = 0

        # 📊 每日限額
        self._brave_daily_count += 1
        if self._brave_daily_count > self._BRAVE_DAILY_LIMIT:
            raise RuntimeError(f"🛑 Brave API 每日請求上限（{self._BRAVE_DAILY_LIMIT}）已達，停止搜尋")

        # 🕐 每次隨機延遲（2~4s，更保守）
        delay = round(random.uniform(2.0, 4.0), 1)
        time.sleep(delay)

        # ⏱️ 每秒限額保護
        self._brave_requests = [t for t in self._brave_requests if now - t < 1]
        if len(self._brave_requests) >= self._BRAVE_LIMIT:
            time.sleep(3.0)
            self._brave_requests = []
        self._brave_requests.append(time.time())

    def _real_github_search(self, keywords: str, max_results: int = 20) -> List[Dict]:
        """真實 GitHub 搜尋 - 含速率控制 + 指數退避重試"""
        try:
            github_token = self._load_github_token()
            headers = {'Accept': 'application/vnd.github.v3+json'}
            if github_token:
                headers['Authorization'] = f'token {github_token}'

            # 提取英文技術關鍵字（過濾中文）
            keyword_parts = keywords.split()
            tech_words = [w for w in keyword_parts if w.isascii() and 2 <= len(w) <= 20]
            tech_words = ['cpp' if w.lower() == 'c++' else w for w in tech_words]
            if tech_words:
                # 去重，避免 "docker docker" 這種重複
                unique_words = list(dict.fromkeys([w.lower() for w in tech_words]))
                primary_kw = unique_words[0]
                skill_query = f"{unique_words[0]} {unique_words[1]}" if len(unique_words) > 1 else unique_words[0]
            else:
                skill_query = 'devops'
                primary_kw = 'devops'

            # 🇹🇼 多城市搜尋 — 涵蓋最主要的台灣城市寫法（平衡覆蓋率與速度）
            TW_LOCATIONS = ['Taiwan', 'Taipei', 'Hsinchu', 'Taichung', 'Kaohsiung']
            seen_logins = set()
            items = []  # 合併所有城市的結果
            search_url_base = "https://api.github.com/search/users"

            for loc in TW_LOCATIONS:
                search_query = f"{skill_query} location:{loc} type:user"
                params = {'q': search_query, 'sort': 'followers', 'order': 'desc', 'per_page': 10}

                self._github_rate_wait()
                print(f"     🔍 [{loc}] {skill_query}...")

                response = None
                for attempt in range(2):
                    try:
                        response = requests.get(search_url_base, params=params, headers=headers, timeout=8)
                        if response.status_code == 429:
                            wait = min(int(response.headers.get('Retry-After', 15)), 15)
                            print(f"     ⚠️  429，等待 {wait}s...")
                            time.sleep(wait)
                            continue
                        if response.status_code == 403:
                            time.sleep(5)
                            continue
                        break
                    except requests.exceptions.Timeout:
                        if attempt == 0: time.sleep(3)
                    except requests.exceptions.SSLError:
                        break

                if response and response.status_code == 200:
                    loc_items = response.json().get('items', [])
                    new_count = 0
                    for u in loc_items:
                        if u['login'] not in seen_logins:
                            seen_logins.add(u['login'])
                            items.append(u)
                            new_count += 1
                    if new_count > 0:
                        print(f"       ✅ +{new_count} 位新用戶（{loc}）")
                    time.sleep(1)  # 城市間小間隔

            total = len(items)
            results = []
            print(f"     📊 多城市合計: {total} 位不重複台灣用戶")

            # 從 JD 分析取得產業背景與核心技能
            jd_industry = ""
            jd_core_skills = []
            if self.jd_analysis:
                jd_core_skills = self.jd_analysis.get("job_profile", {}).get("core_skills", [])
                jd_industry = self.jd_analysis.get("company_profile", {}).get("industry", "Tech")

            # ⚡ 平行抓取 profile（最多 5 個 thread，避免觸發 GitHub 速率限制）
            from concurrent.futures import ThreadPoolExecutor, as_completed

            def _fetch_one(user):
                try:
                    skills, yrs, commits, location, real_name = self._fetch_github_user_profile(
                        user['login'], headers, jd_core_skills
                    )
                    # 🛡️ 明確外國人（location 判斷）→ 跳過
                    origin = self._classify_location(location, user['login'])
                    if origin == 'foreign':
                        print(f"       🚫 跳過外國人: {user['login']} (location: {location})")
                        return None

                    # 🛡️ location unknown → 用真實姓名 + username 雙重判斷
                    if origin == 'unknown':
                        display_name = real_name or user['login']
                        if self._is_likely_foreign_name(real_name) or self._is_likely_foreign_name(user['login']):
                            print(f"       🚫 跳過（名字判斷外國人）: {user['login']} / {real_name} (location: '{location}')")
                            return None

                    display = real_name if real_name else user['login']
                    return {
                        'name': display,
                        'github_url': user['html_url'],
                        'key_skills': skills,
                        'years_experience': yrs,
                        'recent_activity': commits > 0,
                        'github_commits_6m': commits,
                        'industry_background': jd_industry or 'Tech',
                        'education': 'Unknown',
                        'location_raw': location,
                        'location_origin': origin,
                    }
                except Exception as e:
                    return None

            # 🚫 過濾組織帳號（type != 'User'）
            user_only = [u for u in items if u.get('type', 'User') == 'User']
            if len(user_only) < len(items):
                print(f"       🚫 過濾 {len(items) - len(user_only)} 個組織帳號")
            target_users = user_only[:max_results]
            with ThreadPoolExecutor(max_workers=3) as executor:  # 🛡️ 降到 3 thread，避免同時大量請求
                futures = {executor.submit(_fetch_one, u): u for u in target_users}
                for future in as_completed(futures):
                    candidate = future.result()
                    if candidate:
                        results.append(candidate)
            
            return results
            
        except Exception as e:
            print(f"     ❌ GitHub 搜尋失敗: {e}")
            return []

    def _fetch_github_user_profile(self, login: str, headers: dict, jd_core_skills: list) -> tuple:
        """
        抓取 GitHub 用戶真實 profile：bio + 語言 → 推斷真實技能
        Returns: (skills_list, years_experience, commits_6m)
        """
        # 程式語言 → 技能對應表
        LANG_SKILL_MAP = {
            'java': ['Java'],
            'kotlin': ['Java', 'Kotlin'],
            'scala': ['Java', 'Scala'],
            'python': ['Python'],
            'javascript': ['JavaScript', 'Node.js'],
            'typescript': ['TypeScript', 'Node.js'],
            'go': ['Go', 'Golang'],
            'c++': ['C++'],
            'cpp': ['C++'],
            'c': ['C', 'Linux'],
            'c#': ['C#', '.NET'],
            'rust': ['Rust'],
            'ruby': ['Ruby'],
            'php': ['PHP'],
            'swift': ['Swift', 'iOS'],
            'dart': ['Flutter', 'Dart'],
            'shell': ['Linux', 'Bash'],
            'dockerfile': ['Docker'],
            'hcl': ['Terraform', 'Infrastructure'],
            'yaml': ['CI/CD', 'DevOps'],
        }
        # bio 關鍵字 → 技能
        BIO_SKILL_MAP = {
            'spring': 'Spring Boot', 'spring boot': 'Spring Boot',
            'microservice': '微服務', 'microservices': '微服務',
            'kubernetes': 'Kubernetes', 'k8s': 'Kubernetes',
            'docker': 'Docker', 'kafka': 'Message Queue',
            'redis': 'Redis', 'mongodb': 'MongoDB',
            'openapi': 'OpenAPI', 'swagger': 'OpenAPI',
            'ci/cd': 'CI/CD', 'devops': 'CI/CD',
            'c++': 'C++', 'golang': 'Go',
            'machine learning': 'Python', 'ml': 'Python',
            'security': 'Security', 'penetration': 'Penetration Test',
            'fintech': 'Fintech', 'trading': 'Trading',
        }

        skills = []
        years_exp = 3  # 預設
        commits_6m = 0
        location = ''   # 預設空白（未知）
        real_name = ''  # 預設空白（未知）

        try:
            # 1. 抓 user 詳細資料（bio, company, location）
            user_url = f"https://api.github.com/users/{login}"
            ur = requests.get(user_url, headers=headers, timeout=8)
            if ur.status_code == 200:
                ud = ur.json()
                bio = (ud.get('bio') or '').lower()
                location = (ud.get('location') or '').strip()  # ✅ 抓 location 欄位
                real_name = (ud.get('name') or '').strip()     # ✅ 抓真實姓名
                public_repos = ud.get('public_repos', 0)
                followers = ud.get('followers', 0)

                # 從 bio 推斷技能
                for kw, skill in BIO_SKILL_MAP.items():
                    if kw in bio and skill not in skills:
                        skills.append(skill)

                # 用 public_repos + followers 估算年資
                if public_repos >= 50 or followers >= 500:
                    years_exp = 5
                elif public_repos >= 20 or followers >= 100:
                    years_exp = 4
                elif public_repos >= 10 or followers >= 30:
                    years_exp = 3
                else:
                    years_exp = 2

                # 用 followers 估算活躍度
                commits_6m = min(followers, 200)  # 以 followers 作為活躍度代理

            time.sleep(round(random.uniform(0.2, 0.5), 1))

            # 2. 抓最近 5 個 repo 的語言
            repos_url = f"https://api.github.com/users/{login}/repos"
            rr = requests.get(repos_url, headers=headers,
                              params={'sort': 'pushed', 'per_page': 8}, timeout=8)
            if rr.status_code == 200:
                repos = rr.json()
                lang_count = {}
                for repo in repos:
                    lang = (repo.get('language') or '').lower()
                    if lang:
                        lang_count[lang] = lang_count.get(lang, 0) + 1
                    # 從 description 補充技能
                    desc = (repo.get('description') or '').lower()
                    for kw, skill in BIO_SKILL_MAP.items():
                        if kw in desc and skill not in skills:
                            skills.append(skill)

                # 按出現頻率排序，取 top 3 語言
                top_langs = sorted(lang_count.items(), key=lambda x: -x[1])[:3]
                for lang, _ in top_langs:
                    for skill in LANG_SKILL_MAP.get(lang, [lang.capitalize()]):
                        if skill not in skills:
                            skills.insert(0, skill)  # 語言技能放最前面

            time.sleep(round(random.uniform(0.2, 0.5), 1))

        except Exception:
            pass  # profile 抓取失敗不影響主流程

        # 3. 確保至少有一個 JD 相關技能（從搜尋關鍵字補底）
        if not skills and jd_core_skills:
            skills = jd_core_skills[:3]

        return list(dict.fromkeys(skills))[:12], years_exp, commits_6m, location, real_name

    def _classify_location(self, location: str, name: str = '') -> str:
        """
        根據 GitHub location 欄位判斷地區。
        回傳: 'taiwan' | 'foreign' | 'unknown'

        原則：寧可誤判 unknown 也不誤刪台灣人
        只有「明確標注外國城市/國家」才回傳 foreign
        """
        if not location:
            return 'unknown'  # 空白 → 不確定，保留

        loc = location.lower().strip()

        # ✅ 明確台灣
        TAIWAN_SIGNALS = [
            'taiwan', '台灣', 'taipei', '台北', 'taichung', '台中',
            'kaohsiung', '高雄', 'tainan', '台南', 'hsinchu', '新竹',
            'new taipei', '新北', 'taoyuan', '桃園',
        ]
        if any(s in loc for s in TAIWAN_SIGNALS):
            return 'taiwan'

        # ❌ 明確外國（常見誤入來源）
        FOREIGN_SIGNALS = [
            # 南亞
            'india', 'bangalore', 'mumbai', 'delhi', 'hyderabad', 'pune', 'chennai',
            'kolkata', 'ahmedabad', 'jaipur', 'noida', 'gurgaon', 'bengaluru',
            'pakistan', 'karachi', 'lahore', 'islamabad',
            'bangladesh', 'dhaka',
            'sri lanka', 'colombo',
            # 東南亞
            'indonesia', 'jakarta', 'bandung', 'surabaya',
            'philippines', 'manila', 'cebu',
            'vietnam', 'ho chi minh', 'hanoi',
            'myanmar', 'yangon', 'rangoon',
            'cambodia', 'phnom penh',
            'thailand', 'bangkok',
            # 非洲
            'nigeria', 'kenya', 'ghana', 'ethiopia', 'south africa', 'cairo', 'egypt',
            'morocco', 'algeria', 'cameroon', 'senegal',
            # 中東
            'iran', 'tehran', 'saudi arabia', 'riyadh', 'uae', 'dubai',
            'turkey', 'istanbul', 'ankara',
            # 美洲
            'united states', 'usa', 'u.s.a', 'u.s.',
            'san francisco', 'new york', 'seattle', 'austin', 'boston', 'chicago',
            'los angeles', 'california', 'texas', 'washington dc', 'virginia',
            'florida', 'georgia', 'ohio', 'illinois', 'north carolina',
            'canada', 'toronto', 'vancouver', 'montreal',
            'brazil', 'são paulo', 'sao paulo', 'rio de janeiro',
            'colombia', 'bogota', 'argentina', 'buenos aires',
            # 歐洲
            'united kingdom', 'london', 'manchester', 'birmingham', 'uk', 'england',
            'germany', 'berlin', 'munich', 'hamburg',
            'france', 'paris', 'lyon',
            'netherlands', 'amsterdam',
            'spain', 'madrid', 'barcelona',
            'poland', 'warsaw', 'krakow',
            'ukraine', 'kyiv',
            'russia', 'moscow', 'saint petersburg',
            'sweden', 'stockholm', 'norway', 'oslo', 'denmark', 'copenhagen',
            'portugal', 'lisbon', 'romania', 'bucharest',
            # 日本（在日本 = 不在台灣，直接濾）
            'japan', 'tokyo', 'osaka', 'kyoto', 'yokohama', 'nagoya', 'fukuoka', 'sapporo',
            # 韓國
            'korea', 'south korea', 'seoul', 'busan', 'incheon',
            # 中國大陸（不是台灣招募目標）
            'china', 'beijing', 'shanghai', 'shenzhen', 'guangzhou', 'hangzhou',
            'chengdu', 'wuhan', 'nanjing', 'xi\'an', 'tianjin', 'suzhou', 'chongqing',
            'zhengzhou', 'qingdao', 'dalian', 'kunming', 'dongguan', 'foshan',
            # 注意：香港/新加坡 先保留 unknown（有可能找台灣機會）
        ]
        if any(s in loc for s in FOREIGN_SIGNALS):
            return 'foreign'

        return 'unknown'  # 不確定 → 保留，顧問自行判斷

    def _is_likely_foreign_name(self, name: str) -> bool:
        """
        檢查名字是否明顯是非台灣/非華人候選人
        用於 LinkedIn 候選人過濾（無 location 資料時）
        回傳 True = 很可能是外國人，應過濾
        """
        if not name or len(name) < 2:
            return False

        # ✅ 有中文字 → 台灣/華人，保留
        if any('\u4e00' <= c <= '\u9fff' for c in name):
            return False

        # ❌ 含西里爾字母 → 俄/東歐
        if any('\u0400' <= c <= '\u04ff' for c in name):
            return True

        # ❌ 含阿拉伯字母
        if any('\u0600' <= c <= '\u06ff' for c in name):
            return True

        name_lower = name.lower()

        # ❌ 常見南亞名字 pattern（印度/巴基斯坦/孟加拉）
        SOUTH_ASIAN = [
            # 印度常見姓氏
            'kumar', 'singh', 'sharma', 'patel', 'gupta', 'reddy', 'rao',
            'krishna', 'suresh', 'ramesh', 'mahesh', 'ganesh', 'naresh',
            'srini', 'venkat', 'lakshmi', 'priya', 'divya',
            'patidar', 'solanki', 'keshri', 'arora', 'joshi', 'mishra',
            'verma', 'yadav', 'nair', 'menon', 'iyer', 'pillai',
            'chandra', 'pandey', 'dubey', 'tiwari', 'ghosh', 'bose',
            'chatterjee', 'mukherjee', 'banerjee', 'das', 'sinha',
            # 印度常見名字（given names）
            'avinash', 'vaishnavi', 'ankit', 'ankita', 'pooja', 'neha',
            'ayesha', 'faiza', 'shubham', 'siddharth', 'yash', 'hitesh',
            'harsh', 'harshit', 'pranav', 'parag', 'gaurav', 'vikas',
            'vivek', 'vishal', 'prashant', 'prasad', 'karan', 'rohan',
            'varun', 'sweta', 'swati', 'smita', 'rekha', 'kavya',
            'kavitha', 'swapnil', 'sandeep', 'satish', 'shreya', 'shruti',
            'shweta', 'akshay', 'abhishek', 'abhijit', 'arjun', 'aryan',
            'aditya', 'anurag', 'ashish', 'ashutosh', 'atul', 'aditi',
            'aarav', 'aarti', 'aashish', 'ajay', 'akash', 'alok',
            'amol', 'amrit', 'anand', 'ananya', 'aniket', 'anisha',
            'anjali', 'anuj', 'apurv', 'archana', 'ashu', 'atish',
            'ayush', 'bhushan', 'chaitanya', 'chinmay', 'danish',
            'disha', 'dnyanesh', 'esha', 'girish', 'govind', 'hemant',
            'ishaan', 'ishita', 'jagruti', 'jitendra', 'kapil',
            'kartik', 'kedar', 'kishore', 'komal', 'kunal', 'mayur',
            'mihir', 'milind', 'mohit', 'mukesh', 'naman', 'namrata',
            'naveen', 'nilesh', 'nimesh', 'omkar', 'pallavi', 'paresh',
            'parth', 'pawan', 'piyush', 'pramod', 'pratik', 'praveen',
            'preeti', 'preethi', 'prerna', 'priyanka', 'purvi',
            'raghu', 'rakesh', 'ramya', 'ranjit', 'rashmi', 'ravi',
            'rishi', 'ritesh', 'rituraj', 'rupesh', 'sachin', 'sahil',
            'saket', 'sameer', 'samir', 'sanket', 'sapna', 'savita',
            'shailesh', 'shakti', 'shalini', 'shamim', 'shashank',
            'shekhar', 'shivam', 'shivani', 'shrikant', 'siddhi',
            'sonal', 'sonam', 'sonu', 'sooraj', 'sourabh', 'sriram',
            'sudhir', 'sujit', 'sujata', 'sunita', 'supriya', 'surya',
            'sushant', 'tanmay', 'tanvi', 'tejas', 'tushar', 'uday',
            'umesh', 'vaibhav', 'vijay', 'vipul', 'viraj', 'yatin',
            'yogesh', 'yukta', 'zara', 'zubin',
            # 印度常見姓氏（Maharashtra/North）
            'sonawane', 'jadhav', 'jadhaw', 'kulkarni', 'desai',
            'deshpande', 'salunke', 'patil', 'mane', 'shinde', 'bhosale',
            'kadam', 'gaikwad', 'bhagat', 'dhumal', 'thorat', 'sawant',
            'pawar', 'naik', 'gawade', 'chavan', 'phad', 'phade',
            'kakade', 'kale', 'kamble', 'khandagale', 'khot', 'kore',
            'kolhe', 'lokhande', 'more', 'muley', 'nimbalkar', 'pande',
            'randive', 'sable', 'sapkal', 'sutar', 'thakare', 'tidke',
            'tupe', 'wani', 'waghmare', 'jagtap', 'ingale',
            # 常見在 GitHub username 中
            'sneha', 'soumya', 'fathima', 'fathimathu', 'suhaila',
            'aurang', 'manish', 'rajesh', 'sunil', 'anil',
            'dhola', 'kharwal', 'mafuj', 'shikder', 'innocentsax',
            'saish', 'monesh', 'albonid', 'mimaras',
            'sivaprasad', 'nikhil', 'neeraj', 'sumit', 'priyank',
            'deepak', 'amit', 'rohit', 'rahul', 'sanjay',
        ]
        if any(p in name_lower for p in SOUTH_ASIAN):
            return True

        # ❌ 土耳其名字
        TURKISH = ['bekman', 'yilmaz', 'demir', 'kaya', 'celik', 'sahin', 'ozturk', 'mimaras']
        if any(p in name_lower for p in TURKISH):
            return True

        # ❌ 巴西/葡語名字
        BRAZILIAN = ['neres', 'santos', 'oliveira', 'pereira', 'alves', 'silva',
                     'cunha', 'danileao', 'danilo']
        if any(p in name_lower for p in BRAZILIAN):
            return True

        # ❌ 常見非洲名字 pattern
        AFRICAN = ['oluwaseun', 'adekunle', 'chukwu', 'emeka', 'nwosu', 'okafor']
        if any(p in name_lower for p in AFRICAN):
            return True

        return False

    def _search_brave_github_fallback(self, keywords: str, max_results: int = 20, kws: dict = None) -> List[Dict]:
        """Brave Search fallback：GitHub 失敗時全面搜尋（中文 + 英文 + 多平台）
        
        搜尋策略（中英文全覆蓋）：
        1. site:github.com + 英文關鍵字 → 工程師 profile
        2. site:github.com + 中文職稱 → 台灣工程師
        3. site:cakeresume.com + 中英文職稱 → 台灣人才
        4. iThome / T客邦 + 技術詞 → 活躍台灣開發者
        5. 一般 Google/Brave 搜尋 + LinkedIn 補充
        """
        import re

        brave_api_key = os.environ.get('BRAVE_API_KEY') or os.environ.get('BRAVE_SEARCH_API_KEY', '')
        if not brave_api_key:
            print(f"     ⚠️  無 Brave API Key，跳過 Brave fallback")
            return []

        # 從 kws 或 keywords 字串建立關鍵字集合
        if kws is None:
            kws = {}

        keyword_parts = keywords.split()
        raw_english = kws.get('english', [w for w in keyword_parts if w.isascii() and 2 <= len(w) <= 25])
        raw_chinese = kws.get('chinese', [w for w in keyword_parts if not w.isascii() and len(w) >= 2])
        job_title = kws.get('job_title', '')

        # 技術詞處理（c++ → cpp for GitHub API，其他保留）
        en_words = ['cpp' if w.lower() == 'c++' else w for w in raw_english]
        en_primary = ' '.join(en_words[:4])   # 取前 4 個英文詞
        en_secondary = ' '.join(en_words[:2]) # 核心 2 個英文詞
        zh_primary = ' '.join(raw_chinese[:2]) # 取前 2 個中文詞
        zh_title = job_title or zh_primary

        # ====== 搜尋策略（中英全覆蓋）======
        search_queries = []

        # A. GitHub 英文搜尋
        if en_secondary:
            search_queries.append(('github_en', f'site:github.com {en_secondary} developer'))
            search_queries.append(('github_en', f'site:github.com {en_primary} engineer'))
            search_queries.append(('github_en', f'site:github.com {en_secondary} Taiwan'))

        # B. GitHub 中文搜尋（找 bio 含中文的台灣工程師）
        if zh_title:
            search_queries.append(('github_zh', f'site:github.com {zh_title} 工程師'))
            search_queries.append(('github_zh', f'site:github.com {zh_title} 台灣'))
        if zh_primary and en_secondary:
            search_queries.append(('github_zh', f'site:github.com {zh_primary} {en_secondary}'))

        # C. CakeResume（台灣最大求職平台）
        if zh_title:
            search_queries.append(('cake', f'site:cakeresume.com {zh_title} 台灣'))
        if en_secondary:
            search_queries.append(('cake', f'site:cakeresume.com {en_secondary} Taiwan'))

        # D. iThome + PTT Tech（活躍台灣開發者）
        if zh_title:
            search_queries.append(('ithome', f'site:ithome.com.tw {zh_primary or en_secondary} 工程師'))
        if en_secondary:
            search_queries.append(('ithome', f'ithome.com.tw {en_secondary} 工程師 作者'))

        # E. 104 履歷
        if zh_title:
            search_queries.append(('104', f'site:104.com.tw {zh_title} 履歷'))

        # ====== SKILL MAP（中英技能推斷）======
        skill_map = {
            'python': 'Python', 'java': 'Java', 'javascript': 'JavaScript',
            'typescript': 'TypeScript', 'c++': 'C++', 'cpp': 'C++', 'c#': 'C#',
            'golang': 'Go', '.net': '.NET', 'dotnet': '.NET',
            'rust': 'Rust', 'react': 'React', 'node': 'Node.js', 'vue': 'Vue.js',
            'kubernetes': 'Kubernetes', 'k8s': 'Kubernetes', 'docker': 'Docker',
            'aws': 'AWS', 'gcp': 'GCP', 'azure': 'Azure',
            'security': '資安', 'devops': 'DevOps', 'sre': 'SRE',
            'machine learning': 'ML', 'deep learning': 'DL', 'ai': 'AI',
            'spring': 'Spring Boot', 'android': 'Android', 'ios': 'iOS',
            # 中文關鍵字對應技能
            '資安': '資安', '前端': 'Frontend', '後端': 'Backend',
            '全端': 'Fullstack', '維運': 'DevOps', '雲端': 'Cloud',
            '資料': 'Data', '機器學習': 'ML', '人工智慧': 'AI',
        }

        api_url = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip',
            'User-Agent': self._get_ua(),            # 🎭 輪換 UA
            'X-Subscription-Token': brave_api_key
        }

        results = []
        seen = set()
        SKIP_USERNAMES = {
            'orgs', 'topics', 'collections', 'explore', 'features', 'marketplace',
            'enterprise', 'login', 'join', 'about', 'pricing', 'blog', 'events',
            'docs', 'settings', 'notifications', 'issues', 'pulls', 'gist'
        }

        for source_type, query in search_queries:
            if len(results) >= max_results:
                break
            try:
                search_lang = 'zh-TW' if source_type in ('github_zh', 'cake', 'ithome', '104') else 'en'
                params = {'q': query, 'count': 10, 'safesearch': 'off', 'search_lang': search_lang}
                print(f"       🔍 [{source_type}] {query[:65]}...")
                resp = requests.get(api_url, headers=headers, params=params, timeout=8)
                if resp.status_code != 200:
                    print(f"       ⚠️  Brave {resp.status_code}")
                    time.sleep(1)
                    continue

                data = resp.json()
                web_results = data.get('web', {}).get('results', [])

                for item in web_results:
                    url = item.get('url', '')
                    title = item.get('title', '')
                    description = item.get('description', '') or ''

                    # 解析 username / 候選人識別碼
                    username = None
                    profile_url = url

                    # GitHub profile
                    m = re.match(r'https://github\.com/([a-zA-Z0-9][a-zA-Z0-9-]{0,38})(?:/.*)?$', url)
                    if m:
                        username = m.group(1)
                        profile_url = f'https://github.com/{username}'

                    # CakeResume
                    elif 'cakeresume.com' in url:
                        m2 = re.search(r'cakeresume\.com/(?:me/|resumes/)?([a-zA-Z0-9_\-]+)', url)
                        username = m2.group(1) if m2 else title.split('|')[0].strip()[:30]
                        profile_url = url

                    # iThome 作者
                    elif 'ithome.com.tw' in url:
                        m3 = re.search(r'ironman\.ithome\.com\.tw/users/([^/]+)', url)
                        if m3:
                            username = m3.group(1)
                        else:
                            username = title.split('|')[0].strip()[:30]
                        profile_url = url

                    # 104 履歷
                    elif '104.com.tw' in url:
                        username = title.split('-')[0].strip()[:30] or 'candidate_104'
                        profile_url = url

                    # 其他（portfolio/blog）
                    else:
                        name_m = re.search(
                            r'^([A-Za-z\u4e00-\u9fff][A-Za-z\u4e00-\u9fff ]{1,25}?)(?:\s*[-·|–]|\s+GitHub|\s+Developer)',
                            title
                        )
                        username = name_m.group(1).strip() if name_m else title[:35]
                        profile_url = url

                    if not username:
                        continue
                    uid = profile_url or username
                    if uid in seen:
                        continue
                    if username.lower() in SKIP_USERNAMES:
                        continue
                    seen.add(uid)

                    # 推斷技能（中英文兩路）
                    skill_text = f"{title} {description}".lower()
                    inferred = []
                    for kw_pat, skill_name in skill_map.items():
                        if kw_pat in skill_text:
                            inferred.append(skill_name)
                    # 加入職缺核心技能
                    for ew in en_words[:3]:
                        cap = ew.upper() if len(ew) <= 3 else ew.capitalize()
                        if cap not in inferred:
                            inferred.append(cap)
                    if zh_title and zh_title not in inferred:
                        inferred.append(zh_title)

                    # 🛡️ 名字過濾（用 username 或從 title 提取的名字）
                    if self._is_likely_foreign_name(username):
                        print(f"       🚫 Brave fallback 跳過外國人: {username}")
                        continue

                    candidate = {
                        'name': username,
                        'github_url': profile_url,
                        'key_skills': list(dict.fromkeys(inferred))[:8] or [en_secondary or zh_title],
                        'years_experience': 3,
                        'recent_activity': True,
                        'github_commits_6m': 10,
                        'industry_background': f'Brave/{source_type}',
                        'education': 'Unknown',
                        'source': f'brave_{source_type}',
                        'brave_description': description[:150]
                    }
                    results.append(candidate)

                    if len(results) >= max_results:
                        break

                time.sleep(1.2)

            except requests.exceptions.Timeout:
                print(f"       ⚠️  Brave timeout，跳過此 query")
            except Exception as e:
                print(f"       ⚠️  Brave fallback 失敗: {str(e)[:80]}")

        print(f"       📊 Brave fallback 共找到 {len(results)} 位")
        return results[:max_results]

    def _real_linkedin_search(self, keywords: str, max_results: int = 10) -> List[Dict]:
        """真實 LinkedIn 搜尋 - 使用 Brave Search API（修復版）"""
        import urllib.parse
        
        # Brave API Key（從環境變數讀取）
        brave_api_key = os.environ.get('BRAVE_API_KEY') or os.environ.get('BRAVE_SEARCH_API_KEY', '')
        
        if not brave_api_key:
            print(f"     ⚠️  無 Brave API Key，跳過 LinkedIn 搜尋")
            return []
        
        try:
            keywords_clean = keywords.strip()
            
            # 建立 LinkedIn 搜尋查詢（台灣開發者）
            queries = [
                f'site:linkedin.com/in "{keywords_clean}" Taiwan',
                f'site:linkedin.com/in {keywords_clean} 台灣 工程師',
            ]
            
            print(f"     🔍 Brave LinkedIn 搜尋: {keywords_clean}...")
            
            # 使用 Brave Search API 真實搜尋 LinkedIn
            raw_candidates = []
            seen_urls = set()
            
            for query in queries:
                if len(raw_candidates) >= max_results:
                    break
                
                api_url = "https://api.search.brave.com/res/v1/web/search"
                headers = {
                    'Accept': 'application/json',
                    'Accept-Encoding': 'gzip',
                    'User-Agent': self._get_ua(),    # 🎭 輪換 UA
                    'X-Subscription-Token': brave_api_key
                }
                params = {'q': query, 'count': 10, 'country': 'tw'}
                
                try:
                    # 🛡️ 速率控制
                    self._brave_rate_wait()

                    # 🔄 Brave 單次重試（從 3 次縮為 1 次，防超時）
                    resp = None
                    for attempt in range(2):
                        try:
                            resp = requests.get(api_url, headers=headers, params=params, timeout=8)
                            if resp.status_code == 429:
                                wait = int(resp.headers.get('Retry-After', 10)) + 2
                                print(f"     ⚠️  Brave 429，等待 {wait}s...")
                                self._brave_rate_wait(is_error=True)  # 🔴 觸發 Circuit Breaker
                                time.sleep(wait)
                                continue
                            break
                        except requests.exceptions.Timeout:
                            if attempt == 0:
                                print(f"     ⏳ Brave timeout，5s 後重試 (1/1)...")
                                time.sleep(5)
                            else:
                                print(f"     ⏳ Brave 二次 timeout，跳過此 query")

                    if resp is None or resp.status_code != 200:
                        raise Exception(f"Brave API 失敗: {resp.status_code if resp else 'no response'}")

                    resp.raise_for_status()
                    data = resp.json()
                    
                    web_results = data.get('web', {}).get('results', [])
                    for item in web_results:
                        url = item.get('url', '')
                        # 只要 linkedin.com/in/ 格式的個人頁面
                        if 'linkedin.com/in/' not in url:
                            continue
                        if url in seen_urls:
                            continue
                        seen_urls.add(url)
                        
                        title = item.get('title', '')
                        snippet = item.get('description', '') or item.get('extra_snippets', [''])[0] if item.get('extra_snippets') else item.get('description', '')

                        # 🇹🇼 只保留有台灣相關訊號的結果
                        combined_text = (title + ' ' + (snippet or '')).lower()
                        TAIWAN_SIGNALS_LI = ['taiwan', '台灣', 'taipei', '台北', 'taichung', '台中',
                                              'hsinchu', '新竹', 'tainan', '台南', 'kaohsiung', '高雄',
                                              'new taipei', '新北', 'taoyuan', '桃園']
                        has_taiwan_signal = any(s in combined_text for s in TAIWAN_SIGNALS_LI)
                        
                        # 優先從標題提取名字（更乾淨）
                        # LinkedIn 標題格式通常是 "Name - Title | LinkedIn"
                        name = ''
                        if title:
                            name = title.split('|')[0].split('-')[0].strip()
                            # 移除 " - LinkedIn" 等後綴
                            name = name.replace(' - LinkedIn', '').strip()
                        
                        # 備用：從 URL 提取（去除 hash code）
                        if not name or len(name) < 2:
                            import urllib.parse as urlparse
                            url_parts = url.split('/in/')
                            if len(url_parts) > 1:
                                raw_slug = url_parts[1].rstrip('/').split('?')[0]
                                decoded = urlparse.unquote(raw_slug)
                                # 移除尾部 hash code（純數字或含字母的ID，如 -081649284、-869602A4）
                                import re
                                decoded = re.sub(r'-[0-9a-fA-F]{6,}$', '', decoded)
                                name = decoded.replace('-', ' ').title().strip()
                        
                        if not name or len(name) < 2:
                            continue

                        # 🚫 過濾頁面標題（非真實人名）
                        PAGE_TITLE_SIGNALS = ['linkedin', '登入', '註冊', 'sign in', 'log in', 'register',
                                               'login', 'join', 'jobs on', 'people search', 'find']
                        if any(p in name.lower() for p in PAGE_TITLE_SIGNALS):
                            print(f"       🚫 LinkedIn 跳過（頁面標題非人名）: {name}")
                            continue

                        # 🚫 過濾邏輯（雙重保護）
                        is_foreign_name = self._is_likely_foreign_name(name)
                        if is_foreign_name and not has_taiwan_signal:
                            # 名字像外國人 + 沒有台灣訊號 → 過濾
                            print(f"       🚫 LinkedIn 跳過（外國人名字 + 無台灣訊號）: {name}")
                            continue
                        if not has_taiwan_signal and not any('\u4e00' <= c <= '\u9fff' for c in name):
                            # 英文名 + 無台灣訊號 → 保留（可能是台灣人英文名，讓顧問判斷）
                            print(f"       ⚠️  LinkedIn 保留但無台灣訊號（英文名）: {name}")

                        # 解析 LinkedIn 搜尋關鍵字為獨立技能清單
                        _jd_core_li = self.jd_analysis.get("job_profile", {}).get("core_skills", []) if self.jd_analysis else []
                        li_skill_tokens = [t.strip() for t in keywords_clean.replace(',', ' ').split() if t.strip() and len(t) >= 2]
                        # 補入 JD 核心技能中符合關鍵字的
                        kc_lower = keywords_clean.lower()
                        for sk in _jd_core_li:
                            if sk.lower() in kc_lower and sk not in li_skill_tokens:
                                li_skill_tokens.insert(0, sk)
                        li_skill_tokens = list(dict.fromkeys(li_skill_tokens))[:10] or [keywords_clean]
                        
                        # ✅ 偵測 Open to Work 與頭像
                        signals = self._detect_linkedin_signals(item)

                        raw_candidates.append({
                            'name': name,
                            'linkedin_url': url,
                            'source': 'LinkedIn',
                            'key_skills': li_skill_tokens,
                            'years_experience': 3,
                            'recent_activity': True,
                            'github_commits_6m': 0,
                            'industry_background': title[:80],
                            'education': 'Unknown',
                            'open_to_work': signals['open_to_work'],   # ✅ Open to Work 標記
                            'has_photo': signals['has_photo'],          # ✅ 有頭像標記
                        })
                    
                    self._brave_rate_wait()  # 🛡️ 速率控制
                    
                except Exception as e:
                    print(f"     ⚠️  Brave API 查詢失敗: {str(e)[:60]}")
                    time.sleep(2)
            
            result = raw_candidates[:max_results]
            
            if result:
                print(f"     📊 Brave 找到 {len(result)} 位真實 LinkedIn 用戶")
            else:
                print(f"     ⚠️  LinkedIn 無搜尋結果")
            
            return result
            
        except Exception as e:
            print(f"     ❌ LinkedIn 搜尋失敗: {str(e)[:50]}")
            return []
    
    def _detect_linkedin_signals(self, item: dict) -> dict:
        """從 Brave 搜尋結果偵測 LinkedIn 的 Open to Work 標記與頭像狀態"""
        import base64
        signals = {"open_to_work": False, "has_photo": False}

        title = item.get('title', '').lower()
        description = item.get('description', '').lower()
        url = item.get('url', '').lower()

        # ── Open to Work 偵測 ──
        otw_patterns = ['open to work', 'open to opportunities', '#opentowork', 'open-to-work']
        signals['open_to_work'] = any(p in title or p in description or p in url for p in otw_patterns)

        # ── 頭像偵測（從 Brave thumbnail URL 解析原始 LinkedIn 圖片 URL）──
        # 真實頭像：media.licdn.com/dms/image/...
        # 預設頭像：static.licdn.com/aero-v1/...
        thumbnail = item.get('thumbnail')
        if thumbnail and isinstance(thumbnail, dict):
            thumb_src = thumbnail.get('src', '')
            if thumb_src:
                try:
                    # Brave thumbnail URL 末段是 base64 編碼的原始圖片 URL
                    b64_part = thumb_src.rstrip('/').split('/')[-1]
                    # base64 padding
                    padded = b64_part + '=' * (4 - len(b64_part) % 4)
                    decoded = base64.b64decode(padded).decode('utf-8', errors='ignore')
                    signals['has_photo'] = (
                        'media.licdn.com/dms/image' in decoded or
                        'media.linkedin.com' in decoded
                    )
                except Exception:
                    # fallback：直接從 thumb_src 判斷（Brave 有時嵌入原始 URL）
                    signals['has_photo'] = 'media.licdn' in thumb_src

        return signals

    def _stage_deduplication(self):
        """去重 + 智慧回退邏輯"""
        try:
            # 合併 GitHub 和 LinkedIn 候選人
            all_candidates = self.github_candidates + self.linkedin_candidates
            
            # 簡單的去重（實際應更複雜）
            seen_names = set()
            deduplicated = []
            
            for candidate in all_candidates:
                name_lower = candidate['name'].lower()
                if name_lower not in seen_names:
                    seen_names.add(name_lower)
                    deduplicated.append(candidate)
            
            # 【測試模式】故意清空去重結果，以驗證智慧回退邏輯
            if self.test_zero_dedup:
                deduplicated = []
                print(f"\n  🧪 [TEST MODE] 故意清空去重結果，驗證智慧回退邏輯\n")
            
            self.final_candidates = deduplicated
            
            print(f"  ✅ 原始: {len(all_candidates)} 人")
            print(f"  ✅ 去重後: {len(self.final_candidates)} 人")
            
            # 【智慧回退】去重後 0 人，觸發重試
            if len(self.final_candidates) == 0:
                print("\n  ⚠️ 去重後無人選！觸發智慧回退...")
                self._intelligent_fallback()
            
        except Exception as e:
            print(f"  ❌ 去重失敗: {e}")
            raise
    
    def _get_assigned_consultant(self) -> str:
        """
        決定候選人分配給哪個顧問
        
        自動爬蟲匯入的候選人一律設為「待分配」，
        由顧問手動在系統中認領，不自動指派給任何人。
        """
        return "待分配"
    
    def _intelligent_fallback(self):
        """智慧回退 - 放寬搜尋條件，重試 2 次"""
        retry_count = 0
        max_retries = 2
        
        while len(self.final_candidates) == 0 and retry_count < max_retries:
            retry_count += 1
            print(f"\n  🔄 第 {retry_count} 次重試 - 放寬搜尋條件...")
            
            # 清空之前的搜尋結果
            self.github_candidates = []
            self.linkedin_candidates = []
            
            # 放寬搜尋條件重試（技能要求降低 20%、年資要求降低、地域擴大）
            print(f"\n     📍 GitHub 搜尋（放寬模式）...")
            self._search_github(relax=True)
            
            # 搜尋間隔
            HumanBehavior.batch_pause(2, 3)
            
            print(f"\n     💼 LinkedIn Google 搜尋（放寬模式）...")
            self._search_linkedin_google(relax=True)
            
            # 重新去重
            print(f"\n     🧹 重新去重...")
            all_candidates = self.github_candidates + self.linkedin_candidates
            
            seen_names = set()
            deduplicated = []
            for candidate in all_candidates:
                name_lower = candidate['name'].lower()
                if name_lower not in seen_names:
                    seen_names.add(name_lower)
                    deduplicated.append(candidate)
            
            self.final_candidates = deduplicated
            print(f"     ✅ 去重後: {len(self.final_candidates)} 人")
        
        # 檢查最終結果
        if len(self.final_candidates) == 0:
            print("\n  ❌ 重試 2 次後仍無人選")
            print("  ⚠️ 無法為此職位找到符合條件的候選人")
            print("  💡 建議: 可能需要調整職缺要求或手動搜尋")
        else:
            print(f"\n  ✅ 回退成功！找到 {len(self.final_candidates)} 位候選人")
    
    def _stage_scoring(self):
        """評分"""
        try:
            scorer = CandidateScorer(self.jd_analysis)
            
            print(f"\n  🤖 正在評分 {len(self.final_candidates)} 位候選人...")
            
            for idx, candidate in enumerate(self.final_candidates, 1):
                # 評分
                score_result = scorer.score(candidate)
                
                # 保存所有級別的候選人（A+、A、B、C 都匯入）
                self.scored_candidates.append(score_result)
                grade_emoji = {
                    'A+': '⭐⭐',
                    'A': '⭐',
                    'B': '🔶',
                    'C': '⚪',
                    'D': '❌'
                }.get(score_result['grade'], '❓')
                
                print(f"     {grade_emoji} [{idx}] {candidate['name']}: {score_result['grade']} ({score_result['score']} 分)")
                
                # 人類行為延遲
                HumanBehavior.action_pause()
            
            # 統計各級別
            grade_stats = {}
            for sc in self.scored_candidates:
                grade = sc['grade']
                grade_stats[grade] = grade_stats.get(grade, 0) + 1
            
            print(f"\n  ✅ 評分完成:")
            print(f"     • S:  {grade_stats.get('S', 0)} 位 ⭐⭐⭐ → AI推薦")
            print(f"     • A+: {grade_stats.get('A+', 0)} 位 ⭐⭐   → AI推薦")
            print(f"     • A:  {grade_stats.get('A', 0)} 位 ⭐    → AI推薦")
            print(f"     • B:  {grade_stats.get('B', 0)} 位 🔶   → AI推薦")
            print(f"     • C:  {grade_stats.get('C', 0)} 位 ⚪   → 備選人才")
            print(f"     • D:  {grade_stats.get('D', 0)} 位 ❌   → 備選人才")
            print(f"     ───────────────────────────")
            print(f"     • 總計: {len(self.scored_candidates)} 位（全部匯入系統）")
            
        except Exception as e:
            print(f"  ❌ 評分失敗: {e}")
            raise
    
    def _stage_upload(self):
        """批量上傳 + 去重檢查 + 回報"""
        try:
            if not self.scored_candidates:
                print("  ⚠️ 無符合條件的候選人")
                return
            
            # 取得職位名稱用於回報
            job_title = self.jd_analysis['job_profile']['title']
            self.upload_reporter = UploadReporter(job_title)
            
            print(f"\n  📤 正在上傳 {len(self.scored_candidates)} 位候選人...")
            
            # 【直接上傳所有候選人 - 跳過有問題的去重檢查】
            # 【Grade 過濾】只上傳 B 級（含）以上，C/D 直接丟棄
            UPLOAD_GRADES = {'S', 'A+', 'A', 'B'}
            all_candidates = self.scored_candidates
            to_upload = [c for c in all_candidates if c.get('grade', '') in UPLOAD_GRADES]
            skip_list = [c for c in all_candidates if c.get('grade', '') not in UPLOAD_GRADES]
            
            print(f"\n  📋 上傳清單:")
            print(f"     • 待上傳: {len(to_upload)} 人（B 級以上）")
            print(f"     • 跳過: {len(skip_list)} 人（C/D 級不上傳）")
            
            # 【批量上傳】
            print(f"\n  📤 開始上傳 {len(to_upload)} 位候選人...")
            
            uploaded = 0
            failed = 0
            
            for idx, candidate in enumerate(to_upload, 1):
                try:
                    candidate_id = 540 + idx - 1  # 模擬 ID
                    
                    # 🛡️ 每次上傳隨機間隔 0.8~2s，避免 backend 被打爆 + 模擬人工節奏
                    if idx > 1:
                        time.sleep(round(__import__('random').uniform(0.8, 2.0), 1))

                    # 調用 API
                    result = self._upload_candidate_to_api(candidate)
                    
                    if result:
                        print(f"     ✅ [{idx}] {candidate['name']} - 上傳成功")
                        self.upload_reporter.add_result(
                            candidate['name'], 
                            candidate_id, 
                            True, 
                            candidate['score'],
                            candidate['grade']
                        )
                        uploaded += 1
                    else:
                        print(f"     ⚠️ [{idx}] {candidate['name']} - API 回傳失敗")
                        self.upload_reporter.add_result(
                            candidate['name'],
                            candidate_id,
                            False,
                            candidate['score'],
                            candidate['grade'],
                            "API 回傳失敗"
                        )
                        failed += 1
                    
                    HumanBehavior.action_pause()
                    
                except Exception as e:
                    print(f"     ❌ [{idx}] {candidate['name']} - 失敗: {str(e)[:50]}")
                    self.upload_reporter.add_result(
                        candidate['name'],
                        540 + idx - 1,
                        False,
                        candidate['score'],
                        candidate['grade'],
                        str(e)[:50]
                    )
                    failed += 1
            
            print(f"\n  ✅ 上傳完成: {uploaded} 成功, {failed} 失敗, {len(skip_list)} 跳過")
            
            # 【生成回報】
            self._generate_and_print_report()
            
        except Exception as e:
            print(f"  ❌ 上傳失敗: {e}")
            raise
    
    def _generate_and_print_report(self):
        """生成並列印上傳回報"""
        if not self.upload_reporter:
            return
        
        report = self.upload_reporter.generate_report()
        print(report)
        
        # 也儲存到檔案
        import datetime
        report_file = f"/tmp/upload-report-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
        self.upload_reporter.save_report(report_file)
        print(f"  📄 詳細回報已儲存: {report_file}")
    
    def _upload_candidate_to_api(self, candidate_score: Dict) -> bool:
        """
        上傳單個候選人評分到 API
        
        Args:
            candidate_score: 候選人評分結果
        
        Returns:
            是否上傳成功
        """
        try:
            import requests
            from datetime import datetime
            
            # 使用 POST 創建新候選人
            url = f"{self.api_base}/candidates"
            
            # 準備上傳數據（使用 POST 格式）
            payload = {
                "name": candidate_score["name"],
                "email": candidate_score.get("email", "unknown@github.com"),
                "github_url": candidate_score.get("github_url", ""),
                "linkedin_url": candidate_score.get("linkedin_url", ""),
                "status": "AI推薦",  # 自動爬蟲找到的候選人標記為 AI推薦
                "stability_score": candidate_score.get("score", 0),
                "talent_level": candidate_score.get("grade", ""),
                "recruitment_source": "自動爬蟲",
                "added_date": datetime.now().strftime("%Y-%m-%d"),
                "auto_sourced_at": datetime.now().isoformat(),  # 今日新增篩選用
                "notes": (
                    f"Bot 自動匯入 | "
                    f"目標職缺：{candidate_score.get('position', '')} ({candidate_score.get('company', '')}) | "
                    f"負責顧問：{self._get_assigned_consultant()} | "
                    + ("🟢 Open to Work | " if candidate_score.get("open_to_work") else "")
                    + ("📸 有頭像 | " if candidate_score.get("has_photo") else "")
                    + f"{datetime.now().strftime('%Y-%m-%d')}"
                ),
                "assigned_consultant": self._get_assigned_consultant(),
                "ai_match_result": {
                    "score": candidate_score["score"],
                    "grade": candidate_score["grade"],
                    "date": candidate_score["date"],
                    "position": candidate_score["position"],
                    "company": candidate_score["company"],
                    "matched_skills": candidate_score["matched_skills"],
                    "missing_skills": candidate_score["missing_skills"],
                    "strengths": candidate_score["strengths"],
                    "probing_questions": candidate_score["probing_questions"],
                    "salary_fit": candidate_score["salary_fit"],
                    "conclusion": candidate_score["conclusion"],
                    "contact_method": candidate_score["contact_method"],
                    "open_to_work": candidate_score.get("open_to_work", False),
                    "has_photo": candidate_score.get("has_photo", False),
                    "evaluated_by": candidate_score["evaluated_by"],
                    "evaluated_at": candidate_score["evaluated_at"],
                    "sourced_from": "talent-sourcing-pipeline",
                    "auto_sourced_at": datetime.now().isoformat(),
                }
            }
            
            # 調用 API
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'TalentSourcingPipeline/1.0'
            }
            
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            # 檢查響應
            if response.status_code in [200, 201, 204]:
                # ✅ 取得候選人 ID，立刻 PATCH 補寫 ai_match_result（確保無論 POST 有沒有存都寫入）
                try:
                    resp_data = response.json()
                    candidate_id = resp_data.get('data', {}).get('id')
                    if candidate_id and payload.get('ai_match_result'):
                        patch_url = f"{self.api_base}/candidates/{candidate_id}"
                        requests.patch(
                            patch_url,
                            json={'ai_match_result': payload['ai_match_result']},
                            headers=headers,
                            timeout=10
                        )
                except Exception:
                    pass  # PATCH 失敗不中斷流程
                return True
            else:
                print(f"     (API {response.status_code}: {response.text[:100]})")
                return False
                
        except Exception as e:
            print(f"     (API 調用失敗: {str(e)[:50]})")
            return False
    
    def _print_dry_run_summary(self):
        """打印 DRY-RUN 總結"""
        print("\n" + "=" * 60)
        print("📊 DRY-RUN 分析報告")
        print("=" * 60)
        
        print(f"\n【公司畫像】")
        company = self.jd_analysis['company_profile']
        print(f"  • 名稱: {company['name']}")
        print(f"  • 產業: {company['industry']}")
        print(f"  • 階段: {company['stage']}")
        
        print(f"\n【職位畫像】")
        job = self.jd_analysis['job_profile']
        print(f"  • 職位: {job['title']}")
        print(f"  • 等級: {job['level']}")
        print(f"  • 薪資: {job['salary_range']['min']}-{job['salary_range']['max']} TWD")
        print(f"  • 年資: {job['required_experience']}+ 年")
        print(f"  • 必備技能: {', '.join(job['core_skills'][:5])}")
        
        print(f"\n【人才畫像】")
        talent = self.jd_analysis['talent_profile']
        print(f"  • 主要技能: {', '.join(talent['ideal_background']['primary_skills'][:5])}")
        print(f"  • 產業背景: {', '.join(talent['ideal_background']['industry_experience'][:3])}")
        print(f"  • 成長信號: {', '.join(talent['growth_indicators'][:3])}")
        
        print(f"\n【搜尋策略】")
        search = self.jd_analysis['search_strategy']
        print(f"  • GitHub 搜尋:")
        for keyword in search['github']['keywords']:
            print(f"    - {keyword}")
        print(f"    估計結果: {search['github']['estimated_results']} 人")
        print(f"\n  • LinkedIn Google 搜尋:")
        print(f"    查詢: {search['linkedin_google']['query']}")
        print(f"    估計結果: {search['linkedin_google']['estimated_results']} 人")
        
        print(f"\n【預計成果】")
        print(f"  • 最終候選人: {search['deduplication']['final_target']} 人（去重後）")
        print(f"  • 預期 A+/A 級: ~{int(search['deduplication']['final_target'] * 0.7)} 人")
        print(f"  • 預計耗時: ~{search['total_estimated_time_sec']} 秒")
        
        print("\n📋 確認無誤？使用 --execute 模式執行爬蟲")
        print("=" * 60)
    
    def _print_final_summary(self):
        """打印最終總結"""
        print("\n【成果統計】")
        print(f"  • 搜尋階段: GitHub {len(self.github_candidates)} + LinkedIn {len(self.linkedin_candidates)}")
        print(f"  • 去重後: {len(self.final_candidates)} 位")
        print(f"  • 評分後: {len(self.scored_candidates)} 位")
        
        # 統計各級別
        grade_dist = {}
        for sc in self.scored_candidates:
            grade = sc['grade']
            grade_dist[grade] = grade_dist.get(grade, 0) + 1
        
        print(f"\n【評分分布】")
        # 定義等級分類
        recommended_grades = {'S': '⭐⭐⭐', 'A+': '⭐⭐', 'A': '⭐', 'B': '🔶'}
        backup_grades = {'C': '⚪', 'D': '❌'}
        
        rec_count = sum(grade_dist.get(g, 0) for g in recommended_grades)
        backup_count = sum(grade_dist.get(g, 0) for g in backup_grades)
        
        if rec_count > 0:
            print(f"\n  🎯 AI推薦（B 級以上）: {rec_count} 位")
            for grade in ['S', 'A+', 'A', 'B']:
                count = grade_dist.get(grade, 0)
                if count > 0:
                    emoji = recommended_grades.get(grade, '?')
                    print(f"     • {emoji} {grade} 級: {count} 位")
        
        if backup_count > 0:
            print(f"\n  📋 備選人才（C 級以下）: {backup_count} 位")
            for grade in ['C', 'D']:
                count = grade_dist.get(grade, 0)
                if count > 0:
                    emoji = backup_grades.get(grade, '?')
                    print(f"     • {emoji} {grade} 級: {count} 位")
        
        print(f"\n  🎯 總計: {len(self.scored_candidates)} 位候選人（全部已匯入系統）")
        
        if self.scored_candidates:
            print(f"\n【候選人清單（全部）】")
            for idx, cand in enumerate(self.scored_candidates, 1):
                grade_emoji = {
                    'A+': '⭐⭐',
                    'A': '⭐',
                    'B': '🔶',
                    'C': '⚪',
                    'D': '❌'
                }.get(cand['grade'], '❓')
                print(f"  {grade_emoji} [{idx}] {cand['name']} ({cand['grade']}, {cand['score']} 分)")


def main():
    """主函數"""
    parser = argparse.ArgumentParser(
        description="智慧人才搜尋閉環系統",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  # DRY-RUN: 分析職缺，不執行搜尋
  python3 talent-sourcing-pipeline.py --job-id 51 --dry-run
  
  # EXECUTE: 完整執行（搜尋 + 評分 + 上傳）
  python3 talent-sourcing-pipeline.py --job-id 51 --execute
  
  # 批量處理多個職位
  python3 talent-sourcing-pipeline.py --job-ids 51,15 --execute
        """
    )
    
    parser.add_argument("--job-id", type=int, help="單個職缺 ID")
    parser.add_argument("--job-ids", type=str, help="多個職缺 ID（逗號分隔）")
    parser.add_argument("--dry-run", action="store_true", help="DRY-RUN 模式（只分析，不執行）")
    parser.add_argument("--execute", action="store_true", help="EXECUTE 模式（完整執行）")
    parser.add_argument("--test-zero-dedup", action="store_true", help="測試模式：故意讓去重後為 0 人，驗證智慧回退邏輯")
    
    args = parser.parse_args()
    
    # 驗證參數
    if not args.job_id and not args.job_ids:
        parser.print_help()
        sys.exit(1)
    
    # 決定是否 dry-run
    is_dry_run = args.dry_run and not args.execute
    
    # 處理單個職缺
    if args.job_id:
        pipeline = TalentSourcingPipeline(args.job_id, dry_run=is_dry_run, test_zero_dedup=args.test_zero_dedup)
        pipeline.run()
    
    # 處理多個職缺
    if args.job_ids:
        job_ids = [int(id.strip()) for id in args.job_ids.split(',')]
        for job_id in job_ids:
            print(f"\n{'=' * 60}\n")
            pipeline = TalentSourcingPipeline(job_id, dry_run=is_dry_run, test_zero_dedup=args.test_zero_dedup)
            pipeline.run()


if __name__ == "__main__":
    main()
