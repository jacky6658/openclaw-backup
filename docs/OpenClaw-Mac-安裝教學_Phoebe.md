# OpenClaw macOS 一鍵安裝教學（PPA 版 / Phoebe 流程）

> 目標：在 Mac 上用「一鍵安裝腳本」完成 OpenClaw 安裝，並在 Terminal 驗證：
> - `openclaw` 指令存在
> - Gateway 可查看狀態
>
> 適用：要做線上課程（PPA）使用的標準流程。

---

## 0. 先決條件（務必確認）
- 你的 macOS 使用者具備 **Administrator（管理員）** 權限（因為會用到 `sudo`）。
- 可正常連網（會下載 Homebrew / Node / OpenClaw）。

---

## 1. 一鍵安裝（互動式執行，成功率最高）

### 1.1 打開 Terminal（很重要）
- 用 Finder → 應用程式 → 工具程式 → **Terminal**
- 請不要在「非互動式」環境執行（例如某些 IDE 的非 TTY 視窗），不然會出現 `stdin is not a TTY` 導致無法輸入密碼。

### 1.2 貼上指令（一次貼完整行）
在 Terminal 貼上執行：

```bash
/bin/bash -c "$(curl -fsSL https://openclaw.ai/install.sh)"
```

### 1.3 你接下來會看到什麼？要按什麼？（保姆版照做）
下面每一種畫面都很常見：

**A) 看到「按 Enter 繼續」**
- 畫面類似：`Press RETURN/ENTER to continue`
- 你要做：**按 Enter**

**B) 看到要求 sudo / password**
- 畫面類似：`Checking for 'sudo' access...` 或直接跳出要你輸入密碼
- 你要做：
  1. 輸入你的 **Mac 登入密碼**
  2. 按 Enter
- 注意：輸入密碼時 **畫面不會顯示任何字元**（正常）

**C) 看到 Homebrew 要安裝到哪些路徑**
- 會列出很多 `/usr/local/...` 或 `/opt/homebrew/...`
- 你要做：通常會再問一次要不要繼續 → **按 Enter**

**D) 看到安裝 Xcode Command Line Tools**
- 可能會提示你去 Software Update 更新
- 你要做：先讓安裝繼續跑；若後面真的失敗，再依文件第 6 節更新 CLT。

**E) 看到正在裝 node@22 / openssl / sqlite / cmake / make / patching / pouring**
- 你要做：**不要中斷**，這段可能 10–30 分鐘。

**F) 什麼叫安裝完成？**
- 畫面最後會回到你熟悉的提示符號：
  - zsh：`你的電腦名稱 ~ %`
  - bash：`你的電腦名稱 ~ $`
- 回到提示符號就代表這個步驟跑完了，可以進行第 3 節驗收。

### 這條指令會「一次裝到好」哪些東西？
通常會包含：
- Homebrew
- Xcode Command Line Tools（若缺少/需更新會提示你去 Software Update）
- Node.js（含 npm；常見會安裝 `node@22`）
- OpenClaw 本體

> 你不需要另外安裝 npm。npm 會跟著 Node 一起安裝。

### 常見互動提示（照做即可）
- 看到：`Press RETURN/ENTER to continue` → **按 Enter**
- 看到要求 sudo 密碼 → **輸入你的 Mac 登入密碼**（畫面不會顯示字元是正常的）→ Enter

---

## 2. 安裝過程「很久」是正常的（保姆版判斷有沒有卡住）
第一次安裝可能會花 10–30 分鐘以上。

你會看到的關鍵字（看到它們＝正常在跑）：
- `Installing ...`（正在裝套件）
- `Downloading ...`（正在下載）
- `Pouring ...`（Homebrew 正在安裝瓶裝套件）
- `Patching ...`（在套用修補）
- `make` / `cmake`（在編譯）

### 什麼情況才算真的卡住？
- 同一行畫面 **完全不變超過 20–30 分鐘**
- 或出現紅色 error 並停住不動

如果你懷疑卡住：
1) 先截圖
2) 把 Terminal 最後 20 行文字複製貼出來
3) 再問我（不要自己關掉，除非已經確定停死）

