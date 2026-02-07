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
- 這份技能包內含可用 Python 程式碼（`desktop-control-1.0.0/desktop_control/` package + `demo.py`）
- 依賴（Python）：`pyautogui pillow opencv-python pygetwindow pyperclip`
- macOS 權限：需授權「輔助使用（控制鍵盤滑鼠）」；截圖/找圖可能要「螢幕錄製」
- Homebrew Python 有 PEP 668 限制 → 建議用 venv

快速啟用：
```bash
cd /Users/user/clawd/skills-import/desktop-control-1.0.0
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install pyautogui pillow opencv-python pygetwindow pyperclip
python -c "from desktop_control import DesktopController; dc=DesktopController(); print(dc.get_screen_size())"
python demo.py
```
