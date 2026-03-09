#!/usr/bin/env python3
"""
穩定性預測模型 v2 - 文化適配 + 職涯穩定度
用途：綜合評估候選人在特定公司的穩定性（0-100 分）
升級：從單純職涯穩定度，升級為文化適配（60%）+ 職涯穩定度（40%）
"""

import json
import sys
import os
from typing import Dict, Optional
import argparse

# 導入原有的穩定性預測器和文化匹配器
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stability_predictor import StabilityPredictor
from culture_matcher import CultureMatcher


class StabilityPredictorV2:
    """穩定性預測器 v2（文化適配 + 職涯穩定度）"""
    
    def __init__(self):
        self.career_predictor = StabilityPredictor()
        self.culture_matcher = CultureMatcher()
        
        # 權重配置
        self.weights = {
            'culture_fit': 0.60,      # 文化適配度 60%
            'career_stability': 0.40   # 職涯穩定度 40%
        }
    
    def predict(self, candidate: Dict, company: Optional[Dict] = None, mode: str = 'auto') -> Dict:
        """
        預測候選人穩定性
        
        Args:
            candidate: 候選人資料（包含職涯資料 + 價值觀）
            company: 公司文化資料（如果有）
            mode: 'full' (完整評估), 'career_only' (僅職涯), 'auto' (自動判斷)
            
        Returns:
            預測結果
        """
        
        # 自動判斷模式
        if mode == 'auto':
            has_culture_data = (company is not None and 
                                candidate.get('work_pace_preference') is not None)
            mode = 'full' if has_culture_data else 'career_only'
        
        if mode == 'career_only' or company is None:
            # 只計算職涯穩定度（舊版本邏輯）
            career_result = self.career_predictor.predict(candidate, mode='auto')
            
            return {
                'total_score': career_result['score'],
                'grade': career_result['grade'],
                'risk_level': career_result['risk_level'],
                'mode': 'career_only',
                'career_stability': career_result,
                'culture_fit': None,
                'warning': '⚠️ 缺少公司文化資料，僅基於職涯穩定度評估（準確度較低）'
            }
        
        # 完整評估：文化適配 + 職涯穩定度
        
        # 1. 文化適配度（60%）
        culture_result = self.culture_matcher.calculate_culture_fit(company, candidate)
        culture_score = culture_result['total_score']
        culture_contribution = culture_score * self.weights['culture_fit']
        
        # 2. 職涯穩定度（40%）
        career_result = self.career_predictor.predict(candidate, mode='auto')
        career_score = career_result['score']
        career_contribution = career_score * self.weights['career_stability']
        
        # 3. 總分
        total_score = culture_contribution + career_contribution
        
        # 4. 計算等級
        if total_score >= 80:
            grade = 'A（極穩定）'
            risk_level = '極低風險'
        elif total_score >= 70:
            grade = 'B（穩定）'
            risk_level = '低風險'
        elif total_score >= 60:
            grade = 'C（中等）'
            risk_level = '中等風險'
        elif total_score >= 50:
            grade = 'D（不穩定）'
            risk_level = '高風險'
        else:
            grade = 'F（極不穩定）'
            risk_level = '極高風險'
        
        # 5. 綜合風險分析
        all_risks = []
        
        # 文化風險
        if culture_result.get('risk_factors'):
            all_risks.extend(culture_result['risk_factors'])
        
        # 職涯風險
        if career_score < 60:
            if candidate.get('job_changes', 0) > 3:
                all_risks.append('frequent_job_hopping: 頻繁跳槽（{} 次）'.format(candidate.get('job_changes')))
            if candidate.get('avg_tenure_months', 0) < 18:
                all_risks.append('short_tenure: 平均任職時間短（{} 個月）'.format(candidate.get('avg_tenure_months')))
        
        # 6. 保證期建議
        if total_score >= 80:
            guarantee_recommendation = '60 天（標準保證期）'
        elif total_score >= 70:
            guarantee_recommendation = '90 天（標準保證期）'
        elif total_score >= 60:
            guarantee_recommendation = '120 天（建議延長）'
        else:
            guarantee_recommendation = '150 天（強烈建議延長）或考慮其他候選人'
        
        return {
            'total_score': round(total_score, 1),
            'grade': grade,
            'risk_level': risk_level,
            'mode': 'full',
            'breakdown': {
                'culture_fit': {
                    'score': round(culture_score, 1),
                    'contribution': round(culture_contribution, 1),
                    'weight': f'{self.weights["culture_fit"] * 100}%'
                },
                'career_stability': {
                    'score': round(career_score, 1),
                    'contribution': round(career_contribution, 1),
                    'weight': f'{self.weights["career_stability"] * 100}%'
                }
            },
            'culture_fit_detail': culture_result,
            'career_stability_detail': career_result,
            'risk_factors': all_risks,
            'guarantee_period_recommendation': guarantee_recommendation
        }


def main():
    parser = argparse.ArgumentParser(description='穩定性預測工具 v2（文化適配 + 職涯穩定度）')
    parser.add_argument('--candidate', required=True, help='候選人 JSON 檔案（包含職涯 + 價值觀）')
    parser.add_argument('--company', help='公司文化 JSON 檔案（可選）')
    parser.add_argument('--mode', choices=['auto', 'full', 'career_only'], default='auto',
                       help='評估模式')
    parser.add_argument('--output', '-o', help='輸出結果 JSON 檔案')
    
    args = parser.parse_args()
    
    try:
        # 讀取候選人資料
        with open(args.candidate, 'r', encoding='utf-8') as f:
            candidate = json.load(f)
        
        # 讀取公司文化（如果有）
        company = None
        if args.company:
            with open(args.company, 'r', encoding='utf-8') as f:
                company = json.load(f)
        
        print("🎯 穩定性預測 v2（文化適配 + 職涯穩定度）")
        print("=" * 60)
        print(f"候選人: {candidate.get('candidate_name', candidate.get('name', 'N/A'))}")
        if company:
            print(f"公司: {company.get('company_name', 'N/A')}")
        print()
        
        # 預測
        predictor = StabilityPredictorV2()
        result = predictor.predict(candidate, company, mode=args.mode)
        
        # 顯示結果
        print(f"📊 總分: {result['total_score']}/100")
        print(f"等級: {result['grade']}")
        print(f"風險: {result['risk_level']}")
        print(f"模式: {result['mode']}")
        
        if result['mode'] == 'full':
            print(f"\n📋 分數組成:")
            breakdown = result['breakdown']
            print(f"  文化適配: {breakdown['culture_fit']['score']}/100 (貢獻 {breakdown['culture_fit']['contribution']} 分, 權重 {breakdown['culture_fit']['weight']})")
            print(f"  職涯穩定: {breakdown['career_stability']['score']}/100 (貢獻 {breakdown['career_stability']['contribution']} 分, 權重 {breakdown['career_stability']['weight']})")
            
            print(f"\n🔒 保證期建議: {result['guarantee_period_recommendation']}")
        
        if result.get('warning'):
            print(f"\n{result['warning']}")
        
        if result.get('risk_factors'):
            print(f"\n⚠️ 風險因素:")
            for risk in result['risk_factors']:
                print(f"  - {risk}")
        
        # 儲存結果
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\n💾 結果已儲存: {args.output}")
        
    except Exception as e:
        print(f"❌ 錯誤: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
