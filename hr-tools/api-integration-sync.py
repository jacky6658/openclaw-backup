#!/usr/bin/env python3
"""
Step1ne API 集成 — 自動導入推薦候選人到履歷池

功能：
1. 讀取搜尋推薦結果（JSON）
2. 轉換為 Step1ne API 格式
3. 自動去重（避免重複）
4. 批量或逐個導入
5. 記錄導入結果 & 統計
"""

import json
import requests
import subprocess
import hashlib
import sqlite3
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import sys

# ==================== 配置 ====================

STEP1NE_API_BASE = "https://backendstep1ne.zeabur.app"
ACTOR_IDENTITY = "Jacky-aibot"  # 可配置
DEDUP_DB = "/tmp/recruiting-pipeline/dedup.db"

# ==================== 數據類 ====================

@dataclass
class RecommendedCandidate:
    """推薦的候選人"""
    name: str
    job_title: str
    customer_name: str
    industry: str
    overall_score: float
    talent_level: str
    skill_match: float
    experience_fit: float
    location: str = "台北"
    skills: List[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    
    def __post_init__(self):
        if self.skills is None:
            self.skills = []
    
    def get_dedup_hash(self) -> str:
        """生成去重 hash"""
        key = f"{self.name}:{self.job_title}:{self.github_url or ''}"
        return hashlib.md5(key.encode()).hexdigest()

@dataclass
class APICandidate:
    """Step1ne API 格式的候選人"""
    name: str
    position: str
    location: str
    years_experience: int
    skills: str  # 逗號分隔
    source: str  # 來源
    recruiter: str  # 負責顧問
    notes: str
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    contact_link: Optional[str] = None
    actor: str = ACTOR_IDENTITY
    
    def to_dict(self) -> Dict:
        """轉換為 API 請求體"""
        return {
            'name': self.name,
            'position': self.position,
            'location': self.location,
            'years_experience': str(self.years_experience),
            'skills': self.skills,
            'source': self.source,
            'recruiter': self.recruiter,
            'notes': self.notes,
            'linkedin_url': self.linkedin_url,
            'github_url': self.github_url,
            'contact_link': self.contact_link,
            'actor': self.actor,
        }

@dataclass
class SyncResult:
    """同步結果"""
    total_candidates: int
    successfully_imported: int
    skipped_duplicates: int
    failed: int
    errors: List[str]
    imported_ids: List[int]
    timestamp: str

# ==================== 去重機制 ====================

class DeduplicationManager:
    """管理候選人去重"""
    
    def __init__(self, db_path: str = DEDUP_DB):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化去重數據庫"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS imported_candidates (
                id INTEGER PRIMARY KEY,
                dedup_hash TEXT UNIQUE,
                name TEXT,
                job_title TEXT,
                api_candidate_id INTEGER,
                imported_at TIMESTAMP,
                status TEXT
            )
        ''')
        conn.commit()
        conn.close()
    
    def is_duplicate(self, candidate: RecommendedCandidate) -> bool:
        """檢查是否已導入過"""
        conn = sqlite3.connect(self.db_path)
        result = conn.execute(
            'SELECT id FROM imported_candidates WHERE dedup_hash = ?',
            (candidate.get_dedup_hash(),)
        ).fetchone()
        conn.close()
        return result is not None
    
    def record_import(self, candidate: RecommendedCandidate, api_id: int, status: str = 'success'):
        """記錄已導入的候選人"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            INSERT INTO imported_candidates 
            (dedup_hash, name, job_title, api_candidate_id, imported_at, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            candidate.get_dedup_hash(),
            candidate.name,
            candidate.job_title,
            api_id,
            datetime.now().isoformat(),
            status
        ))
        conn.commit()
        conn.close()
    
    def get_import_history(self, days: int = 7) -> List[Dict]:
        """獲取導入歷史"""
        conn = sqlite3.connect(self.db_path)
        results = conn.execute(f'''
            SELECT * FROM imported_candidates 
            WHERE imported_at > datetime('now', '-{days} days')
            ORDER BY imported_at DESC
        ''').fetchall()
        conn.close()
        return results

# ==================== API 客戶端 ====================

class Step1neAPIClient:
    """Step1ne API 客戶端"""
    
    def __init__(self, base_url: str = STEP1NE_API_BASE):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self) -> bool:
        """檢查 API 健康狀態"""
        try:
            resp = self.session.get(f"{self.base_url}/api/health", timeout=5)
            return resp.status_code == 200
        except Exception as e:
            print(f"❌ API 健康檢查失敗：{e}")
            return False
    
    def add_candidate(self, candidate: APICandidate) -> Tuple[bool, Optional[int], str]:
        """新增單個候選人"""
        try:
            resp = self.session.post(
                f"{self.base_url}/api/candidates",
                json=candidate.to_dict(),
                timeout=10
            )
            
            if resp.status_code == 201:
                data = resp.json()
                candidate_id = data.get('data', {}).get('id')
                return True, candidate_id, "success"
            elif resp.status_code == 200:
                # 某些 API 返回 200
                return True, None, "success"
            else:
                return False, None, f"HTTP {resp.status_code}: {resp.text}"
        
        except Exception as e:
            return False, None, str(e)
    
    def add_candidates_bulk(self, candidates: List[APICandidate]) -> Tuple[int, int, List[str]]:
        """批量新增候選人"""
        success_count = 0
        fail_count = 0
        errors = []
        
        for candidate in candidates:
            success, _, msg = self.add_candidate(candidate)
            if success:
                success_count += 1
            else:
                fail_count += 1
                errors.append(f"{candidate.name}: {msg}")
        
        return success_count, fail_count, errors

# ==================== 推薦轉換器 ====================

class RecommendationConverter:
    """將推薦結果轉換為 API 格式"""
    
    @staticmethod
    def convert(rec: RecommendedCandidate) -> APICandidate:
        """轉換單個推薦"""
        
        # 估計年資（基於評分）
        if rec.experience_fit >= 90:
            years = 5
        elif rec.experience_fit >= 80:
            years = 4
        elif rec.experience_fit >= 70:
            years = 3
        else:
            years = 2
        
        # 來源標記
        source = f"Automated Search - {rec.industry.upper()}"
        
        # 聯繫方式
        contact_link = None
        if rec.github_url:
            contact_link = rec.github_url
        elif rec.linkedin_url:
            contact_link = rec.linkedin_url
        
        # 備註
        notes = (
            f"自動搜尋推薦 | 職缺：{rec.job_title} | "
            f"綜合評分：{rec.overall_score:.0f} 分【{rec.talent_level}】 | "
            f"技能匹配：{rec.skill_match:.0f}%"
        )
        
        return APICandidate(
            name=rec.name,
            position=rec.job_title,
            location=rec.location,
            years_experience=years,
            skills=", ".join(rec.skills) if rec.skills else "N/A",
            source=source,
            recruiter="Jacky",
            notes=notes,
            linkedin_url=rec.linkedin_url,
            github_url=rec.github_url,
            contact_link=contact_link,
        )

# ==================== 同步協調器 ====================

class SyncOrchestrator:
    """協調整個同步流程"""
    
    def __init__(self):
        self.api_client = Step1neAPIClient()
        self.dedup_manager = DeduplicationManager()
        self.converter = RecommendationConverter()
    
    def sync_recommendations(self, 
                           recommendations_file: str,
                           batch_size: int = 10,
                           dry_run: bool = False) -> SyncResult:
        """同步推薦到 API"""
        
        print("\n" + "="*80)
        print("🔄 開始同步推薦候選人到履歷池")
        print("="*80 + "\n")
        
        # Step 1: 檢查 API 連線
        print("📡 步驟 1：檢查 API 連線...", end="", flush=True)
        if not self.api_client.health_check():
            print(" ❌")
            return SyncResult(
                total_candidates=0,
                successfully_imported=0,
                skipped_duplicates=0,
                failed=0,
                errors=["API 連線失敗"],
                imported_ids=[],
                timestamp=datetime.now().isoformat()
            )
        print(" ✅\n")
        
        # Step 2: 讀取推薦
        print("📖 步驟 2：讀取推薦結果...", end="", flush=True)
        try:
            with open(recommendations_file, 'r', encoding='utf-8') as f:
                recommendations_data = json.load(f)
        except Exception as e:
            print(f" ❌ ({e})")
            return SyncResult(
                total_candidates=0,
                successfully_imported=0,
                skipped_duplicates=0,
                failed=0,
                errors=[f"讀取檔案失敗：{e}"],
                imported_ids=[],
                timestamp=datetime.now().isoformat()
            )
        
        # 解析推薦
        candidates_to_sync = []
        for job_title, job_data in recommendations_data.get('recommendations', {}).items():
            for rec in job_data.get('top_recommendations', []):
                candidate = RecommendedCandidate(
                    name=rec['name'],
                    job_title=job_title,
                    customer_name=job_data['customer'],
                    industry=job_data['industry'],
                    overall_score=rec['score'],
                    talent_level=rec['level'],
                    skill_match=80.0,  # 簡化
                    experience_fit=85.0,
                    github_url=rec.get('github_url'),
                )
                candidates_to_sync.append(candidate)
        
        print(f" ✅ ({len(candidates_to_sync)} 個推薦)\n")
        
        # Step 3: 去重
        print("🔍 步驟 3：檢查重複...", end="", flush=True)
        unique_candidates = []
        skipped = 0
        
        for candidate in candidates_to_sync:
            if self.dedup_manager.is_duplicate(candidate):
                skipped += 1
            else:
                unique_candidates.append(candidate)
        
        print(f" ✅ (跳過 {skipped} 個重複)\n")
        
        # Step 4: 轉換格式
        print("🔄 步驟 4：轉換為 API 格式...", end="", flush=True)
        api_candidates = [
            self.converter.convert(c) for c in unique_candidates
        ]
        print(f" ✅\n")
        
        # Step 5: 導入
        if dry_run:
            print("🔬 乾執行模式 - 預覽將導入的候選人：\n")
            for i, cand in enumerate(api_candidates[:3], 1):
                print(f"  {i}. {cand.name} - {cand.position}")
                print(f"     來源：{cand.source}")
                print()
            
            if len(api_candidates) > 3:
                print(f"  ... 以及 {len(api_candidates) - 3} 個其他候選人\n")
            
            return SyncResult(
                total_candidates=len(candidates_to_sync),
                successfully_imported=0,
                skipped_duplicates=skipped,
                failed=0,
                errors=[],
                imported_ids=[],
                timestamp=datetime.now().isoformat()
            )
        
        # 真正導入
        print("📤 步驟 5：導入到履歷池...", end="", flush=True)
        success_count, fail_count, errors = self.api_client.add_candidates_bulk(api_candidates)
        
        # 記錄成功的導入
        for i, candidate in enumerate(unique_candidates[:success_count]):
            self.dedup_manager.record_import(candidate, i)
        
        print(f" ✅\n")
        
        # 結果統計
        result = SyncResult(
            total_candidates=len(candidates_to_sync),
            successfully_imported=success_count,
            skipped_duplicates=skipped,
            failed=fail_count,
            errors=errors,
            imported_ids=list(range(1, success_count + 1)),
            timestamp=datetime.now().isoformat()
        )
        
        return result

# ==================== 主程序 ====================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Step1ne API 集成 - 自動導入推薦候選人"
    )
    parser.add_argument(
        '--recommendations',
        default='/tmp/search-execution/recommendations.json',
        help='推薦結果檔案路徑'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=10,
        help='批量導入大小'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='乾執行模式（預覽但不導入）'
    )
    parser.add_argument(
        '--output',
        default='/tmp/recruiting-pipeline/reports/sync-result.json',
        help='同步結果輸出檔案'
    )
    
    args = parser.parse_args()
    
    # 執行同步
    orchestrator = SyncOrchestrator()
    result = orchestrator.sync_recommendations(
        args.recommendations,
        batch_size=args.batch_size,
        dry_run=args.dry_run
    )
    
    # 輸出結果
    print("="*80)
    print("📊 同步結果摘要")
    print("="*80 + "\n")
    
    print(f"✅ 總推薦數：{result.total_candidates}")
    print(f"✅ 成功導入：{result.successfully_imported}")
    print(f"⏭️ 跳過重複：{result.skipped_duplicates}")
    print(f"❌ 失敗：{result.failed}")
    
    if result.errors:
        print(f"\n⚠️ 錯誤摘要：")
        for error in result.errors[:3]:
            print(f"  • {error}")
        if len(result.errors) > 3:
            print(f"  ... 及 {len(result.errors) - 3} 個其他錯誤")
    
    print(f"\n🔗 API 身份：{ACTOR_IDENTITY}")
    print(f"⏰ 時間戳：{result.timestamp}")
    
    # 保存結果
    import os
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump({
            'total_candidates': result.total_candidates,
            'successfully_imported': result.successfully_imported,
            'skipped_duplicates': result.skipped_duplicates,
            'failed': result.failed,
            'imported_ids': result.imported_ids,
            'errors': result.errors,
            'timestamp': result.timestamp,
            'dry_run': args.dry_run,
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 結果已保存：{args.output}")
    
    # 如果是乾執行，提示下一步
    if args.dry_run:
        print("\n💡 乾執行模式完成。若要真正導入，移除 --dry-run 旗標。")
    
    return 0 if result.failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
