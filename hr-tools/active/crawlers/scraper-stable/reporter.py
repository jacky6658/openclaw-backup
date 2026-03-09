#!/usr/bin/env python3
"""
進度報告 - BD 爬蟲穩定版
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional

class ProgressReporter:
    """進度報告器"""
    
    def __init__(self, progress_file: str, telegram_group: Optional[str] = None):
        self.progress_file = progress_file
        self.telegram_group = telegram_group
        self.start_time = datetime.now()
    
    def report(self, checkpoint_data: dict, message: Optional[str] = None):
        """生成並輸出進度報告"""
        stats = self._calculate_stats(checkpoint_data)
        report_text = self._format_report(stats, message)
        
        # 保存到檔案
        self._save_progress(stats)
        
        # 輸出到控制台
        print("\n" + "="*50)
        print(report_text)
        print("="*50 + "\n")
        
        return report_text
    
    def _calculate_stats(self, checkpoint_data: dict) -> dict:
        """計算統計數據"""
        total_processed = checkpoint_data.get('total_processed', 0)
        total_success = checkpoint_data.get('total_success', 0)
        total_failed = checkpoint_data.get('total_failed', 0)
        
        # 計算成功率
        success_rate = (total_success / total_processed * 100) if total_processed > 0 else 0
        
        # 計算運行時間
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        elapsed_minutes = int(elapsed_time // 60)
        elapsed_seconds = int(elapsed_time % 60)
        
        # 計算預估剩餘時間
        if total_processed > 0:
            avg_time_per_company = elapsed_time / total_processed
            # 假設總共 302 家公司需要處理
            remaining_companies = 302 - total_processed
            remaining_time = avg_time_per_company * remaining_companies
            remaining_minutes = int(remaining_time // 60)
        else:
            remaining_minutes = 0
        
        return {
            'total_processed': total_processed,
            'total_success': total_success,
            'total_failed': total_failed,
            'success_rate': success_rate,
            'elapsed_minutes': elapsed_minutes,
            'elapsed_seconds': elapsed_seconds,
            'remaining_minutes': remaining_minutes,
            'last_row': checkpoint_data.get('last_processed_row', 1)
        }
    
    def _format_report(self, stats: dict, message: Optional[str] = None) -> str:
        """格式化報告文字"""
        lines = []
        
        if message:
            lines.append(f"📊 {message}")
            lines.append("")
        
        lines.append(f"✅ 已處理: {stats['total_processed']} 家")
        lines.append(f"🎯 成功: {stats['total_success']} 家 ({stats['success_rate']:.1f}%)")
        lines.append(f"❌ 失敗: {stats['total_failed']} 家")
        lines.append(f"⏱️ 已運行: {stats['elapsed_minutes']}分{stats['elapsed_seconds']}秒")
        
        if stats['remaining_minutes'] > 0:
            lines.append(f"⏳ 預估剩餘: {stats['remaining_minutes']} 分鐘")
        
        lines.append(f"📍 當前進度: 第 {stats['last_row']} 行")
        
        return "\n".join(lines)
    
    def _save_progress(self, stats: dict):
        """保存進度到檔案"""
        try:
            progress_data = {
                'timestamp': datetime.now().isoformat(),
                'stats': stats
            }
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save progress: {e}")
    
    def report_final(self, checkpoint_data: dict):
        """最終報告"""
        stats = self._calculate_stats(checkpoint_data)
        
        lines = []
        lines.append("🎉 BD 爬蟲完成！")
        lines.append("")
        lines.append(f"✅ 總共處理: {stats['total_processed']} 家")
        lines.append(f"🎯 成功: {stats['total_success']} 家 ({stats['success_rate']:.1f}%)")
        lines.append(f"❌ 失敗: {stats['total_failed']} 家")
        lines.append(f"⏱️ 總耗時: {stats['elapsed_minutes']}分{stats['elapsed_seconds']}秒")
        
        # 計算平均處理時間
        if stats['total_processed'] > 0:
            avg_seconds = (stats['elapsed_minutes'] * 60 + stats['elapsed_seconds']) / stats['total_processed']
            lines.append(f"📊 平均: {avg_seconds:.1f} 秒/家")
        
        report_text = "\n".join(lines)
        
        print("\n" + "="*50)
        print(report_text)
        print("="*50 + "\n")
        
        return report_text
