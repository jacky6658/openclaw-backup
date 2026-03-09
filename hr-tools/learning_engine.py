#!/usr/bin/env python3
"""
主動學習系統 - 記錄決策、分析偏好、優化推薦
用途：從 Jacky 的選擇中學習，自動優化候選人推薦
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import statistics

class LearningEngine:
    def __init__(self, data_dir: str = None):
        """初始化學習引擎"""
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.decision_log_file = self.data_dir / "decision-log.json"
        self.weights_file = self.data_dir / "learned-weights.json"
        
        # 載入決策日誌
        self.decisions = self._load_decisions()
        
        # 載入學習到的權重
        self.weights = self._load_weights()
    
    def _load_decisions(self) -> List[Dict]:
        """載入決策日誌"""
        if self.decision_log_file.exists():
            with open(self.decision_log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_decisions(self):
        """儲存決策日誌"""
        with open(self.decision_log_file, 'w', encoding='utf-8') as f:
            json.dump(self.decisions, f, ensure_ascii=False, indent=2)
    
    def _load_weights(self) -> Dict:
        """載入學習到的權重"""
        if self.weights_file.exists():
            with open(self.weights_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 預設權重（與 ai-matcher-v2.py 一致）
        return {
            'skill_match': 0.40,
            'experience': 0.30,
            'industry': 0.20,
            'bonus': 0.10,
            'last_updated': datetime.now().isoformat()
        }
    
    def _save_weights(self):
        """儲存學習到的權重"""
        self.weights['last_updated'] = datetime.now().isoformat()
        with open(self.weights_file, 'w', encoding='utf-8') as f:
            json.dump(self.weights, f, ensure_ascii=False, indent=2)
    
    def record_decision(self, candidate: Dict, jd_id: str, decision: str, score: float, features: Dict):
        """記錄一個決策"""
        decision_record = {
            'date': datetime.now().isoformat(),
            'jd_id': jd_id,
            'candidate_fingerprint': candidate.get('fingerprint', candidate.get('name', 'unknown')),
            'candidate_name': candidate.get('name', ''),
            'decision': decision,  # 'contacted' | 'skipped' | 'pending'
            'score': score,
            'features': features
        }
        
        self.decisions.append(decision_record)
        self._save_decisions()
        
        return decision_record
    
    def analyze_preferences(self, days: int = 30) -> Dict:
        """分析偏好模式（過去 N 天）"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # 篩選最近 N 天的決策
        recent_decisions = [
            d for d in self.decisions
            if datetime.fromisoformat(d['date']) > cutoff_date
        ]
        
        if len(recent_decisions) < 5:
            return {
                'status': 'insufficient_data',
                'message': f'需要至少 5 個決策才能分析（目前 {len(recent_decisions)} 個）',
                'total_decisions': len(recent_decisions)
            }
        
        # 分離「聯繫」和「略過」的候選人
        contacted = [d for d in recent_decisions if d['decision'] == 'contacted']
        skipped = [d for d in recent_decisions if d['decision'] == 'skipped']
        
        analysis = {
            'period_days': days,
            'total_decisions': len(recent_decisions),
            'contacted_count': len(contacted),
            'skipped_count': len(skipped),
            'contact_rate': len(contacted) / len(recent_decisions) if recent_decisions else 0,
            'preferences': {},
            'red_flags': {}
        }
        
        # 分析特徵偏好
        if contacted:
            # GitHub 活躍度
            github_active_contacted = sum(1 for d in contacted if d['features'].get('github_active', False))
            github_active_rate = github_active_contacted / len(contacted)
            
            # 公司等級
            company_a_contacted = sum(1 for d in contacted if d['features'].get('company_tier') == 'A')
            company_a_rate = company_a_contacted / len(contacted)
            
            # 平均分數
            avg_contacted_score = statistics.mean(d['score'] for d in contacted)
            
            # 技能匹配度
            avg_skill_match = statistics.mean(
                d['features'].get('skill_match_ratio', 0) for d in contacted
            )
            
            analysis['preferences'] = {
                'github_active_rate': round(github_active_rate, 2),
                'company_a_rate': round(company_a_rate, 2),
                'avg_score': round(avg_contacted_score, 1),
                'avg_skill_match': round(avg_skill_match, 2),
                'min_score_threshold': round(min(d['score'] for d in contacted), 1)
            }
        
        # 分析紅旗（常被略過的特徵）
        if skipped:
            freq_job_hopping_skipped = sum(
                1 for d in skipped 
                if 'frequent_job_hopping' in d['features'].get('red_flags', [])
            )
            
            skill_mismatch_skipped = sum(
                1 for d in skipped
                if 'skill_mismatch' in d['features'].get('red_flags', [])
            )
            
            analysis['red_flags'] = {
                'frequent_job_hopping_rate': round(freq_job_hopping_skipped / len(skipped), 2) if skipped else 0,
                'skill_mismatch_rate': round(skill_mismatch_skipped / len(skipped), 2) if skipped else 0
            }
        
        return analysis
    
    def suggest_weight_adjustments(self, analysis: Dict) -> Dict:
        """根據分析結果建議權重調整"""
        if analysis.get('status') == 'insufficient_data':
            return {'adjustments': [], 'reason': 'insufficient_data'}
        
        suggestions = []
        current_weights = self.weights.copy()
        
        prefs = analysis.get('preferences', {})
        
        # 如果 GitHub 活躍度高（>70%），提高 bonus 權重
        if prefs.get('github_active_rate', 0) > 0.7:
            suggestions.append({
                'parameter': 'bonus',
                'current': current_weights['bonus'],
                'suggested': min(0.15, current_weights['bonus'] + 0.05),
                'reason': f'你常選 GitHub 活躍的候選人（{prefs["github_active_rate"]*100:.0f}%）'
            })
        
        # 如果技能匹配度要求高（>0.8），提高 skill_match 權重
        if prefs.get('avg_skill_match', 0) > 0.8:
            suggestions.append({
                'parameter': 'skill_match',
                'current': current_weights['skill_match'],
                'suggested': min(0.50, current_weights['skill_match'] + 0.05),
                'reason': f'你偏好技能匹配度高的候選人（平均 {prefs["avg_skill_match"]*100:.0f}%）'
            })
        
        # 如果公司等級重要（>60% A級公司），調整加分
        if prefs.get('company_a_rate', 0) > 0.6:
            suggestions.append({
                'parameter': 'company_tier_bonus',
                'current': 3,
                'suggested': 5,
                'reason': f'你偏好知名公司背景（{prefs["company_a_rate"]*100:.0f}%）'
            })
        
        return {
            'adjustments': suggestions,
            'analysis_summary': analysis
        }
    
    def apply_weight_adjustments(self, adjustments: List[Dict]):
        """應用權重調整"""
        for adj in adjustments:
            param = adj['parameter']
            new_value = adj['suggested']
            
            if param in self.weights:
                old_value = self.weights[param]
                self.weights[param] = new_value
                print(f"✅ {param}: {old_value} → {new_value}")
            else:
                # 新參數（如 company_tier_bonus）
                self.weights[param] = new_value
                print(f"✅ 新增 {param}: {new_value}")
        
        self._save_weights()
    
    def generate_weekly_report(self) -> str:
        """生成每週學習報告"""
        analysis = self.analyze_preferences(days=7)
        
        if analysis.get('status') == 'insufficient_data':
            return f"📊 本週學習報告\n\n{analysis['message']}\n\n繼續累積決策資料以啟用主動學習。"
        
        report = f"""📊 每週學習報告 ({datetime.now().strftime('%Y-%m-%d')})

📈 決策統計（過去 7 天）
• 總決策數：{analysis['total_decisions']}
• 已聯繫：{analysis['contacted_count']} 位
• 已略過：{analysis['skipped_count']} 位
• 聯繫率：{analysis['contact_rate']*100:.1f}%

💡 偏好分析
• GitHub 活躍偏好：{analysis['preferences'].get('github_active_rate', 0)*100:.0f}%
• 知名公司偏好：{analysis['preferences'].get('company_a_rate', 0)*100:.0f}%
• 平均聯繫分數：{analysis['preferences'].get('avg_score', 0):.1f} 分
• 技能匹配要求：{analysis['preferences'].get('avg_skill_match', 0)*100:.0f}%
• 最低分數門檻：{analysis['preferences'].get('min_score_threshold', 0):.1f} 分

⚠️ 紅旗識別
• 頻繁跳槽被略過率：{analysis['red_flags'].get('frequent_job_hopping_rate', 0)*100:.0f}%
• 技能不符被略過率：{analysis['red_flags'].get('skill_mismatch_rate', 0)*100:.0f}%

🔧 權重調整建議
"""
        
        suggestions = self.suggest_weight_adjustments(analysis)
        
        if suggestions['adjustments']:
            for adj in suggestions['adjustments']:
                report += f"\n• {adj['parameter']}: {adj['current']} → {adj['suggested']}"
                report += f"\n  理由：{adj['reason']}\n"
        else:
            report += "\n目前權重設定良好，暫不需調整。\n"
        
        return report

