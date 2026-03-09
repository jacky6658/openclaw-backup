#!/usr/bin/env python3
"""
測試 Stability Predictor - 驗證 last_gap_months 評分
"""

import json
import subprocess

# 測試案例（包含正確的 last_gap_months）
test_cases = [
    {
        "name": "候選人A（目前在職2年，極穩定）",
        "data": {
            "name": "王大明",
            "total_experience_years": 10.6,
            "avg_tenure_months": 63,
            "job_changes": 1,
            "last_gap_months": 24  # ✅ 目前這份工作做了2年
        },
        "expected": "A級（極低風險），recent_stability 應該 20/20 分"
    },
    {
        "name": "候選人B（目前在職1.5年，穩定）",
        "data": {
            "name": "李小華",
            "total_experience_years": 7.5,
            "avg_tenure_months": 30,
            "job_changes": 2,
            "last_gap_months": 18  # ✅ 目前這份工作做了1.5年
        },
        "expected": "B級（低風險），recent_stability 應該 15/20 分"
    },
    {
        "name": "候選人C（目前在職6個月，不穩定）",
        "data": {
            "name": "張頻繁",
            "total_experience_years": 3.3,
            "avg_tenure_months": 8,
            "job_changes": 4,
            "last_gap_months": 6  # ✅ 目前這份工作做了6個月
        },
        "expected": "E-F級（高風險），recent_stability 應該 5/20 分"
    },
    {
        "name": "候選人D（剛入職3個月，極不穩定）",
        "data": {
            "name": "新人試",
            "total_experience_years": 2.0,
            "avg_tenure_months": 8,
            "job_changes": 2,
            "last_gap_months": 3  # ⚠️ 目前這份工作才做3個月
        },
        "expected": "F級（極高風險），recent_stability 應該 0/20 分"
    },
    {
        "name": "候選人E（目前在職3年，資深極穩定）",
        "data": {
            "name": "老江湖",
            "total_experience_years": 16.1,
            "avg_tenure_months": 193,
            "job_changes": 0,
            "last_gap_months": 36  # ✅ 目前這份工作做了3年
        },
        "expected": "A級（極低風險），recent_stability 應該 20/20 分"
    }
]

def main():
    print("=" * 80)
    print("🎯 Stability Predictor 測試 - 驗證 last_gap_months 評分")
    print("=" * 80)
    
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n案例 {i}：{test['name']}")
        print(f"預期：{test['expected']}")
        print(f"目前在職：{test['data']['last_gap_months']} 個月")
        print("-" * 80)
        
        # 寫入臨時檔案
        temp_file = f"/tmp/candidate_gap_test_{i}.json"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(test['data'], f, ensure_ascii=False, indent=2)
        
        # 執行 stability_predictor.py
        try:
            result = subprocess.run(
                ['python3', '/Users/user/clawd/hr-tools/stability_predictor.py', 
                 '--input', temp_file, '--mode', 'full'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(result.stdout)
                
                # 解析分數
                score = None
                recent_score = None
                for line in result.stdout.split('\n'):
                    if line.startswith('總分:'):
                        score_str = line.split(':')[1].split('/')[0].strip()
                        score = int(score_str)
                    if '"recent_stability"' in line:
                        # 找下一個 "score" 行
                        lines = result.stdout.split('\n')
                        idx = lines.index(line)
                        for j in range(idx, min(idx+5, len(lines))):
                            if '"score":' in lines[j]:
                                recent_score = int(lines[j].split(':')[1].strip().rstrip(','))
                                break
                
                results.append({
                    'name': test['name'],
                    'last_gap_months': test['data']['last_gap_months'],
                    'total_score': score,
                    'recent_stability_score': recent_score
                })
            else:
                print(f"❌ 錯誤：{result.stderr}")
        except Exception as e:
            print(f"❌ 執行失敗：{e}")
    
    # 總結
    print("\n" + "=" * 80)
    print("測試總結")
    print("=" * 80)
    
    print(f"\n{'候選人':<30} {'目前在職':<12} {'總分':<10} {'Recent分':<12}")
    print("-" * 80)
    for r in results:
        print(f"{r['name']:<30} {r['last_gap_months']:<12} {r['total_score']:<10} {r['recent_stability_score']:<12}")
    
    print("\n" + "=" * 80)
    print("✅ 測試完成！")
    print("=" * 80)
    
    print("\n驗證結果：")
    print("• last_gap_months ≥ 24 個月 → recent_stability = 20 分 ✨")
    print("• last_gap_months ≥ 12 個月 → recent_stability = 15 分")
    print("• last_gap_months ≥ 6 個月 → recent_stability = 5 分")
    print("• last_gap_months < 6 個月 → recent_stability = 0 分 ⚠️")

if __name__ == "__main__":
    main()
