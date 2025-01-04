# -*- coding: utf-8 -*-
import yt_dlp
import json
from pathlib import Path
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time
from datetime import datetime
import logging
import re

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('subtitle_download.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def convert_vtt_to_markdown(vtt_content, video_info):
    """將 VTT 字幕轉換為 Markdown 格式"""
    # 添加影片資訊
    markdown_lines = [
        f"# {video_info['title']}",
        "",
        f"- **影片網址**: {video_info['url']}",
        f"- **發布時間**: {video_info['published_at']}",
        "",
        "## 字幕內容",
        "",
    ]
    
    # 解析 VTT 內容
    lines = vtt_content.split('\n')
    current_time = ""
    
    for line in lines:
        # 跳過 VTT 檔案頭
        if line.startswith('WEBVTT') or line.strip() == '':
            continue
            
        # 處理時間戳
        if '-->' in line:
            current_time = line.strip()
            continue
            
        # 處理字幕文字
        if line.strip() and not line.startswith('NOTE'):
            markdown_lines.append(f"[{current_time}] {line.strip()}")
            markdown_lines.append("")
    
    return '\n'.join(markdown_lines)

def download_subtitle(video, output_dir, retries=3):
    """下載單個影片的字幕"""
    video_url = video['url']
    output_dir = Path(output_dir)
    
    # 建立一個安全的檔案名稱（移除不合法的字元）
    safe_title = re.sub(r'[<>:"/\\|?*]', '_', video['title'])
    
    # 設定 yt-dlp 選項
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['zh-Hant', 'zh-TW', 'zh-HK', 'en'],
        'outtmpl': str(output_dir / f'{safe_title}'),
        'quiet': True,
        'no_warnings': True
    }
    
    for attempt in range(retries):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 獲取影片資訊
                info = ydl.extract_info(video_url, download=False)
                
                # 檢查是否有字幕
                has_subtitles = False
                if 'subtitles' in info and info['subtitles']:
                    has_subtitles = True
                elif 'automatic_captions' in info and info['automatic_captions']:
                    has_subtitles = True
                
                if has_subtitles:
                    # 下載字幕
                    ydl.download([video_url])
                    
                    # 找到下載的 vtt 檔案
                    vtt_files = list(output_dir.glob(f'{safe_title}.*.vtt'))
                    if vtt_files:
                        vtt_file = vtt_files[0]
                        # 讀取 VTT 內容
                        with open(vtt_file, 'r', encoding='utf-8') as f:
                            vtt_content = f.read()
                        
                        # 轉換為 Markdown
                        markdown_content = convert_vtt_to_markdown(vtt_content, video)
                        
                        # 保存 Markdown 檔案
                        markdown_file = output_dir / f'{safe_title}.md'
                        with open(markdown_file, 'w', encoding='utf-8') as f:
                            f.write(markdown_content)
                        
                        # 刪除原始的 vtt 檔案
                        vtt_file.unlink()
                    
                    return {
                        'success': True,
                        'video_id': video['id'],
                        'title': video['title'],
                        'message': '下載成功'
                    }
                else:
                    return {
                        'success': False,
                        'video_id': video['id'],
                        'title': video['title'],
                        'message': '影片沒有字幕'
                    }
                
        except Exception as e:
            if 'Premieres' in str(e):
                return {
                    'success': False,
                    'video_id': video['id'],
                    'title': video['title'],
                    'message': f'影片尚未發布: {str(e)}'
                }
            elif attempt < retries - 1:
                time.sleep(2 ** attempt)  # 指數退避重試
                continue
            else:
                return {
                    'success': False,
                    'video_id': video['id'],
                    'title': video['title'],
                    'message': f'下載失敗: {str(e)}'
                }

def batch_download_subtitles(videos, output_dir, max_workers=3):
    """批量下載字幕"""
    output_dir = Path(output_dir)
    subtitle_dir = output_dir / "subtitles"
    subtitle_dir.mkdir(exist_ok=True)
    
    # 準備下載結果記錄
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = output_dir / f"download_results_{timestamp}.json"
    
    # 建立進度條
    pbar = tqdm(total=len(videos), desc="下載字幕中")
    results = []
    
    # 使用線程池進行並行下載
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有下載任務
        future_to_video = {
            executor.submit(download_subtitle, video, subtitle_dir): video
            for video in videos
        }
        
        # 處理完成的任務
        for future in as_completed(future_to_video):
            video = future_to_video[future]
            try:
                result = future.result()
                results.append(result)
                
                # 記錄日誌
                if result['success']:
                    logging.info(f"成功: {result['title']}")
                else:
                    logging.warning(f"失敗: {result['title']} - {result['message']}")
                
            except Exception as e:
                results.append({
                    'success': False,
                    'video_id': video['id'],
                    'title': video['title'],
                    'message': f'發生異常: {str(e)}'
                })
                logging.error(f"異常: {video['title']} - {str(e)}")
            
            pbar.update(1)
    
    pbar.close()
    
    # 保存下載結果
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 統計結果
    success_count = sum(1 for r in results if r['success'])
    fail_count = len(results) - success_count
    
    print(f"\n下載完成！")
    print(f"成功: {success_count} 個")
    print(f"失敗: {fail_count} 個")
    print(f"詳細結果已保存至: {results_file}")
    
    return results

def main():
    # 設置輸出編碼為 UTF-8
    sys.stdout.reconfigure(encoding='utf-8')
    
    # 讀取影片列表
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
    
    print(f"找到 {len(videos)} 個影片，開始下載字幕...")
    batch_download_subtitles(videos, output_dir)

if __name__ == "__main__":
    main()
