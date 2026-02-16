#!/bin/bash
# 安全讀取加密的憑證

MACHINE_ID=$(ioreg -rd1 -c IOPlatformExpertDevice | awk '/IOPlatformUUID/ { print $3; }' | tr -d '"')

export THREADS_APP_ID="1127637525886751"
export THREADS_APP_SECRET=$(openssl enc -aes-256-cbc -d -pbkdf2 -salt -in .secret.enc -pass pass:"$MACHINE_ID" 2>/dev/null)

if [ -z "$THREADS_APP_SECRET" ]; then
  echo "❌ 無法解密憑證"
  exit 1
fi

echo "✅ 憑證已載入（加密儲存）"
