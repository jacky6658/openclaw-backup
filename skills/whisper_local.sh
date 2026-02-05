#!/bin/bash
set -e

# 用法: whisper_local.sh <audio_file>

BIN="/usr/local/bin/whisper-cli"
MODEL="/Users/user/whisper-models/ggml-tiny.bin"
FFMPEG="/usr/local/bin/ffmpeg"

IN="$1"

if [ -z "$IN" ]; then
  echo "Usage: $0 <audio_file>"
  exit 1
fi

if [ ! -f "$IN" ]; then
  echo "Audio file not found: $IN"
  exit 1
fi

# 建立暫存 wav 檔（放在 /tmp）
BASENAME="$(basename "$IN")"
TMP_WAV="/tmp/${BASENAME%.*}.wav"

# 若不是 wav，就轉成 16k/mono/pcm wav
EXT="${IN##*.}"
if [ "$EXT" != "wav" ] && [ "$EXT" != "WAV" ]; then
  "$FFMPEG" -y -i "$IN" -ar 16000 -ac 1 -c:a pcm_s16le "$TMP_WAV" >/dev/null 2>&1
else
  TMP_WAV="$IN"
fi

# 跑 whisper
"$BIN" -m "$MODEL" -f "$TMP_WAV" -l zh -otxt

# 清理暫存檔（如果是轉出來的）
if [ "$TMP_WAV" != "$IN" ]; then
  rm -f "$TMP_WAV"
fi
