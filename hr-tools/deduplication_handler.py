#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
上傳前去重 & 回報機制
版本：v1.0
用途：檢查候選人是否已在系統中，避免重複評分；上傳後生成詳細回報
"""

import requests
import json
from typing import Dict, List, Tuple
from datetime import datetime


class DeduplicationHandler:
    """上傳前去重處理器"""
    
    def __init__(self, api_base: str = "https://backendstep1ne.zeabur.app/api"):
        """初始化"""
        self.api_base = api_base
        self.duplicate_count = 0
        self.new_count = 0
        self.updated_count = 0
        self.failed_count = 0
    
    def check_candidate_exists(self, candidate_id: int) -> Dict:
        """
        檢查候選人是否已在系統中
        
        Args:
            candidate_id: 候選人 ID
        
        Returns:
            {
                "exists": bool,
                "has_ai_match": bool,
                "current_score": int or None,
                "current_grade": str or None,
                "data": dict
            }
        """
        try:
            url = f"{self.api_base}/candidates/{candidate_id}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json().get('data', {})
                ai_match = data.get('aiMatchResult', {})
                
                return {
                    "exists": True,
                    "has_ai_match": bool(ai_match),
                    "current_score": ai_match.get('score') if ai_match else None,
                    "current_grade": ai_match.get('grade') if ai_match else None,
                    "evaluated_at": ai_match.get('evaluated_at') if ai_match else None,
                    "data": data
                }
            else:
                return {
                    "exists": False,
                    "has_ai_match": False,
                    "current_score": None,
                    "current_grade": None,
                    "data": {}
                }
                
        except Exception as e:
            print(f"     ⚠️ 檢查失敗: {str(e)[:50]}")
            return {
                "exists": None,
                "has_ai_match": None,
                "current_score": None,
                "current_grade": None,
                "data": {}
            }
    
    def should_update_candidate(self, candidate_id: int, new_score: int) -> Tuple[bool, str]:
        """
        判斷是否應該更新候選人
        
        Args:
            candidate_id: 候選人 ID
            new_score: 新評分
        
        Returns:
            (should_update: bool, reason: str)
        """
        existing = self.check_candidate_exists(candidate_id)
        
        if not existing["exists"]:
            return (True, "新候選人（系統中不存在）")
        
        if not existing["has_ai_match"]:
            return (True, "候選人存在但無評分（首次評分）")
        
        old_score = existing["current_score"] or 0
        
        if new_score > old_score:
            score_diff = new_score - old_score
            return (True, f"新評分更高（舊: {old_score}, 新: {new_score}, +{score_diff}）")
        elif new_score < old_score:
            score_diff = old_score - new_score
            return (False, f"新評分更低（舊: {old_score}, 新: {new_score}, -{score_diff}）- 保留舊評分")
        else:
            return (False, "評分相同 - 無需更新")
    
    def pre_upload_check(self, candidates: List[Dict]) -> Dict:
        """
        上傳前全面檢查
        
        Args:
            candidates: 待上傳的候選人清單（已評分）
        
        Returns:
            {
                "to_upload": [...],     # 需要上傳的
                "duplicates": [...],    # 重複的
                "skip": [...],          # 跳過的
                "stats": {...}
            }
        """
        to_upload = []
        duplicates = []
        skip = []
        
        print("\n  🔍 執行上傳前去重檢查...")
        print("     ─────────────────────────")
        
        for idx, candidate in enumerate(candidates, 1):
            name = candidate["name"]
            score = candidate["score"]
            
            # 模擬 ID（實際應根據名字查詢）
            candidate_id = 540 + idx - 1
            
            should_upload, reason = self.should_update_candidate(candidate_id, score)
            
            if should_upload:
                to_upload.append(candidate)
                print(f"     ✅ [{idx}] {name}: {reason}")
            else:
                skip.append({
                    "name": name,
                    "score": score,
                    "reason": reason
                })
                print(f"     ⏭️ [{idx}] {name}: {reason}")
        
        print("     ─────────────────────────")
        
        return {
            "to_upload": to_upload,
            "duplicates": duplicates,
            "skip": skip,
            "stats": {
                "total": len(candidates),
                "to_upload": len(to_upload),
                "skip": len(skip),
                "duplicate": len(duplicates)
            }
        }


class UploadReporter:
    """上傳後回報機制"""
    
    def __init__(self, job_title: str):
        """初始化"""
        self.job_title = job_title
        self.upload_results = []
        self.start_time = datetime.now()
    
    def add_result(self, candidate_name: str, candidate_id: int, success: bool, 
                   score: int = None, grade: str = None, message: str = ""):
        """記錄上傳結果"""
        self.upload_results.append({
            "name": candidate_name,
            "id": candidate_id,
            "success": success,
            "score": score,
            "grade": grade,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    def generate_report(self) -> str:
        """生成上傳回報"""
        report = f"""
