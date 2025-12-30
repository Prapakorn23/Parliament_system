# โครงสร้างโปรเจค (Project Structure)

## 📁 โครงสร้างโฟลเดอร์

```
duplicate-word-detector/
├── 📱 app.py                       # Flask Backend (main entry point)
├── 📄 requirements.txt             # Python dependencies
├── 📖 README.md                    # คู่มือหลัก
├── 🚀 QUICK_START.md              # เริ่มใช้งานด่วน
├── 🗄️ database/                   # Database files
│   └── schema.sql                 # Database schema
│
├── 🧠 core/                        # Core modules
│   ├── __init__.py
│   ├── duplicate_word_detector.py  # ตัววิเคราะห์คำ
│   ├── word_categorizer.py         # ระบบจัดหมวดหมู่
│   ├── pdf_processor.py            # ประมวลผล PDF/OCR
│   ├── doc_processor.py            # ประมวลผล Word Documents
│   ├── database.py                 # Database operations (MariaDB)
│   └── performance_utils.py        # Performance tracking
│
├── ⚙️ config/                      # Configuration
│   ├── __init__.py
│   └── config.py                   # ไฟล์การตั้งค่า
│
├── 🌐 templates/                   # HTML templates
│   └── dashboard.html              # Frontend UI
│
├── 🎨 static/                      # Static files
│   ├── style.css                   # Styles
│   ├── script.js                   # JavaScript
│   └── *.png                       # Charts (auto-generated, gitignored)
│
├── 📚 docs/                        # Documentation
│   ├── INDEX.md                    # สารบัญเอกสาร
│   ├── INSTALL.md                  # คู่มือการติดตั้ง
│   ├── DATABASE_SETUP.md           # คู่มือการตั้งค่า Database
│   ├── README_DATABASE.md          # ข้อมูลเกี่ยวกับ Database
│   ├── PDF_OCR_SETUP_GUIDE.md     # คู่มือ PDF/OCR
│   ├── FOLDER_ORGANIZATION.md      # โครงสร้างโปรเจคเดิม
│   └── ... (more docs)
│
├── 🔧 scripts/                     # Installation & utility scripts
│   ├── install_windows.bat         # Windows installer
│   ├── install_linux_mac.sh        # Linux/Mac installer
│   ├── database/                   # Database scripts
│   │   ├── create_database.py      # Database creation (รองรับ --drop flag)
│   │   └── verify_database.py     # Verify database
│   ├── tests/                      # Test scripts
│   │   ├── test_db_connection.py  # Test database connection
│   │   └── test_date_extractor.py  # Test date extractor
│   └── migrations/                 # Migration scripts
│       ├── add_file_fields.py      # Add file fields
│       └── alter_file_type_column.py # Alter file type column
│
├── 📤 uploads/                     # Temp uploads (gitignored, auto-created)
├── 💾 cache/                       # Cache files (gitignored, auto-created)
└── 🗄️ data/                        # Database files (gitignored, auto-created)
```

## 📝 ไฟล์สำคัญ

### Backend
- **app.py** - Flask application และ API endpoints
- **core/** - Business logic และ core modules

### Configuration
- **config/config.py** - Application settings
- **.env** - Environment variables (create from .env.example)
- **database/schema.sql** - Database schema

### Frontend
- **templates/dashboard.html** - Main UI
- **static/** - CSS, JS, และ generated files

### Documentation
- **README.md** - คู่มือหลัก
- **docs/** - เอกสารเพิ่มเติมทั้งหมด

## 🗑️ ไฟล์ที่ไม่ควร commit

ไฟล์เหล่านี้ถูก ignore ใน `.gitignore`:

- `venv/` หรือ `.venv/` - Virtual environment
- `__pycache__/` - Python cache
- `*.pyc`, `*.pyo` - Compiled Python files
- `uploads/` - Uploaded files (temporary)
- `cache/` - Cache files
- `static/*.png`, `static/*.jpg` - Generated charts
- `.env` - Environment variables
- `*.db`, `*.sqlite` - Database files
- `*.log` - Log files

## 📦 Dependencies

ดูรายการทั้งหมดใน `requirements.txt`

## 🔄 การใช้งาน

1. ติดตั้ง: `pip install -r requirements.txt`
2. ตั้งค่า: Copy `.env.example` เป็น `.env` และแก้ไข
3. Create DB: `python scripts/database/create_database.py --yes`
4. รัน: `python app.py`

