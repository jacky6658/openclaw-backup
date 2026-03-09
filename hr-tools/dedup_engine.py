#!/usr/bin/env python3
"""
去重引擎 - 候選人跨平台去重與已推薦歷史追蹤
用途：合併來自 LinkedIn、GitHub、履歷池的候選人，避免重複推薦
"""

import json
import sys
import re
import hashlib
from datetime import datetime
from typing import Dict, List, Set
from pathlib import Path

class DedupEngine:
    def __init__(self, history_file: str = None):
        """初始化去重引擎"""
        if history_file is None:
            history_file = Path(__file__).parent / "data" / "recommended-history.json"
        
        self.history_file = Path(history_file)
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 載入已推薦歷史
        self.history = self._load_history()
    
    def _load_history(self) -> Dict:
        """載入已推薦歷史"""
        if self.history_file.exists():
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'candidates': []}
    
    def _save_history(self):
        """儲存已推薦歷史"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def normalize_name(self, name: str) -> str:
        """標準化姓名"""
        if not name:
            return ""
        
        # 轉小寫
        name = name.lower().strip()
        
        # 移除空格
        name = re.sub(r'\s+', '', name)
        
        # 繁簡轉換（簡單映射，可擴展）
        traditional_to_simplified = {
            '陳': '陈', '張': '张', '劉': '刘', '林': '林',
            '黃': '黄', '吳': '吴', '鄭': '郑', '王': '王',
            '李': '李', '楊': '杨', '蔡': '蔡', '許': '许'
        }
        
        for trad, simp in traditional_to_simplified.items():
            name = name.replace(trad, simp)
        
        return name
    
    def normalize_company(self, company: str) -> str:
        """標準化公司名稱"""
        if not company:
            return ""
        
        company = company.lower().strip()
        
        # 移除常見後綴
        suffixes = [
            '股份有限公司', '有限公司', '科技股份有限公司',
            'co., ltd.', 'co., ltd', 'ltd.', 'ltd',
            'inc.', 'inc', 'corporation', 'corp.',
            '公司', 'company'
        ]
        
        for suffix in suffixes:
            company = company.replace(suffix, '')
        
        # 移除空格
        company = re.sub(r'\s+', '', company)
        
        return company
    
    def generate_fingerprint(self, candidate: Dict) -> str:
        """生成候選人指紋（唯一識別碼）"""
        name = self.normalize_name(candidate.get('name', ''))
        company = self.normalize_company(candidate.get('company', ''))
        
        # 如果有 email，優先使用 email 作為唯一識別
        email = candidate.get('email', '').lower().strip()
        if email:
            return hashlib.md5(email.encode()).hexdigest()[:16]
        
        # 否則使用 姓名+公司
        fingerprint = f"{name}_{company}"
        
        # 如果姓名和公司都為空，使用 LinkedIn/GitHub URL
        if not fingerprint or fingerprint == '_':
            linkedin = candidate.get('linkedin_url', '')
            github = candidate.get('github_url', '')
            
            if linkedin:
                return hashlib.md5(linkedin.encode()).hexdigest()[:16]
            elif github:
                return hashlib.md5(github.encode()).hexdigest()[:16]
        
        return fingerprint
    
    def merge_candidates(self, candidates: List[Dict]) -> List[Dict]:
        """合併重複的候選人"""
        fingerprint_map = {}
        
        for candidate in candidates:
            fingerprint = self.generate_fingerprint(candidate)
            
            if fingerprint in fingerprint_map:
                # 合併資訊（保留更完整的資料）
                existing = fingerprint_map[fingerprint]
                merged = self._merge_candidate_data(existing, candidate)
                fingerprint_map[fingerprint] = merged
            else:
                candidate['fingerprint'] = fingerprint
                fingerprint_map[fingerprint] = candidate
        
        return list(fingerprint_map.values())
    
    def _merge_candidate_data(self, c1: Dict, c2: Dict) -> Dict:
        """合併兩個候選人的資料（保留更完整的）"""
        merged = c1.copy()
        
        # 合併技能（取聯集）
        skills1 = set(c1.get('skills', []))
        skills2 = set(c2.get('skills', []))
        merged['skills'] = list(skills1 | skills2)
        
        # 合併平台來源
        platforms1 = set(c1.get('platforms', []))
        platforms2 = set(c2.get('platforms', []))
        merged['platforms'] = list(platforms1 | platforms2)
        
        # 補充缺失欄位（優先使用非空值）
        for key in c2:
            if key not in merged or not merged[key]:
                merged[key] = c2[key]
        
        # 保留更高的經驗年資
        if 'years_of_experience' in c1 and 'years_of_experience' in c2:
            merged['years_of_experience'] = max(
                c1.get('years_of_experience', 0),
                c2.get('years_of_experience', 0)
            )
        
        return merged
    
    def filter_already_recommended(self, candidates: List[Dict], jd_id: str = None) -> List[Dict]:
        """過濾已推薦的候選人"""
        recommended_fingerprints = set()
        
        for record in self.history['candidates']:
            # 如果指定 jd_id，只過濾該職缺已推薦的
            if jd_id and record.get('jd_id') != jd_id:
                continue
            
            recommended_fingerprints.add(record['fingerprint'])
        
        # 過濾掉已推薦的候選人
        new_candidates = []
        for candidate in candidates:
            fingerprint = candidate.get('fingerprint', self.generate_fingerprint(candidate))
            
            if fingerprint not in recommended_fingerprints:
                new_candidates.append(candidate)
        
        return new_candidates
    
    def mark_as_recommended(self, candidates: List[Dict], jd_id: str, status: str = 'pending'):
        """標記候選人為已推薦"""
        for candidate in candidates:
            fingerprint = candidate.get('fingerprint', self.generate_fingerprint(candidate))
            
            # 檢查是否已存在
            existing = None
            for record in self.history['candidates']:
                if record['fingerprint'] == fingerprint and record.get('jd_id') == jd_id:
                    existing = record
                    break
            
            if existing:
                # 更新狀態
                existing['status'] = status
                existing['last_updated'] = datetime.now().isoformat()
            else:
                # 新增記錄
                self.history['candidates'].append({
                    'fingerprint': fingerprint,
                    'candidate_name': candidate.get('name', ''),
                    'first_recommended': datetime.now().isoformat(),
                    'last_updated': datetime.now().isoformat(),
                    'jd_id': jd_id,
                    'status': status,
                    'platforms': candidate.get('platforms', [])
                })
        
        self._save_history()
    
    def update_status(self, fingerprint: str, jd_id: str, status: str):
        """更新候選人狀態（contacted / skipped / pending）"""
        for record in self.history['candidates']:
            if record['fingerprint'] == fingerprint and record.get('jd_id') == jd_id:
                record['status'] = status
                record['last_updated'] = datetime.now().isoformat()
                break
        
        self._save_history()
    
    def get_recommendation_stats(self, jd_id: str = None) -> Dict:
        """取得推薦統計"""
        stats = {
            'total': 0,
            'contacted': 0,
            'skipped': 0,
            'pending': 0
        }
        
        for record in self.history['candidates']:
            if jd_id and record.get('jd_id') != jd_id:
                continue
            
            stats['total'] += 1
            status = record.get('status', 'pending')
            if status in stats:
                stats[status] += 1
        
        return stats

def main():
    """測試用主函數"""
    # 測試資料
    candidates = [
        {
            'name': '王小明',
            'company': '台積電股份有限公司',
            'email': 'wang@tsmc.com',
            'skills': ['python', 'tensorflow'],
            'platforms': ['linkedin']
        },
        {
            'name': '王小明',  # 重複（同一人）
            'company': '台積電',
            'email': 'wang@tsmc.com',
            'skills': ['python', 'tensorflow', 'pytorch'],
            'platforms': ['github']
        },
        {
            'name': 'Wang Xiaoming',  # 重複（同一人，英文名）
            'company': 'TSMC',
            'linkedin_url': 'https://linkedin.com/in/wangxiaoming',
            'skills': ['python'],
            'platforms': ['linkedin']
        },
        {
            'name': '李小華',
            'company': 'Google Taiwan',
            'email': 'lee@google.com',
            'skills': ['java', 'golang'],
            'platforms': ['github']
        }
    ]
    
    print("=== 去重引擎測試 ===\n")
    print(f"原始候選人數量: {len(candidates)}\n")
    
    # 初始化引擎
    engine = DedupEngine(history_file='/tmp/test-dedup-history.json')
    
    # 合併重複候選人
    merged = engine.merge_candidates(candidates)
    print(f"去重後候選人數量: {len(merged)}\n")
    
    for candidate in merged:
        print(f"姓名: {candidate['name']}")
        print(f"指紋: {candidate['fingerprint']}")
        print(f"平台: {', '.join(candidate['platforms'])}")
        print(f"技能: {', '.join(candidate['skills'])}")
        print("-" * 50)
    
    # 過濾已推薦
    print("\n=== 過濾已推薦測試 ===\n")
    
    # 標記第一個候選人為已推薦
    engine.mark_as_recommended([merged[0]], jd_id='AI工程師-001', status='contacted')
    
    # 過濾已推薦
    new_candidates = engine.filter_already_recommended(merged, jd_id='AI工程師-001')
    print(f"過濾後候選人數量: {len(new_candidates)}")
    
    # 統計
    stats = engine.get_recommendation_stats(jd_id='AI工程師-001')
    print(f"\n推薦統計: {json.dumps(stats, ensure_ascii=False, indent=2)}")

if __name__ == '__main__':
    main()
