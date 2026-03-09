#!/usr/bin/env python3
"""
文化匹配度計算引擎
用途：計算候選人與公司文化的適配度（0-100 分）
"""

import json
import sys
from typing import Dict, List, Tuple
import argparse


class CultureMatcher:
    """文化匹配度計算器"""
    
    def __init__(self):
        # 各維度權重（總和 100%）
        self.dimension_weights = {
            'work_pace': 10,           # 工作節奏
            'decision_style': 10,      # 決策風格
            'team_atmosphere': 10,     # 團隊氛圍
            'overtime_culture': 15,    # 加班文化
            'communication_style': 10, # 溝通方式
            'growth_path': 10,         # 成長路徑
            'failure_tolerance': 10,   # 失敗容忍度
            'work_life_balance': 15,   # Work-Life Balance
            'work_priorities': 5,      # 工作價值觀
            'motivations': 5           # 工作動力
        }
    
    def match_work_pace(self, company: str, candidate: str) -> Tuple[int, str]:
        """匹配工作節奏"""
        compatibility_matrix = {
            ('快速迭代', '快速變化'): (100, '完美匹配'),
            ('快速迭代', '混合型'): (70, '可適應'),
            ('快速迭代', '穩定可預測'): (30, '可能不適應'),
            ('穩定發展', '穩定可預測'): (100, '完美匹配'),
            ('穩定發展', '混合型'): (70, '可適應'),
            ('穩定發展', '快速變化'): (40, '可能感到無聊'),
            ('混合型', '快速變化'): (80, '適配'),
            ('混合型', '穩定可預測'): (80, '適配'),
            ('混合型', '混合型'): (90, '適配')
        }
        
        score, desc = compatibility_matrix.get((company, candidate), (50, '中等'))
        return score, desc
    
    def match_decision_style(self, company: str, candidate: str) -> Tuple[int, str]:
        """匹配決策風格"""
        compatibility_matrix = {
            ('扁平化', '高度自主'): (100, '完美匹配'),
            ('扁平化', '協作決策'): (90, '適配'),
            ('扁平化', '聽從指導'): (50, '可能感到不適'),
            ('階層化', '聽從指導'): (100, '完美匹配'),
            ('階層化', '協作決策'): (70, '可適應'),
            ('階層化', '高度自主'): (40, '可能產生衝突'),
            ('混合型', '高度自主'): (80, '適配'),
            ('混合型', '協作決策'): (90, '適配'),
            ('混合型', '聽從指導'): (80, '適配')
        }
        
        score, desc = compatibility_matrix.get((company, candidate), (60, '中等'))
        return score, desc
    
    def match_team_atmosphere(self, company: str, candidate: str) -> Tuple[int, str]:
        """匹配團隊氛圍"""
        compatibility_matrix = {
            ('競爭導向', '競爭型'): (100, '完美匹配'),
            ('競爭導向', '平衡型'): (70, '可適應'),
            ('競爭導向', '協作型'): (40, '可能感到壓力'),
            ('協作導向', '協作型'): (100, '完美匹配'),
            ('協作導向', '平衡型'): (80, '適配'),
            ('協作導向', '競爭型'): (50, '可能感到受限'),
            ('平衡型', '競爭型'): (80, '適配'),
            ('平衡型', '協作型'): (80, '適配'),
            ('平衡型', '平衡型'): (90, '適配')
        }
        
        score, desc = compatibility_matrix.get((company, candidate), (60, '中等'))
        return score, desc
    
    def match_overtime_culture(self, company: str, candidate: str) -> Tuple[int, str]:
        """匹配加班文化（重要！）"""
        compatibility_matrix = {
            ('幾乎無加班', '完全不接受'): (100, '完美匹配'),
            ('幾乎無加班', '偶爾可接受'): (100, '適配'),
            ('幾乎無加班', '可以接受'): (90, '適配'),
            ('幾乎無加班', '主動加班'): (70, '可能浪費熱情'),
            
            ('偶爾加班', '完全不接受'): (40, '⚠️ 重大風險'),
            ('偶爾加班', '偶爾可接受'): (100, '完美匹配'),
            ('偶爾加班', '可以接受'): (90, '適配'),
            ('偶爾加班', '主動加班'): (80, '適配'),
            
            ('經常加班', '完全不接受'): (10, '❌ 極高風險'),
            ('經常加班', '偶爾可接受'): (30, '⚠️ 高風險'),
            ('經常加班', '可以接受'): (80, '可適應'),
            ('經常加班', '主動加班'): (100, '完美匹配'),
            
            ('常態加班', '完全不接受'): (0, '❌ 絕對不適配'),
            ('常態加班', '偶爾可接受'): (20, '❌ 極高風險'),
            ('常態加班', '可以接受'): (60, '可能勉強適應'),
            ('常態加班', '主動加班'): (100, '完美匹配')
        }
        
        score, desc = compatibility_matrix.get((company, candidate), (50, '中等'))
        return score, desc
    
    def match_communication_style(self, company: str, candidate: str) -> Tuple[int, str]:
        """匹配溝通方式"""
        compatibility_matrix = {
            ('直接坦率', '直接坦率'): (100, '完美匹配'),
            ('直接坦率', '委婉含蓄'): (50, '可能感到壓力'),
            ('直接坦率', '視情況調整'): (80, '可適應'),
            ('委婉含蓄', '委婉含蓄'): (100, '完美匹配'),
            ('委婉含蓄', '直接坦率'): (60, '可能產生誤會'),
            ('委婉含蓄', '視情況調整'): (80, '可適應'),
            ('正式規範', '直接坦率'): (60, '可能感到繁瑣'),
            ('正式規範', '委婉含蓄'): (80, '適配'),
            ('正式規範', '視情況調整'): (80, '適配'),
            ('非正式彈性', '直接坦率'): (90, '適配'),
            ('非正式彈性', '委婉含蓄'): (70, '可適應'),
            ('非正式彈性', '視情況調整'): (90, '適配')
        }
        
        score, desc = compatibility_matrix.get((company, candidate), (70, '中等'))
        return score, desc
    
    def match_growth_path(self, company: str, candidate_goals: List[str]) -> Tuple[int, str]:
        """匹配成長路徑"""
        # 公司成長路徑 vs 候選人職涯目標
        compatibility = {
            '快速晉升': {
                '快速晉升': 100,
                '技術專家': 40,
                '創業準備': 70,
                '平衡生活': 30,
                '多元發展': 70,
                '財務自由': 60
            },
            '穩定發展': {
                '快速晉升': 40,
                '技術專家': 80,
                '創業準備': 60,
                '平衡生活': 90,
                '多元發展': 70,
                '財務自由': 70
            },
            '專業深耕': {
                '快速晉升': 30,
                '技術專家': 100,
                '創業準備': 50,
                '平衡生活': 80,
                '多元發展': 40,
                '財務自由': 60
            },
            '多元發展': {
                '快速晉升': 70,
                '技術專家': 60,
                '創業準備': 90,
                '平衡生活': 60,
                '多元發展': 100,
                '財務自由': 70
            }
        }
        
        scores = []
        for goal in candidate_goals:
            score = compatibility.get(company, {}).get(goal, 50)
            scores.append(score)
        
        avg_score = sum(scores) / len(scores) if scores else 50
        
        if avg_score >= 80:
            desc = '高度匹配'
        elif avg_score >= 60:
            desc = '適配'
        else:
            desc = '可能不匹配'
        
        return int(avg_score), desc
    
    def match_failure_tolerance(self, company: str, candidate: str) -> Tuple[int, str]:
        """匹配失敗容忍度"""
        compatibility_matrix = {
            ('高度容忍', '從錯誤中學習'): (100, '完美匹配'),
            ('高度容忍', '謹慎避免犯錯'): (60, '可能感到壓力'),
            ('高度容忍', '壓力很大'): (40, '⚠️ 風險'),
            ('中度容忍', '從錯誤中學習'): (80, '適配'),
            ('中度容忍', '謹慎避免犯錯'): (90, '適配'),
            ('中度容忍', '壓力很大'): (60, '可能有壓力'),
            ('低度容忍', '從錯誤中學習'): (40, '可能產生衝突'),
            ('低度容忍', '謹慎避免犯錯'): (100, '完美匹配'),
            ('低度容忍', '壓力很大'): (50, '壓力可能更大')
        }
        
        score, desc = compatibility_matrix.get((company, candidate), (60, '中等'))
        return score, desc
    
    def match_work_life_balance(self, company: str, candidate_priority: int) -> Tuple[int, str]:
        """匹配 Work-Life Balance（重要！）"""
        # candidate_priority: 1-8 (排名)
        
        if company == '非常重視':
            if candidate_priority <= 3:
                return 100, '完美匹配'
            elif candidate_priority <= 5:
                return 80, '適配'
            else:
                return 60, '可適應'
        
        elif company == '適度重視':
            if candidate_priority <= 3:
                return 80, '適配'
            elif candidate_priority <= 5:
                return 90, '適配'
            else:
                return 70, '可適應'
        
        elif company == '工作優先':
            if candidate_priority <= 3:
                return 30, '⚠️ 重大風險'
            elif candidate_priority <= 5:
                return 60, '可能有壓力'
            else:
                return 90, '適配'
        
        return 60, '中等'
    
    def match_work_priorities(self, company_values: List[str], candidate_priorities: List[Dict]) -> Tuple[int, str]:
        """匹配工作價值觀"""
        # 計算公司核心價值與候選人優先級的重疊度
        
        # 候選人 top 3 優先級
        top_3 = [p['value'] for p in candidate_priorities[:3]]
        
        # 映射表
        value_mapping = {
            '創新突破': ['工作挑戰', '職涯發展'],
            '穩定可靠': ['工作穩定', '平衡生活'],
            '快速執行': ['工作挑戰', '薪資福利'],
            '團隊協作': ['團隊氛圍', '企業文化'],
            '個人績效': ['薪資福利', '職涯發展'],
            '客戶至上': ['企業文化', '工作穩定'],
            '技術領先': ['工作挑戰', '職涯發展'],
            '成本控制': ['薪資福利', '工作穩定']
        }
        
        # 計算重疊
        overlap_count = 0
        for company_val in company_values:
            mapped_candidate_vals = value_mapping.get(company_val, [])
            for cand_val in top_3:
                if cand_val in mapped_candidate_vals:
                    overlap_count += 1
        
        # 計算分數
        max_possible = len(company_values) * 2  # 每個公司價值最多對應 2 個候選人優先級
        score = min(100, int((overlap_count / max_possible) * 100)) if max_possible > 0 else 50
        
        if score >= 70:
            desc = '價值觀契合'
        elif score >= 50:
            desc = '部分契合'
        else:
            desc = '價值觀差異'
        
        return score, desc
    
    def match_motivations(self, company_culture: Dict, candidate_motivations: List[str]) -> Tuple[int, str]:
        """匹配工作動力"""
        # 根據公司文化推斷候選人動力是否能被滿足
        
        motivation_satisfaction = {
            '挑戰性任務': {
                '快速迭代': 90,
                '穩定發展': 50,
                '高度容忍': 80
            },
            '明確目標': {
                '階層化': 90,
                '正式規範': 90,
                '穩定發展': 80
            },
            '團隊認同': {
                '協作導向': 90,
                '平衡型': 80,
                '非正式彈性': 80
            },
            '薪資獎勵': {
                '個人績效': 90,
                '競爭導向': 80
            },
            '學習成長': {
                '快速迭代': 90,
                '專業深耕': 90,
                '多元發展': 90
            },
            '社會影響': {
                '客戶至上': 80
            }
        }
        
        scores = []
        for motivation in candidate_motivations:
            satisfaction_map = motivation_satisfaction.get(motivation, {})
            # 檢查公司文化是否滿足此動力
            score = 50  # 預設
            for culture_key, culture_value in company_culture.items():
                # 跳過 list 類型的值
                if isinstance(culture_value, str) and culture_value in satisfaction_map:
                    score = max(score, satisfaction_map[culture_value])
            scores.append(score)
        
        avg_score = sum(scores) / len(scores) if scores else 50
        
        if avg_score >= 80:
            desc = '動力可充分滿足'
        elif avg_score >= 60:
            desc = '動力可滿足'
        else:
            desc = '動力可能不足'
        
        return int(avg_score), desc
    
    def calculate_culture_fit(self, company: Dict, candidate: Dict) -> Dict:
        """計算文化匹配度總分"""
        
        results = {}
        total_score = 0
        
        # 1. 工作節奏
        score, desc = self.match_work_pace(
            company.get('work_pace', ''),
            candidate.get('work_pace_preference', '')
        )
        results['work_pace'] = {'score': score, 'description': desc, 'weight': self.dimension_weights['work_pace']}
        total_score += score * self.dimension_weights['work_pace'] / 100
        
        # 2. 決策風格
        score, desc = self.match_decision_style(
            company.get('decision_style', ''),
            candidate.get('decision_preference', '')
        )
        results['decision_style'] = {'score': score, 'description': desc, 'weight': self.dimension_weights['decision_style']}
        total_score += score * self.dimension_weights['decision_style'] / 100
        
        # 3. 團隊氛圍
        score, desc = self.match_team_atmosphere(
            company.get('team_atmosphere', ''),
            candidate.get('team_atmosphere_preference', '')
        )
        results['team_atmosphere'] = {'score': score, 'description': desc, 'weight': self.dimension_weights['team_atmosphere']}
        total_score += score * self.dimension_weights['team_atmosphere'] / 100
        
        # 4. 加班文化（重要！）
        score, desc = self.match_overtime_culture(
            company.get('overtime_culture', ''),
            candidate.get('overtime_attitude', '')
        )
        results['overtime_culture'] = {'score': score, 'description': desc, 'weight': self.dimension_weights['overtime_culture']}
        total_score += score * self.dimension_weights['overtime_culture'] / 100
        
        # 5. 溝通方式
        score, desc = self.match_communication_style(
            company.get('communication_style', ''),
            candidate.get('communication_style', '')
        )
        results['communication_style'] = {'score': score, 'description': desc, 'weight': self.dimension_weights['communication_style']}
        total_score += score * self.dimension_weights['communication_style'] / 100
        
        # 6. 成長路徑
        score, desc = self.match_growth_path(
            company.get('growth_path', ''),
            candidate.get('career_goals', [])
        )
        results['growth_path'] = {'score': score, 'description': desc, 'weight': self.dimension_weights['growth_path']}
        total_score += score * self.dimension_weights['growth_path'] / 100
        
        # 7. 失敗容忍度
        score, desc = self.match_failure_tolerance(
            company.get('failure_tolerance', ''),
            candidate.get('failure_attitude', '')
        )
        results['failure_tolerance'] = {'score': score, 'description': desc, 'weight': self.dimension_weights['failure_tolerance']}
        total_score += score * self.dimension_weights['failure_tolerance'] / 100
        
        # 8. Work-Life Balance（重要！）
        # 找出候選人 work_priorities 中 "Work-Life Balance" 的排名
        wlb_priority = 8  # 預設最低
        for i, p in enumerate(candidate.get('work_priorities', []), 1):
            if 'work-life balance' in p.get('value', '').lower() or 'work life balance' in p.get('value', '').lower():
                wlb_priority = i
                break
        
        score, desc = self.match_work_life_balance(
            company.get('work_life_balance', ''),
            wlb_priority
        )
        results['work_life_balance'] = {'score': score, 'description': desc, 'weight': self.dimension_weights['work_life_balance']}
        total_score += score * self.dimension_weights['work_life_balance'] / 100
        
        # 9. 工作價值觀
        score, desc = self.match_work_priorities(
            company.get('core_values', []),
            candidate.get('work_priorities', [])
        )
        results['work_priorities'] = {'score': score, 'description': desc, 'weight': self.dimension_weights['work_priorities']}
        total_score += score * self.dimension_weights['work_priorities'] / 100
        
        # 10. 工作動力
        score, desc = self.match_motivations(
            company,
            candidate.get('work_motivations', [])
        )
        results['motivations'] = {'score': score, 'description': desc, 'weight': self.dimension_weights['motivations']}
        total_score += score * self.dimension_weights['motivations'] / 100
        
        # 計算等級
        if total_score >= 80:
            grade = 'A（高度適配）'
            risk_level = '極低風險'
        elif total_score >= 70:
            grade = 'B（適配）'
            risk_level = '低風險'
        elif total_score >= 60:
            grade = 'C（中等適配）'
            risk_level = '中等風險'
        elif total_score >= 50:
            grade = 'D（較低適配）'
            risk_level = '高風險'
        else:
            grade = 'F（不適配）'
            risk_level = '極高風險'
        
        # 識別風險因素
        risk_factors = []
        for dim_name, dim_result in results.items():
            if dim_result['score'] < 50:
                risk_factors.append(f"{dim_name}: {dim_result['description']}")
        
        return {
            'total_score': round(total_score, 1),
            'grade': grade,
            'risk_level': risk_level,
            'dimension_results': results,
            'risk_factors': risk_factors
        }


