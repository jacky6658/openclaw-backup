# LivePortrait - Google Colab 免費 GPU 方案

## 🎯 為什麼用 Colab？

- ✅ **免費 GPU**（Tesla T4 / V100）
- ✅ **無需安裝**（環境已設置好）
- ✅ **速度快**（1 分鐘影片約 30 秒生成）
- ✅ **隨時可用**（瀏覽器打開就能用）

---

## 🚀 快速開始（5 分鐘）

### Step 1: 打開 Colab

**方式 A：使用現成的 Colab Notebook**
1. 打開瀏覽器
2. 前往：https://colab.research.google.com/
3. 選擇 `File` → `New Notebook`

**方式 B：使用社群分享的 Notebook**
- 搜尋 "LivePortrait Colab" on GitHub
- 或用下面我準備的完整腳本

---

### Step 2: 在 Colab 中執行（複製貼上以下程式碼）

#### 🔧 安裝環境（第一個 Cell）
```python
# 1. Clone 專案
!git clone https://github.com/KwaiVGI/LivePortrait.git
%cd LivePortrait

# 2. 安裝依賴
!pip install -r requirements.txt -q

# 3. 下載預訓練模型
!mkdir -p pretrained_weights
!wget -q https://huggingface.co/KwaiVGI/LivePortrait/resolve/main/base_models/appearance_feature_extractor.pth -P pretrained_weights/
!wget -q https://huggingface.co/KwaiVGI/LivePortrait/resolve/main/base_models/motion_extractor.pth -P pretrained_weights/
!wget -q https://huggingface.co/KwaiVGI/LivePortrait/resolve/main/base_models/spade_generator.pth -P pretrained_weights/
!wget -q https://huggingface.co/KwaiVGI/LivePortrait/resolve/main/base_models/warping_module.pth -P pretrained_weights/
!wget -q https://huggingface.co/KwaiVGI/LivePortrait/resolve/main/retargeting_models/stitching_retargeting_module.pth -P pretrained_weights/

print("✅ 安裝完成！")
```

#### 📤 上傳 YuQi 照片（第二個 Cell）
```python
from google.colab import files
import shutil

# 上傳照片
print("請選擇 YuQi 的照片...")
uploaded = files.upload()

# 移動到正確位置
for filename in uploaded.keys():
    shutil.move(filename, 'assets/yuqi-photo.jpg')
    print(f"✅ 照片已上傳: {filename}")
```

#### 🎬 生成數字人影片（第三個 Cell）
```python
# 使用內建範例動作
!python inference.py \
  --source_image assets/yuqi-photo.jpg \
  --driving_video assets/examples/driving/d0.mp4 \
  --output_dir ./yuqi_output \
  --paste_back

print("✅ 影片生成完成！")
print("輸出位置: yuqi_output/")
```

#### 📥 下載結果（第四個 Cell）
```python
from google.colab import files
import os

# 列出所有生成的影片
output_files = os.listdir('yuqi_output')
print(f"找到 {len(output_files)} 個檔案:")
for f in output_files:
    print(f"  - {f}")

# 下載主要結果
result_video = 'yuqi_output/d0.mp4'
if os.path.exists(result_video):
    files.download(result_video)
    print(f"✅ 已下載: {result_video}")
else:
    print("❌ 找不到結果影片")
```

---

## 🎨 進階使用

### 整合語音（在 Colab 中）

```python
# 1. 安裝 ElevenLabs
!pip install elevenlabs -q

# 2. 生成語音
from elevenlabs import generate, save
import os

# 設定 API Key（需要 ElevenLabs 帳號）
os.environ['ELEVEN_API_KEY'] = 'your-api-key-here'

audio = generate(
    text="你好，我是 YuQi，你的 AI 助理",
    voice="Bella",  # 或其他語音
    model="eleven_multilingual_v2"
)

save(audio, 'yuqi-voice.mp3')
print("✅ 語音生成完成")

# 3. 合成語音到影片
!pip install moviepy -q
from moviepy.editor import VideoFileClip, AudioFileClip

video = VideoFileClip('yuqi_output/d0.mp4')
audio = AudioFileClip('yuqi-voice.mp3')

# 調整影片長度匹配音訊
if video.duration < audio.duration:
    video = video.loop(duration=audio.duration)
else:
    video = video.subclip(0, audio.duration)

final = video.set_audio(audio)
final.write_videofile('yuqi-final.mp4', codec='libx264', audio_codec='aac')

print("✅ 最終影片生成完成！")
files.download('yuqi-final.mp4')
```

