# YouTube 字幕批量下載工具

這個專案用於批量下載 YouTube 頻道影片的字幕，並支援將字幕轉換為繁體中文。

## 完整操作步驟說明

### 第一步：環境準備
1. 安裝 Python 3.6 或更高版本
2. 安裝所需套件：
   ```bash
   pip install -r requirements.txt
   ```
   - google-api-python-client：用於存取 YouTube API
   - python-dotenv：用於管理環境變數
   - yt-dlp：用於下載 YouTube 字幕
   - tqdm：用於顯示進度條
   - googletrans：用於翻譯功能

### 第二步：設定 YouTube API
1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 創建新專案或選擇現有專案
3. 在「API 和服務」中啟用 YouTube Data API v3
4. 在「憑證」中創建 API 金鑰
5. 將 API 金鑰保存在專案根目錄的 `.env` 檔案中：
   ```
   YOUTUBE_API_KEY=你的API金鑰
   ```

### 第三步：獲取頻道影片列表
1. 找到目標 YouTube 頻道的頻道 ID
   - 在頻道頁面網址中可以找到，格式如：UC...
2. 執行 `get_channel_videos.py`：
   ```bash
   python get_channel_videos.py
   ```
   - 這個腳本會獲取頻道中所有影片的資訊
   - 資訊會保存在 `output/video_list.json` 中

### 第四步：批量下載字幕
1. 執行 `batch_download_subtitles.py`：
   ```bash
   python batch_download_subtitles.py
   ```
   - 這個腳本會讀取 `video_list.json`
   - 為每個影片下載字幕
   - 字幕會保存在 `output/頻道名稱_subtitles` 目錄下

### 第五步：轉換字幕格式（選擇性）
1. 執行 `convert_subtitle.py`：
   ```bash
   python convert_subtitle.py
   ```
   - 這個腳本會將 JSON 格式的字幕轉換為 TXT 格式
   - 同時將內容翻譯成繁體中文
   - 轉換後的檔案會保存在 `output/頻道名稱_subtitles_txt` 目錄下

### 輸出檔案格式
1. 字幕 JSON 檔案包含：
   - 影片資訊（標題、URL、上傳時間）
   - 字幕內容（時間戳、文字）

2. 轉換後的 TXT 檔案包含：
   - 影片基本資訊
   - 逐行字幕內容
   - 原文及繁體中文翻譯
   - 精確的時間戳

### 注意事項
1. API 使用限制
   - YouTube API 有每日配額限制
   - 建議批次處理時控制請求頻率

2. 字幕可用性
   - 並非所有影片都有字幕
   - 某些影片可能只有自動生成的字幕

3. 翻譯 API 限制
   - 使用 Google Translate API 有請求頻率限制
   - 腳本中已加入延遲機制避免超過限制

4. 檔案備份
   - 建議定期備份下載的字幕檔案
   - 可使用 Git 進行版本控制

### 常見問題排除
1. API 金鑰問題
   - 確認 `.env` 檔案存在且格式正確
   - 確認 API 金鑰有啟用正確的服務

2. 下載失敗
   - 檢查網路連接
   - 確認影片是否可用
   - 查看錯誤日誌了解具體原因

3. 翻譯問題
   - 如遇到翻譯失敗，腳本會保留原文
   - 可以稍後重新執行翻譯程序

### 版本控制
每次完成重要更新後，記得更新 Git 版本：
```bash
git add .
git commit -m "更新說明"
git push
```