════════════════════════════════════════════════════════════════════
📊 上傳完成回報 - {self.job_title}
時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
════════════════════════════════════════════════════════════════════

【上傳統計】
"""
        
        # 統計
        total = len(self.upload_results)
        success_count = sum(1 for r in self.upload_results if r["success"])
        failed_count = total - success_count
        
        grade_dist = {}
        for result in self.upload_results:
            if result["success"] and result["grade"]:
                grade = result["grade"]
                grade_dist[grade] = grade_dist.get(grade, 0) + 1
        
        report += f"""
  • 總計: {total} 位
  • 成功: {success_count} 位 ✅
  • 失敗: {failed_count} 位 ❌
  • 成功率: {success_count/max(1, total)*100:.1f}%

【等級分布】
"""
        
        for grade in ['A+', 'A', 'B', 'C', 'D']:
            count = grade_dist.get(grade, 0)
            if count > 0:
                report += f"  • {grade} 級: {count} 位\n"
        
        report += f"""
【詳細清單】
"""
        
        for idx, result in enumerate(self.upload_results, 1):
            status = "✅" if result["success"] else "❌"
            grade = result.get("grade", "N/A")
            score = result.get("score", "N/A")
            
            report += f"""
  {status} [{idx}] {result['name']}
     └─ ID: {result['id']}
     └─ 評分: {score} 分 / {grade} 級
     └─ 狀態: {'上傳成功' if result['success'] else f'上傳失敗 ({result.get("message", "未知錯誤")})'}
"""
        
        # 耗時
        duration = (datetime.now() - self.start_time).total_seconds()
        
        report += f"""
【性能指標】
  ⏱️  總耗時: {duration:.1f} 秒
  📊 平均時間: {duration/max(1, total):.1f} 秒/人
  🎯 吞吐量: {total/max(1, duration)*60:.0f} 人/分鐘

════════════════════════════════════════════════════════════════════
"""
        
        return report
    
    def save_report(self, filepath: str):
        """儲存回報到檔案"""
        report = self.generate_report()
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        return filepath
    
    def send_notification(self, message: str):
        """
        發送通知（Telegram / 郵件 / 日誌）
        
        當前實現：寫入日誌檔案
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
        
        # 寫入日誌
        log_file = f"/tmp/talent-sourcing-{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        return log_file


# 使用範例
if __name__ == "__main__":
    # 去重檢查
    dedup = DeduplicationHandler()
    
    candidates = [
        {"name": "charkchalk", "score": 89, "grade": "A"},
        {"name": "James Wong", "score": 68, "grade": "C"},
        {"name": "Magic Len", "score": 86, "grade": "A"},
    ]
    
    check_result = dedup.pre_upload_check(candidates)
    print(f"\n✅ 檢查完成:")
    print(f"   待上傳: {check_result['stats']['to_upload']} 人")
    print(f"   跳過: {check_result['stats']['skip']} 人")
    
    # 上傳回報
    reporter = UploadReporter("C++ Developer")
    for cand in candidates:
        reporter.add_result(cand["name"], 540 + candidates.index(cand), True, cand["score"], cand["grade"])
    
    report = reporter.generate_report()
    print(report)
    
    # 儲存回報
    saved_file = reporter.save_report(f"/tmp/upload-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt")
    print(f"\n✅ 回報已儲存: {saved_file}")
