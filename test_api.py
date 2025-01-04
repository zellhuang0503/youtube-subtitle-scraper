# -*- coding: utf-8 -*-
from dotenv import load_dotenv
import os
from googleapiclient.discovery import build

def test_api_key():
    # 載入 .env 檔案中的環境變數
    load_dotenv()
    
    # 取得 API 密鑰
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("錯誤：找不到 API 密鑰，請確認 .env 檔案中已設置 YOUTUBE_API_KEY")
        return False
    
    try:
        # 建立 YouTube API 服務
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        # 測試 API - 取得一個熱門影片的資訊
        request = youtube.videos().list(
            part="snippet",
            chart="mostPopular",
            regionCode="TW",
            maxResults=1
        )
        response = request.execute()
        
        # 如果能成功取得資料，表示 API 密鑰有效
        if 'items' in response:
            video = response['items'][0]
            print("API 測試成功！")
            print(f"成功取得影片資訊：{video['snippet']['title']}")
            return True
        
    except Exception as e:
        print(f"錯誤：API 測試失敗 - {str(e)}")
        return False

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    test_api_key()
