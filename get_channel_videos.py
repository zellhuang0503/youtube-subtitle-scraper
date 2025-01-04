# -*- coding: utf-8 -*-
from dotenv import load_dotenv
import os
from googleapiclient.discovery import build
import re
from datetime import datetime
import json
import csv
from pathlib import Path

def get_channel_id_from_url(url):
    """從頻道URL獲取頻道ID"""
    username_match = re.search(r'@(\w+)', url)
    if not username_match:
        raise ValueError("無法從URL中獲取頻道用戶名")
    
    return username_match.group(1)

def get_channel_id(youtube, username):
    """通過用戶名獲取頻道ID"""
    request = youtube.search().list(
        part="id",
        q=f"@{username}",
        type="channel",
        maxResults=1
    )
    response = request.execute()
    
    if not response.get('items'):
        raise ValueError(f"找不到用戶名為 @{username} 的頻道")
    
    return response['items'][0]['id']['channelId']

def get_channel_videos(youtube, channel_id, max_results=50):
    """獲取頻道最新的影片列表"""
    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        maxResults=max_results,
        order="date",
        type="video"
    )
    response = request.execute()
    
    videos = []
    for item in response['items']:
        video = {
            'id': item['id']['videoId'],
            'title': item['snippet']['title'],
            'published_at': datetime.strptime(
                item['snippet']['publishedAt'], 
                '%Y-%m-%dT%H:%M:%SZ'
            ).strftime('%Y-%m-%d %H:%M:%S'),
            'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
        }
        videos.append(video)
    
    return videos

def save_videos_to_json(videos, filename):
    """將影片列表保存為JSON檔案"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)
    print(f"已將影片列表保存至 {filename}")

def save_videos_to_csv(videos, filename):
    """將影片列表保存為CSV檔案"""
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'title', 'published_at', 'url'])
        writer.writeheader()
        writer.writerows(videos)
    print(f"已將影片列表保存至 {filename}")

def main():
    # 設置輸出編碼為 UTF-8
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    # 建立輸出目錄
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # 載入環境變數
    load_dotenv()
    api_key = os.getenv('YOUTUBE_API_KEY')
    
    # 建立 YouTube API 服務
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    # 頻道 URL
    channel_url = "https://www.youtube.com/@YuanShiDian/videos"
    
    try:
        # 獲取頻道用戶名和ID
        username = get_channel_id_from_url(channel_url)
        channel_id = get_channel_id(youtube, username)
        
        print(f"頻道ID: {channel_id}")
        print("\n獲取最新影片列表中...\n")
        
        # 獲取影片列表
        videos = get_channel_videos(youtube, channel_id)
        
        # 保存影片列表
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_file = output_dir / f"videos_{timestamp}.json"
        csv_file = output_dir / f"videos_{timestamp}.csv"
        
        save_videos_to_json(videos, json_file)
        save_videos_to_csv(videos, csv_file)
        
        # 輸出影片資訊
        print(f"\n共找到 {len(videos)} 個影片：\n")
        for i, video in enumerate(videos, 1):
            print(f"{i}. {video['title']}")
            print(f"   發布時間: {video['published_at']}")
            print(f"   影片網址: {video['url']}")
            print()
            
    except Exception as e:
        print(f"錯誤：{str(e)}")

if __name__ == "__main__":
    main()
