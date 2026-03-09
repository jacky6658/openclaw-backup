#!/usr/bin/env python3
"""
穩定性預測模型 - 基於職涯資料評估候選人穩定性
用途：計算候選人穩定性評分（0-100 分），降低保證期退費風險
"""

import json
import sys
from typing import Dict, Optional
from datetime import datetime
import argparse


class StabilityPredictor:
    """穩定性預測器"""
    
    def __init__(self):
        # 評分權重配置
        self.weights = {
            'total_experience': 15,      # 總年資權重
            'avg_tenure': 35,             # 平均任職時間權重
            'job_frequency': 30,          # 跳槽頻率權重
            'recent_stability': 20        # 最近穩定度權重
        }
    
    def calculate_full_score(self, candidate: Dict) -> Dict:
        """
        完整評分（有詳細職涯資料）
        
        Args:
            candidate: 候選人資料（包含 work_history）
            
        Returns:
            評分結果與細節
        """
        score = 0
        details = {}
        
        # 1. 總年資評分（0-15 分）
        years = candidate.get('total_experience_years', 0)
        if years >= 5:
            exp_score = 15
        elif years >= 3:
            exp_score = 10
        elif years >= 1:
            exp_score = 5
        else:
            exp_score = 0
        
        score += exp_score
        details['total_experience'] = {
            'years': years,
            'score': exp_score,
            'max_score': 15
        }
        
        # 2. 平均任職時間評分（0-35 分）
        avg_months = candidate.get('avg_tenure_months', 0)
        if avg_months >= 36:  # ≥3 年
            tenure_score = 35
            tenure_level = '極穩定'
        elif avg_months >= 24:  # ≥2 年
            tenure_score = 25
            tenure_level = '穩定'
        elif avg_months >= 12:  # ≥1 年
            tenure_score = 15
            tenure_level = '普通'
        elif avg_months >= 6:
            tenure_score = 5
            tenure_level = '不穩定'
        else:
            tenure_score = 0
            tenure_level = '極不穩定'
        
        score += tenure_score
        details['avg_tenure'] = {
            'months': avg_months,
            'score': tenure_score,
            'max_score': 35,
            'level': tenure_level
        }
        
        # 3. 跳槽頻率評分（0-30 分）
        job_changes = candidate.get('job_changes', 0)
        years_for_calc = max(years, 1)  # 避免除以 0
        job_changes_per_year = job_changes / years_for_calc
        
        if job_changes_per_year <= 0.3:  # 每 3 年跳 1 次
            freq_score = 30
            freq_level = '極穩定'
        elif job_changes_per_year <= 0.5:  # 每 2 年跳 1 次
            freq_score = 20
            freq_level = '穩定'
        elif job_changes_per_year <= 1:  # 每年跳 1 次
            freq_score = 10
            freq_level = '頻繁'
        else:
            freq_score = 0
            freq_level = '極頻繁'
        
        score += freq_score
        details['job_frequency'] = {
            'job_changes': job_changes,
            'per_year': round(job_changes_per_year, 2),
            'score': freq_score,
            'max_score': 30,
            'level': freq_level
        }
        
        # 4. 最近跳槽間隔評分（0-20 分）
        last_gap = candidate.get('last_gap_months', 0)
        if last_gap >= 24:  # ≥2 年
            gap_score = 20
            gap_level = '極穩定'
        elif last_gap >= 12:  # ≥1 年
            gap_score = 15
            gap_level = '穩定'
        elif last_gap >= 6:
            gap_score = 5
            gap_level = '不穩定'
        else:
            gap_score = 0
            gap_level = '極不穩定'
        
        score += gap_score
        details['recent_stability'] = {
            'months': last_gap,
            'score': gap_score,
            'max_score': 20,
            'level': gap_level
        }
        
        # 總分
        total_score = min(score, 100)
        
        return {
            'score': total_score,
            'grade': self._get_grade(total_score),
            'risk_level': self._get_risk_level(total_score),
            'details': details
        }
    
    def calculate_simple_score(self, experience_years: float) -> Dict:
        """
        簡化評分（只有經驗年數）
        
        Args:
            experience_years: 總年資
            
        Returns:
            評分結果與細節
        """
        score = 0
        details = {}
        
        # 假設：經驗越多，穩定性越高
        # 但保守評分（最高 55 分）
        
        # 1. 總年資（0-15 分）
        if experience_years >= 5:
            exp_score = 15
        elif experience_years >= 3:
            exp_score = 10
        elif experience_years >= 1:
            exp_score = 5
        else:
            exp_score = 0
        
        score += exp_score
        details['total_experience'] = {
            'years': experience_years,
            'score': exp_score,
            'max_score': 15
        }
        
        # 2. 粗估穩定度（0-40 分）
        # 假設：5 年以上經驗的人通常較穩定
        if experience_years >= 7:
            est_score = 40
            est_level = '推測穩定'
        elif experience_years >= 5:
            est_score = 30
            est_level = '推測穩定'
        elif experience_years >= 3:
            est_score = 20
            est_level = '推測普通'
        elif experience_years >= 1:
            est_score = 10
            est_level = '推測不穩定'
        else:
            est_score = 0
            est_level = '推測極不穩定'
        
        score += est_score
        details['estimated_stability'] = {
            'score': est_score,
            'max_score': 40,
            'level': est_level,
            'note': '基於年資粗估，建議補充完整職涯資料以提升準確度'
        }
        
        # 保守總分（最高 55）
        total_score = min(score, 55)
        
        return {
            'score': total_score,
            'grade': self._get_grade(total_score),
            'risk_level': self._get_risk_level(total_score),
            'details': details,
            'estimation_mode': True
        }
    
    def _get_grade(self, score: int) -> str:
        """根據分數返回等級"""
        if score >= 80:
            return 'A（極穩定）'
        elif score >= 60:
            return 'B（穩定）'
        elif score >= 40:
            return 'C（普通）'
        elif score >= 20:
            return 'D（不穩定）'
        else:
            return 'F（極不穩定）'
    
    def _get_risk_level(self, score: int) -> str:
        """根據分數返回風險等級"""
        if score >= 80:
            return '極低風險'
        elif score >= 60:
            return '低風險'
        elif score >= 40:
            return '中等風險'
        elif score >= 20:
            return '高風險'
        else:
            return '極高風險'
    
    def predict(self, candidate: Dict, mode: str = 'auto') -> Dict:
        """
        預測穩定性
        
        Args:
            candidate: 候選人資料
            mode: 'auto' (自動判斷), 'full' (完整), 'simple' (簡化)
            
        Returns:
            預測結果
        """
        if mode == 'auto':
            # 自動判斷：有 work_history 就用完整評分
            has_work_history = bool(candidate.get('work_history') or 
                                    candidate.get('avg_tenure_months') or 
                                    candidate.get('job_changes'))
            mode = 'full' if has_work_history else 'simple'
        
        if mode == 'full':
            return self.calculate_full_score(candidate)
        else:
            experience_years = candidate.get('total_experience_years', 
                                            candidate.get('experience_years', 0))
            return self.calculate_simple_score(experience_years)


