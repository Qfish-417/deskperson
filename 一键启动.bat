@echo off
chcp 936 > nul
echo =============================================
echo Mate-Engine One-Click Startup
echo =============================================
echo.

:: Step 1: Kill old processes
echo [1/5] Closing old Python processes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo [OK] Old processes cleaned
echo.

:: Step 2: Start GPT-SoVITS API
echo [2/5] Starting GPT-SoVITS API (port 9880)...
start "GPT-SoVITS API" cmd /k "cd /d D:\voice\GPT-SoVITS-windows\GPT-SoVITS-v3lora-20250228 && runtime\python.exe api_v2.py -a 127.0.0.1 -p 9880 -c GPT_SoVITS\configs\tts_infer_v3.yaml"
echo [OK] GPT-SoVITS starting (wait 15s)...
timeout /t 15 /nobreak >nul
echo.

:: Step 3: Check API
echo [3/5] Checking API status...
curl -s http://127.0.0.1:9880/health >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] API ready
) else (
    echo [WARN] API may not be ready, continuing...
)
echo.

:: Step 4: Start interaction sound (互动音效 - 先启动)
echo [4/5] Starting interaction sound player...
start "Interaction Sound" cmd /k "cd /d D:\voice && C:\Users\admin\.workbuddy\binaries\python\versions\3.13.12\python.exe interaction_sound_final.py"
echo [OK] Interaction sound started
echo.

:: Step 5: Start TTS monitor (对话转语音 - 后启动)
echo [5/5] Starting TTS monitor...
start "TTS Monitor" cmd /k "cd /d D:\voice && C:\Users\admin\.workbuddy\binaries\python\versions\3.13.12\python.exe tts_monitor_gpt_sovits.py"
echo [OK] TTS monitor started
echo.

echo =============================================
echo All services started!
echo =============================================
echo.
echo Started services:
echo   - GPT-SoVITS API (port 9880)
echo   - TTS Monitor
echo   - Interaction Sound Player
echo.
echo Now you can:
echo   1. Start Mate-Engine game (D:\Mate-Engine\MateEngineX.exe)
echo   2. Chat with AI - will auto-play Furina voice
echo   3. Click character - will play random sound effects
echo.
echo To stop: close cmd windows or run stop_all.bat
echo.
pause
