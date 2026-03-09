#!/usr/bin/env python3
"""
使用 Google Gemini Imagen 3 生成圖片
需要：Google AI Studio API Key
"""

import requests
import base64
import json
import sys
import os

# Google AI Studio API Key（從環境變數或配置讀取）
# 你需要到 https://aistudio.google.com/app/apikey 取得
API_KEY = os.getenv("GOOGLE_AI_API_KEY", "")

def generate_image_with_gemini(prompt, output_path="generated_image.png"):
    """
    使用 Gemini 3 Flash 生成圖片
    
    注意：截至 2025，Gemini API 尚未正式支援圖片生成
    這個腳本示範如何用 Gemini 生成圖片描述，然後用其他工具生圖
    """
    
    if not API_KEY:
        print("❌ 請設定 GOOGLE_AI_API_KEY 環境變數")
        print("   訪問：https://aistudio.google.com/app/apikey")
        return False
    
    # Gemini API endpoint
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-3-flash:generateContent?key={API_KEY}"
    
    # 構建請求
    enhanced_prompt = f"""You are an expert graphic designer. Create a detailed visual description for:

{prompt}

Provide:
1. Exact layout (dimensions, positions)
2. Color codes (hex)
3. Typography (fonts, sizes)
4. Visual elements
5. Style guidelines

Format as JSON with keys: layout, colors, typography, elements, style"""
    
    payload = {
        "contents": [{
            "parts": [{
                "text": enhanced_prompt
            }]
        }]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"🎨 生成圖片設計稿：{prompt}")
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        design_spec = result['candidates'][0]['content']['parts'][0]['text']
        
        # 儲存設計稿
        spec_file = output_path.replace('.png', '_spec.json')
        with open(spec_file, 'w', encoding='utf-8') as f:
            f.write(design_spec)
        
        print(f"✅ 設計稿已儲存：{spec_file}")
        print(f"\n📋 設計規格：\n{design_spec[:500]}...")
        
        return design_spec
    else:
        print(f"❌ API 錯誤：{response.status_code}")
        print(response.text)
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方式：")
        print("  python3 gemini-imagen-generate.py \"圖片描述\" [output.png]")
        print("\n範例：")
        print("  python3 gemini-imagen-generate.py \"LinkedIn 封面照片，藍色漸層，Step1ne 獵頭\" banner.png")
        sys.exit(1)
    
    prompt = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else "generated_image.png"
    
    generate_image_with_gemini(prompt, output)
    
    print("\n💡 提示：")
    print("Gemini API 目前不支援直接生圖")
    print("建議使用：")
    print("1. Canva（最簡單）- https://www.canva.com/")
    print("2. DALL-E 3（OpenAI）")
    print("3. Midjourney")
    print("4. Stable Diffusion（本地）")