---

## 3. 安裝完成後驗收（看到提示符號 `%` 或 `$` 後執行）

```bash
openclaw --help
openclaw gateway status
node -v
```

預期：
- `openclaw --help` 會顯示指令說明
- `node -v` 會顯示版本（代表 Node/npm 已就緒）
- `openclaw gateway status` 會輸出狀態（stopped/running 都可以，重點是不要 command not found）

---

## 4. nvm 需要裝嗎？
不需要。

- 一鍵腳本通常是用 Homebrew 直接安裝 Node（含 npm）。
- nvm 是「選配」，不影響 OpenClaw 使用。

想確認有沒有 nvm：
```bash
command -v nvm
```

---

## 5. 若卡在 sudo / 權限
先測：
```bash
sudo -v
```
- 若失敗：代表你不是管理員，需要用管理員帳號或請管理員協助授權。

---

## 6. Xcode Command Line Tools 顯示可更新怎麼辦？
若 Terminal 出現：Command Line Tools 有新版
- 直接到：**系統設定 → 軟體更新**
- 優先更新：**Command Line Tools for Xcode**（macOS 本體可先不更新）

> `sudo xcode-select --install` 若顯示已安裝，表示「要更新」請走 Software Update。

---

## 7.（重要）若你用 nvm 安裝 Node：重開 Terminal 後 openclaw/node 可能會不見
現象：
- `zsh: command not found: openclaw`
- `zsh: command not found: node`
- 或補全報錯：`compdef: command not found`

原因：nvm 需要在每次開啟 shell 時自動載入。

### 7.1 一次修好（建立 ~/.zshrc）
在 Terminal 執行：

```bash
cat > ~/.zshrc <<'EOF'
# ---- zsh completion init (fix: compdef not found) ----
autoload -Uz compinit
compinit

# ---- nvm ----
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"

# ---- OpenClaw completions (optional) ----
fpath=("$HOME/.openclaw/completions" $fpath)
EOF
```

立即生效：
```bash
source ~/.zshrc
```

驗收：
```bash
node -v
openclaw --help
openclaw gateway status
```

---

## 8. Gateway 最終驗收（跑起來才算完成）
```bash
openclaw gateway status
```

預期看到：
- `Runtime: running`
- `RPC probe: ok`

如果看到 warning：`Gateway service uses Node from a version manager`
- 這是提醒「nvm 版本可能未來升級會影響 service」，但不影響你現在先跑通。
- 正式上線時再依官方建議搬到 system node 即可。

---

## 9.（加碼）Google OAuth / gog 驗證與授權（終端機指令）

> 用途：讓 OpenClaw 能透過 `gog` 存取 Gmail / Calendar / Drive / Docs / Sheets。

### 9.1 先說「要不要 Google 官方驗證？」
- **自己用 / 少量內部用**：不用送 Google 驗證。
  - 在 Google Cloud Console 的 OAuth consent screen 把狀態設為 **Testing**
  - 並把你自己的 Gmail 加到 **Test users**
- **要公開給大量外部使用者**：才需要送審（會牽涉隱私權政策、網域驗證、scope 審核）。

### 9.2 下載 OAuth 用戶端 JSON
在 Google Cloud Console 建立 OAuth Client（Desktop app）後，按 **下載 JSON**。

> ⚠️ `client_secret` 等同密碼，請勿貼到群組/對話。

### 9.3 安裝 gogcli
```bash
brew install steipete/tap/gogcli
```

### 9.4 放好 credentials.json
```bash
mkdir -p "$HOME/Library/Application Support/gogcli"
mv ~/Downloads/client_secret_*.json \
  "$HOME/Library/Application Support/gogcli/credentials.json"
```

### 9.5 設定 gog 使用憑證
```bash
gog auth credentials "$HOME/Library/Application Support/gogcli/credentials.json"
```

### 9.6 對你的 Google 帳號授權（只開需要的服務）
把 `you@gmail.com` 換成你的帳號：
```bash
gog auth add you@gmail.com --services gmail,calendar,drive,docs,sheets
gog auth list
```

> 授權過程會開瀏覽器，完成後回到 Terminal 即可。
