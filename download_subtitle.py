# -*- coding: utf-8 -*-
import yt_dlp
import json
from pathlib import Path
import sys

def download_subtitle(video_url, output_dir):
    """下載指定影片的字幕"""
    # 建立輸出目錄
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # 設定 yt-dlp 選項
    ydl_opts = {
        'skip_download': True,  # 不下載影片
        'writesubtitles': True,  # 下載字幕
        'writeautomaticsub': True,  # 下載自動生成的字幕
        'subtitleslangs': ['zh-Hant', 'zh-TW', 'zh-HK', 'en'],  # 指定字幕語言
        'outtmpl': str(output_dir / '%(title)s.%(ext)s'),  # 輸出檔案名稱格式
        'quiet': False,  # 顯示下載進度
        'no_warnings': False  # 顯示警告訊息
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 獲取影片資訊
            info = ydl.extract_info(video_url, download=False)
            print(f"\n影片標題: {info.get('title')}")
            
            # 檢查是否有字幕
            if 'subtitles' in info or 'automatic_captions' in info:
                print("\n可用的字幕:")
                if 'subtitles' in info:
                    print("手動字幕:", list(info['subtitles'].keys()))
                if 'automatic_captions' in info:
                    print("自動字幕:", list(info['automatic_captions'].keys()))
                
                # 下載字幕
                print("\n開始下載字幕...")
                ydl.download([video_url])
                print("字幕下載完成！")
                
                return True
            else:
                print("此影片沒有任何字幕！")
                return False
            
    except Exception as e:
        print(f"下載字幕時發生錯誤: {str(e)}")
        return False

def main():
    # 設置輸出編碼為 UTF-8
    sys.stdout.reconfigure(encoding='utf-8')
    
    # 讀取最新的影片列表
    output_dir = Path("output")
    json_files = list(output_dir.glob("videos_*.json"))
    
    if not json_files:
        print("找不到影片列表檔案！請先執行 get_channel_videos.py")
        return
    
    # 使用最新的檔案
    latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        videos = json.load(f)
    
    if not videos:
        print("影片列表是空的！")
        return
    
    # 顯示並測試第四個影片（已發布的影片）
    video = videos[3]
    print(f"測試下載影片字幕：")
    print(f"標題: {video['title']}")
    print(f"發布時間: {video['published_at']}")
    print(f"影片網址: {video['url']}\n")
    
    # 建立字幕輸出目錄
    subtitle_dir = output_dir / "subtitles"
    download_subtitle(video['url'], subtitle_dir)

if __name__ == "__main__":
    main()
