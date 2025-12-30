# Database Files

โฟลเดอร์นี้เก็บไฟล์ที่เกี่ยวข้องกับ database

## ไฟล์ในโฟลเดอร์นี้

- **`schema.sql`** - SQL schema สำหรับสร้างตารางทั้งหมดใน database

## Schema Structure

Schema นี้ประกอบด้วยตารางหลัก:

- **`analyses`** - ประวัติการวิเคราะห์
- **`word_frequencies`** - ความถี่ของคำ
- **`categories`** - หมวดหมู่คำ
- **`category_words`** - คำในแต่ละหมวดหมู่

## การใช้งาน

```bash
# รัน schema โดยตรง
mysql -u root -p Duplicate_word < database/schema.sql

# หรือใช้ Python script
python scripts/database/create_database.py --yes
```

