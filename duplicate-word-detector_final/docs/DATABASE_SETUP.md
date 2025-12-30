# คู่มือการติดตั้งและตั้งค่าฐานข้อมูล MariaDB

## 📋 สิ่งที่ต้องการ

- MariaDB หรือ MySQL Server (10.3+)
- Python 3.8+
- PyMySQL (จะติดตั้งอัตโนมัติจาก requirements.txt)

## 🚀 ขั้นตอนการติดตั้ง

### 1. ติดตั้ง MariaDB/MySQL

#### Windows:
```bash
# ดาวน์โหลดและติดตั้งจาก
https://mariadb.org/download/
```

#### macOS:
```bash
brew install mariadb
brew services start mariadb
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install mariadb-server
sudo systemctl start mariadb
sudo systemctl enable mariadb
```

### 2. สร้าง Database

```sql
-- เข้าใช้งาน MariaDB/MySQL
mysql -u root -p

-- สร้าง database
CREATE DATABASE IF NOT EXISTS `Duplicate_word` 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- สร้าง user (optional - ถ้าต้องการแยก user)
CREATE USER 'parliament_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON `Duplicate_word`.* TO 'parliament_user'@'localhost';
FLUSH PRIVILEGES;

EXIT;
```

### 3. ตั้งค่าไฟล์ .env

```bash
# Copy ไฟล์ .env.example เป็น .env
cp .env.example .env

# แก้ไขไฟล์ .env
# Windows: notepad .env
# Linux/Mac: nano .env
```

แก้ไขค่าต่อไปนี้ในไฟล์ `.env`:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root              # หรือ parliament_user ถ้าสร้าง user แยก
DB_PASSWORD=your_password # ใส่รหัสผ่านของคุณ
DB_NAME=Duplicate_word
```

### 4. ติดตั้ง Python Dependencies

```bash
# ติดตั้ง dependencies ใหม่ (รวม PyMySQL)
pip install -r requirements.txt
```

### 5. สร้างตารางใน Database

#### วิธีที่ 1: ใช้ Python script
```python
from core.database import DatabaseManager

db = DatabaseManager()
db.execute_schema('database/schema.sql')  # หรือจะสร้างอัตโนมัติ
```

#### วิธีที่ 2: รัน SQL file โดยตรง
```bash
mysql -u root -p Duplicate_word < database/schema.sql
```

#### วิธีที่ 3: สร้างอัตโนมัติ (แนะนำ)
```python
from core.database import get_db_manager

db = get_db_manager()  # จะสร้างตารางอัตโนมัติถ้ายังไม่มี
```

## 🧪 ทดสอบการเชื่อมต่อ

```python
# test_connection.py
from core.database import get_db_manager

try:
    db = get_db_manager()
    stats = db.get_statistics()
    print("✅ เชื่อมต่อฐานข้อมูลสำเร็จ!")
    print(f"สถิติ: {stats}")
except Exception as e:
    print(f"❌ เกิดข้อผิดพลาด: {e}")
```

## 📊 โครงสร้าง Database

### ตารางหลัก:

1. **analyses** - เก็บประวัติการวิเคราะห์
2. **word_frequencies** - เก็บความถี่ของคำ
3. **categories** - เก็บหมวดหมู่คำ
4. **category_words** - เก็บคำในแต่ละหมวดหมู่
5. **pos_frequencies** - เก็บความถี่ของ POS tags
6. **charts** - เก็บข้อมูลกราฟ
7. **analysis_settings** - เก็บการตั้งค่าการวิเคราะห์

## 🔧 การใช้งาน

### ตัวอย่าง: บันทึกการวิเคราะห์

```python
from core.database import get_db_manager

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
word_freq = {'คำ1': 10, 'คำ2': 5, 'คำ3': 3}
pos_tags = {'คำ1': 'NCMN', 'คำ2': 'VACT'}
db.save_word_frequencies(analysis_id, word_freq, pos_tags)

# บันทึก categories
categorized = {
    'การศึกษา': {'โรงเรียน': 5, 'ครู': 3},
    'เศรษฐกิจ': {'เงิน': 10}
}
db.save_categories(analysis_id, categorized)

print(f"บันทึกการวิเคราะห์ ID: {analysis_id} สำเร็จ!")
```

### ตัวอย่าง: ดึงข้อมูล

```python
# ดึงรายการการวิเคราะห์ทั้งหมด
analyses = db.list_analyses(limit=10)

# ดึงข้อมูลการวิเคราะห์เฉพาะ
analysis = db.get_analysis(analysis_id=1)

# ดึง word frequencies
word_freq = db.get_word_frequencies(analysis_id=1)

# ดึง categories
categories = db.get_categories(analysis_id=1)
```

## 🛠️ Troubleshooting

### ปัญหา: "Access denied for user"

**แก้ไข:**
1. ตรวจสอบ username และ password ในไฟล์ `.env`
2. ตรวจสอบว่า user มีสิทธิ์เข้าถึง database:
   ```sql
   SHOW GRANTS FOR 'your_user'@'localhost';
   ```

### ปัญหา: "Unknown database 'Duplicate_word'"

**แก้ไข:**
```sql
CREATE DATABASE `Duplicate_word` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### ปัญหา: "Can't connect to MySQL server"

**แก้ไข:**
1. ตรวจสอบว่า MariaDB/MySQL service กำลังทำงาน:
   ```bash
   # Windows
   net start MySQL
   
   # Linux/Mac
   sudo systemctl status mariadb
   sudo systemctl start mariadb
   ```

2. ตรวจสอบ host และ port ในไฟล์ `.env`

### ปัญหา: Character encoding ผิดพลาด

**แก้ไข:**
ตรวจสอบว่า database ใช้ charset `utf8mb4`:
```sql
SHOW CREATE DATABASE `Duplicate_word`;
-- ต้องเป็น: CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
```

## 📝 หมายเหตุ

- ไฟล์ `.env` ไม่ควรถูก commit เข้า git (อยู่ใน .gitignore)
- ใช้ไฟล์ `.env.example` เป็น template
- สำหรับ production ควรใช้ user แยกและตั้งรหัสผ่านที่แข็งแรง
- แนะนำให้ทำ backup ฐานข้อมูลเป็นประจำ

## 🔐 Security Tips

1. **อย่าใช้ root user ใน production**
   ```sql
   CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'strong_password';
   GRANT SELECT, INSERT, UPDATE, DELETE ON `Duplicate_word`.* TO 'app_user'@'localhost';
   ```

2. **ตั้งรหัสผ่านที่แข็งแรง**
   - ใช้รหัสผ่านที่ยาวและซับซ้อน
   - เปลี่ยนรหัสผ่านเป็นระยะ

3. **Backup ข้อมูลเป็นประจำ**
   ```bash
   mysqldump -u root -p Duplicate_word > backup_$(date +%Y%m%d).sql
   ```

