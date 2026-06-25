"""
Mate-Engine Interaction Sound Player v6
- Windows PlaySoundW API (100% no window, kernel level)
- Polling mouse detection (non-blocking)
"""
import time
import random
import os
import sys
import ctypes
import threading

# Config
AUDIO_FILES = [
    r"D:\voice\game_tts_sample1.mp3",
    r"D:\voice\game_tts_sample2.mp3",
]
GAME_WINDOW_TITLE = "MateEngineX"
CLICK_COOLDOWN = 0.3
POLL_INTERVAL = 0.05

# Global
last_click_time = 0
playing = False

# Windows API
winmm = ctypes.windll.winmm

# PlaySound flags
SND_FILENAME = 0x00020000
SND_ASYNC = 0x00000001
SND_NODEFAULT = 0x00000002

def play_mp3_playsound(mp3_path):
    """Play MP3 using PlaySoundW (no window, kernel level)"""
    global playing
    try:
        # PlaySoundW can play MP3 directly
        ret = winmm.PlaySoundW(
            ctypes.c_wchar_p(mp3_path),
            None,  # hmod
            SND_FILENAME | SND_ASYNC | SND_NODEFAULT
        )
        if not ret:
            # PlaySoundW failed, trying sounddevice...
            pass
            # Fallback: use sounddevice to play MP3
            try:
                import sounddevice as sd
                import subprocess
                # Convert MP3 to raw PCM using ffmpeg (in memory)
                result = subprocess.run(
                    ['ffmpeg', '-i', mp3_path, '-f', 'wav', '-'],
                    capture_output=True, timeout=5
                )
                import io
                import wave
                wav_data = io.BytesIO(result.stdout)
                with wave.open(wav_data, 'rb') as wf:
                    audio_data = wf.readframes(wf.getnframes())
                    sd.play(audio_data, wf.getframerate(), blocking=False)
            except Exception as e2:
                pass  # Fallback also failed
        playing = False
    except Exception as e:
        pass  # PlaySoundW exception
        playing = False

def play_audio_random():
    """Play random audio in background thread"""
    global playing
    if playing:
        return
    
    audio_file = random.choice(AUDIO_FILES)
    if not os.path.exists(audio_file):
        return  # File not found
    
    pass  # Audio file selected
    playing = True
    t = threading.Thread(target=play_mp3_playsound, args=(audio_file,), daemon=True)
    t.start()

def is_game_window_active():
    """Check if game window is foreground"""
    try:
        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        length = user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        return GAME_WINDOW_TITLE.lower() in (buf.value or "").lower()
    except:
        return False

def get_mouse_state():
    """Get current mouse button state (non-blocking)"""
    try:
        user32 = ctypes.windll.user32
        return (user32.GetAsyncKeyState(0x01) & 0x8000) != 0  # VK_LBUTTON
    except:
        return False

def main_loop():
    """Main polling loop"""
    global last_click_time
    mouse_was_down = False
    
    pass  # Monitoring started
    
    try:
        while True:
            mouse_down = get_mouse_state()
            
            # Detect mouse down edge
            if mouse_down and not mouse_was_down:
                current_time = time.time()
                if current_time - last_click_time < CLICK_COOLDOWN:
                    mouse_was_down = mouse_down
                    time.sleep(POLL_INTERVAL)
                    continue
                
                last_click_time = current_time
                
                if is_game_window_active():
                    pass  # Click detected
                    play_audio_random()
            
            mouse_was_down = mouse_down
            time.sleep(POLL_INTERVAL)
            
    except KeyboardInterrupt:
        pass  # Monitoring stopped

def main():
    """Main entry point - no debug output"""
    main_loop()

if __name__ == "__main__":
    main()
