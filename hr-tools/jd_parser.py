#!/usr/bin/env python3
"""
JD 解析工具 - 將職缺描述結構化
用途：從客戶提供的 JD 文字中提取關鍵資訊
使用 Claude API 進行智能解析
"""

import json
import sys
import os
import re
from typing import Dict, Optional
import argparse


class JDParser:
    """JD 解析器"""
    
    def __init__(self, api_key: Optional[str] = None):
        """初始化 JD 解析器"""
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            # 如果沒有 API key，使用 OpenClaw 內建的 Claude
            self.use_openclaw = True
        else:
            self.use_openclaw = False
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=self.api_key)
                self.model = "claude-sonnet-4-6"
            except ImportError:
                print("❌ 需要安裝 anthropic: pip install anthropic")
                sys.exit(1)
    
    def parse_jd_text(self, jd_text: str) -> Dict:
        """解析 JD 文字"""
        
        prompt = f"""請分析以下職缺描述（JD），提取結構化資訊。請以 JSON 格式輸出，不要有任何額外說明。

職缺描述：
{jd_text}

請輸出以下格式的 JSON（純 JSON，不要有 markdown 標記）：
{{
  "job_title": "職位名稱",
  "department": "部門（如果有）",
  "company": "公司名稱（如果有）",
  "required_skills": ["必備技能1", "必備技能2", "必備技能3"],
  "preferred_skills": ["加分技能1", "加分技能2"],
  "experience_years": 最低年資要求（數字，如果未提及填 0）,
  "education": "學歷要求（如：大學、碩士、博士、不限）",
  "responsibilities": ["主要工作內容1", "主要工作內容2"],
  "team_culture": "團隊文化描述（如果有）",
  "work_location": "工作地點",
  "remote_ok": true/false（是否可遠端）,
  "salary_range": "薪資範圍（如果有）",
  "overtime_frequency": "加班頻率（無/偶爾/經常，如果未提及填 null）",
  "onboard_urgency": "到職時間要求（如：立即、1個月內、可討論，如果未提及填 null）",
  "benefits": ["福利1", "福利2"]
}}

注意：
1. 只提取 JD 中明確提到的資訊
2. 如果某項資訊未提及，填 null 或空陣列
3. required_skills 和 preferred_skills 要明確區分（通常 required 會用「必須」「需要」等詞）
4. 回覆必須是純 JSON，不要有任何額外文字
"""
        
        if self.use_openclaw:
            # 使用 OpenClaw 內建 Claude
            result_json = self._parse_with_openclaw(prompt)
        else:
            # 使用 anthropic SDK
            result_json = self._parse_with_anthropic(prompt)
        
        # 清理和驗證
        result_json = self._clean_and_validate(result_json)
        
        return result_json
    
    def _parse_with_openclaw(self, prompt: str) -> Dict:
        """使用 subprocess 呼叫 claude CLI（macOS）"""
        import subprocess
        
        try:
            # 使用 echo + pipe 方式呼叫 claude
            cmd = ['claude', '--model', 'claude-sonnet-4-6']
            
            result = subprocess.run(
                cmd,
                input=prompt,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            if result.returncode != 0:
                # 如果 claude CLI 不可用，fallback 到環境變數中的 API key
                if 'ANTHROPIC_API_KEY' in os.environ:
                    return self._parse_with_anthropic(prompt)
                raise Exception(f"Claude CLI 執行失敗: {result.stderr}")
            
            response_text = result.stdout.strip()
            
            # 移除可能的 markdown 格式
            response_text = re.sub(r'^```json\s*', '', response_text)
            response_text = re.sub(r'\s*```$', '', response_text)
            
            return json.loads(response_text)
            
        except FileNotFoundError:
            # claude CLI 不存在，嘗試使用 API key
            if 'ANTHROPIC_API_KEY' in os.environ:
                return self._parse_with_anthropic(prompt)
            raise Exception("找不到 claude CLI，且未設定 ANTHROPIC_API_KEY")
    
    def _parse_with_anthropic(self, prompt: str) -> Dict:
        """使用 Anthropic SDK 解析"""
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
            
            # 移除可能的 markdown 格式
            response_text = re.sub(r'^```json\s*', '', response_text)
            response_text = re.sub(r'\s*```$', '', response_text)
            
            return json.loads(response_text)
            
        except Exception as e:
            raise Exception(f"Claude API 呼叫失敗: {e}")
    
    def _clean_and_validate(self, data: Dict) -> Dict:
        """清理和驗證解析結果"""
        
        # 確保必要欄位存在
        required_fields = [
            'job_title', 'required_skills', 'experience_years', 
            'education', 'responsibilities', 'work_location'
        ]
        
        for field in required_fields:
            if field not in data:
                if field == 'experience_years':
                    data[field] = 0
                elif field in ['required_skills', 'responsibilities']:
                    data[field] = []
                else:
                    data[field] = ''
        
        # 確保數字類型
        if not isinstance(data.get('experience_years'), (int, float)):
            data['experience_years'] = 0
        
        # 確保布林類型
        if 'remote_ok' in data and not isinstance(data['remote_ok'], bool):
            data['remote_ok'] = False
        
        # 確保列表類型
        for list_field in ['required_skills', 'preferred_skills', 'responsibilities', 'benefits']:
            if list_field in data and not isinstance(data[list_field], list):
                data[list_field] = []
        
        return data
    
    def format_for_google_sheets(self, data: Dict) -> Dict:
        """格式化為 Google Sheets 可用的格式"""
        
        return {
            'job_title': data.get('job_title', ''),
            'department': data.get('department', ''),
            'company': data.get('company', ''),
            'required_skills': ', '.join(data.get('required_skills', [])),
            'preferred_skills': ', '.join(data.get('preferred_skills', [])),
            'experience_years': data.get('experience_years', 0),
            'education': data.get('education', ''),
            'responsibilities': ' | '.join(data.get('responsibilities', [])),
            'team_culture': data.get('team_culture', ''),
            'work_location': data.get('work_location', ''),
            'remote_ok': '是' if data.get('remote_ok') else '否',
            'salary_range': data.get('salary_range', ''),
            'overtime_frequency': data.get('overtime_frequency', ''),
            'onboard_urgency': data.get('onboard_urgency', ''),
            'benefits': ', '.join(data.get('benefits', []))
        }


def main():
    parser = argparse.ArgumentParser(description='JD 解析工具')
    parser.add_argument('file', nargs='?', help='JD 文字檔案路徑（可選，或從 stdin 讀取）')
    parser.add_argument('--output', '-o', help='輸出 JSON 檔案路徑（可選）')
    parser.add_argument('--format', '-f', choices=['raw', 'sheets'], default='raw',
                       help='輸出格式：raw（完整 JSON）或 sheets（Google Sheets 格式）')
    
    args = parser.parse_args()
    
    try:
        # 讀取 JD 文字
        if args.file:
            with open(args.file, 'r', encoding='utf-8') as f:
                jd_text = f.read()
        else:
            print("📝 請輸入 JD 文字（輸入完成後按 Ctrl+D）:")
            jd_text = sys.stdin.read()
        
        if not jd_text.strip():
            print("❌ JD 文字不能為空", file=sys.stderr)
            sys.exit(1)
        
        print(f"📄 正在解析 JD...")
        
        # 初始化解析器
        jd_parser = JDParser()
        
        # 解析 JD
        data = jd_parser.parse_jd_text(jd_text)
        
        # 格式化輸出
        if args.format == 'sheets':
            output_data = jd_parser.format_for_google_sheets(data)
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
        print(f"  職位: {data.get('job_title', 'N/A')}")
        print(f"  必備技能: {len(data.get('required_skills', []))} 項")
        print(f"  加分技能: {len(data.get('preferred_skills', []))} 項")
        print(f"  年資要求: {data.get('experience_years', 0)} 年")
        print(f"  地點: {data.get('work_location', 'N/A')}")
        print(f"  遠端: {'可以' if data.get('remote_ok') else '不可以'}")
        
    except Exception as e:
        print(f"❌ 錯誤: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
