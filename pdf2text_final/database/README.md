# Database Schema

สคริปต์สำหรับสร้างฐานข้อมูล MariaDB สำหรับระบบ PDF2Text

## โครงสร้างฐานข้อมูล

### Database: `pdf2text`

#### ตาราง `extraction_records`
เก็บข้อมูลการสกัดข้อความจากไฟล์

**ฟิลด์หลัก:**
- ข้อมูลไฟล์: filename, file_type, file_size, file_hash
- ข้อมูลข้อความที่สกัด: extracted_text_preview, extracted_text_keywords, extracted_text_length
- ข้อมูลหน้าและ OCR: total_pages, ocr_used, ocr_pages
- ข้อมูลเส้นทางไฟล์: original_file_path, extracted_text_path
- ข้อมูลการประมวลผล: processing_time, status, error_message
- Timestamps: created_at, updated_at

#### ตาราง `summary_records`
เก็บข้อมูลการสรุปข้อความ

**ฟิลด์หลัก:**
- Foreign Key: extraction_id (อ้างอิง extraction_records.id)
- ข้อมูลสรุป: summary_preview, summary_keywords
- ข้อมูลความยาว: original_text_length, summary_length, compression_ratio
- ข้อมูลการประมวลผล: processing_time, language, provider, max_length, min_length
- Timestamp: created_at

## วิธีการใช้งาน

### วิธีที่ 1: ใช้ Python Script (แนะนำ)

1. ตั้งค่า environment variable `DATABASE_URL` ในไฟล์ `.env`:
```
DATABASE_URL=mysql+pymysql://user:password@host:port/database
```

2. รันสคริปต์:
```bash
python database/init_database.py
```

### วิธีที่ 2: ใช้ MariaDB Command Line

1. เชื่อมต่อ MariaDB:
```bash
mysql -u root -p
```

2. รัน SQL script:
```bash
mysql -u root -p < database/schema.sql
```

หรือภายใน MariaDB prompt:
```sql
source database/schema.sql;
```

### วิธีที่ 3: ใช้ GUI Tool (เช่น phpMyAdmin, HeidiSQL, DBeaver)

1. เปิดไฟล์ `database/schema.sql`
2. Copy เนื้อหาทั้งหมด
3. Paste และรันใน SQL editor ของ GUI tool

## ตรวจสอบการสร้างฐานข้อมูล

หลังจากรันสคริปต์แล้ว สามารถตรวจสอบได้ด้วยคำสั่ง:

```sql
USE pdf2text;
SHOW TABLES;
DESCRIBE extraction_records;
DESCRIBE summary_records;
```

## Foreign Key Constraints

- `summary_records.extraction_id` → `extraction_records.id`
- ตั้งค่า `ON DELETE CASCADE` และ `ON UPDATE CASCADE`
- เมื่อลบ extraction record จะลบ summary records ที่เกี่ยวข้องอัตโนมัติ

## Indexes

ตารางทั้งสองมี indexes สำหรับเพิ่มประสิทธิภาพการค้นหา:
- `extraction_records`: file_hash, status, created_at, file_type
- `summary_records`: extraction_id, status, created_at, provider

## Character Set

- ใช้ `utf8mb4` สำหรับรองรับอักขระ Unicode ครบถ้วน (รวมถึง emoji)
- Collation: `utf8mb4_unicode_ci`

## Engine

- ใช้ `InnoDB` สำหรับรองรับ Foreign Keys และ Transactions

