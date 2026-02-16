# LivePortrait 本機安裝指南

## 📋 系統需求

### 硬體
- **GPU**: NVIDIA RTX 3060+ （建議 RTX 4090）
- **顯存**: 至少 6GB VRAM
- **硬碟**: 10GB 空間（模型 + 依賴）

### 軟體
- Python 3.9
- CUDA 11.8+ （NVIDIA GPU）
- Conda 或 venv

---

## 🚀 安裝步驟

### 1. Clone 專案
```bash
cd ~/clawd/projects
git clone https://github.com/KwaiVGI/LivePortrait.git
cd LivePortrait
```

### 2. 建立虛擬環境
```bash
# 使用 Conda（推薦）
conda create -n LivePortrait python=3.9
conda activate LivePortrait

# 或使用 venv
python3.9 -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows
```

### 3. 安裝依賴
```bash
# 安裝 PyTorch（根據你的 CUDA 版本）
# CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 安裝其他依賴
pip install -r requirements.txt
```

### 4. 下載模型（自動）
```bash
# 第一次執行會自動下載模型（約 2GB）
python inference.py --help
```

---

## 🎬 快速測試

### 使用內建範例
```bash
python inference.py
```
輸出會在 `animations/` 資料夾

### 使用自己的照片
```bash
python inference.py \
  --source_image /path/to/your/photo.jpg \
  --driving_video assets/examples/driving/demo.mp4 \
  --output_dir ./my_output
```

---

## 🦞 YuQi 數字人製作流程

### Step 1: 準備 YuQi 照片
- **格式**: JPG/PNG
- **尺寸**: 512×512 以上（會自動裁切）
- **要求**: 正面、清晰、光線均勻
- **建議**: 用 AI 生成（Midjourney / DALL-E）

範例 prompt（如果用 AI 生成）:
```
Portrait of a professional young Asian woman, friendly smile, 
business casual attire, professional headshot, natural lighting,
high quality, centered composition
```

### Step 2: 生成語音
```bash
# 使用 ElevenLabs（我們已有 sag 工具）
sag "你好，我是 YuQi，你的 AI 助理。我可以幫你自動化招募流程、管理候選人、發送開發信，讓你專注在最重要的決策上。" \
  --output ~/clawd/projects/LivePortrait/assets/yuqi-voice.mp3
```

### Step 3: 準備驅動影片
LivePortrait 需要一個「驅動影片」（別人的動作範本）

**選項 A: 使用內建範例**
```bash
# 直接用官方範例（簡單）
assets/examples/driving/demo.mp4
```

**選項 B: 錄製自己的影片**
- 對著鏡頭講話（10-30 秒）
- 表情自然、頭部稍微擺動
- 不用出聲（只需要動作）

**選項 C: 從語音生成動作**（需要額外腳本）
- 使用 Wav2Lip 或 SadTalker
- 從音訊推算臉部動作

### Step 4: 生成 YuQi 數字人影片
```bash
python inference.py \
  --source_image assets/yuqi-photo.jpg \
  --driving_video assets/examples/driving/demo.mp4 \
  --output_dir ./yuqi_output \
  --paste_back \
  --flag_relative
```

參數說明:
- `--source_image`: YuQi 的照片
- `--driving_video`: 動作範本影片
- `--paste_back`: 保留背景（不只臉部）
- `--flag_relative`: 保持相對動作（更自然）

### Step 5: 合成語音
```bash
# 使用 FFmpeg 合成最終影片
ffmpeg -i yuqi_output/result.mp4 -i assets/yuqi-voice.mp3 \
  -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 \
  yuqi-final.mp4
```

---

## 🔧 進階選項

### 批量生成（多個影片）
```bash
python inference.py \
  --source_image yuqi.jpg \
  --driving_video_list videos/*.mp4 \
  --output_dir ./batch_output
```

### 調整品質
```bash
python inference.py \
  --source_image yuqi.jpg \
  --driving_video demo.mp4 \
  --flag_do_crop \           # 自動裁切臉部
  --flag_pasteback \          # 保留背景
  --output_size 512           # 輸出解析度
```

### GPU 記憶體優化
```bash
# 如果顯存不足（<8GB）
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128
python inference.py --source_image yuqi.jpg --driving_video demo.mp4
```

---

## 🎨 完整自動化腳本

```bash
#!/bin/bash
# generate-yuqi-video.sh

PHOTO="assets/yuqi-photo.jpg"
VOICE_TEXT="你好，我是 YuQi，你的 AI 助理"
OUTPUT="yuqi-video-$(date +%Y%m%d-%H%M%S).mp4"

# 1. 生成語音
echo "📢 生成語音..."
sag "$VOICE_TEXT" --output /tmp/yuqi-voice.mp3

# 2. 生成數字人動畫
echo "🎬 生成數字人動畫..."
python inference.py \
  --source_image $PHOTO \
  --driving_video assets/examples/driving/demo.mp4 \
  --output_dir /tmp/yuqi_anim \
  --paste_back

# 3. 合成語音
echo "🔊 合成語音..."
ffmpeg -y -i /tmp/yuqi_anim/result.mp4 -i /tmp/yuqi-voice.mp3 \
  -c:v copy -c:a aac -shortest \
  $OUTPUT

echo "✅ 完成！輸出檔案: $OUTPUT"
```

使用方式:
```bash
chmod +x generate-yuqi-video.sh
./generate-yuqi-video.sh
```

---

## 🐛 常見問題

### 1. CUDA out of memory
**解決方案**:
```bash
# 降低解析度
python inference.py --output_size 256

# 或使用 CPU（會很慢）
export CUDA_VISIBLE_DEVICES=""
```

### 2. 臉部偵測失敗
**原因**: 照片角度不正、解析度太低、光線太暗
**解決方案**:
- 使用正面照片
- 提高解析度（至少 512×512）
- 使用 `--flag_do_crop` 自動裁切

### 3. 動作不自然
**解決方案**:
- 使用 `--flag_relative` 參數
- 換一個品質更好的驅動影片
- 調整 `--flag_stitching` 參數

### 4. Mac 沒有 NVIDIA GPU
**選項 A: CPU 模式**（慢 10-20 倍）
```bash
export CUDA_VISIBLE_DEVICES=""
python inference.py --source_image yuqi.jpg --driving_video demo.mp4
```

**選項 B: 使用 Google Colab**
- 免費 GPU
- Colab 連結: https://colab.research.google.com/
- 上傳照片 + 執行腳本

---

## 📚 延伸閱讀

- **官方文檔**: https://github.com/KwaiVGI/LivePortrait
- **論文**: https://arxiv.org/abs/2407.03168
- **Demo 網站**: https://liveportrait.github.io/

---

## 🎯 下一步

1. **建立 YuQi 形象**
   - 決定真人照片 or AI 生成
   - 準備多種情境（正式、輕鬆、簡報）

2. **整合進 OpenClaw**
   - 建立 skill: `yuqi-avatar`
   - 輸入文字 → 自動生成影片
   - 發送到 Telegram

3. **應用場景**
   - 每日報告（影片版本）
   - 客戶展示（「這是我的 AI 助理」）
   - 教學影片（OpenClaw 操作教學）

---

**需要協助？**
- GitHub Issues: https://github.com/KwaiVGI/LivePortrait/issues
- 或找 YuQi（我）幫你 debug 😄