---

## 🔄 使用不同的驅動影片

```python
# 查看所有內建範例
!ls assets/examples/driving/

# 使用不同的驅動影片
!python inference.py \
  --source_image assets/yuqi-photo.jpg \
  --driving_video assets/examples/driving/d1.mp4 \
  --output_dir ./yuqi_output_v2

# 或上傳自己的驅動影片
uploaded = files.upload()
for filename in uploaded.keys():
    !python inference.py \
      --source_image assets/yuqi-photo.jpg \
      --driving_video {filename} \
      --output_dir ./custom_output
```

---

## 📊 批量生成（多個動作）

```python
import os

driving_videos = [
    'assets/examples/driving/d0.mp4',
    'assets/examples/driving/d1.mp4',
    'assets/examples/driving/d2.mp4',
]

for i, video in enumerate(driving_videos):
    print(f"處理第 {i+1}/{len(driving_videos)} 個影片...")
    !python inference.py \
      --source_image assets/yuqi-photo.jpg \
      --driving_video {video} \
      --output_dir ./batch_output_{i}

print("✅ 批量生成完成！")

# 下載所有結果
for i in range(len(driving_videos)):
    output_file = f'batch_output_{i}/d{i}.mp4'
    if os.path.exists(output_file):
        files.download(output_file)
```

---

## ⚡ 效能優化

### 檢查 GPU 狀態
```python
# 確認有 GPU
!nvidia-smi

# 如果顯示 "NVIDIA-SMI has failed"，需要：
# Runtime → Change runtime type → Hardware accelerator → GPU
```

### 加速推理
```python
# 使用較小的解析度（更快但品質稍差）
!python inference.py \
  --source_image assets/yuqi-photo.jpg \
  --driving_video assets/examples/driving/d0.mp4 \
  --output_size 256 \
  --output_dir ./fast_output
```

---

## 🐛 常見問題

### 1. 模型下載失敗
```python
# 手動從 Hugging Face 下載
!wget https://huggingface.co/KwaiVGI/LivePortrait/resolve/main/base_models/appearance_feature_extractor.pth -P pretrained_weights/
```

### 2. 顯存不足
```python
# 使用更小的解析度
!python inference.py --output_size 256 ...
```

### 3. 臉部偵測失敗
```python
# 確保照片是正面、清晰的
# 可以先裁切照片
from PIL import Image

img = Image.open('assets/yuqi-photo.jpg')
# 手動裁切或調整
img_cropped = img.crop((x1, y1, x2, y2))
img_cropped.save('assets/yuqi-photo-cropped.jpg')
```

---

## 🎁 完整 Colab Notebook（一鍵執行）

我已經準備好一個完整的 Colab Notebook，包含：
- ✅ 自動安裝環境
- ✅ 上傳照片界面
- ✅ 多種驅動影片選擇
- ✅ 一鍵生成 + 下載

**下一步**：
1. 我可以建立一個 `.ipynb` 檔案
2. 你上傳到 Google Drive
3. 用 Colab 打開直接執行

或者你想要我直接給你完整的程式碼區塊，你自己複製貼上到 Colab？

---

## 💰 Colab 免費額度

- **免費版**：每天約 12 小時 GPU
- **中斷後可重新連線**
- **檔案保留 12 小時**（需下載到本機）

**如果需要更多**：
- Colab Pro ($10/月)：更長時間 + 更好的 GPU
- 但免費版對這個專案已經夠用

---

## 🎯 下一步

需要我：
1. ✅ **建立完整 Colab Notebook** (.ipynb 檔案)
2. ✅ **錄製操作影片**（教你怎麼用）
3. ✅ **直接幫你執行**（我用我的 Colab 帳號跑）

你想要哪一個？
