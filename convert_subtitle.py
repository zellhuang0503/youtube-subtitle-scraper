import json
import os
from googletrans import Translator
from tqdm import tqdm
import time

def convert_json_to_txt():
    # 設定輸入和輸出目錄
    input_dir = r"E:\CascadeProjects\YTsubtitle_scrape\output\figma_video_subtitles"
    output_dir = r"E:\CascadeProjects\YTsubtitle_scrape\output\figma_video_subtitles_txt"
    
    # 創建輸出目錄（如果不存在）
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 初始化翻譯器
    translator = Translator()
    
    # 獲取所有JSON檔案
    json_files = [f for f in os.listdir(input_dir) if f.endswith('.json')]
    print(f"找到 {len(json_files)} 個JSON檔案需要處理")
    
    # 使用tqdm顯示進度條
    for json_file in tqdm(json_files, desc="處理檔案"):
        try:
            # 讀取JSON檔案
            input_file = os.path.join(input_dir, json_file)
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 準備輸出的TXT檔案名稱
            txt_file = os.path.splitext(json_file)[0] + '.txt'
            txt_path = os.path.join(output_dir, txt_file)
            
            # 開啟TXT檔案進行寫入
            with open(txt_path, 'w', encoding='utf-8') as f:
                # 寫入影片資訊
                if 'video_info' in data:
                    f.write("影片資訊：\n")
                    f.write(f"標題: {data['video_info'].get('title', '')}\n")
                    f.write(f"網址: {data['video_info'].get('url', '')}\n")
                    f.write(f"上傳時間: {data['video_info'].get('upload_time', '')}\n\n")
                
                # 如果JSON中包含字幕內容
                if 'subtitles' in data:
                    f.write("字幕內容：\n")
                    for subtitle in data['subtitles']:
                        if 'text' in subtitle:
                            original_text = subtitle['text'].strip()
                            if original_text:  # 只處理非空字串
                                try:
                                    # 翻譯成繁體中文
                                    translated = translator.translate(original_text, dest='zh-tw')
                                    # 寫入時間戳和翻譯後的文字
                                    f.write(f"\n時間: [{subtitle.get('start', '')} - {subtitle.get('start', '') + subtitle.get('duration', '')}]\n")
                                    f.write(f"原文: {original_text}\n")
                                    f.write(f"翻譯: {translated.text}\n")
                                    
                                    # 避免翻譯太快被限制，加入短暫延遲
                                    time.sleep(0.1)
                                except Exception as e:
                                    print(f"\n翻譯錯誤 ({json_file}): {str(e)}")
                                    continue
                
        except Exception as e:
            print(f"\n處理檔案時發生錯誤 ({json_file}): {str(e)}")
            continue
    
    print("\n全部處理完成！")

if __name__ == "__main__":
    convert_json_to_txt()
