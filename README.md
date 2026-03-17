# Parliament Main Dashboard

หน้าเว็บหลัก (Landing/Dashboard Page) สำหรับระบบสนับสนุนการประชุมรัฐสภา

---

## 📋 ภาพรวมโปรเจกต์

โปรเจกต์นี้เป็น Dashboard หลักสำหรับระบบสนับสนุนการประชุมรัฐสภา ซึ่งรวม 3 ระบบย่อยไว้ในที่เดียว:

1. **Main Dashboard** - หน้าหลักแสดงภาพรวม (port 5003)
2. **Document Recommendation System** - ระบบแปลง PDF และ AI สรุป (port 5001)
3. **Trend Analysis** - ระบบตรวจจับคำซ้ำและวิเคราะห์แนวโน้ม (port 5002)

---

## 🎨 UI/UX Design

### Layout Structure

```
┌─────────────────────────────────────────────────────┐
│              HEADER SECTION                          │
│  ┌────────────────┐  ┌──────────────────────────┐  │
│  │ หัวข้อการประชุม │  │ การติดตามการดำเนินนโยบาย │  │
│  └────────────────┘  └──────────────────────────┘  │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────┐    ┌──────────────────────────┐  │
│  │ LEFT COLUMN  │    │      RIGHT COLUMN        │  │
│  │              │    │                          │  │
│  │ ┌──────────┐ │    │ ┌──────────────────────┐ │  │
│  │ │ รายชื่อ  │ │    │ │ Document Recommend.  │ │  │
│  │ │ (20คน)   │ │    │ │                      │ │  │
│  │ │          │ │    │ │ - แปลง PDF/DOCX      │ │  │
│  │ │ 1. ...   │ │    │ │ - OCR                │ │  │
│  │ │ 2. ...   │ │    │ │ - AI สรุป            │ │  │
│  │ │ ...      │ │    │ └──────────────────────┘ │  │
│  │ │ [< 1/2 >]│ │    │                          │  │
│  │ └──────────┘ │    │ ┌──────────────────────┐ │  │
│  │              │    │ │ Trend                │ │  │
│  │              │    │ │ วิเคราะห์แนวโน้ม...   │ │  │
│  │              │    │ └──────────────────────┘ │  │
│  │              │    │                          │  │
│  │              │    │ ┌──────────────────────┐ │  │
│  │              │    │ │ AI Monitor           │ │  │
│  │              │    │ │ (Mockup)             │ │  │
│  │              │    │ └──────────────────────┘ │  │
│  └──────────────┘    └──────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### Design Features

- **Layout**: 2-column dashboard (Left: รายชื่อ, Right: ระบบต่างๆ)
- **Header**: 2 boxes (หัวข้อการประชุม + การติดตามนโยบาย)
- **Color Scheme**: Blue (#2563eb), Green (#16a34a), Purple (#9333ea)
- **Typography**: Sarabun (Thai font) - อ่านง่าย
- **Style**: Modern/Minimal design with rounded boxes และ white space
- **Responsive**: รองรับ Desktop, Tablet, Mobile

### Components

#### 1. Header Section (ด้านบน)
- **กล่องซ้าย**: "หัวข้อการประชุม" (ไม่มี subtitle)
- **กล่องขวา**: "การติดตามการดำเนินนโยบายของหน่วยงาน" (ไม่มี subtitle)

#### 2. Left Column - Information Panel
- **รายชื่อผู้เข้าร่วมประชุม**: แสดง 20 คน
- **Pagination**: แบ่งหน้าละ 10 คน (2 หน้า)
- **Features**: 
  - แสดงรายชื่อแบบลิสต์หมายเลข
  - Hover effects
  - Sticky position (เมื่อ scroll)

#### 3. Right Column - Analysis & AI Section
- **Document Recommendation System**: 
  - แปลง PDF/DOCX/TXT เป็นข้อความ
  - OCR สำหรับรูปภาพ
  - AI สรุปข้อความอัตโนมัติ
  - Link → `http://localhost:5001`
  
- **Trend**: 
  - วิเคราะห์แนวโน้มและสถิติข้อมูล
  - Link → `http://localhost:5002`
  
- **AI Monitor**: 
  - Mockup UI เท่านั้น (ไม่มี backend)
  - แสดงสถานะการทำงานของ AI

---

## 🚀 การติดตั้งและรัน

