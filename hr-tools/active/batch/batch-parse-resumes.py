#!/usr/bin/env python3
"""
批量解析履歷 PDF，提取姓名、職位、技能等資訊
"""
import os
import json
import re
from pathlib import Path
import pdfplumber

# 已處理的文件（不重複處理）
PROCESSED_FILES = [
    'file_638', 'file_639', 'file_640', 'file_641', 'file_642', 'file_643',
    'file_644', 'file_645', 'file_646', 'file_647', 'file_648'
]

def extract_text_from_pdf(pdf_path):
    """使用 pdfplumber 提取 PDF 文字"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ''
            for page in pdf.pages[:3]:  # 只讀前 3 頁（履歷通常不超過 3 頁）
                text += page.extract_text() or ''
            return text
    except Exception as e:
        print(f"⚠️  PDF 解析失敗: {e}")
        return ""

def extract_name(text):
    """從履歷中提取姓名"""
    # LinkedIn 履歷通常第一行是姓名
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if not lines:
        return "未知"
    
    # 第一個非空行通常是姓名
    first_line = lines[0]
    
    # 過濾明顯不是姓名的（太長、包含特定關鍵字）
    if len(first_line) > 50 or any(kw in first_line.lower() for kw in ['resume', 'cv', 'curriculum', 'profile']):
        # 嘗試第二行
        if len(lines) > 1:
            return lines[1][:50]  # 限制長度
    
    return first_line[:50]

def extract_position(text):
    """提取職位"""
    # 常見職位關鍵字
    finance_positions = [
        'finance manager', 'financial manager', 'accounting manager',
        'finance controller', 'chief financial officer', 'cfo',
        'finance director', 'finance and accounting manager'
    ]
    
    text_lower = text.lower()
    for pos in finance_positions:
        if pos in text_lower:
            return pos.title()
    
    return "Finance Manager"

def extract_skills(text):
    """提取技能關鍵字"""
    skills = []
    skill_keywords = [
        'sap', 'excel', 'quickbooks', 'erp', 'financial accounting',
        'taxation', 'payroll', 'budgeting', 'forecasting', 'auditing',
        'ifrs', 'gaap', 'cost accounting', 'management accounting',
        'accounts payable', 'accounts receivable', 'general ledger'
    ]
    
    text_lower = text.lower()
    for skill in skill_keywords:
        if skill in text_lower:
            skills.append(skill.upper() if len(skill) <= 4 else skill.title())
    
    return ', '.join(skills[:5]) if skills else "待確認"

def parse_resume(pdf_path):
    """解析單個履歷"""
    text = extract_text_from_pdf(pdf_path)
    if not text:
        return None
    
    name = extract_name(text)
    position = extract_position(text)
    skills = extract_skills(text)
    
    filename = Path(pdf_path).name
    file_id = filename.split('---')[0] if '---' in filename else filename.replace('.pdf', '')
    
    return {
        'name': name,
        'contact': '待補充',
        'position': position,
        'skills': skills,
        'experience_years': '待確認',
        'education': '待確認',
        'file_link': file_id,
        'status': 'PDF已解析',
        'consultant': 'Jacky',
        'notes': 'LinkedIn公開搜尋候選人',
        'created_date': '2026-02-12',
        'updated_date': '2026-02-12'
    }

def main():
    # 找出所有 PDF 文件
    pdf_dir = Path('/Users/user/clawd/hr-recruitment/candidates/cambodia-finance/待分类-稍后处理')
    pdf_files = list(pdf_dir.glob('*.pdf'))
    
    print(f"📂 找到 {len(pdf_files)} 個 PDF 文件")
    
    # 過濾已處理的
    unprocessed = [
        f for f in pdf_files 
        if not any(proc in f.name for proc in PROCESSED_FILES)
    ]
    
    print(f"📝 待處理：{len(unprocessed)} 個")
    
    results = []
    for i, pdf_path in enumerate(unprocessed, 1):
        print(f"[{i}/{len(unprocessed)}] 解析 {pdf_path.name}...", end=' ')
        
        candidate = parse_resume(str(pdf_path))
        if candidate:
            results.append(candidate)
            print(f"✓ {candidate['name']}")
        else:
            print("✗ 失敗")
    
    # 輸出 JSON（供 Google Sheets 匯入）
    output_path = '/tmp/batch-parsed-resumes.json'
    
    # 轉換成 Google Sheets 格式
    sheet_data = [
        [
            c['name'], c['contact'], c['position'], c['skills'],
            c['experience_years'], c['education'], c['file_link'],
            c['status'], c['consultant'], c['notes'],
            c['created_date'], c['updated_date']
        ]
        for c in results
    ]
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sheet_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 完成！共解析 {len(results)} 人")
    print(f"📄 結果：{output_path}")
    
    return results

if __name__ == '__main__':
    main()
