# PDF to Text Converter & AI Summarizer

เว็บแอปพลิเคชันแปลงไฟล์ PDF, DOCX, TXT และรูปภาพเป็นข้อความ พร้อมระบบสรุปเนื้อหาด้วย AI และการค้นหาข้อมูลที่บันทึกไว้

## ✨ คุณสมบัติหลัก

- 📄 **แปลงไฟล์หลายรูปแบบ**: PDF, DOCX, TXT → ข้อความล้วน
- 📑 **แสดงทีละหน้า**: ดูข้อความ PDF แยกทีละหน้า พร้อม Navigation
- 🖼️ **แปลงรูปภาพด้วย OCR**: JPG, PNG, GIF, BMP, TIFF → ข้อความด้วย Tesseract OCR
- 🔍 **OCR อัตโนมัติ**: รองรับไฟล์สแกนและรูปภาพ พร้อมแก้ไขช่องว่างอัตโนมัติ
- 🤖 **สรุป AI**: ใช้ SCB10X/typhoon-7b model ผ่าน FastAPI
- 🔎 **ค้นหาไฟล์**: ค้นหาจากชื่อไฟล์, เนื้อหา, หรือ tags
- 💾 **บันทึกข้อมูล**: เก็บประวัติการแปลงไฟล์ในฐานข้อมูล
- 🌏 **รองรับภาษา**: ภาษาไทยและอังกฤษ
- 📥 **ดาวน์โหลด**: บันทึกผลลัพธ์เป็นไฟล์ .txt

## 🚀 วิธีติดตั้งและใช้งาน

### ความต้องการของระบบ

- Python 3.8 หรือสูงกว่า
- Poppler (สำหรับแปลง PDF เป็นรูปภาพ)
- Tesseract OCR (สำหรับแปลงรูปภาพเป็นข้อความ)
- MySQL/MariaDB หรือ SQLite (สำหรับเก็บข้อมูล)

### ขั้นตอนที่ 1: ติดตั้งโปรแกรม

```powershell
# เปิด PowerShell ในโฟลเดอร์โปรเจกต์
cd <path-to-project>

# สร้างและเปิดใช้งาน virtual environment
python -m venv .venv
. .venv\Scripts\Activate.ps1

# ติดตั้งแพ็กเกจที่จำเป็น
pip install --upgrade pip
pip install -r requirements.txt
```

### ขั้นตอนที่ 2: ตั้งค่าฐานข้อมูล

#### ตัวเลือก A: SQLite (แนะนำสำหรับการทดสอบ)

ไม่ต้องตั้งค่าอะไร - ระบบจะสร้างไฟล์ `pdf2text.db` อัตโนมัติในโฟลเดอร์ `instance/`

#### ตัวเลือก B: MySQL/MariaDB (แนะนำสำหรับ Production)

1. **สร้างฐานข้อมูล**
   ```sql
   CREATE DATABASE pdf2text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

2. **ตั้งค่า DATABASE_URL**
   
   สร้างไฟล์ `.env` ในโฟลเดอร์ root ของโปรเจกต์ (คัดลอกจาก `env.example`):
   
   ```env
   # สำหรับ Laragon (MariaDB) - password ว่างเปล่า
   DATABASE_URL=mysql+pymysql://root:@localhost:3306/pdf2text
   
   # สำหรับ Laragon (MariaDB) - ถ้ามี password
   # DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/pdf2text
   
   # สำหรับ MySQL มาตรฐาน (port 3306)
   # DATABASE_URL=mysql+pymysql://root:root@localhost:3306/pdf2text
   
   # สำหรับ MAMP (default port 8889)
   # DATABASE_URL=mysql+pymysql://root:root@localhost:8889/pdf2text
   ```

3. **รัน Database Migration**
   ```powershell
   # สร้างตารางเริ่มต้น
   python database/init_database.py
   
   # หรือใช้ migration script
   python database/migrate_database.py
   ```

### ขั้นตอนที่ 3: ติดตั้ง Poppler (สำหรับ OCR)

**Windows:**
- ดาวน์โหลด: [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/)
- แตกไฟล์ไปที่: `C:\Program Files\poppler`
- หรือระบุใน `.env`: `POPPLER_PATH=C:\Program Files\poppler\Library\bin`
- **ดูคู่มือเต็ม**: [QUICK_SETUP_POPPLER.md](docs/setup/QUICK_SETUP_POPPLER.md)

**macOS:**
```bash
brew install poppler
```

**Ubuntu/Debian:**
```bash
sudo apt-get install poppler-utils
```

**ทดสอบ:**
```bash
pdfinfo -v
```

### ขั้นตอนที่ 4: ติดตั้ง Tesseract OCR

**Windows:**
- ดาวน์โหลด: [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
- ติดตั้งและเลือกภาษา **Thai** + **English**
- หรือระบุใน `.env`: `TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe`
- **ดูคู่มือเต็ม**: [QUICK_SETUP_TESSERACT.md](docs/setup/QUICK_SETUP_TESSERACT.md)

**macOS:**
```bash
brew install tesseract tesseract-lang
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-tha
```

**ทดสอบ:**
```bash
tesseract --version
tesseract --list-langs  # ต้องมี 'tha' และ 'eng'
```

### ขั้นตอนที่ 5: รัน Typhoon API Service (Optional)

```powershell
# รัน Typhoon API service (ใน terminal แรก)
python scripts/setup/run_typhoon_api.py
```

หรือใช้ batch script:
```powershell
scripts\setup\run_typhoon_api.bat
```

**หมายเหตุ**: ถ้าไม่รัน Typhoon API ระบบจะใช้โมเดลสรุปภายในเครื่องแทน

### ขั้นตอนที่ 6: รัน Flask App

```powershell
# รัน Flask app (ใน terminal ที่สอง)
python app.py
```

เปิดเบราว์เซอร์ไปที่: `http://localhost:5000`

