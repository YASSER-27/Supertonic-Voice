@echo off
title Supertonic Voice - Build
echo ============================================
echo   Building Supertonic Voice (.exe)
echo ============================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    pause
    exit /b 1
)

:: Install dependencies
echo [1/3] Installing dependencies...
pip install PySide6 pyinstaller pyttsx3 --quiet

:: Build EXE
echo [2/3] Building EXE with PyInstaller...
pyinstaller supertonic_voice.spec --noconfirm --clean

:: Copy required files next to EXE
echo [3/3] Copying required files...
if exist "dist\SupertonicVoice.exe" (
    echo.
    echo ============================================
    echo   BUILD SUCCESSFUL!
    echo   Output: dist\SupertonicVoice.exe
    echo ============================================
    echo.
    echo Copy these files next to SupertonicVoice.exe:
    echo   - tts_worker.exe
    echo   - icon.ico
    echo   - onnx\ folder
    echo   - voice_styles\ folder
    echo   - config.json
    echo.
) else (
    echo [ERROR] Build failed!
)

pause
