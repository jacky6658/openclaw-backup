#!/usr/bin/env python3
"""
斷點續傳管理 - BD 爬蟲穩定版
"""

import json
import os
from typing import Optional, Dict, List
from datetime import datetime

class CheckpointManager:
    """Checkpoint 管理器"""
    
    def __init__(self, checkpoint_file: str):
        self.checkpoint_file = checkpoint_file
        self.data = self._load()
    
    def _load(self) -> dict:
        """載入 checkpoint"""
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load checkpoint: {e}")
                return self._init_data()
        return self._init_data()
    
    def _init_data(self) -> dict:
        """初始化數據結構"""
        return {
            'last_processed_row': 1,  # 最後處理的行號（從 2 開始，1 是標題）
            'total_processed': 0,
            'total_success': 0,
            'total_failed': 0,
            'start_time': datetime.now().isoformat(),
            'last_update': datetime.now().isoformat(),
            'failed_companies': [],  # 失敗的公司清單
            'success_companies': []  # 成功的公司清單
        }
    
    def save(self):
        """保存 checkpoint"""
        self.data['last_update'] = datetime.now().isoformat()
        try:
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error: Failed to save checkpoint: {e}")
    
    def update_progress(self, row: int, company_name: str, success: bool, data: Optional[Dict] = None):
        """更新進度"""
        self.data['last_processed_row'] = row
        self.data['total_processed'] += 1
        
        if success:
            self.data['total_success'] += 1
            self.data['success_companies'].append({
                'row': row,
                'name': company_name,
                'data': data,
                'timestamp': datetime.now().isoformat()
            })
        else:
            self.data['total_failed'] += 1
            self.data['failed_companies'].append({
                'row': row,
                'name': company_name,
                'timestamp': datetime.now().isoformat()
            })
    
    def get_last_row(self) -> int:
        """獲取最後處理的行號"""
        return self.data.get('last_processed_row', 1)
    
    def get_statistics(self) -> dict:
        """獲取統計數據"""
        return {
            'total_processed': self.data['total_processed'],
            'total_success': self.data['total_success'],
            'total_failed': self.data['total_failed'],
            'success_rate': (self.data['total_success'] / self.data['total_processed'] * 100) 
                           if self.data['total_processed'] > 0 else 0
        }
    
    def reset(self):
        """重置 checkpoint（重新開始）"""
        self.data = self._init_data()
        self.save()
    
    def get_failed_companies(self) -> List[dict]:
        """獲取失敗的公司清單"""
        return self.data.get('failed_companies', [])
    
    def should_save(self, interval: int = 5) -> bool:
        """判斷是否應該保存（每處理 N 家公司保存一次）"""
        return self.data['total_processed'] % interval == 0
