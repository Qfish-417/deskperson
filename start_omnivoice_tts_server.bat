@echo off
REM Start OmniVoice TTS Server (Port 8083)

set PYTHONPATH=D:\voice
set TTS_PORT=8083

echo ========================================
echo   OmniVoice TTS Server (Port %TTS_PORT%)
echo ========================================
echo.

"C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe" "D:\voice\omnivoice_tts_server.py"

echo.
echo [Server stopped]
pause
