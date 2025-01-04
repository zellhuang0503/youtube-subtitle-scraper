# YouTube Subtitle Scraper

這個專案用於批量下載 YouTube 頻道影片的字幕，並將其轉換為 Markdown 格式。

## 功能特點

- 批量下載 YouTube 頻道的影片字幕
- 支援多線程並行下載
- 自動轉換字幕為 Markdown 格式
- 包含影片資訊（標題、URL、發布時間）
- 錯誤處理和重試機制
- 下載進度顯示
- 詳細的下載結果記錄

## 安裝需求

1. Python 3.6 或更高版本
2. 安裝所需套件：
```bash
pip install -r requirements.txt
```

## 使用方法

1. 設定 YouTube API 金鑰：
   - 在 Google Cloud Console 創建專案並啟用 YouTube Data API
   - 創建 API 金鑰
   - 將金鑰保存在 `.env` 文件中：
     ```
     YOUTUBE_API_KEY=你的API金鑰
     ```

2. 獲取頻道影片列表：
```bash
python get_channel_videos.py
```

3. 下載字幕：
```bash
python batch_download_subtitles.py
```

## 輸出格式

下載的字幕將保存為 Markdown 格式，包含：
- 影片標題
- 影片 URL
- 發布時間
- 字幕內容（包含時間戳）

## 注意事項

- 部分影片可能因為以下原因無法下載字幕：
  - 影片尚未發布（預告片）
  - 需要年齡驗證
  - 沒有字幕
- 下載結果會保存在 JSON 文件中，方便查看成功和失敗的記錄
