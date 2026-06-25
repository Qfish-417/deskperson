"""
OmniVoice TTS Server for Mate-Engine
Listens on port 8083, accepts POST /tts with {"text": "..."}, returns WAV audio.

Run:
  PYTHONPATH=D:/voice python omnivoice_tts_server.py
"""
import sys
import os
import io
import logging
import uuid
import re
import time
import concurrent.futures
from threading import Lock

sys.path.insert(0, r"D:/voice")

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
from omnivoice.models.omnivoice import OmniVoice

MODEL_DIR = r"D:\voice\omnivoice"
REF_AUDIO_PATH = r"C:\Users\admin\Downloads\k9xk6x.mp3"
REF_TEXT = "你，我，他，他，他，你好呀，我是水神芙宁娜，欢迎各位来到水的国度，我在这里欢迎你们的到来，当然，我喜欢你啊，主人，喵喵喵，汪汪汪，哈哈哈，嘻嘻嘻，呜呜呜"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
model = None
dtype = torch.float16 if DEVICE == "cuda" else torch.float32
model_lock = Lock()  # 保护 model.generate() 的线程安全

# 分句：按中文标点切分，每句最多 ~80 字符
_SENT_SEP = re.compile(r'([。！？!?\n]+)')

def split_text(text: str, max_len: int = 80) -> list[str]:
    """按句子切分文本，每句不超过 max_len 字符。"""
    parts = []
    for seg in _SENT_SEP.split(text):
        if not seg.strip():
            continue
        # seg 可能是标点或正文
        if _SENT_SEP.match(seg):
            # 标点和前一句合并
            if parts:
                parts[-1] += seg
            continue
        # 正文部分按 max_len 再切
        while len(seg) > max_len:
            # 找最近的标点或空格切
            cut = max_len
            for i in range(max_len, max(0, max_len - 30), -1):
                if seg[i] in '，,、；;：: ':
                    cut = i + 1
                    break
            parts.append(seg[:cut])
            seg = seg[cut:]
    if seg:
        parts.append(seg)
    return parts

def generate_sentence(sent: str, language: str = "zh", speed: float = 1.0) -> np.ndarray:
    """Generate audio for one sentence (thread-safe with model_lock)."""
    with model_lock:
        vc_prompt = model.create_voice_clone_prompt(
            ref_audio=REF_AUDIO_PATH,
            ref_text=REF_TEXT,
            preprocess_prompt=True,
        )
        audios = model.generate(
            text=sent,
            language=language,
            voice_clone_prompt=vc_prompt,
            instruct=None,
            num_step=8,
            guidance_scale=3.0,
            speed=speed,
            denoise=True,
            postprocess_output=True,
        )
    return audios[0]

def crossfade_concat(audio_parts: list, sr: int, fade_time: float = 0.1) -> np.ndarray:
    """
    Concatenate audio segments with crossfade to avoid clicks/pops.
    Each segment fades out at the end, next segment fades in at the start.
    """
    if len(audio_parts) == 1:
        return audio_parts[0]
    
    fade_samples = int(fade_time * sr)
    result = audio_parts[0]
    
    for i in range(1, len(audio_parts)):
        prev = result
        curr = audio_parts[i]
        
        # 如果片段太短，跳过交叉淡入淡出，直接拼接（加个微小淡入淡出避免爆音）
        if len(prev) < fade_samples * 2 or len(curr) < fade_samples * 2:
            # 简单拼接，两端稍微减弱
            edge_samples = min(100, len(prev) // 10, len(curr) // 10)
            if edge_samples > 0:
                prev[-edge_samples:] *= np.linspace(1.0, 0.5, edge_samples)
                curr[:edge_samples] *= np.linspace(0.5, 1.0, edge_samples)
            result = np.concatenate([prev, curr])
            continue
        
        # 交叉淡入淡出
        # 前一段结尾淡出
        fade_out = np.linspace(1.0, 0.0, fade_samples)
        prev_end = prev[-fade_samples:] * fade_out
        
        # 后一段开头淡入
        fade_in = np.linspace(0.0, 1.0, fade_samples)
        curr_start = curr[:fade_samples] * fade_in
        
        # 交叉区域 = 淡出 + 淡入
        crossfaded = prev_end + curr_start
        # 防止削波
        crossfaded = np.clip(crossfaded, -1.0, 1.0)
        
        # 拼接：前段(去掉结尾淡出部分) + 交叉区域 + 后段(去掉开头淡入部分)
        result = np.concatenate([
            prev[:-fade_samples],
            crossfaded,
            curr[fade_samples:],
        ])
    
    return result

class TTSRequest(BaseModel):
    text: str
    language: str = "zh"
    speed: float = 1.0

app = FastAPI(title="OmniVoice TTS Server")

@app.on_event("startup")
def load_model():
    global model
    logging.info(f"Loading OmniVoice from {MODEL_DIR} on {DEVICE}...")
    try:
        model = OmniVoice.from_pretrained(
            MODEL_DIR,
            device_map=DEVICE,
            torch_dtype=dtype,
            train=False,
        )
        logging.info(f"Model loaded on {model.device}, sr={model.sampling_rate}")
    except Exception as e:
        logging.error(f"Model loading FAILED: {e}")
        import traceback
        traceback.print_exc()
        raise

@app.post("/tts")
def tts(req: TTSRequest):
    if model is None:
        raise HTTPException(500, "Model not loaded")
    logging.info(f"TTS request: {req.text[:60]}...")
    try:
        import time as time_mod
        t0 = time_mod.time()

        # 分句：长文本按句子切分，避免声音漂移
        sentences = split_text(req.text)
        if len(sentences) <= 1:
            vc_prompt = model.create_voice_clone_prompt(
                ref_audio=REF_AUDIO_PATH,
                ref_text=REF_TEXT,
                preprocess_prompt=True,
            )
            audios = model.generate(
                text=req.text,
                language=req.language,
                voice_clone_prompt=vc_prompt,
                instruct=None,
                num_step=8,
                guidance_scale=3.0,
                speed=req.speed,
                denoise=True,
                postprocess_output=True,
            )
            audio_np = audios[0]  # (T,) float32
        else:
            # 并发生成所有句子（CPU预处理并行，GPU推理受锁保护串行）
            with concurrent.futures.ThreadPoolExecutor(max_workers=min(4, len(sentences))) as executor:
                futures = [
                    executor.submit(generate_sentence, sent, req.language, req.speed)
                    for sent in sentences
                ]
                audio_parts = [f.result() for f in futures]

            # 交叉淡入淡出拼接（无静音间隙，流畅过渡）
            audio_np = crossfade_concat(audio_parts, model.sampling_rate, fade_time=0.12)

        t1 = time_mod.time()
        buf = io.BytesIO()
        sf.write(buf, audio_np, model.sampling_rate, format="WAV")
        buf.seek(0)
        wav_bytes = buf.read()
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
    return {"status": "ok", "device": str(model.device) if model else "not_loaded"}

if __name__ == "__main__":
    import uvicorn
    import os as os_mod
    port = int(os_mod.environ.get("TTS_PORT", 8083))
    uvicorn.run(app, host="0.0.0.0", port=port)
