#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
展示帶有真實延遲的爬蟲流程
對比：模擬 vs 真實延遲
"""

import sys
import time
sys.path.insert(0, '/Users/user/clawd/hr-tools')

from human_behavior import HumanBehavior, BatchDispatcher
from datetime import datetime

def simulate_crawl_with_delays():
    """展示帶有真實延遲的完整爬蟲流程"""
    
    print("=" * 80)
    print("🚀 爬蟲流程模擬 - 帶有人類行為延遲")
    print("=" * 80)
    print()
    
    start_time = time.time()
    
    # ===== 第二階段：搜尋 =====
    print("【第二階段】雙管道智慧搜尋")
    print()
    
    # GitHub 搜尋
    print("📍 GitHub 搜尋中...")
    github_start = time.time()
    
    # 模擬：搜尋延遲
    print("   🔄 搜尋查詢... ", end='', flush=True)
    HumanBehavior.think_pause(2, 3)  # 2-3 秒思考延遲
    print(f"✅ ({time.time() - github_start:.1f}s)")
    
    # 模擬：找到 2 位候選人，每人間隔 3-5 秒
    candidates_github = ["charkchalk", "James Wong"]
    for idx, name in enumerate(candidates_github, 1):
        print(f"   • 候選人 {idx}: {name} ", end='', flush=True)
        HumanBehavior.request_pause(2, 5)  # 2-5 秒請求延遲
        print(f"✅")
    
    github_duration = time.time() - github_start
    print(f"   GitHub 搜尋完成：{github_duration:.1f} 秒")
    print()
    
    # LinkedIn 搜尋
    print("💼 LinkedIn Google 搜尋中...")
    linkedin_start = time.time()
    
    print("   🔄 Google 搜尋... ", end='', flush=True)
    HumanBehavior.think_pause(1, 2)  # 1-2 秒思考延遲
    print(f"✅ ({time.time() - linkedin_start:.1f}s)")
    
    candidates_linkedin = ["Magic Len", "David Chen"]
    for idx, name in enumerate(candidates_linkedin, 1):
        print(f"   • 候選人 {idx}: {name} ", end='', flush=True)
        HumanBehavior.action_pause(0.5, 1)  # 0.5-1 秒操作延遲
        print(f"✅")
    
    linkedin_duration = time.time() - linkedin_start
    print(f"   LinkedIn 搜尋完成：{linkedin_duration:.1f} 秒")
    print()
    
    search_total = time.time() - start_time
    print(f"✅ 第二階段完成：{search_total:.1f} 秒")
    print()
    
    # ===== 第三階段：去重 =====
    print("【第三階段】智慧去重")
    print("   ⚡ 瞬間完成（無延遲）")
    print()
    
    # ===== 第四階段：評分 =====
    print("【第四階段】AI 配對評分")
    print()
    
    all_candidates = candidates_github + candidates_linkedin
    scoring_start = time.time()
    
    for idx, name in enumerate(all_candidates, 1):
        print(f"   🤖 [{idx}] {name} ", end='', flush=True)
        # 每人評分間隔 2-5 秒
        HumanBehavior.request_pause(2, 5)
        print(f"✅ ({(time.time() - scoring_start):.1f}s 累計)")
    
    scoring_duration = time.time() - scoring_start
    print(f"   評分完成：{scoring_duration:.1f} 秒")
    print()
    
    # ===== 第五階段：批量上傳（帶批次延遲）=====
    print("【第五階段】批量上傳系統")
    print()
    
    upload_start = time.time()
    dispatcher = BatchDispatcher(batch_size=2, batch_delay_min=10, batch_delay_max=12)
    
    # 模擬上傳
    def mock_upload(candidate):
        time.sleep(0.5)  # 模擬 API 調用
        return f"✅ {candidate} 上傳成功"
    
    print("   📤 第一批（2 人）：", end='', flush=True)
    for i in range(2):
        mock_upload(all_candidates[i])
    print(f"完成")
    
    print("   ⏸️ 批次休息... ", end='', flush=True)
    HumanBehavior.batch_pause(10, 12)  # 10-12 秒批次延遲
    print(f"✅")
    
    print("   📤 第二批（2 人）：", end='', flush=True)
    for i in range(2, 4):
        mock_upload(all_candidates[i])
    print(f"完成")
    
    upload_duration = time.time() - upload_start
    print(f"   上傳完成：{upload_duration:.1f} 秒")
    print()
    
    # ===== 總結 =====
    total_duration = time.time() - start_time
    
    print("=" * 80)
    print("【完整流程統計】")
    print("=" * 80)
    print()
    print("第二階段 - 搜尋:")
    print(f"  • GitHub:    {github_duration:.1f} 秒")
    print(f"  • LinkedIn:  {linkedin_duration:.1f} 秒")
    print(f"  小計:       {search_total:.1f} 秒")
    print()
    print("第四階段 - 評分:")
    print(f"  • 4 位候選人，每人 2-5 秒")
    print(f"  小計:       {scoring_duration:.1f} 秒")
    print()
    print("第五階段 - 上傳:")
    print(f"  • 2 批次，每批 2 人")
    print(f"  • 批次間隔: 10-12 秒")
    print(f"  小計:       {upload_duration:.1f} 秒")
    print()
    print(f"【總耗時】{total_duration:.1f} 秒 (~{int(total_duration/60)} 分 {int(total_duration % 60)} 秒)")
    print()
    print("=" * 80)
    print()
    print("✅ 這才是真實的爬蟲速度！")
    print()
    print("對比：")
    print(f"  • 當前模擬:  ~150 秒 (2-3 分鐘)")
    print(f"  • 真實延遲:  ~{int(total_duration)} 秒 ({int(total_duration/60)} 分)")
    print(f"  • 差異因素:  實際 API 調用、更多延遲、人類化行為")
    print()


if __name__ == "__main__":
    simulate_crawl_with_delays()
