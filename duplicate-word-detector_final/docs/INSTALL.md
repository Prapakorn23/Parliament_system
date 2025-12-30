# 📦 คู่มือการติดตั้งและตั้งค่า

## 🚀 Quick Start

### Windows

```bash
# วิธีที่ 1: ใช้ install script (แนะนำ)
scripts\install_windows.bat

# วิธีที่ 2: ติดตั้งด้วยตัวเอง
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Linux / macOS

```bash
# วิธีที่ 1: ใช้ install script (แนะนำ)
chmod +x scripts/install_linux_mac.sh
./scripts/install_linux_mac.sh

# วิธีที่ 2: ติดตั้งด้วยตัวเอง
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 📋 ขั้นตอนการติดตั้งแบบละเอียด

### 1. สร้าง Virtual Environment (.venv)

```bash
# Windows
python -m venv .venv

# Linux/Mac
python3 -m venv .venv
```

### 2. Activate Virtual Environment

```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

⚠️ **สำคัญ:** ต้อง activate virtual environment ทุกครั้งก่อนใช้งาน

### 3. อัพเกรด pip

```bash
python -m pip install --upgrade pip
```

### 4. ติดตั้ง Dependencies

```bash
pip install -r requirements.txt
```

## 🔧 ตั้งค่า Database (MariaDB/MySQL)

### 1. ติดตั้ง MariaDB/MySQL

ดูรายละเอียดใน `DATABASE_SETUP.md`

### 2. สร้างไฟล์ .env

```bash
# Copy จาก template
cp .env.example .env

# Windows
copy .env.example .env
```

### 3. แก้ไขไฟล์ .env

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=Duplicate_word
```

### 4. Initialize Database

```bash
python scripts/database/create_database.py --yes
```

## 📝 ตรวจสอบการติดตั้ง

```bash
# ตรวจสอบว่า virtual environment ทำงาน
python --version

# ตรวจสอบ libraries
python -c "import flask; import pythainlp; import pandas; print('OK')"
```

## 🎯 ใช้งาน

```bash
# Activate virtual environment ก่อน
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate

# รันแอปพลิเคชัน
python app.py
```

เปิดเบราว์เซอร์ที่: `http://localhost:5000`

## 🛠️ Troubleshooting

### ปัญหา: "python: command not found"

**แก้ไข:**
- Windows: ตรวจสอบว่า Python ถูกเพิ่มใน PATH
- Linux/Mac: ใช้ `python3` แทน `python`

### ปัญหา: "pip: command not found"

**แก้ไข:**
```bash
python -m ensurepip --upgrade
python -m pip install --upgrade pip
```

### ปัญหา: "ModuleNotFoundError"

**แก้ไข:**
```bash
# ตรวจสอบว่า virtual environment ถูก activate แล้ว
# ตรวจสอบว่า libraries ถูกติดตั้งแล้ว
pip list

# ติดตั้งใหม่
pip install -r requirements.txt
```

### ปัญหา: Virtual Environment ไม่ทำงาน

**แก้ไข:**
```bash
# ลบ virtual environment เก่า
rm -rf .venv  # Linux/Mac
rmdir /s .venv  # Windows

# สร้างใหม่
python -m venv .venv

# Activate และติดตั้งใหม่
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
```

## 📚 เอกสารเพิ่มเติม

- `DATABASE_SETUP.md` - คู่มือการตั้งค่า Database
- `README_DATABASE.md` - ข้อมูลเกี่ยวกับ Database
- `requirements.txt` - รายการ dependencies ทั้งหมด

