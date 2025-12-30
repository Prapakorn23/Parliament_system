# 🗄️ Database Setup Guide

## 📦 ไฟล์ที่สร้างไว้แล้ว

1. **`database/schema.sql`** - SQL schema สำหรับสร้างตารางทั้งหมด
2. **`.env.example`** - Template สำหรับไฟล์ .env
3. **`core/database.py`** - Python module สำหรับจัดการ database
4. **`scripts/database/create_database.py`** - Script สำหรับสร้าง database
5. **`DATABASE_SETUP.md`** - คู่มือการติดตั้งแบบละเอียด

## 🚀 Quick Start

### ขั้นตอนที่ 1: สร้างไฟล์ .env

```bash
# Copy ไฟล์ .env.example เป็น .env
cp .env.example .env

# Windows
copy .env.example .env
```

### ขั้นตอนที่ 2: แก้ไขไฟล์ .env

เปิดไฟล์ `.env` และแก้ไขค่าต่อไปนี้:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password_here    # ← แก้ไขตรงนี้
DB_NAME=Duplicate_word
```

### ขั้นตอนที่ 3: สร้าง Database

```bash
# เข้าใช้งาน MariaDB/MySQL
mysql -u root -p

# สร้าง database
CREATE DATABASE IF NOT EXISTS `Duplicate_word` 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### ขั้นตอนที่ 4: ติดตั้ง Dependencies

```bash
pip install -r requirements.txt
```

### ขั้นตอนที่ 5: Initialize Database

```bash
# วิธีที่ 1: ใช้ Python script
python scripts/database/create_database.py --yes

# วิธีที่ 2: รัน SQL file โดยตรง
mysql -u root -p Duplicate_word < database/schema.sql

# วิธีที่ 3: ใช้ Python (จะสร้างอัตโนมัติ)
python -c "from core.database import get_db_manager; get_db_manager()"
```

## 📝 ตัวอย่างการใช้งาน

```python
from core.database import get_db_manager

# Get database manager
db = get_db_manager()

# สร้างการวิเคราะห์ใหม่
analysis_id = db.create_analysis({
    'title': 'การวิเคราะห์รายงานการประชุม',
    'source_type': 'file',
    'file_name': 'report.pdf',
    'file_type': 'pdf',
    'total_words': 1500,
    'unique_words': 300,
    'processing_time': 2.5
})

# บันทึก word frequencies
word_freq = {'คำ1': 10, 'คำ2': 5}
pos_tags = {'คำ1': 'NCMN', 'คำ2': 'VACT'}
db.save_word_frequencies(analysis_id, word_freq, pos_tags)

# บันทึก categories
categorized = {
    'การศึกษา': {'โรงเรียน': 5, 'ครู': 3},
    'เศรษฐกิจ': {'เงิน': 10}
}
db.save_categories(analysis_id, categorized)

# ดึงข้อมูล
analysis = db.get_analysis(analysis_id)
analyses = db.list_analyses(limit=10)
stats = db.get_statistics()
```

## 🔧 Database Schema

### ตารางหลัก:

- **analyses** - ประวัติการวิเคราะห์
- **word_frequencies** - ความถี่ของคำ
- **categories** - หมวดหมู่คำ
- **category_words** - คำในแต่ละหมวดหมู่
- **pos_frequencies** - ความถี่ของ POS tags
- **charts** - ข้อมูลกราฟ
- **analysis_settings** - การตั้งค่าการวิเคราะห์

ดูรายละเอียดใน `database/schema.sql`

## ❓ Troubleshooting

ดูรายละเอียดเพิ่มเติมใน `DATABASE_SETUP.md`

## 📚 เอกสารเพิ่มเติม

- `DATABASE_SETUP.md` - คู่มือการติดตั้งแบบละเอียด
- `database/schema.sql` - SQL schema สำหรับตารางทั้งหมด

