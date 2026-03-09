#!/usr/bin/env python3
"""
測試 Stability Predictor - 完整模式與簡化模式比較
"""

import json
import subprocess
import sys

# 測試案例：完整工作歷史資料
test_cases_full = [
    {
        "name": "候選人A（穩定型）",
        "candidate": {
            "name": "王大明",
            "work_history": [
                {"company": "台積電", "start": "2018-01", "end": "2026-02", "duration_months": 97},
                {"company": "聯發科", "start": "2015-06", "end": "2017-12", "duration_months": 30}
            ]
        },
        "expected": "A級（極低風險）"
    },
    {
        "name": "候選人B（中等穩定）",
        "candidate": {
            "name": "李小華",
            "work_history": [
                {"company": "Google", "start": "2022-03", "end": "2026-02", "duration_months": 47},
                {"company": "Meta", "start": "2020-01", "end": "2022-02", "duration_months": 25},
                {"company": "Amazon", "start": "2018-06", "end": "2019-12", "duration_months": 18}
            ]
        },
        "expected": "B-C級（低-中等風險）"
    },
    {
        "name": "候選人C（高風險型）",
        "candidate": {
            "name": "張不安",
            "work_history": [
                {"company": "公司A", "start": "2025-06", "end": "2026-02", "duration_months": 8},
                {"company": "公司B", "start": "2024-09", "end": "2025-05", "duration_months": 8},
                {"company": "公司C", "start": "2023-12", "end": "2024-08", "duration_months": 8},
                {"company": "公司D", "start": "2023-03", "end": "2023-11", "duration_months": 8},
                {"company": "公司E", "start": "2022-06", "end": "2023-02", "duration_months": 8}
            ]
        },
        "expected": "D-F級（高風險）"
    },
    {
        "name": "候選人D（資深穩定）",
        "candidate": {
            "name": "老江湖",
            "work_history": [
                {"company": "鴻海", "start": "2010-01", "end": "2026-02", "duration_months": 193}
            ]
        },
        "expected": "A級（極低風險）"
    }
]

# 測試案例：簡化模式（僅年資）
test_cases_simple = [
    {"years": 1.5, "expected_range": "30-40", "risk": "高"},
    {"years": 3.0, "expected_range": "40-50", "risk": "中高"},
    {"years": 5.0, "expected_range": "45-55", "risk": "中等"},
    {"years": 8.0, "expected_range": "50-55", "risk": "中等偏低"},
    {"years": 12.0, "expected_range": "52-55", "risk": "中等偏低"}
]

def test_full_mode():
    """測試完整模式"""
    print("=" * 80)
    print("測試一：完整模式（基於工作歷史）")
    print("=" * 80)
    
    for i, test in enumerate(test_cases_full, 1):
        print(f"\n案例 {i}：{test['name']}")
        print(f"預期：{test['expected']}")
        print("-" * 80)
        
        # 寫入臨時 JSON 檔案
        temp_file = f"/tmp/candidate_{i}.json"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(test['candidate'], f, ensure_ascii=False, indent=2)
        
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
            else:
                print(f"❌ 錯誤：{result.stderr}")
        except Exception as e:
            print(f"❌ 執行失敗：{e}")

def test_simple_mode():
    """測試簡化模式"""
    print("\n" + "=" * 80)
    print("測試二：簡化模式（僅基於年資）")
    print("=" * 80)
    
    print(f"\n{'年資':<10} {'預期分數':<15} {'風險等級':<10} {'實際結果':<30}")
    print("-" * 80)
    
    for test in test_cases_simple:
        try:
            result = subprocess.run(
                ['python3', '/Users/user/clawd/hr-tools/stability_predictor.py', 
                 '--mode', 'simple', '--years', str(test['years'])],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # 解析輸出
                output = result.stdout.strip()
                print(f"{test['years']:<10.1f} {test['expected_range']:<15} {test['risk']:<10} {output}")
            else:
                print(f"{test['years']:<10.1f} {test['expected_range']:<15} {test['risk']:<10} ❌ 錯誤")
        except Exception as e:
            print(f"{test['years']:<10.1f} {test['expected_range']:<15} {test['risk']:<10} ❌ 執行失敗")

def test_auto_mode():
    """測試自動模式"""
    print("\n" + "=" * 80)
    print("測試三：自動模式（智能判斷）")
    print("=" * 80)
    
    # 測試有完整資料的候選人（應該用 full mode）
    print("\n測試 3.1：有完整工作歷史（應使用 full mode）")
    print("-" * 80)
    temp_file = "/tmp/candidate_auto_full.json"
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(test_cases_full[0]['candidate'], f, ensure_ascii=False, indent=2)
    
    try:
        result = subprocess.run(
            ['python3', '/Users/user/clawd/hr-tools/stability_predictor.py', 
             '--input', temp_file, '--mode', 'auto'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"❌ 錯誤：{result.stderr}")
    except Exception as e:
        print(f"❌ 執行失敗：{e}")
    
    # 測試只有年資的候選人（應該用 simple mode）
    print("\n測試 3.2：只有年資資料（應使用 simple mode）")
    print("-" * 80)
    temp_file = "/tmp/candidate_auto_simple.json"
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump({
            "name": "簡化候選人",
            "experience_years": 4.5
        }, f, ensure_ascii=False, indent=2)
    
    try:
        result = subprocess.run(
            ['python3', '/Users/user/clawd/hr-tools/stability_predictor.py', 
             '--input', temp_file, '--mode', 'auto'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"❌ 錯誤：{result.stderr}")
    except Exception as e:
        print(f"❌ 執行失敗：{e}")

def main():
    print("\n🎯 Stability Predictor 完整測試\n")
    
    # 執行三個測試
    test_full_mode()
    test_simple_mode()
    test_auto_mode()
    
    print("\n" + "=" * 80)
    print("✅ 所有測試完成！")
    print("=" * 80)
    print("\n總結：")
    print("- Full mode：基於完整工作歷史，評估 4 個維度")
    print("- Simple mode：僅基於年資，保守評分（最高 55 分）")
    print("- Auto mode：智能判斷使用哪種模式")
    print("=" * 80)

if __name__ == "__main__":
    main()
