#!/usr/bin/env python3
"""
履歷解析工具 v2 - 提取結構化職涯資料
用途：從 PDF/DOCX 履歷提取姓名、聯絡方式、工作經歷、技能、學歷等
使用 Claude API 進行智能解析
"""

import json
import sys
import os
import re
from datetime import datetime
from typing import Dict, List, Optional
import argparse

try:
    import PyPDF2
except ImportError:
    print("❌ 需要安裝 PyPDF2: pip install PyPDF2")
    sys.exit(1)

try:
    from anthropic import Anthropic
except ImportError:
    print("❌ 需要安裝 anthropic: pip install anthropic")
    sys.exit(1)


class ResumeParser:
    def __init__(self, api_key: Optional[str] = None):
        """初始化履歷解析器"""
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("請設定 ANTHROPIC_API_KEY 環境變數或傳入 api_key")
        
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-6"
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """從 PDF 提取文字內容"""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            raise Exception(f"PDF 讀取失敗: {e}")
    
    def extract_text_from_docx(self, docx_path: str) -> str:
        """從 DOCX 提取文字內容（需要 python-docx）"""
        try:
            import docx
        except ImportError:
            raise ImportError("請安裝 python-docx: pip install python-docx")
        
        try:
            doc = docx.Document(docx_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            raise Exception(f"DOCX 讀取失敗: {e}")
    
    def parse_resume_text(self, resume_text: str) -> Dict:
        """使用 Claude API 解析履歷文字"""
        
        prompt = f"""請分析以下履歷，提取結構化資訊。請以 JSON 格式輸出，不要有任何額外說明或 markdown 格式。

履歷內容：
{resume_text}

請輸出以下格式的 JSON（純 JSON，不要有 ```json 標記）：
{{
  "name": "姓名",
  "contact": {{
    "email": "電子郵件（如果有）",
    "phone": "電話（如果有）",
    "linkedin": "LinkedIn URL（如果有）",
    "github": "GitHub URL（如果有）"
  }},
  "work_history": [
    {{
      "company": "公司名稱",
      "position": "職位",
      "start_date": "YYYY-MM 格式",
      "end_date": "YYYY-MM 格式或 present",
      "duration_months": 計算的月數（數字）,
      "responsibilities": ["主要職責1", "主要職責2"]
    }}
  ],
  "education": [
    {{
      "school": "學校名稱",
      "degree": "學位（學士/碩士/博士）",
      "major": "科系",
      "graduation_year": "畢業年份（YYYY 格式）"
    }}
  ],
  "skills": ["技能1", "技能2", "技能3"],
  "total_experience_years": 總年資（數字，保留一位小數）,
  "job_changes": 跳槽次數（數字）
}}

注意：
1. start_date 和 end_date 必須是 YYYY-MM 格式
2. 如果目前仍在職，end_date 填 "present"
3. duration_months 要精確計算月數
4. total_experience_years 要計算總工作年資（不含教育期間）
5. job_changes 計算跳槽次數（工作經歷數量 - 1）
6. 如果資訊不完整，填 null 或空陣列
7. 回覆必須是純 JSON，不要有任何額外文字或格式標記
"""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            response_text = response.content[0].text.strip()
            
            # 移除可能的 markdown 格式標記
            response_text = re.sub(r'^```json\s*', '', response_text)
            response_text = re.sub(r'\s*```$', '', response_text)
            
            # 解析 JSON
            data = json.loads(response_text)
            
            # 計算額外指標
            data = self._calculate_career_metrics(data)
            
            return data
            
        except json.JSONDecodeError as e:
            raise Exception(f"JSON 解析失敗: {e}\n回應內容: {response_text[:500]}")
        except Exception as e:
            raise Exception(f"Claude API 呼叫失敗: {e}")
    
    def _calculate_career_metrics(self, data: Dict) -> Dict:
        """計算職涯指標（平均任職時間、最近跳槽間隔等）"""
        
        work_history = data.get('work_history', [])
        
        if not work_history:
            data['avg_tenure_months'] = 0
            data['last_gap_months'] = 0
            return data
        
        # 計算平均任職時間
        total_months = sum(job.get('duration_months', 0) for job in work_history)
        data['avg_tenure_months'] = round(total_months / len(work_history), 1) if work_history else 0
        
        # 計算最近跳槽間隔（最近一份工作的任職時間）
        if work_history:
            # 假設工作經歷按時間順序排列（最新的在前）
            latest_job = work_history[0]
            data['last_gap_months'] = latest_job.get('duration_months', 0)
        else:
            data['last_gap_months'] = 0
        
        return data
    
    def parse_resume_file(self, file_path: str) -> Dict:
        """解析履歷檔案（自動判斷 PDF 或 DOCX）"""
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"檔案不存在: {file_path}")
        
        # 判斷檔案類型
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            text = self.extract_text_from_pdf(file_path)
        elif ext in ['.docx', '.doc']:
            text = self.extract_text_from_docx(file_path)
        else:
            raise ValueError(f"不支援的檔案格式: {ext}（僅支援 .pdf, .docx）")
        
        # 解析文字
        return self.parse_resume_text(text)
    
    def format_for_google_sheets(self, data: Dict) -> Dict:
        """格式化為 Google Sheets 可用的格式"""
        
        return {
            'name': data.get('name', ''),
            'email': data.get('contact', {}).get('email', ''),
            'phone': data.get('contact', {}).get('phone', ''),
            'skills': ', '.join(data.get('skills', [])),
            'education': data.get('education', [{}])[0].get('degree', '') if data.get('education') else '',
            'experience_years': data.get('total_experience_years', 0),
            'work_history_json': json.dumps(data.get('work_history', []), ensure_ascii=False),
            'job_changes': data.get('job_changes', 0),
            'avg_tenure_months': data.get('avg_tenure_months', 0),
            'last_gap_months': data.get('last_gap_months', 0),
            'education_json': json.dumps(data.get('education', []), ensure_ascii=False),
            'linkedin': data.get('contact', {}).get('linkedin', ''),
            'github': data.get('contact', {}).get('github', '')
        }


