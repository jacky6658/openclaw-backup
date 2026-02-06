# skills-import

來源：Jacky 下載的 3 個技能 zip 解壓後集中放這裡。

## 目錄
- `tunneling-1.0.0/` — tinyfi.sh SSH tunnel（快速把本機服務暴露成 https URL）
- `clawiskill-0.1.0/` — Clawiskill 市集技能（需要 OAuth device flow + API key）
- `desktop-control-1.0.0/` — Desktop Control（Python + pyautogui/opencv，滑鼠鍵盤螢幕自動化）

## 快速筆記（我已讀過 SKILL.md）

### tunneling
- 指令：`ssh -o StrictHostKeyChecking=accept-new -R 80:localhost:<PORT> tinyfi.sh`
- 可加 keepalive：`-o ServerAliveInterval=60`
- 可自訂 subdomain：`-R myname:80:localhost:<PORT>`

### clawiskill
- 需要版本檢查（本機 skill.json vs 遠端 skill.json）
- 需要 OAuth device flow：/api/auth/init → human 授權 → /api/auth/token 取得 api_key
- api_key 需保存到 `~/.config/clawiskill/api_key`（權限 600）
- 可做：search / download / feedback / comment / submit( beta )

### desktop-control
- 依賴（Python）：`pyautogui pillow opencv-python pygetwindow`
- 能做：mouse/keyboard/screenshot/find_on_screen/window/clipboard
- 有安全機制：failsafe（滑鼠移到角落中止）、approval mode
