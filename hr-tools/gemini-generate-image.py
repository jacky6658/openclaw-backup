#!/usr/bin/env python3
"""
使用 Gemini Imagen 3 生成圖片
需要：gemini CLI 已授權
"""

import subprocess
import sys
import os

def generate_image(prompt, output_path=None, count=1):
    """
    使用 Gemini Imagen 生成圖片
    
    Args:
        prompt: 圖片描述（英文效果最好）
        output_path: 輸出路徑（可選）
        count: 生成數量（1-4）
    """
    
    cmd = ["gemini", "imagen", prompt]
    
    if output_path:
        cmd.extend(["--output", output_path])
    
    if count > 1:
        cmd.extend(["--count", str(count)])
    
    print(f"🎨 生成圖片：{prompt}")
    print(f"📂 輸出：{output_path or '當前目錄'}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ 圖片已生成！")
        print(result.stdout)
        return True
    else:
        print(f"❌ 生成失敗：{result.stderr}")
        return False

# 預設模板
TEMPLATES = {
    "salary_chart": {
        "prompt": "Professional salary comparison chart for .NET engineers, modern blue gradient design, clean typography, showing 4 levels: Junior (55k), Mid (85k), Senior (120k), Lead (170k), business infographic style",
        "output": "/Users/user/clawd/hr-tools/linkedin-salary-dotnet.png"
    },
    "skill_trend": {
        "prompt": "Technology skill demand trend chart, showing programming languages with growth arrows, modern tech style, blue and orange colors, minimalist infographic",
        "output": "/Users/user/clawd/hr-tools/linkedin-skill-trend.png"
    },
    "linkedin_banner": {
        "prompt": "LinkedIn banner image 1584x396px, blue gradient background, text 'Tech Talent Expert | Career Growth | Step1ne', professional modern design, minimalist",
        "output": "/Users/user/clawd/hr-tools/linkedin-banner.png"
    },
    "job_post": {
        "prompt": "Job posting social media image, blue tech style, text area for job details, modern gradient, professional recruitment design",
        "output": "/Users/user/clawd/hr-tools/linkedin-job-template.png"
    }
}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方式：")
        print("  python3 gemini-generate-image.py <template_name>")
        print("  python3 gemini-generate-image.py \"custom prompt\" [output_path]")
        print("\n可用模板：")
        for name in TEMPLATES.keys():
            print(f"  - {name}")
        sys.exit(1)
    
    template_name = sys.argv[1]
    
    # 檢查是否為預設模板
    if template_name in TEMPLATES:
        template = TEMPLATES[template_name]
        generate_image(template["prompt"], template["output"])
    else:
        # 自訂 prompt
        custom_prompt = sys.argv[1]
        custom_output = sys.argv[2] if len(sys.argv) > 2 else None
        generate_image(custom_prompt, custom_output)
