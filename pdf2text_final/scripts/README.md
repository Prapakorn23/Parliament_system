# 🔧 Scripts

โฟลเดอร์นี้รวมสคริปต์สำหรับการจัดการและติดตั้งระบบ

## 📂 โครงสร้างโฟลเดอร์

### `/migrations` - Database Migrations
สคริปต์สำหรับอัพเดทโครงสร้างฐานข้อมูล

- `migrate_database.py` - สร้างฐานข้อมูลเริ่มต้น
- `migrate_add_pages.py` - เพิ่มฟีเจอร์แสดงผลทีละหน้า

#### การใช้งาน:
```bash
# สร้างฐานข้อมูลใหม่
python scripts/migrations/migrate_database.py

# อัพเดทเพิ่ม PageRecord
python scripts/migrations/migrate_add_pages.py
```

### `/setup` - Setup Scripts
สคริปต์สำหรับติดตั้งและรันระบบ

- `install_thai_tesseract.bat` - ติดตั้ง Thai language สำหรับ Tesseract OCR
- `run_typhoon_api.py` - รัน Typhoon API server สำหรับ summarization
- `run_typhoon_api.bat` - รัน Typhoon API (Windows batch file)

#### การใช้งาน:
```bash
# ติดตั้ง Thai language สำหรับ Tesseract (Windows)
scripts\setup\install_thai_tesseract.bat

# รัน Typhoon API server
python scripts/setup/run_typhoon_api.py
# หรือ
scripts\setup\run_typhoon_api.bat
```

## ⚠️ สำคัญ

- รัน migration scripts จากโฟลเดอร์ root ของโปรเจค
- ตรวจสอบว่ามีไฟล์ `.env` ก่อนรัน scripts
- Backup ฐานข้อมูลก่อนรัน migration scripts

## 🔗 Quick Links

- [README หลัก](../README.md)
- [Database Migration Guide](../docs/guides/DATABASE_MIGRATION.md)

