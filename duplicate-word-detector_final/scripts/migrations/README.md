# Migration Scripts

โฟลเดอร์นี้เก็บ scripts สำหรับ migrate database schema

## ไฟล์ในโฟลเดอร์นี้

- **`add_file_fields.py`** - เพิ่มฟิลด์ `original_file_path`, `file_size`, `file_content` ในตาราง `analyses`
- **`alter_file_type_column.py`** - แก้ไขขนาด column `file_type` จาก VARCHAR(10) เป็น VARCHAR(50)

## หมายเหตุ

Scripts เหล่านี้ใช้สำหรับ database ที่มีอยู่แล้วที่ยังไม่ได้ migrate  
สำหรับ database ใหม่ ให้ใช้ `scripts/database/create_database.py` ซึ่งจะสร้าง schema ที่สมบูรณ์แล้ว

## การใช้งาน

```bash
# เพิ่มฟิลด์ไฟล์
python scripts/migrations/add_file_fields.py

# แก้ไขขนาด column
python scripts/migrations/alter_file_type_column.py
```

