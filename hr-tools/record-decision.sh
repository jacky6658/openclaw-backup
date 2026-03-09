#!/bin/bash
# 記錄候選人決策（Telegram 互動用）
# 用法：./record-decision.sh <候選人指紋> <職缺ID> <決策>

FINGERPRINT="$1"
JD_ID="$2"
DECISION="$3"  # contacted | skipped | pending

if [ -z "$FINGERPRINT" ] || [ -z "$JD_ID" ] || [ -z "$DECISION" ]; then
  echo "用法：$0 <候選人指紋> <職缺ID> <決策>"
  echo "決策：contacted | skipped | pending"
  exit 1
fi

# 從配對結果中找候選人資料
RESULTS_FILE="/Users/user/clawd/hr-tools/data/sourcing_results_${JD_ID}_$(date +%Y%m%d).json"

if [ ! -f "$RESULTS_FILE" ]; then
  # 嘗試找最近的結果檔
  RESULTS_FILE=$(ls -t /Users/user/clawd/hr-tools/data/sourcing_results_${JD_ID}_*.json 2>/dev/null | head -1)
fi

if [ ! -f "$RESULTS_FILE" ]; then
  echo "❌ 找不到職缺 $JD_ID 的配對結果"
  exit 1
fi

# 提取候選人資料
CANDIDATE=$(cat "$RESULTS_FILE" | jq ".[] | select(.candidate_id == \"$FINGERPRINT\" or .candidate_name == \"$FINGERPRINT\")" | head -1)

if [ -z "$CANDIDATE" ]; then
  echo "❌ 找不到候選人 $FINGERPRINT"
  exit 1
fi

# 提取資訊
NAME=$(echo "$CANDIDATE" | jq -r '.candidate_name')
SCORE=$(echo "$CANDIDATE" | jq -r '.total_score')

# 建立 features
FEATURES=$(cat <<EOF
{
  "skill_match_ratio": $(echo "$CANDIDATE" | jq -r '.details.skill.required_ratio'),
  "github_active": $(echo "$CANDIDATE" | jq -r '.details.bonus.github_active // false'),
  "company_tier": $(echo "$CANDIDATE" | jq -r '.details.bonus.company_tier // "C"'),
  "red_flags": $(echo "$CANDIDATE" | jq -r '.details.red_flags')
}
EOF
)

# 呼叫 Python 記錄
python3 -c "
import sys
sys.path.append('/Users/user/clawd/hr-tools')
from learning_engine import LearningEngine
import json

engine = LearningEngine()

candidate = {
    'name': '$NAME',
    'fingerprint': '$FINGERPRINT'
}

features = json.loads('''$FEATURES''')

engine.record_decision(
    candidate,
    '$JD_ID',
    '$DECISION',
    $SCORE,
    features
)

print('✅ 記錄完成')
print(f'  候選人：$NAME')
print(f'  決策：$DECISION')
print(f'  分數：$SCORE')
"

# 更新 dedup-engine 的歷史
python3 -c "
import sys
sys.path.append('/Users/user/clawd/hr-tools')
from dedup_engine import DedupEngine

engine = DedupEngine()
engine.update_status('$FINGERPRINT', '$JD_ID', '$DECISION')

print('✅ 已更新推薦歷史')
"
