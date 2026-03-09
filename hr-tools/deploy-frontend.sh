#!/bin/bash
# 前端一鍵 build + commit + push 腳本
set -e
cd /Users/user/clawd/projects/step1ne-headhunter-system

echo "🔨 Building..."
npm run build

echo "📦 Adding dist files..."
git add -f dist/

MSG="${1:-feat: update frontend}"
git add pages/ components/ constants.ts src/ 2>/dev/null || true
git commit -m "$MSG" || echo "nothing to commit"

echo "🚀 Pushing..."
git push

echo "✅ Done! https://step1ne.zeabur.app"