def main():
    parser = argparse.ArgumentParser(description='文化匹配度計算工具')
    parser.add_argument('--company', required=True, help='公司文化 JSON 檔案')
    parser.add_argument('--candidate', required=True, help='候選人價值觀 JSON 檔案')
    parser.add_argument('--output', '-o', help='輸出結果 JSON 檔案')
    
    args = parser.parse_args()
    
    try:
        # 讀取資料
        with open(args.company, 'r', encoding='utf-8') as f:
            company = json.load(f)
        
        with open(args.candidate, 'r', encoding='utf-8') as f:
            candidate = json.load(f)
        
        print("🎯 文化匹配度分析")
        print("=" * 60)
        print(f"公司: {company.get('company_name', 'N/A')}")
        print(f"候選人: {candidate.get('candidate_name', 'N/A')}")
        print()
        
        # 計算匹配度
        matcher = CultureMatcher()
        result = matcher.calculate_culture_fit(company, candidate)
        
        # 顯示結果
        print(f"📊 總分: {result['total_score']}/100")
        print(f"等級: {result['grade']}")
        print(f"風險: {result['risk_level']}")
        
        print(f"\n📋 各維度匹配結果:")
        for dim_name, dim_result in result['dimension_results'].items():
            icon = '✅' if dim_result['score'] >= 70 else '⚠️' if dim_result['score'] >= 50 else '❌'
            print(f"  {icon} {dim_name}: {dim_result['score']}/100 ({dim_result['description']})")
        
        if result['risk_factors']:
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
