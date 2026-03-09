#!/bin/bash
# 等 Zeabur 恢復後執行這個腳本，自動批量上傳 .NET 候選人
# 用法：bash upload-dotnet-when-ready.sh

API="https://backendstep1ne.zeabur.app/api"
JSON_FILE="/Users/user/clawd/hr-tools/data/dotnet-candidates-20260301.json"

echo "🔍 先確認 API 是否正常..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$API/health")

if [ "$STATUS" != "200" ]; then
  echo "❌ API 仍不可用（HTTP $STATUS），請稍後再試"
  exit 1
fi

echo "✅ API 正常！開始上傳 .NET 候選人..."

# 提取 candidates 陣列並上傳
python3 - <<'PYEOF'
import json, requests, time, sys

with open("/Users/user/clawd/hr-tools/data/dotnet-candidates-20260301.json") as f:
    data = json.load(f)

candidates = data.get("candidates", [])
print(f"📋 共 {len(candidates)} 位候選人準備上傳")

success = 0
failed = 0

for idx, c in enumerate(candidates, 1):
    try:
        r = requests.post(
            "https://backendstep1ne.zeabur.app/api/candidates",
            json=c,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if r.status_code in [200, 201]:
            print(f"  ✅ [{idx:02d}] {c['name']}")
            success += 1
        else:
            print(f"  ❌ [{idx:02d}] {c['name']} - HTTP {r.status_code}")
            failed += 1
        time.sleep(1)
    except Exception as e:
        print(f"  ❌ [{idx:02d}] {c['name']} - {e}")
        failed += 1

print(f"\n════════════════════════════")
print(f"✅ 成功：{success} 位")
print(f"❌ 失敗：{failed} 位")
PYEOF
