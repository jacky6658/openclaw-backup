#!/usr/bin/env python3
"""
PDF 履歷解析工具
用途：從 PDF 提取候選人資訊（姓名、LinkedIn、技能等）
"""

import sys
import re
import subprocess
from pathlib import Path

def extract_text_from_pdf(pdf_path):
    """使用 macOS 內建工具提取 PDF 文字"""
    try:
        # macOS 內建的 textutil 可以轉換 PDF
        result = subprocess.run(
            ['mdls', '-name', 'kMDItemTextContent', '-raw', pdf_path],
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout:
            return result.stdout
        
        # 備用方案：使用 strings 提取可見文字
        result = subprocess.run(
            ['strings', pdf_path],
            capture_output=True,
            text=True
        )
        return result.stdout if result.returncode == 0 else ""
    
    except Exception as e:
        print(f"❌ PDF 解析失敗: {e}", file=sys.stderr)
        return ""

def extract_candidate_name(text):
    """提取候選人姓名"""
    lines = text.split('\n')[:20]  # 只看前 20 行
    
    # 策略 1：英文姓名（大寫開頭）
    for line in lines:
        match = re.search(r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b', line)
        if match:
            return match.group(1)
    
    # 策略 2：中文姓名（2-4 個中文字）
    for line in lines:
        match = re.search(r'[\u4e00-\u9fa5]{2,4}', line)
        if match:
            return match.group(0)
    
    return None

def extract_linkedin(text):
    """提取 LinkedIn URL"""
    match = re.search(r'linkedin\.com/in/([a-zA-Z0-9_-]+)', text, re.IGNORECASE)
    if match:
        return match.group(1)
    return None

def extract_email(text):
    """提取 Email"""
    match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    if match:
        return match.group(0)
    return None

def extract_phone(text):
    """提取電話"""
    # 台灣手機格式：09XX-XXX-XXX 或 09XXXXXXXX
    match = re.search(r'09\d{2}[-\s]?\d{3}[-\s]?\d{3}', text)
    if match:
        return match.group(0)
    return None

def main():
    if len(sys.argv) < 2:
        print("用法：python3 parse-resume-pdf.py <PDF路徑>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not Path(pdf_path).exists():
        print(f"❌ 找不到檔案：{pdf_path}")
        sys.exit(1)
    
    print(f"📄 解析履歷：{pdf_path}")
    print("")
    
    # 提取文字
    text = extract_text_from_pdf(pdf_path)
    
    if not text:
        print("❌ 無法從 PDF 提取文字")
        sys.exit(1)
    
    # 提取資訊
    name = extract_candidate_name(text)
    linkedin = extract_linkedin(text)
    email = extract_email(text)
    phone = extract_phone(text)
    
    # 輸出結果（機器可讀格式）
    print(f"NAME={name or ''}")
    print(f"LINKEDIN={linkedin or ''}")
    print(f"EMAIL={email or ''}")
    print(f"PHONE={phone or ''}")
    
    # 人類可讀格式（註解輸出）
    print("")
    print("# 解析結果：")
    if name:
        print(f"#   姓名：{name}")
    if linkedin:
        print(f"#   LinkedIn：{linkedin}")
    if email:
        print(f"#   Email：{email}")
    if phone:
        print(f"#   電話：{phone}")

if __name__ == '__main__':
    main()
