import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import youtube_dl
import logging
from tqdm import tqdm

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('youtube_scraper.log'),
        logging.StreamHandler()
    ]
)

class YouTubeSubtitleScraper:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        if not self.api_key:
            raise ValueError("請在.env文件中設置YOUTUBE_API_KEY")
        
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        self.ydl_opts = {
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en', 'zh-Hant'],  # 可以根據需要修改語言
            'quiet': True,
        }

    def get_channel_videos(self, channel_id, max_results=50):
        """獲取頻道最新視頻列表"""
        try:
            request = self.youtube.search().list(
                part="id,snippet",
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
                    'published_at': item['snippet']['publishedAt']
                }
                videos.append(video)
            
            return videos
        
        except HttpError as e:
            logging.error(f"獲取視頻列表時發生錯誤: {str(e)}")
            return []

    def download_subtitle(self, video_id):
        """下載視頻字幕"""
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        try:
            with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
                ydl.download([video_url])
            return True
        except Exception as e:
            logging.error(f"下載字幕時發生錯誤 {video_id}: {str(e)}")
            return False

def main():
    scraper = YouTubeSubtitleScraper()
    
    # 測試用頻道ID (請替換為實際的頻道ID)
    channel_id = "UC_x5XG1OV2P6uZZ5FSM9Ttw"  # Google Developers channel
    
    logging.info("開始獲取視頻列表...")
    videos = scraper.get_channel_videos(channel_id, max_results=5)
    
    if not videos:
        logging.error("沒有找到視頻")
        return
    
    logging.info(f"找到 {len(videos)} 個視頻")
    
    for video in tqdm(videos, desc="下載字幕"):
        success = scraper.download_subtitle(video['id'])
        if success:
            logging.info(f"成功下載視頻字幕: {video['title']}")
        else:
            logging.warning(f"無法下載視頻字幕: {video['title']}")

if __name__ == "__main__":
    main()
