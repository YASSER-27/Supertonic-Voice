@echo off
title Supertonic Voice - Distribution Package
echo ============================================
echo   Creating Distribution Package
echo ============================================
echo.

set DIST_DIR=dist\SupertonicVoice

:: Create distribution folder
if not exist "%DIST_DIR%" mkdir "%DIST_DIR%"

:: Copy EXE
if exist "dist\SupertonicVoice.exe" (
    copy /Y "dist\SupertonicVoice.exe" "%DIST_DIR%\" >nul
    echo [OK] SupertonicVoice.exe
) else (
    echo [SKIP] SupertonicVoice.exe not found - run build.bat first!
)

:: Copy TTS worker
if exist "tts_worker.exe" (
    copy /Y "tts_worker.exe" "%DIST_DIR%\" >nul
    echo [OK] tts_worker.exe
)

:: Copy icon
copy /Y "icon.ico" "%DIST_DIR%\" >nul
echo [OK] icon.ico

:: Copy config
copy /Y "config.json" "%DIST_DIR%\" >nul
echo [OK] config.json

:: Copy ONNX models
if not exist "%DIST_DIR%\onnx" mkdir "%DIST_DIR%\onnx"
xcopy /E /Y /Q "onnx\*" "%DIST_DIR%\onnx\" >nul
echo [OK] onnx\ models

:: Copy voice styles
if not exist "%DIST_DIR%\voice_styles" mkdir "%DIST_DIR%\voice_styles"
xcopy /E /Y /Q "voice_styles\*" "%DIST_DIR%\voice_styles\" >nul
echo [OK] voice_styles\

:: Copy Chrome extension
if not exist "%DIST_DIR%\chrome_extension" mkdir "%DIST_DIR%\chrome_extension"
xcopy /E /Y /Q "chrome_extension\*" "%DIST_DIR%\chrome_extension\" >nul
echo [OK] chrome_extension\

echo.
echo ============================================
echo   Distribution ready: %DIST_DIR%\
echo ============================================
echo.
echo Contents:
echo   - SupertonicVoice.exe (main app)
echo   - tts_worker.exe (TTS engine)
echo   - onnx\ (AI models)
echo   - voice_styles\ (voice data)
echo   - chrome_extension\ (load in Chrome)
echo.
pause
