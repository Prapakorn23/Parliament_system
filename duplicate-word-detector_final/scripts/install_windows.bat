@echo off
echo ========================================
echo ระบบตรวจจับคำซ้ำสำหรับรัฐสภาไทย
echo Parliament Duplicate Word Detector
echo ========================================
echo.

REM ตรวจสอบว่ามี .venv หรือยัง
if not exist ".venv" (
    echo [0/4] กำลังสร้าง Virtual Environment (.venv)...
    python -m venv .venv
    if errorlevel 1 (
        echo ❌ ไม่สามารถสร้าง virtual environment ได้
        echo    กรุณาตรวจสอบว่า Python ติดตั้งแล้ว
        pause
        exit /b 1
    )
    echo ✅ สร้าง Virtual Environment สำเร็จ!
    echo.
)

echo [1/4] กำลัง Activate Virtual Environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ ไม่สามารถ activate virtual environment ได้
    pause
    exit /b 1
)
echo ✅ Virtual Environment Activated!
echo.

echo [2/4] กำลังอัพเกรด pip...
python -m pip install --upgrade pip
echo.

echo [3/4] กำลังติดตั้ง Python Libraries จาก requirements.txt...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ การติดตั้งล้มเหลว
    pause
    exit /b 1
)
echo.

echo [4/4] ตรวจสอบการติดตั้ง...
python -c "import flask; import pythainlp; import pandas; print('✅ Core libraries installed successfully')"
echo.

echo ========================================
echo ✅ ติดตั้ง Python Libraries เสร็จสิ้น!
echo ========================================
echo.

echo 📝 หมายเหตุ:
echo.
echo - Virtual Environment: .venv (activated)
echo - ใช้คำสั่ง 'deactivate' เพื่อออกจาก virtual environment
echo.
echo ⚠️  สำหรับ OCR (PDF ภาพ) ต้องติดตั้งเพิ่ม:
echo.
echo 1. Tesseract-OCR:
echo    - ดาวน์โหลด: https://github.com/UB-Mannheim/tesseract/wiki
echo    - ติดตั้งพร้อมเลือกภาษาไทย (Thai)
echo    - เพิ่ม PATH: C:\Program Files\Tesseract-OCR
echo.
echo 2. Poppler:
echo    - ดาวน์โหลด: http://blog.alivate.com.au/poppler-windows/
echo    - แตกไฟล์และเพิ่ม bin folder ใน PATH
echo.
echo 3. Database (MariaDB/MySQL):
echo    - ติดตั้ง MariaDB หรือ MySQL
echo    - สร้างไฟล์ .env จาก .env.example
echo    - รัน: python scripts/init_database.py
echo.

echo ========================================
echo 🚀 พร้อมใช้งาน! รันด้วยคำสั่ง:
echo    .venv\Scripts\activate
echo    python app.py
echo ========================================
echo.

pause

