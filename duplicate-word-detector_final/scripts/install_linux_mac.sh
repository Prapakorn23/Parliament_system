#!/bin/bash

echo "========================================"
echo "ระบบตรวจจับคำซ้ำสำหรับรัฐสภาไทย"
echo "Parliament Duplicate Word Detector"
echo "========================================"
echo ""

# ตรวจสอบว่ามี .venv หรือยัง
if [ ! -d ".venv" ]; then
    echo "[0/4] กำลังสร้าง Virtual Environment (.venv)..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "❌ ไม่สามารถสร้าง virtual environment ได้"
        echo "   กรุณาตรวจสอบว่า Python3 ติดตั้งแล้ว"
        exit 1
    fi
    echo "✅ สร้าง Virtual Environment สำเร็จ!"
    echo ""
fi

echo "[1/4] กำลัง Activate Virtual Environment..."
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ ไม่สามารถ activate virtual environment ได้"
    exit 1
fi
echo "✅ Virtual Environment Activated!"
echo ""

echo "[2/4] กำลังอัพเกรด pip..."
python -m pip install --upgrade pip
echo ""

echo "[3/4] กำลังติดตั้ง Python Libraries จาก requirements.txt..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ การติดตั้งล้มเหลว"
    exit 1
fi
echo ""

echo "[4/4] ตรวจสอบการติดตั้ง..."
python -c "import flask; import pythainlp; import pandas; print('✅ Core libraries installed successfully')"
echo ""

echo "========================================"
echo "✅ ติดตั้ง Python Libraries เสร็จสิ้น!"
echo "========================================"
echo ""

echo "📝 หมายเหตุ:"
echo ""
echo "- Virtual Environment: .venv (activated)"
echo "- ใช้คำสั่ง 'deactivate' เพื่อออกจาก virtual environment"
echo ""

echo "⚠️  สำหรับ OCR (PDF ภาพ) ต้องติดตั้งเพิ่ม:"
echo ""

# ตรวจสอบ OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 macOS - ติดตั้งด้วย Homebrew:"
    echo "   brew install tesseract tesseract-lang poppler"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 Linux (Ubuntu/Debian):"
    echo "   sudo apt update"
    echo "   sudo apt install tesseract-ocr tesseract-ocr-tha poppler-utils"
fi

echo ""
echo "ทดสอบ Tesseract:"
echo "   tesseract --version"
echo "   tesseract --list-langs  # ต้องมี 'tha'"
echo ""

echo "📦 Database (MariaDB/MySQL):"
echo "   - ติดตั้ง MariaDB หรือ MySQL"
echo "   - สร้างไฟล์ .env จาก .env.example"
echo "   - รัน: python scripts/init_database.py"
echo ""

echo "========================================"
echo "🚀 พร้อมใช้งาน! รันด้วยคำสั่ง:"
echo "   source .venv/bin/activate"
echo "   python app.py"
echo "========================================"
echo ""

