@echo off
chcp 65001 > nul
echo ======================================
echo Installing Thai Language for Tesseract
echo ======================================
echo.

set TESSDATA_DIR=C:\Program Files\Tesseract-OCR\tessdata
set DOWNLOAD_URL=https://github.com/tesseract-ocr/tessdata/raw/main/tha.traineddata
set TARGET_FILE=%TESSDATA_DIR%\tha.traineddata

echo 📥 Downloading Thai language data...
echo From: %DOWNLOAD_URL%
echo To: %TARGET_FILE%
echo.

REM Download using PowerShell
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%TARGET_FILE%'}"

if exist "%TARGET_FILE%" (
    echo.
    echo ✅ Thai language installed successfully!
    echo File: %TARGET_FILE%
    echo Size: 
    dir "%TARGET_FILE%" | find "tha.traineddata"
    echo.
    echo 🔄 Please restart your Flask app (Ctrl+C and run again)
    echo.
    pause
) else (
    echo.
    echo ❌ Download failed!
    echo 💡 Try manual method:
    echo    1. Download: %DOWNLOAD_URL%
    echo    2. Copy to: %TESSDATA_DIR%
    echo.
    pause
)