## 🎯 วิธีใช้งาน

### 1. อัปโหลดและแปลงไฟล์

- คลิก "เลือกไฟล์" → เลือกไฟล์ PDF, DOCX, TXT หรือรูปภาพ
- กด "แปลงไฟล์เป็นข้อความ"
- ระบบจะแปลงและแก้ไขช่องว่างอัตโนมัติ
- ข้อมูลจะถูกบันทึกในฐานข้อมูลอัตโนมัติ

### 2. ดูข้อความ (PDF หลายหน้า)

- **ดูทุกหน้า**: ดูข้อความรวมกันทั้งหมด (ค่าเริ่มต้น)
- **ดูทีละหน้า**: คลิก "ดูทีละหน้า" → ใช้ปุ่มหรือลูกศรคีย์บอร์ดเปลี่ยนหน้า
- กรอกหมายเลขหน้าเพื่อข้ามไปหน้าที่ต้องการ

### 3. สรุปข้อความ

- กด "สรุปข้อความ"
- ระบบจะสรุปด้วย AI อัตโนมัติ
- รองรับข้อความยาว (แบ่งเป็นส่วนๆ อัตโนมัติ)
- สามารถเลือกความยาวของสรุปได้

### 4. ค้นหาไฟล์

- ใช้ช่องค้นหาที่ด้านบน
- ค้นหาจากชื่อไฟล์, เนื้อหา, หรือ tags
- กรองตามประเภทไฟล์และช่วงวันที่
- คลิกผลลัพธ์เพื่อโหลดไฟล์เดิม

### 5. ดาวน์โหลดผลลัพธ์

- กด "ดาวน์โหลด" เพื่อบันทึกข้อความที่แปลงได้
- กด "ดาวน์โหลดสรุป" เพื่อบันทึกสรุป

## 📁 โครงสร้างโปรเจกต์

```
pdf2text29-12-68/
├── 📄 app.py                      # Flask app หลัก
├── 📄 requirements.txt            # รายการแพ็กเกจ Python
├── 📄 env.example                 # ตัวอย่างไฟล์ .env
├── 📄 README.md                   # เอกสารหลัก
│
├── 📚 docs/                       # เอกสารทั้งหมด
│   ├── api/                       # API Documentation
│   │   └── API_DOCUMENTATION.md
│   ├── setup/                     # คู่มือติดตั้ง
│   │   ├── QUICK_SETUP_POPPLER.md
│   │   └── QUICK_SETUP_TESSERACT.md
│   └── SUMMARIZATION_IMPROVEMENTS.md
│
├── 🔧 scripts/                     # สคริปต์ต่างๆ
│   └── setup/                     # Setup scripts
│       ├── install_thai_tesseract.bat
│       ├── run_typhoon_api.py
│       └── run_typhoon_api.bat
│
├── 🔌 apis/                       # API clients
│   ├── typhoon_summarizer_api.py  # FastAPI service สำหรับสรุป
│   └── typhoon_client.py          # Client สำหรับเรียก API
│
├── 💾 database/                   # Database management
│   ├── connection.py              # Database connection
│   ├── init_database.py           # Initialize database
│   ├── migrate_database.py        # Database migration
│   ├── schema.sql                 # Database schema
│   └── README.md                  # Database documentation
│
├── 📄 extractors/                 # Text extraction
│   ├── pdf_text_extractor.py     # PDF extraction + OCR
│   └── file_text_extractor.py    # Multi-format extraction
│
├── 📝 summarizers/                # Text summarization
│   └── text_summarizer.py        # AI summarization logic
│
├── 🎨 static/                     # Frontend assets
│   ├── style.css                 # Styles
│   └── script.js                 # JavaScript
│
└── 📱 templates/                   # HTML templates
    └── index.html                # Main page
```

## 🔧 การแก้ไขปัญหา

### ❌ ปัญหา: Typhoon API ไม่ทำงาน

**สาเหตุ**: API service ไม่ได้รัน

**แก้ไข**:
1. ตรวจสอบว่า Typhoon API service รันอยู่ที่ port 8000
2. ทดสอบ: `curl http://localhost:8000/health`
3. รันใหม่: `python scripts/setup/run_typhoon_api.py`

### ❌ ปัญหา: โมเดลโหลดช้า

