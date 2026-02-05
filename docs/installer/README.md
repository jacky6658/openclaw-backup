# OpenClaw 一鍵安裝器（商品化）

目標：給「完全不會終端機」的一般使用者。

- Windows：雙擊安裝（MSI/EXE）→ 安裝 Node LTS（若缺）→ 安裝 OpenClaw → 驗證
- macOS：雙擊 PKG → 安裝 Node LTS（若缺）→ 安裝 OpenClaw → 驗證

重要原則（避免 bot 消失/設定被洗掉）：
- **安裝器階段不自動啟動 Gateway**
- **不修改使用者 Telegram/模型 Key**（Wizard 另一步）
- 所有寫入設定必須：先備份 → 顯示 preview → 使用者確認

## 里程碑
- M1：安裝器只負責「安裝 OpenClaw + 驗證」
- M2：安裝後提供「開啟 Dashboard」但不自動啟動 gateway（按下才啟動）
- M3：UI Wizard：填 Telegram token / API key（需要明確確認才寫入/重啟）

## macOS（未簽章/未公證）安裝提醒
如果沒有 Apple Developer 帳號做簽章與 notarization：
- 第一次雙擊 PKG 可能被 Gatekeeper 擋
- 解法：到「系統設定 → 隱私權與安全性」往下滑，會看到『已阻擋某某安裝器』→ 點「仍要打開」
- 或：右鍵點 PKG → 打開（Open）→ 再確認一次

> 正式商品化建議：後續補上簽章 + notarization（否則一般用戶會被擋，體驗不夠一鍵）。