### ความต้องการของระบบ

- **Python**: 3.8 หรือสูงกว่า
- **Flask**: 3.0.0
- **Dependencies อื่นๆ**: ดูใน `requirements.txt`

### ขั้นตอนการติดตั้ง

#### 1. Clone Repository

```bash
git clone <repository-url>
cd main_Parliament
```

#### 2. สร้าง Virtual Environment (แนะนำ)

**Windows:**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. ติดตั้ง Dependencies

```bash
# ติดตั้ง dependencies ของ Main Dashboard
pip install -r requirements.txt

# ติดตั้ง dependencies ของ sub-projects (ถ้าต้องการ)
pip install -r pdf2text_final/requirements.txt
pip install -r duplicate-word-detector_final/requirements.txt
```

---

## ▶️ วิธีการรัน

### วิธีที่ 1: รัน Main Dashboard เท่านั้น

```bash
# ตรวจสอบว่า activate virtual environment แล้ว
.venv\Scripts\activate  # Windows
# หรือ
source .venv/bin/activate  # Linux/Mac

# รันแอป
python app.py
```

เปิดเบราว์เซอร์: `http://localhost:5003`

### วิธีที่ 2: รันทั้ง 3 แอปพร้อมกัน (แนะนำ)

```bash
# ตรวจสอบว่า activate virtual environment แล้ว
.venv\Scripts\activate  # Windows
# หรือ
source .venv/bin/activate  # Linux/Mac

# รันทั้ง 3 แอปพร้อมกัน
python run_all.py
```

**URLs ที่จะเปิด:**
- Main Dashboard: `http://localhost:5003`
- Document System: `http://localhost:5001`
- Trend Analysis: `http://localhost:5002`

**หมายเหตุ:**
- `run_all.py` จะรันทั้ง 3 services ในหน้าต่างเดียวกัน
- กด `Ctrl+C` เพื่อหยุดทุก services พร้อมกัน
- Script จะตรวจสอบว่าโฟลเดอร์ sub-projects มีอยู่หรือไม่ก่อนรัน

---

## 📁 โครงสร้างโปรเจกต์

```
main_Parliament/
├── app.py                      # Flask application หลัก
├── run_all.py                  # Script สำหรับรันทั้ง 3 แอปพร้อมกัน
├── requirements.txt            # Python dependencies
├── README.md                   # เอกสารหลัก (คุณอยู่ที่นี่)
├── .gitignore                  # Git ignore rules
│
├── templates/                  # HTML templates
│   └── index.html             # Main dashboard template
│
├── static/                     # Static files
│   └── style.css              # Custom CSS styles
│
├── pdf2text_final/            # Document Recommendation System
│   ├── app.py
│   ├── requirements.txt
│   └── ...
│
├── duplicate-word-detector_final/  # Trend Analysis System
│   ├── app.py
│   ├── requirements.txt
│   └── ...
│
├── .venv/                      # Virtual environment (สร้างเอง)
└── __pycache__/               # Python cache (auto-generated)
```

---

## 🔧 การตั้งค่า

### Port Configuration

**Default Ports:**
- Main Dashboard: `5003`
- Document System: `5001`
- Trend Analysis: `5002`

**เปลี่ยน Port:**

```bash
# Windows
set PORT=5003
python app.py

# Linux/Mac
export PORT=5003
python app.py
```

**หรือแก้ไขในไฟล์:**
- Main Dashboard: `app.py` (บรรทัด 22)
- Document System: `pdf2text_final/app.py`
- Trend Analysis: `duplicate-word-detector_final/app.py`

### การเปลี่ยน Links ใน Dashboard

แก้ไขไฟล์ `templates/index.html`:
- Document Recommendation System: หา `http://localhost:5001`
- Trend Analysis: หา `http://localhost:5002`

---

## 🎯 ฟีเจอร์หลัก

