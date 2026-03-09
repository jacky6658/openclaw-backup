#!/usr/bin/env python3
"""
數據驗證 - BD 爬蟲穩定版
"""

import re
from typing import Optional, Dict

class DataValidator:
    """數據驗證器"""
    
    @staticmethod
    def validate_phone(phone: Optional[str]) -> bool:
        """驗證電話號碼格式"""
        if not phone:
            return False
        
        # 台灣電話格式
        patterns = [
            r'^0\d{1,2}-\d{3,4}-\d{4}$',  # 02-1234-5678
            r'^0\d{9,10}$',  # 0912345678
        ]
        
        for pattern in patterns:
            if re.match(pattern, phone):
                return True
        
        return False
    
    @staticmethod
    def validate_email(email: Optional[str]) -> bool:
        """驗證 Email 格式"""
        if not email:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_website(website: Optional[str]) -> bool:
        """驗證網址格式"""
        if not website:
            return False
        
        pattern = r'^https?://[^\s]+\.[a-z]{2,}$'
        return bool(re.match(pattern, website, re.IGNORECASE))
    
    @staticmethod
    def validate_company_data(data: Dict[str, Optional[str]]) -> Dict[str, bool]:
        """驗證公司數據（返回各欄位驗證結果）"""
        results = {
            'phone': DataValidator.validate_phone(data.get('phone')),
            'email': DataValidator.validate_email(data.get('email')),
            'website': DataValidator.validate_website(data.get('website')),
            'address': bool(data.get('address')),
            'industry': bool(data.get('industry')),
            'services': bool(data.get('services'))
        }
        
        return results
    
    @staticmethod
    def get_quality_score(validation_results: Dict[str, bool]) -> float:
        """計算數據品質分數（0-100）"""
        total = len(validation_results)
        valid = sum(1 for v in validation_results.values() if v)
        return (valid / total) * 100 if total > 0 else 0
    
    @staticmethod
    def get_data_summary(data: Dict[str, Optional[str]]) -> str:
        """生成數據摘要"""
        validation = DataValidator.validate_company_data(data)
        score = DataValidator.get_quality_score(validation)
        
        summary_parts = []
        if validation['phone']:
            summary_parts.append(f"電話:{data['phone']}")
        if validation['email']:
            summary_parts.append(f"Email:{data['email']}")
        if validation['website']:
            summary_parts.append(f"網站:✓")
        if validation['address']:
            summary_parts.append(f"地址:✓")
        
        summary = " | ".join(summary_parts) if summary_parts else "無有效數據"
        return f"{summary} (品質:{score:.0f}%)"
