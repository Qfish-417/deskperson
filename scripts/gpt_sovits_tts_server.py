"""
GPT-SoVITS TTS Server for Mate-Engine
监听端口 8084，接收POST /tts请求，返回WAV音频
使用Zero-shot语音克隆（无需训练，直接用参考音频）
"""
import sys
import os
import io
import logging
import uuid
import time

# 添加GPT-SoVITS到Python路径
GPT_SOVITS_DIR = r"D:\voice\GPT-SoVITS\GPT_SoVITS"
sys.path.insert(0, GPT_SOVITS_DIR)
# 还要添加父目录（因为text模块在GPT_SoVITS/text）
sys.path.insert(0, r"D:\voice\GPT-SoVITS")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

import torch
import numpy as np
import soundfile as sf
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

# 模型路径
GPT_MODEL_PATH = r"D:\voice\GPT-SoVITS\GPT_SoVITS\pretrained_models\s1v3.ckpt"
SOVITS_MODEL_PATH = r"D:\voice\GPT-SoVITS\GPT_SoVITS\pretrained_models\s2Gv3.pth"
REF_AUDIO_PATH = r"C:\Users\admin\Downloads\k9xk6x.mp3"  # 芙宁娜参考音频
REF_TEXT = "你，我，他，他，他，你好呀，我是水神芙宁娜，欢迎各位来到水的国度，我在这里欢迎你们的到来，当然，我喜欢你啊，主人，喵喵喵，汪汪汪，哈哈哈，嘻嘻嘻，呜呜呜"

# 全局变量
app = FastAPI(title="GPT-SoVITS TTS Server")
gpt_model = None
sovits_model = None
device = "cuda" if torch.cuda.is_available() else "cpu"

class TTSRequest(BaseModel):
    text: str
    language: str = "中文"
    speed: float = 1.0

@app.on_event("startup")
def load_models():
    """启动时加载GPT-SoVITS模型"""
    global gpt_model, sovits_model
    logging.info(f"Loading GPT-SoVITS models on {device}...")
    
    try:
        # 导入GPT-SoVITS推理模块
        from GPT_SoVITS.inference_webui import (
            change_gpt_weights, 
            change_sovits_weights,
            get_tts_wav
        )
        
        # 加载GPT模型
        logging.info(f"Loading GPT model: {GPT_MODEL_PATH}")
        change_gpt_weights(gpt_path=GPT_MODEL_PATH)
        logging.info("GPT model loaded")
        
        # 加载SoVITS模型
        logging.info(f"Loading SoVITS model: {SOVITS_MODEL_PATH}")
        change_sovits_weights(sovits_path=SOVITS_MODEL_PATH)
        logging.info("SoVITS model loaded")
        
        logging.info("All models loaded successfully!")
        
    except Exception as e:
        logging.error(f"Model loading failed: {e}")
        import traceback
        traceback.print_exc()
        raise

@app.post("/tts")
def tts(req: TTSRequest):
    """TTS推理接口"""
    logging.info(f"TTS request: {req.text[:60]}...")
    
    try:
        t0 = time.time()
        
        # 导入推理函数
        from GPT_SoVITS.inference_webui import get_tts_wav
        
        # Zero-shot TTS（无需训练，直接用参考音频）
        logging.info("Starting TTS generation...")
        synthesis_result = get_tts_wav(
            ref_wav_path=REF_AUDIO_PATH,
            prompt_text=REF_TEXT,
            prompt_language="中文",
            text=req.text,
            text_language=req.language,
            how_to_cut="不切",  # 不切分，让模型自己处理
            top_k=20,
            top_p=0.6,
            temperature=0.6,
            ref_free=False,
            speed=req.speed,
            if_freeze=False,
            sample_steps=8,
            if_sr=False,  # 不做超分（节省时间）
            pause_second=0.3,
            use_cuda_graph=False,
        )
        
        # get_tts_wav是生成器，需要遍历获取结果
        # 格式: yield (sampling_rate, audio_data)
        audio_np = None
        sr = 22050  # 默认采样率
        
        for result in synthesis_result:
            if isinstance(result, tuple) and len(result) == 2:
                sr, audio_data = result
                audio_np = audio_data.astype(np.float32)
        
        if audio_np is None:
            raise Exception("TTS generation returned no audio")
        
        t1 = time.time()
        logging.info(f"TTS done in {t1-t0:.1f}s, shape={audio_np.shape}, sr={sr}")
        
        # 保存为WAV
        buf = io.BytesIO()
        sf.write(buf, audio_np, sr, format="WAV")
        buf.seek(0)
        wav_bytes = buf.read()
        
        logging.info(f"TTS response: {len(wav_bytes)} bytes")
        return Response(
            content=wav_bytes,
            media_type="audio/wav",
            headers={"Content-Disposition": f"inline; filename=tts_{uuid.uuid4().hex[:8]}.wav"},
        )
        
    except Exception as e:
        logging.exception("TTS failed")
        raise HTTPException(500, str(e))

@app.get("/health")
def health():
    return {"status": "ok", "device": device}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("TTS_PORT", 8084))
    uvicorn.run(app, host="0.0.0.0", port=port)