def main():
    parser = argparse.ArgumentParser(description='穩定性預測工具')
    parser.add_argument('--input', '-i', help='候選人 JSON 檔案路徑')
    parser.add_argument('--mode', '-m', choices=['auto', 'full', 'simple'], 
                       default='auto', help='評分模式')
    parser.add_argument('--years', '-y', type=float, help='經驗年數（簡化模式）')
    
    args = parser.parse_args()
    
    try:
        predictor = StabilityPredictor()
        
        if args.input:
            # 從檔案讀取候選人資料
            with open(args.input, 'r', encoding='utf-8') as f:
                candidate = json.load(f)
        elif args.years:
            # 使用年資進行簡化評分
            candidate = {'total_experience_years': args.years}
            args.mode = 'simple'
        else:
            print("❌ 請提供 --input 或 --years 參數", file=sys.stderr)
            sys.exit(1)
        
        # 預測穩定性
        result = predictor.predict(candidate, mode=args.mode)
        
        # 輸出結果
        print("\n📊 穩定性預測結果")
        print("=" * 50)
        print(f"總分: {result['score']}/100")
        print(f"等級: {result['grade']}")
        print(f"風險評估: {result['risk_level']}")
        
        if result.get('estimation_mode'):
            print("\n⚠️  注意：使用簡化評分（僅基於年資）")
            print("   建議補充完整職涯資料以提升準確度")
        
        print("\n📋 評分細節:")
        print(json.dumps(result['details'], ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"❌ 錯誤: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
