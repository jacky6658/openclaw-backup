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

## 安裝（給新手 / 最終交付）

### 下載
- DMG：`openclaw-setup_0.1.0_x64.dmg`

### 安裝步驟
1. 雙擊打開 `openclaw-setup_0.1.0_x64.dmg`
2. 把 **OpenClaw Setup.app** 拖到 **Applications（應用程式）**
3. 到「應用程式」資料夾找到 **OpenClaw Setup** 開啟

### 第一次開啟（macOS 可能阻擋）
因為目前未做 Apple Developer ID 簽名，macOS 可能會跳出「無法開啟／無法驗證開發者」。

**建議新手操作（最穩）：**
- 到「應用程式」資料夾 → 對 **OpenClaw Setup.app** 按右鍵 → 選 **開啟 (Open)** → 再按一次 **開啟**

**或**
- 系統設定 → 隱私權與安全性 → 在底部會看到「已阻擋 OpenClaw Setup」→ 點 **仍要打開**

> 如果你下載後被標記為「來自網路的 App」導致一直被擋，可以用下面指令移除隔離標記（進階用法，**也適用遠端測試**）：
> ```bash
> xattr -dr com.apple.quarantine "/Applications/OpenClaw Setup.app"
> ```
> 
> 補充：純 SSH/headless 的情境下，即使 `open -a` 被呼叫成功，也可能因為遠端沒有登入的 GUI session 而看不到視窗；此時可以改用直接執行 binary 來做 smoke test。

### 使用前置（你可能需要先有 OpenClaw）
- 這個 App 會呼叫 `openclaw` CLI（例如 `openclaw --version` / `openclaw status`）
- 如果你還沒安裝 OpenClaw，請先完成 OpenClaw 安裝再回來用本 App

## Troubleshooting
- **按下 Check 看到「openclaw not found」**：代表你系統找不到 `openclaw` 指令；請先安裝或把 OpenClaw 加到 PATH。
- **按下 Start gateway 沒反應**：需要你本機允許啟動 LaunchAgent/背景服務（視 OpenClaw 安裝方式而定）。

## Dev
```bash
# 開發環境需要 Rust toolchain
source ~/.cargo/env  # 或確保 PATH 內含 ~/.cargo/bin
npm install
npm run tauri dev
```

## Build / Bundle（產出 .app）
```bash
source ~/.cargo/env
npm run tauri -- build --bundles app

# 產物：
# src-tauri/target/release/bundle/macos/OpenClaw Setup.app
```

## Build / Bundle（產出 .dmg，無需 create-dmg/osascript）
> 我們避免使用 Tauri 內建 DMG 腳本（有機會卡住/被系統 kill）。

```bash
APP_PATH="src-tauri/target/release/bundle/macos/OpenClaw Setup.app"
OUT_DIR="dist-macos"
VOLNAME="OpenClaw Setup"
DMG_NAME="openclaw-setup_0.1.0_x64.dmg"

rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"
cp -R "$APP_PATH" "$OUT_DIR/"
ln -s /Applications "$OUT_DIR/Applications"

hdiutil create -volname "$VOLNAME" -srcfolder "$OUT_DIR" -ov -format UDZO "$DMG_NAME"
```