### 1. Main Dashboard (port 5003)
- **Real-time Attendance Tracking**: ติดตามสถานะผู้เข้าร่วมประชุมแบบเรียลไทม์ผ่าน WebSocket (Flask-SocketIO)
- **Toggle สถานะ**: คลิกเปลี่ยนสถานะ เข้า/ออก ของผู้เข้าร่วมได้ทันที พร้อม broadcast ไปยังทุก client
- **Pagination**: แบ่งหน้ารายชื่อ 10 คนต่อหน้า พร้อม Sticky position เมื่อ scroll
- **Summary Badges**: แสดงจำนวนผู้เข้าร่วม/ไม่เข้าร่วมแบบ real-time
- **Polling Indicator**: แสดงสถานะการเชื่อมต่อ (จุดสีเขียว/แดง)
- **Thai Clock**: แสดงวันที่และเวลาภาษาไทยแบบ real-time
- **Header Boxes**: แสดงหัวข้อการประชุม และการติดตามนโยบาย พร้อม hover effects
- **Settings Dropdown**: 
  - เปลี่ยนหัวข้อการประชุม
  - จัดการฐานข้อมูลเอกสารแนะนำ (เพิ่ม/แก้ไข/ลบ/รีเซ็ต พร้อมดู PDF ใน iframe)
- **Toast Notifications**: แจ้งเตือนการทำงานต่างๆ แบบ slide-in/out
- **Database**: เชื่อมต่อ MySQL (meeting_attendance) ผ่าน PyMySQL

### 2. Document Recommendation System (port 5001)
- **รองรับหลายรูปแบบไฟล์**: PDF, DOCX, TXT, รูปภาพ (JPG/PNG/GIF/BMP/TIFF) ขนาดสูงสุด 50MB
- **OCR (Optical Character Recognition)**: ใช้ Pytesseract แปลงรูปภาพและ Scanned PDF เป็นข้อความ รองรับทั้งภาษาไทยและอังกฤษ
- **AI Summarization**: 
  - ใช้ **Typhoon API** เป็นตัวหลักในการสรุปเนื้อหาอัตโนมัติ
  - มี **Extractive Summarization** เป็น fallback (keyword scoring, sentence position)
  - รองรับ **Hierarchical Summarization** สำหรับข้อความยาว (>10,000 ตัวอักษร)
  - ตรวจจับภาษาอัตโนมัติ (ไทย/อังกฤษ)
- **ค้นหาประวัติ**: ค้นหาเอกสารที่เคย extract พร้อม autocomplete suggestions และ popular tags
- **ดาวน์โหลด**: ดาวน์โหลดข้อความที่ extract แล้ว, ไฟล์ต้นฉบับ, หรือสรุป
- **Re-extract**: สามารถ extract ซ้ำจากไฟล์ที่เก็บไว้
- **Memory Management**: จัดการ garbage collection อัตโนมัติเมื่อใช้หน่วยความจำเกิน 80%

### 3. Trend Analysis & Duplicate Detection (port 5002)
- **ตรวจจับคำซ้ำ**: 
  - ใช้ **PyThaiNLP** สำหรับ tokenization และ POS tagging ภาษาไทย
  - ตรวจจับ N-gram (bigrams/trigrams)
  - จัดกลุ่มคำที่คล้ายกัน (similarity grouping)
  - คำนวณคะแนนการซ้ำ (frequency, spread, length)
  - มี Parliament-specific stopwords สำหรับกรองคำที่ไม่เกี่ยวข้อง
- **วิเคราะห์แนวโน้ม**: 
  - `TrendAnalysisEngine` วิเคราะห์แนวโน้มตามหมวดหมู่
  - คำนวณ policy score (growth + z-score)
  - จัดหมวดหมู่คำด้วย `ParliamentWordCategorizer`
- **Hybrid Recommendation Engine**: 
  - ใช้ scikit-learn คำนวณ cosine similarity บน keyword + category vectors
  - จับคู่เอกสารแนะนำกับผลวิเคราะห์อัตโนมัติ
- **จัดการเอกสารแนะนำ**: CRUD เต็มรูปแบบ (สร้าง/อ่าน/แก้ไข/ลบ) พร้อมแบ่งตามหมวดหมู่
- **รองรับหลายไฟล์**: อัปโหลดหลายไฟล์พร้อมกัน (TXT, PDF, DOC, DOCX)
- **Export**: ส่งออกผลวิเคราะห์เป็น JSON

### 4. AI Monitor (Mockup)
- Mockup UI สำหรับแสดงสถานะการทำงานของ AI services
- ยังไม่มี backend connection (พร้อมสำหรับพัฒนาต่อในอนาคต)

