"""
Mate-Engine TTS Monitor - GPT-SoVITS版本
监控ZomeAI.json，检测到新AI回复时调用GPT-SoVITS API生成语音并播放
"""
import json
import time
import requests
import sounddevice as sd
import numpy as np
import os
from pathlib import Path

# 配置
ZOMEAI_PATH = r"C:\Users\admin\AppData\LocalLow\Shinymoon\MateEngineX\ZomeAI.json"
GPT_SOVITS_API = "http://127.0.0.1:9880/tts"
REF_AUDIO_PATH = r"D:\voice\声音\芙宁娜.mp3"
REF_TEXT = "你好，我是芙宁娜，一二三四，四三二一，你还在吗，我还在呢让我们期待未来"

# 状态跟踪
last_msg_count = 0

def check_and_tts():
    """检查ZomeAI.json是否有新消息，如果有则调用TTS"""
    global last_msg_count
    
    try:
        with open(ZOMEAI_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        chat = data.get('chat', [])
        current_count = len(chat)
        
        # 检测新消息
        if current_count > last_msg_count:
            # 获取最新消息
            latest_msg = chat[-1]
            content = latest_msg.get('content', '').strip()
            
            if content:
                # 调用GPT-SoVITS API生成语音
                audio_data = call_gpt_sovits_tts(content)
                
                if audio_data is not None:
                    # 播放音频
                    play_audio(audio_data)
                else:
                    print("[ERROR] TTS生成失败")
            
            last_msg_count = current_count
        
        elif current_count < last_msg_count:
            # 消息被清空（新对话开始）
            print("[INFO] 检测到对话重置")
            last_msg_count = current_count
            
        except Exception as e:
        pass  # 检查ZomeAI.json失败

def call_gpt_sovits_tts(text: str):
    """调用GPT-SoVITS API生成语音"""
    try:
        params = {
            "text": text,
            "text_lang": "zh",
            "ref_audio_path": REF_AUDIO_PATH,
            "prompt_text": REF_TEXT,
            "prompt_lang": "zh",
            "text_split_method": "cut0",
            "speed_factor": 1.0,
            "top_k": 5,
            "top_p": 1.0,
            "temperature": 1.0,
            "batch_size": 1,
            "batch_threshold": 0.75,
            "split_bucket": True,
            "fragment_interval": 0.3,
            "seed": -1,
            "streaming_mode": False,
            "parallel_infer": True,
            "repetition_penalty": 1.35
        }
        
        resp = requests.get(GPT_SOVITS_API, params=params, timeout=120)
        
        if resp.status_code == 200:
            # 解析WAV音频数据
            import io
            import soundfile as sf
            
            audio_io = io.BytesIO(resp.content)
            audio_data, sample_rate = sf.read(audio_io)
            
            return audio_data, sample_rate
        else:
            print(f"[ERROR] API返回错误: {resp.status_code}, {resp.text[:200]}")
            return None
            
    except Exception as e:
        print(f"[ERROR] 调用TTS API失败: {e}")
        return None

def play_audio(audio_data_tuple):
    """播放音频"""
    try:
        audio_data, sample_rate = audio_data_tuple
        
        sd.play(audio_data, sample_rate)
        sd.wait()  # 等待播放完成
        
    except Exception as e:
        print(f"[ERROR] 播放音频失败: {e}")

def main():
    """主循环"""
    global last_msg_count
    
    print("=" * 60)
    print("Mate-Engine TTS Monitor (GPT-SoVITS版本)")
    print("=" * 60)
    print(f"监控文件: {ZOMEAI_PATH}")
    print(f"TTS API: {GPT_SOVITS_API}")
    print(f"参考音频: {REF_AUDIO_PATH}")
    print("=" * 60)
    print("\n等待新消息...\n")
    
    # 初始化：跳过历史消息
    try:
        with open(ZOMEAI_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        last_msg_count = len(data.get('chat', []))
        print(f"[INFO] 初始化完成，当前消息数: {last_msg_count}（将跳过历史消息）\n")
    except:
        last_msg_count = 0
    
    # 主循环
    while True:
        try:
            check_and_tts()
            time.sleep(1)  # 每秒检查一次
        except KeyboardInterrupt:
            print("\n[INFO] 监控停止")
            break
        except Exception as e:
            print(f"[ERROR] 主循环异常: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
