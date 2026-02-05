#!/usr/bin/env bash
set -euo pipefail

PROMPT_FILE="${1:-/Users/user/clawd/skills/auto_cursor/prompt.txt}"

if [[ ! -f "$PROMPT_FILE" ]]; then
  echo "Prompt file not found: $PROMPT_FILE" >&2
  exit 1
fi

PROMPT="$(cat "$PROMPT_FILE")"

# 1) Open Cursor
open -a "Cursor"
sleep 1

# 2) Put prompt into clipboard (avoid quoting issues)
printf "%s" "$PROMPT" | pbcopy

# 3) Drive UI: bring to front, focus chat input, paste, send
osascript <<'APPLESCRIPT'
tell application "Cursor" to activate
delay 0.8

tell application "System Events"
  -- Make sure Cursor is frontmost
  set frontmost of process "Cursor" to true
  delay 0.4

  -- Try to focus chat input: press Cmd+L (often focuses command bar) then Cmd+Shift+L or other
  -- We'll use a robust approach: click near bottom-right area of the front window (chat input zone)
  try
    tell process "Cursor"
      set theWin to front window
      set {x1, y1} to position of theWin
      set {w1, h1} to size of theWin

      -- Click in the chat input area (approx bottom center)
      click at {x1 + (w1 * 0.83), y1 + (h1 * 0.93)}
      delay 0.2
    end tell
  end try

  -- Paste
  keystroke "v" using {command down}
  delay 0.2

  -- Send (Enter)
  key code 36
end tell
APPLESCRIPT

echo "Done. Cursor opened, prompt pasted and sent."
