# Database Scripts

โฟลเดอร์นี้เก็บ scripts ที่เกี่ยวข้องกับการจัดการ database

## ไฟล์ในโฟลเดอร์นี้

- **`create_database.py`** - สร้าง database และตารางทั้งหมดจาก schema.sql (จะลบ database เก่าก่อนสร้างใหม่อัตโนมัติ)
- **`verify_database.py`** - ตรวจสอบสถานะและโครงสร้างของ database

## การใช้งาน

```bash
# สร้าง database (จะลบ database เก่าก่อนสร้างใหม่)
python scripts/database/create_database.py --yes

# หรือไม่ใช้ --yes เพื่อให้ถามยืนยันก่อน
python scripts/database/create_database.py

# ตรวจสอบ database
python scripts/database/verify_database.py
```

## คำเตือน

⚠️ **`create_database.py` จะลบ database เก่าก่อนสร้างใหม่**  
หากต้องการเก็บข้อมูลเดิมไว้ โปรดสำรองข้อมูลก่อนรัน script นี้

## หมายเหตุ

- `create_database.py` มีฟังก์ชัน `drop_database()` อยู่ภายใน ซึ่งจะถูกเรียกใช้ก่อนสร้าง database ใหม่
- สำหรับการลบข้อมูลทั้งหมดใน database แต่คงโครงสร้างตารางไว้ สามารถใช้ SQL command ต่อไปนี้:
  ```sql
  TRUNCATE TABLE category_words;
  TRUNCATE TABLE word_frequencies;
  TRUNCATE TABLE categories;
  TRUNCATE TABLE analyses;
  ```