def main():
    parser = argparse.ArgumentParser(description='履歷解析工具 v2')
    parser.add_argument('file', help='履歷檔案路徑（PDF 或 DOCX）')
    parser.add_argument('--output', '-o', help='輸出 JSON 檔案路徑（可選）')
    parser.add_argument('--format', '-f', choices=['raw', 'sheets'], default='raw',
                       help='輸出格式：raw（完整 JSON）或 sheets（Google Sheets 格式）')
    
    args = parser.parse_args()
    
    try:
        # 初始化解析器
        resume_parser = ResumeParser()
        
        print(f"📄 正在解析履歷: {args.file}")
        
        # 解析履歷
        data = resume_parser.parse_resume_file(args.file)
        
        # 格式化輸出
        if args.format == 'sheets':
            output_data = resume_parser.format_for_google_sheets(data)
        else:
            output_data = data
        
        # 輸出結果
        json_output = json.dumps(output_data, ensure_ascii=False, indent=2)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(json_output)
            print(f"✅ 已儲存至: {args.output}")
        else:
            print("\n✅ 解析結果:")
            print(json_output)
        
        # 簡單統計
        print(f"\n📊 統計:")
        print(f"  姓名: {data.get('name', 'N/A')}")
        print(f"  總年資: {data.get('total_experience_years', 0)} 年")
        print(f"  跳槽次數: {data.get('job_changes', 0)} 次")
        print(f"  平均任職: {data.get('avg_tenure_months', 0)} 個月")
        print(f"  技能數量: {len(data.get('skills', []))} 項")
        print(f"  工作經歷: {len(data.get('work_history', []))} 筆")
        
    except Exception as e:
        print(f"❌ 錯誤: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
