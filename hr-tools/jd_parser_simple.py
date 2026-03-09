#!/usr/bin/env python3
"""
JD 解析工具 - 簡化版（使用檔案交換）
用途：將職缺描述結構化
"""

import json
import sys
import os
import subprocess
import tempfile
import argparse


def parse_jd_with_llm(jd_text: str) -> dict:
    """使用 LLM 解析 JD（透過檔案交換）"""
    
    prompt = f"""請分析以下職缺描述（JD），提取結構化資訊。請以 JSON 格式輸出。

職缺描述：
{jd_text}

請輸出以下格式的 JSON：
{{
  "job_title": "職位名稱",
  "department": "部門（如果有）",
  "company": "公司名稱（如果有）",
  "required_skills": ["必備技能1", "必備技能2"],
  "preferred_skills": ["加分技能1", "加分技能2"],
  "experience_years": 最低年資（數字）,
  "education": "學歷要求",
  "responsibilities": ["工作內容1", "工作內容2"],
  "team_culture": "團隊文化描述",
  "work_location": "工作地點",
  "remote_ok": true/false,
  "salary_range": "薪資範圍",
  "overtime_frequency": "加班頻率",
  "onboard_urgency": "到職時間",
  "benefits": ["福利1", "福利2"]
}}

只輸出 JSON，不要有其他說明。"""
    
    # 寫入臨時檔案
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(prompt)
        prompt_file = f.name
    
    output_file = tempfile.mktemp(suffix='.json')
    
    try:
        # 使用 claude CLI（如果可用）
        result = subprocess.run(
            ['claude', prompt_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            response_text = result.stdout.strip()
        else:
            # Fallback: 手動輸入模式
            raise FileNotFoundError("Claude CLI 不可用")
        
        # 清理 markdown 格式
        import re
        response_text = re.sub(r'^```json\s*', '', response_text)
        response_text = re.sub(r'\s*```$', '', response_text)
        
        # 解析 JSON
        data = json.loads(response_text)
        return data
        
    finally:
        # 清理臨時檔案
        if os.path.exists(prompt_file):
            os.remove(prompt_file)
        if os.path.exists(output_file):
            os.remove(output_file)


def main():
    parser = argparse.ArgumentParser(description='JD 解析工具（簡化版）')
    parser.add_argument('file', help='JD 文字檔案路徑')
    parser.add_argument('--output', '-o', help='輸出 JSON 檔案路徑')
    
    args = parser.parse_args()
    
    try:
        # 讀取 JD
        with open(args.file, 'r', encoding='utf-8') as f:
            jd_text = f.read()
        
        print("📄 正在解析 JD...")
        
        # 解析
        data = parse_jd_with_llm(jd_text)
        
        # 輸出
        json_output = json.dumps(data, ensure_ascii=False, indent=2)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(json_output)
            print(f"✅ 已儲存至: {args.output}")
        else:
            print("\n✅ 解析結果:")
            print(json_output)
        
        # 統計
        print(f"\n📊 統計:")
        print(f"  職位: {data.get('job_title', 'N/A')}")
        print(f"  必備技能: {len(data.get('required_skills', []))} 項")
        print(f"  年資: {data.get('experience_years', 0)} 年")
        print(f"  地點: {data.get('work_location', 'N/A')}")
        
    except Exception as e:
        print(f"❌ 錯誤: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