### 5. ระบบรวม (run_all.py)
- รันทั้ง 3 services พร้อมกันด้วย script เดียว
- ตรวจสอบ sub-project folders อัตโนมัติก่อนเริ่ม
- เว้น 2 วินาทีระหว่างการเริ่มแต่ละ service
- Graceful shutdown: กด Ctrl+C จะ terminate ก่อน → รอ 3 วินาที → kill ถ้าจำเป็น
- แสดง URLs และ exit codes ของแต่ละ service

---

## 🛠️ Development

### แก้ไข Styles

แก้ไขไฟล์ `static/style.css`:
- Colors: ปรับ CSS variables ใน `:root`
- Layout: ปรับ spacing, padding, margin
- Responsive: ปรับ media queries

### แก้ไข Layout

แก้ไขไฟล์ `templates/index.html`:
- Header Section: แก้ไข header boxes
- Left Column: แก้ไขรายชื่อ
- Right Column: แก้ไข cards ต่างๆ

### เพิ่มรายชื่อ

แก้ไขใน `templates/index.html`:
- เพิ่ม `<li>` ใหม่ใน `participants-list`
- ตั้งค่า `data-page` ให้ถูกต้อง (1 หรือ 2)
- เพิ่มหมายเลขใน `participant-number`

### แก้ไข Pagination

แก้ไขใน JavaScript section (บรรทัดท้าย):
- `itemsPerPage`: เปลี่ยนจำนวนรายการต่อหน้า
- `totalItems`: เปลี่ยนจำนวนรายการทั้งหมด

---

## 📝 Technical Details

### Technologies Used

- **Backend**: 
  - Flask 3.0.0 + Flask-SocketIO (WebSocket real-time)
  - PyMySQL (MySQL database connector)
  - Typhoon API (AI summarization)
  - Pytesseract (OCR - Thai + English)
  - PyThaiNLP (Thai NLP tokenization & POS tagging)
  - scikit-learn (Cosine similarity, recommendation engine)
  - pdfplumber, python-docx (Document parsing)
- **Frontend**: 
  - HTML5 + CSS3 (Custom)
  - Tailwind CSS (CDN)
  - JavaScript (Vanilla) + Socket.IO client
  - Chart.js (Data visualization)
- **Icons**: Font Awesome 6.4.0
- **Fonts**: Google Fonts (Sarabun - Thai)
- **Database**: MySQL (meeting_attendance, extraction_records, summary_records)

### Browser Support

- Chrome (แนะนำ)
- Firefox
- Edge
- Safari

### Performance

- Lightweight: ใช้ CDN สำหรับ CSS framework
- Fast loading: Minimal dependencies
- Real-time: WebSocket สำหรับอัปเดตข้อมูลทันที
- Responsive: ทำงานได้ดีบนทุกขนาดหน้าจอ

---

## 🐛 Troubleshooting

### ปัญหา: Port ถูกใช้งานแล้ว

**แก้ไข:**
```bash
# ตรวจสอบ port ที่ถูกใช้งาน
netstat -ano | findstr :5003  # Windows
lsof -i :5003                 # Linux/Mac

# เปลี่ยน port
set PORT=5004
python app.py
```

### ปัญหา: ไม่สามารถเชื่อมต่อ sub-projects ได้

**ตรวจสอบ:**
1. รัน sub-projects ก่อน หรือใช้ `run_all.py`
2. ตรวจสอบว่า port ถูกต้อง (5001, 5002)
3. ตรวจสอบว่า dependencies ติดตั้งครบ

### ปัญหา: Pagination ไม่ทำงาน

**แก้ไข:**
1. ตรวจสอบ JavaScript console (F12)
2. ตรวจสอบว่า `participantsList` element มีอยู่
3. ตรวจสอบ `data-page` attributes

---

## 📚 Related Documentation

- [pdf2text_final/README.md](pdf2text_final/README.md) - Document System documentation
- [duplicate-word-detector_final/README.md](duplicate-word-detector_final/README.md) - Trend Analysis documentation

---

## 📄 License

MIT License - ใช้งานได้อย่างอิสระ

---

## 👥 Credits

**Developed for:** Thai Parliament  
**Version:** 1.0  
**Last Updated:** December 2025

---

## 🔗 Quick Links

- **Main Dashboard**: http://localhost:5003
- **Document System**: http://localhost:5001
- **Trend Analysis**: http://localhost:5002

---

**🏛️ สร้างเพื่อรัฐสภาไทย | Built for Thai Parliament 🏛️**
