# OpenClaw macOS Installer (.pkg)

完全 GUI 的 OpenClaw 安裝包，使用者只需雙擊安裝，無需碰 Terminal。

## 系統需求

- **macOS 12 Monterey 或更新版本**（必需）
- 管理員權限
- 網路連線

⚠️ **macOS 11 Big Sur 或更舊版本不支援**（Homebrew 編譯會失敗）

## 使用方式

1. 雙擊 `openclaw-installer.pkg`
2. 跟著 macOS 安裝程式指示（會要求輸入管理員密碼）
3. 安裝完成後，開啟「OpenClaw Setup.app」繼續設定

## 安裝過程

- 會自動安裝 Homebrew、Node.js、OpenClaw
- 安裝時間：10–30 分鐘（視網路速度而定）
- 安裝日誌：`/tmp/openclaw-install.log`

## 打包方式（開發者用）

```bash
cd /Users/user/clawd/installers/openclaw-pkg

# 1. 建立 component package
pkgbuild --root payload \
  --scripts . \
  --identifier ai.openclaw.installer \
  --version 1.0 \
  --install-location / \
  openclaw-installer-component.pkg

# 2. 建立 product package (最終交付)
productbuild --distribution distribution.xml \
  --resources . \
  --package-path . \
  openclaw-installer.pkg
```

## 檔案說明

- `postinstall` - 安裝後執行的腳本（下載並執行 OpenClaw installer）
- `distribution.xml` - 安裝程式介面定義
- `welcome.html` - 歡迎頁面（含系統需求警告）
- `conclusion.html` - 完成頁面
- `openclaw-installer.pkg` - 最終交付的安裝包（雙擊安裝）

## 注意事項

- 需要管理員權限（會彈密碼視窗）
- 必須有網路連線（需下載 Homebrew/Node）
- 安裝過程不可中斷
- **macOS 11 或更舊版本會安裝失敗**（請先升級系統）