**สาเหตุ**: ครั้งแรกจะโหลด model จาก internet (ประมาณ 7B parameters)

**แก้ไข**: รอสักครู่ model จะถูก cache ไว้

### ❌ ปัญหา: OCR ไม่ทำงาน

**OCR ต้องใช้ทั้งคู่:**
1. **Poppler** - แปลง PDF เป็นรูปภาพ
2. **Tesseract** - แปลงรูปภาพเป็นข้อความ

ตรวจสอบว่าติดตั้งทั้งสองโปรแกรมแล้ว และตั้งค่า path ใน `.env` ถูกต้อง

### ❌ ปัญหา: Database connection error

**แก้ไข**:
1. ตรวจสอบว่า DATABASE_URL ใน `.env` ถูกต้อง
2. ตรวจสอบว่า database service รันอยู่
3. ตรวจสอบว่า database ถูกสร้างแล้ว
4. รัน `python database/init_database.py` เพื่อสร้างตาราง

## 🧪 ทดสอบระบบ

### ทดสอบ Typhoon API

```powershell
# ตรวจสอบ health
curl http://localhost:8000/health

# ทดสอบสรุป
curl -X POST "http://localhost:8000/summarize" -H "Content-Type: application/json" -d "{\"text\":\"ทดสอบข้อความภาษาไทย\"}"
```

### ทดสอบโมเดลภายในเครื่อง

```powershell
python -c "from summarizers.text_summarizer import summarize_text; print(summarize_text('ทดสอบข้อความ', lang='th', provider='local'))"
```

### ทดสอบ Database

```powershell
python database/init_database.py
```

## 📋 แพ็กเกจที่ใช้

### หลัก
- `Flask` - เว็บแอปพลิเคชัน
- `FastAPI` - Typhoon API service
- `PyMuPDF` - อ่าน PDF
- `python-docx` - อ่าน DOCX
- `chardet` - ตรวจจับ encoding

### AI/ML
- `transformers` - Typhoon model
- `torch` - PyTorch
- `accelerate` - Model acceleration
- `bitsandbytes` - Memory optimization
- `requests` - HTTP client

### OCR และ Image Processing
- `pytesseract` - Tesseract OCR engine
- `pdf2image` - แปลง PDF เป็นรูป
- `Pillow` - จัดการรูปภาพ
- `opencv-python` - ประมวลผลภาพขั้นสูง

### Database
- `PyMySQL` - MySQL/MariaDB driver
- `Flask-SQLAlchemy` - ORM สำหรับ Flask

### อื่นๆ
- `python-dotenv` - จัดการ environment variables
- `psutil` - ตรวจสอบการใช้ทรัพยากรระบบ
- `gunicorn` - Production WSGI server

## 🔒 ความปลอดภัย

- ตรวจสอบนามสกุลไฟล์ก่อนอัปโหลด
- ไม่แสดงข้อมูลภายในในข้อความ error
- API service รันแยกจาก web app
- ข้อมูลไฟล์ถูกเก็บในฐานข้อมูลอย่างปลอดภัย

## 💡 เคล็ดลับ

1. **ไฟล์สแกน**: OCR ทำงานอัตโนมัติ พร้อมแก้ไขช่องว่างระหว่างตัวอักษร
2. **PDF หลายหน้า**: สลับระหว่าง "ดูทุกหน้า" และ "ดูทีละหน้า" ได้ตามต้องการ
3. **Keyboard Navigation**: ใช้ลูกศรซ้าย/ขวาเปลี่ยนหน้าได้เลย
4. **ภาษาไทย**: ตรวจจับและแก้ไขปัญหาช่องว่างอัตโนมัติ
5. **ข้อความยาว**: สรุปเป็นหลายส่วนอัตโนมัติ
6. **Typhoon Model**: SCB10X/typhoon-7b รองรับภาษาไทยได้ดีเยี่ยม
7. **Database**: เริ่มต้นด้วย SQLite ง่ายๆ แล้วค่อยย้ายไป MySQL/MariaDB ในภายหลัง
8. **การค้นหา**: ใช้ tags เพื่อค้นหาไฟล์ได้ง่ายขึ้น

## 📖 เอกสารเพิ่มเติม

- [📚 All Documentation](docs/)
- [🔌 API Documentation](docs/api/API_DOCUMENTATION.md)
- [💾 Database README](database/README.md)
- [⚙️ Setup Guides](docs/setup/)

## 🆘 สนับสนุน

หากมีปัญหา:
1. ตรวจสอบ error ในคอนโซล
2. อ่านคู่มือใน `docs/` folder
3. ตรวจสอบว่า Typhoon API service รันอยู่ (ถ้าใช้งาน)
4. ทดสอบ API: `curl http://localhost:8000/health`
5. ตรวจสอบว่าติดตั้ง Poppler และ Tesseract แล้ว (สำหรับ OCR)
6. ตรวจสอบไฟล์ `.env` ว่าตั้งค่าถูกต้อง

---

**Data Science Lab** | จัดทำโดย Prapakorn Kanjina
