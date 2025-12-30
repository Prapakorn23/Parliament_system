# Database API Documentation

## 📋 สารบัญ

- [ภาพรวม](#ภาพรวม)
- [การเชื่อมต่อฐานข้อมูล](#การเชื่อมต่อฐานข้อมูล)
- [API Endpoints](#api-endpoints)
- [ตัวอย่างการใช้งาน](#ตัวอย่างการใช้งาน)

## ภาพรวม

ระบบนี้ใช้ **MySQL/MariaDB** เป็นฐานข้อมูล โดยเก็บข้อมูล:
- **Extraction Records**: ประวัติการแปลงไฟล์
- **Summary Records**: ประวัติการสรุปข้อความ

## การเชื่อมต่อฐานข้อมูล

### ข้อกำหนดเบื้องต้น

1. **ติดตั้ง Database Driver (PyMySQL)**
   ```bash
   pip install PyMySQL
   ```
   หรือติดตั้งทุกอย่างจาก requirements.txt:
   ```bash
   pip install -r requirements.txt
   ```

2. **สร้างฐานข้อมูลบน MySQL/MariaDB**
   - สร้างฐานข้อมูลชื่อ `pdf2text` (หรือชื่อที่ต้องการ)
   - ใช้ Character Set: `utf8mb4` และ Collation: `utf8mb4_unicode_ci`

3. **ตั้งค่า DATABASE_URL**

   สร้างไฟล์ `.env` ในโฟลเดอร์ root ของโปรเจกต์ (ระดับเดียวกับ `app.py`):
   
   ```env
   # Database Configuration
   # Format: mysql+pymysql://username:password@host:port/database_name
   
   # สำหรับ Laragon (MariaDB) - password ว่างเปล่า
   DATABASE_URL=mysql+pymysql://root:@localhost:3306/pdf2text
   
   # สำหรับ Laragon (MariaDB) - ถ้ามี password
   # DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/pdf2text
   
   # สำหรับ MySQL มาตรฐาน (port 3306)
   # DATABASE_URL=mysql+pymysql://root:root@localhost:3306/pdf2text
   
   # สำหรับ MAMP (default port 8889)
   # DATABASE_URL=mysql+pymysql://root:root@localhost:8889/pdf2text
   
   # Optional: Enable SQL query logging (สำหรับ debugging)
   # SQLALCHEMY_ECHO=True
   ```

   หรือตั้งค่าเป็น environment variable ใน PowerShell:
   ```powershell
   # Laragon (MariaDB)
   $env:DATABASE_URL="mysql+pymysql://root:@localhost:3306/pdf2text"
   ```

4. **รันแอปพลิเคชัน**
   ```bash
   python app.py
   ```
   
   ระบบจะ:
   - อ่าน `DATABASE_URL` จากไฟล์ `.env` หรือ environment variable
   - เชื่อมต่อ MySQL/MariaDB
   - สร้างตารางอัตโนมัติ (`extraction_records` และ `summary_records`)

### ตัวอย่าง DATABASE_URL

```bash
# Laragon (MariaDB) - password ว่างเปล่า
DATABASE_URL=mysql+pymysql://root:@localhost:3306/pdf2text

# Laragon (MariaDB) - ถ้ามี password
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/pdf2text

# MySQL (localhost, port 3306)
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/pdf2text

# MySQL (MAMP, port 8889)
DATABASE_URL=mysql+pymysql://root:root@localhost:8889/pdf2text

# MySQL/MariaDB (remote server)
DATABASE_URL=mysql+pymysql://user:password@example.com:3306/pdf2text
```

## API Endpoints

### Base URL
```
http://localhost:5000/api
```

---

### 1. Health Check

ตรวจสอบสถานะการเชื่อมต่อฐานข้อมูล

**Endpoint**: `GET /api/health`

**Response (200 OK)**:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

**Response (503 Service Unavailable)**:
```json
{
  "status": "unhealthy",
  "database": "disconnected",
  "error": "error message",
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

---

### 2. ดึงข้อมูล Extraction Records

**Endpoint**: `GET /api/extractions`

**Query Parameters**:
- `page` (int, optional): หน้าที่ต้องการ (default: 1)
- `per_page` (int, optional): จำนวนรายการต่อหน้า (default: 20, max: 100)

**Example**:
```bash
curl http://localhost:5000/api/extractions?page=1&per_page=20
```

**Response (200 OK)**:
```json
{
  "extractions": [
    {
      "id": 1,
      "filename": "document.pdf",
      "file_type": "pdf",
      "file_size": 1024000,
      "extracted_text_length": 50000,
      "ocr_used": false,
      "ip_address": "127.0.0.1",
      "user_agent": "Mozilla/5.0...",
      "created_at": "2024-01-01T12:00:00.000000",
      "summary_count": 2
    }
  ],
  "total": 100,
  "page": 1,
  "per_page": 20,
  "pages": 5
}
```

---

### 3. ดึงข้อมูล Extraction Record แบบระบุ ID

**Endpoint**: `GET /api/extractions/<extraction_id>`

**Example**:
```bash
curl http://localhost:5000/api/extractions/1
```

**Response (200 OK)**:
```json
{
  "id": 1,
  "filename": "document.pdf",
  "file_type": "pdf",
  "file_size": 1024000,
  "extracted_text_length": 50000,
  "ocr_used": false,
  "ip_address": "127.0.0.1",
  "user_agent": "Mozilla/5.0...",
  "created_at": "2024-01-01T12:00:00.000000",
  "summary_count": 2
}
```

**Response (404 Not Found)**:
```json
{
  "error": "404 Not Found"
}
```

---

### 4. ลบ Extraction Record

**Endpoint**: `DELETE /api/extractions/<extraction_id>`

**Example**:
```bash
curl -X DELETE http://localhost:5000/api/extractions/1
```

**Response (200 OK)**:
```json
{
  "message": "ลบข้อมูลสำเร็จ",
  "id": 1
}
```

---

### 5. ดึงข้อมูล Summary Records

**Endpoint**: `GET /api/summaries`

**Query Parameters**:
- `page` (int, optional): หน้าที่ต้องการ (default: 1)
- `per_page` (int, optional): จำนวนรายการต่อหน้า (default: 20, max: 100)
- `extraction_id` (int, optional): กรองตาม extraction_id

**Example**:
```bash
curl http://localhost:5000/api/summaries?page=1&per_page=20
curl http://localhost:5000/api/summaries?extraction_id=1
```

**Response (200 OK)**:
```json
{
  "summaries": [
    {
      "id": 1,
      "extraction_id": 1,
      "original_text_length": 50000,
      "summary_length": 5000,
      "compression_ratio": 90.0,
      "processing_time": 2.5,
      "language": "th",
      "provider": "typhoon",
      "ip_address": "127.0.0.1",
      "user_agent": "Mozilla/5.0...",
      "created_at": "2024-01-01T12:00:00.000000"
    }
  ],
  "total": 50,
  "page": 1,
  "per_page": 20,
  "pages": 3
}
```

---

### 6. ดึงข้อมูล Summary Record แบบระบุ ID

**Endpoint**: `GET /api/summaries/<summary_id>`

**Example**:
```bash
curl http://localhost:5000/api/summaries/1
```

**Response (200 OK)**:
```json
{
  "id": 1,
  "extraction_id": 1,
  "original_text_length": 50000,
  "summary_length": 5000,
  "compression_ratio": 90.0,
  "processing_time": 2.5,
  "language": "th",
  "provider": "typhoon",
  "ip_address": "127.0.0.1",
  "user_agent": "Mozilla/5.0...",
  "created_at": "2024-01-01T12:00:00.000000"
}
```

---

### 7. ลบ Summary Record

**Endpoint**: `DELETE /api/summaries/<summary_id>`

**Example**:
```bash
curl -X DELETE http://localhost:5000/api/summaries/1
```

**Response (200 OK)**:
```json
{
  "message": "ลบข้อมูลสำเร็จ",
  "id": 1
}
```

---

### 8. สถิติระบบ

**Endpoint**: `GET /api/stats`

**Example**:
```bash
curl http://localhost:5000/api/stats
```

**Response (200 OK)**:
```json
{
  "total_extractions": 100,
  "total_summaries": 150,
  "total_files_size": 104857600,
  "total_text_length": 5000000,
  "recent_extractions_24h": 10,
  "recent_summaries_24h": 15,
  "file_type_distribution": {
    "pdf": 60,
    "docx": 30,
    "txt": 10
  }
}
```

---

## ตัวอย่างการใช้งาน

### Python

```python
import requests

BASE_URL = "http://localhost:5000/api"

# ตรวจสอบสถานะ
response = requests.get(f"{BASE_URL}/health")
print(response.json())

# ดึงข้อมูล extractions
response = requests.get(f"{BASE_URL}/extractions", params={"page": 1, "per_page": 20})
extractions = response.json()
print(f"Total: {extractions['total']}")

# ดึงข้อมูล summaries
response = requests.get(f"{BASE_URL}/summaries", params={"extraction_id": 1})
summaries = response.json()

# ดึงสถิติ
response = requests.get(f"{BASE_URL}/stats")
stats = response.json()
print(f"Total extractions: {stats['total_extractions']}")
```

### JavaScript (Fetch API)

```javascript
const BASE_URL = 'http://localhost:5000/api';

// ตรวจสอบสถานะ
fetch(`${BASE_URL}/health`)
  .then(res => res.json())
  .then(data => console.log(data));

// ดึงข้อมูล extractions
fetch(`${BASE_URL}/extractions?page=1&per_page=20`)
  .then(res => res.json())
  .then(data => console.log(data));

// ดึงสถิติ
fetch(`${BASE_URL}/stats`)
  .then(res => res.json())
  .then(data => console.log(data));
```

### cURL

```bash
# Health check
curl http://localhost:5000/api/health

# ดึง extractions
curl http://localhost:5000/api/extractions?page=1&per_page=20

# ดึง summaries
curl http://localhost:5000/api/summaries?extraction_id=1

# ลบ extraction
curl -X DELETE http://localhost:5000/api/extractions/1

# ดึงสถิติ
curl http://localhost:5000/api/stats
```

---

## หมายเหตุ

- ระบบจะบันทึกข้อมูลการแปลงไฟล์และการสรุปอัตโนมัติเมื่อมีการใช้งาน
- การลบ extraction record จะลบ summaries ที่เกี่ยวข้องด้วย (cascade delete)
- ทุก endpoint รองรับ CORS และส่งคืน JSON

