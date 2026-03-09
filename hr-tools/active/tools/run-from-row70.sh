#!/bin/bash
# 從 Row 70 開始執行爬蟲

echo "🚀 從 Row 70 開始處理 247 家公司..."
echo "⏱️  預計時間：約 50 分鐘"
echo ""

cd /Users/user/clawd/hr-tools/scraper-stable

# 修改 main.py 使用新清單
cat > run.py << 'PYEOF'
import json
import sys
from pathlib import Path

# 動態修改導入
exec(open('main.py').read().replace(
    "with open('/tmp/missing-contacts.json'",
    "with open('/tmp/companies-from-70.json'"
))
PYEOF

python3 run.py ${1:-247}
