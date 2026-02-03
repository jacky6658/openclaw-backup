# macOS：中文 MD → PDF 安裝與使用（穩定版）

> 目標：能穩定把中文 Markdown 轉成 PDF（避免亂碼）
> 原則：用 XeLaTeX + 指定中文字體

---

## 1) 安裝必要工具

```bash
# 安裝 pandoc 與 LaTeX
brew install pandoc
brew install --cask basictex

# 補齊常用 LaTeX 套件（含中文字型與版面）
sudo tlmgr install collection-fontsrecommended fancyhdr titlesec enumitem xcolor booktabs longtable geometry hyperref graphicx setspace array multirow

# 若你有需要中文排版的額外支援（可選）
sudo tlmgr install ctex
```

> 如果 `tlmgr` 指令找不到：重新開啟終端機或執行 `sudo /Library/TeX/texbin/tlmgr update --self`。

---

## 2) 確認字體可用（擇一）

macOS 常見可用字體：
- **PingFang TC**（內建）
- **Noto Sans CJK TC**（需自行安裝）
- **Microsoft JhengHei**（部分系統有）

---

## 3) 轉檔指令（推薦）

```bash
pandoc 檔案.md -o 檔案.pdf \
  --pdf-engine=xelatex \
  -V mainfont="PingFang TC"
```

若 `PingFang TC` 不可用，改用：

```bash
# Noto Sans CJK TC
pandoc 檔案.md -o 檔案.pdf \
  --pdf-engine=xelatex \
  -V mainfont="Noto Sans CJK TC"

# Microsoft JhengHei
pandoc 檔案.md -o 檔案.pdf \
  --pdf-engine=xelatex \
  -V mainfont="Microsoft JhengHei"
```

---

## 4) 常見問題

### Q1：出現亂碼或方框？
通常是字體不可用或沒有指定字體。
→ 改用可用的中文字體名稱。

### Q2：`xelatex` 找不到？
代表 LaTeX 沒安裝完整或 PATH 未載入。
→ 重新開終端機，或執行：
```bash
sudo /Library/TeX/texbin/tlmgr update --self
```

### Q3：轉檔很慢？
第一次跑 XeLaTeX 會慢一點，正常。

---

## 5) 進階：用 LuaLaTeX（可選）

```bash
pandoc 檔案.md -o 檔案.pdf \
  --pdf-engine=lualatex \
  -V mainfont="PingFang TC"
```

---

## ✅ 完成標準

你能成功執行以下指令，且 PDF 中文顯示正常，即完成：

```bash
pandoc 檔案.md -o 檔案.pdf --pdf-engine=xelatex -V mainfont="PingFang TC"
```
