#!/usr/bin/env python3
"""使用 Google Sheets API 创建新分页"""

import subprocess
import json
import sys

SHEET_ID = "1PunpaDAFBPBL_I76AiRYGXKaXDZvMl1c262SEtxRk6Q"
NEW_SHEET_NAME = "履歷池v2"
ACCOUNT = "aiagentg888@gmail.com"

# 获取 access token（从 gog 的存储中）
def get_access_token():
    # gog 的 token 存储路径通常在 ~/.config/gog/
    # 但我们可以尝试用 gog 本身来获取
    try:
        # 尝试用 gog 的内部机制
        result = subprocess.run(
            ["gog", "sheets", "get", SHEET_ID, "A1", "--account", ACCOUNT, "--json"],
            capture_output=True,
            text=True
        )
        # 如果成功，说明 token 有效
        if result.returncode == 0:
            print("✅ gog 认证有效")
            return True
    except Exception as e:
        print(f"❌ 无法验证 gog 认证: {e}")
        return False
    return False

# 使用 gog 的简化方法：直接在第一个 sheet 操作，稍后手动创建新分页
def create_sheet_simple():
    print("⚠️ gog CLI 无法直接创建新分页")
    print("📋 需要手动步骤：")
    print("   1. 打开 Google Sheets:")
    print(f"      https://docs.google.com/spreadsheets/d/{SHEET_ID}")
    print("   2. 点击左下角 '+' 号建立新分页")
    print("   3. 将新分页命名为：履歷池v2")
    print("   4. 完成后回來告知")
    return False

if __name__ == "__main__":
    if not get_access_token():
        create_sheet_simple()
        sys.exit(1)
    
    # 如果能用 API，继续创建
    create_sheet_simple()