def main():
    """測試與示範"""
    engine = LearningEngine(data_dir='/tmp/test-learning')
    
    print("=== 主動學習系統測試 ===\n")
    
    # 模擬一些決策
    test_decisions = [
        {
            'candidate': {'name': '王小明', 'fingerprint': 'wang123'},
            'jd_id': 'AI工程師-001',
            'decision': 'contacted',
            'score': 85,
            'features': {
                'skill_match_ratio': 0.9,
                'github_active': True,
                'company_tier': 'A',
                'red_flags': []
            }
        },
        {
            'candidate': {'name': '李小華', 'fingerprint': 'lee456'},
            'jd_id': 'AI工程師-001',
            'decision': 'contacted',
            'score': 78,
            'features': {
                'skill_match_ratio': 0.85,
                'github_active': True,
                'company_tier': 'A',
                'red_flags': []
            }
        },
        {
            'candidate': {'name': '張大同', 'fingerprint': 'chang789'},
            'jd_id': 'AI工程師-001',
            'decision': 'skipped',
            'score': 45,
            'features': {
                'skill_match_ratio': 0.3,
                'github_active': False,
                'company_tier': 'C',
                'red_flags': ['frequent_job_hopping', 'skill_mismatch']
            }
        }
    ]
    
    for td in test_decisions:
        engine.record_decision(
            td['candidate'],
            td['jd_id'],
            td['decision'],
            td['score'],
            td['features']
        )
    
    print(f"✅ 記錄了 {len(test_decisions)} 個決策\n")
    
    # 分析偏好
    print("📊 偏好分析：\n")
    analysis = engine.analyze_preferences(days=30)
    print(json.dumps(analysis, ensure_ascii=False, indent=2))
    print()
    
    # 生成報告
    print("\n📋 每週學習報告：\n")
    report = engine.generate_weekly_report()
    print(report)

if __name__ == '__main__':
    main()
