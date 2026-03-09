#!/usr/bin/env python3
"""
測試 Stability Predictor - 修正版（使用預計算指標）
"""

import json
import subprocess

# 測試案例：使用預計算指標
test_cases = [
    {
        "name": "候選人A（極穩定）",
        "data": {
            "name": "王大明",
            "total_experience_years": 10.6,
            "avg_tenure_months": 63,  # 平均 5.3 年/份工作
            "job_changes": 1,
            "last_gap_months": 0
        },
        "expected": "A級（極低風險）"
    },
    {
        "name": "候選人B（穩定）",
        "data": {
            "name": "李小華",
            "total_experience_years": 7.5,
            "avg_tenure_months": 30,  # 平均 2.5 年/份工作
            "job_changes": 2,
            "last_gap_months": 1
        },
        "expected": "B級（低風險）"
    },
    {
        "name": "候選人C（不穩定）",
        "data": {
            "name": "張頻繁",
            "total_experience_years": 3.3,
            "avg_tenure_months": 8,  # 平均 8 個月/份工作
            "job_changes": 4,
            "last_gap_months": 0
        },
        "expected": "D-E級（高風險）"
    },
    {
        "name": "候選人D（資深極穩定）",
        "data": {
            "name": "老江湖",
            "total_experience_years": 16.1,
            "avg_tenure_months": 193,  # 單一公司 16 年
            "job_changes": 0,
            "last_gap_months": 0
        },
        "expected": "A級（極低風險）"
    },
    {
        "name": "候選人E（經驗少但穩定）",
        "data": {
            "name": "新人穩",
            "total_experience_years": 2.5,
            "avg_tenure_months": 30,  # 2.5 年單一公司
            "job_changes": 0,
            "last_gap_months": 0
        },
        "expected": "B-C級（中等風險，年資不足）"
    }
]

def main():
    print("=" * 80)
    print("🎯 Stability Predictor 測試（修正版）")
    print("=" * 80)
    
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n案例 {i}：{test['name']}")
        print(f"預期：{test['expected']}")
        print(f"年資：{test['data']['total_experience_years']} 年 | "
              f"平均任期：{test['data']['avg_tenure_months']} 個月 | "
              f"跳槽：{test['data']['job_changes']} 次")
        print("-" * 80)
        
        # 寫入臨時檔案
        temp_file = f"/tmp/candidate_test_{i}.json"
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
                
                # 解析分數（從輸出中提取）
                for line in result.stdout.split('\n'):
                    if line.startswith('總分:'):
                        score_str = line.split(':')[1].split('/')[0].strip()
                        score = int(score_str)
                        results.append({
                            'name': test['name'],
                            'score': score,
                            'expected': test['expected']
                        })
                        break
            else:
                print(f"❌ 錯誤：{result.stderr}")
        except Exception as e:
            print(f"❌ 執行失敗：{e}")
    
    # 總結
    print("\n" + "=" * 80)
    print("測試總結")
    print("=" * 80)
    print(f"\n{'候選人':<25} {'分數':<10} {'預期':<30}")
    print("-" * 80)
    for r in results:
        print(f"{r['name']:<25} {r['score']:<10} {r['expected']:<30}")
    
    print("\n" + "=" * 80)
    print("✅ 測試完成！")
    print("=" * 80)

if __name__ == "__main__":
    main()
