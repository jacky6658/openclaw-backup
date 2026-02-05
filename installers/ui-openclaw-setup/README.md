# OpenClaw Setup (Tauri) — v1

Goal: a **standalone UI app** for non-technical users to enable OpenClaw.

## v1 Scope (Milestone 2-A)
- Detect OpenClaw installation (`openclaw --version`)
- Collect inputs:
  - Telegram Bot Token
  - OpenAI API Key (single provider for v1)
- Preview config changes (diff/patch)
- Apply config changes safely:
  - Backup `~/.openclaw/openclaw.json` to timestamped `.bak`
  - Write config values
- Test buttons:
  - `openclaw status` (basic)
- Optional: Start gateway **only after explicit confirmation**

## Safety rules
- No arbitrary shell execution from UI.
- Only whitelisted actions implemented in Rust commands.
- Never auto-start gateway during install.

## Dev
```bash
source ~/.cargo/env
npm install
npm run tauri dev
```
