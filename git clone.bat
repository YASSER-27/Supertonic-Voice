@echo off
title Downloading Supertonic-3 Repository...
echo ===================================================
echo [!] Starting clone for Supertone/supertonic-3
echo Make sure Git and Git LFS are installed!
echo ===================================================

:: التأكد من تفعيل Git LFS للتعامل مع الملفات الضخمة
git lfs install

:: أمر التحميل (Cloning)
git clone https://huggingface.co/Supertone/supertonic-3

echo ===================================================
echo [+] Download completed successfully!
echo ===================================================
pause