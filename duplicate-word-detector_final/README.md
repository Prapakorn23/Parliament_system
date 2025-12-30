# ระบบตรวจจับคำซ้ำอัตโนมัติสำหรับรัฐสภาไทย
## Thai Parliament Duplicate Word Detector System

<div align="center">

![Version](https://img.shields.io/badge/version-4.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

**ระบบวิเคราะห์ความถี่ของคำและจัดหมวดหมู่อัตโนมัติสำหรับเอกสารรัฐสภา**

</div>

---

## 🌟 Features

### ✨ **ฟีเจอร์หลัก:**

- 🔍 **ตรวจจับคำซ้ำอัตโนมัติ** - วิเคราะห์ความถี่ของคำในข้อความ
- 📂 **จัดหมวดหมู่คำ** - แบ่งกลุ่มคำตามบริบทรัฐสภา (16 หมวดหมู่)
- 📄 **รองรับ PDF** - แปลง PDF ทั้งข้อความและภาพ (OCR)
- 🗄️ **ฐานข้อมูล** - บันทึก วิเคราะห์ และค้นหาประวัติการวิเคราะห์ (NEW!)
- 📊 **กราฟและสถิติ** - แสดงผลด้วย Chart.js แบบ Interactive
- 💾 **ส่งออก CSV** - ดาวน์โหลดผลลัพธ์เป็น CSV
- 📱 **Responsive Design** - ใช้งานได้บนทุกอุปกรณ์

### 📂 **หมวดหมู่ที่รองรับ (16 หมวด):**

1. **การศึกษา** - การเรียน, โรงเรียน, ครู, นักเรียน
2. **เศรษฐกิจ** - งบประมาณ, การเงิน, ธนาคาร, GDP
3. **การเมือง** - รัฐสภา, รัฐบาล, ส.ส., นโยบาย
4. **สังคม** - ประชาชน, สวัสดิการ, สิทธิมนุษยชน
5. **สาธารณสุข** - โรงพยาบาล, สุขภาพ, โรค
6. **เกษตรกรรม** - เกษตรกร, ข้าว, ยางพารา
7. **กฎหมาย** - พระราชบัญญัติ, ศาล, รัฐธรรมนูญ
8. **คมนาคม** - ถนน, รถไฟ, สนามบิน
9. **พลังงาน** - ไฟฟ้า, น้ำมัน, พลังงานทดแทน
10. **สื่อสารและเทคโนโลยี** - ดิจิทัล, AI, อินเทอร์เน็ต
11. **สิ่งแวดล้อม** - มลพิษ, ป่าไม้, PM2.5
12. **การต่างประเทศ** - อาเซียน, ทูต, สนธิสัญญา
13. **ท่องเที่ยว** - นักท่องเที่ยว, วัฒนธรรม
14. **กีฬา** - นักกีฬา, การแข่งขัน
15. **แรงงาน** - ค่าจ้าง, ประกันสังคม
16. **มหาดไทย** - ท้องถิ่น, จังหวัด, อำเภอ

---

## 🚀 Quick Start

### **1. ติดตั้ง Dependencies:**

```bash
# ติดตั้ง Python packages พื้นฐาน
pip install -r requirements.txt
```

### **2. รันโปรแกรม:**

```bash
python app.py
```

### **3. เปิดเบราว์เซอร์:**

```
http://localhost:5000
```

---

## 📦 Installation (ขั้นสูง)

### **สำหรับ PDF ข้อความ (แนะนำ):**

```bash
pip install PyPDF2 pdfplumber
```

### **สำหรับ PDF ภาพ (OCR - ต้องติดตั้งเพิ่ม):**

#### **Windows:**

1. ติดตั้ง Python packages:
   ```bash
   pip install pdf2image pytesseract Pillow
   ```

2. ติดตั้ง Tesseract-OCR:
   - ดาวน์โหลด: https://github.com/UB-Mannheim/tesseract/wiki
   - เลือกติดตั้งภาษาไทย (Thai) ระหว่างการติดตั้ง
   - เพิ่ม `C:\Program Files\Tesseract-OCR` ใน PATH

3. ติดตั้ง Poppler:
   - ดาวน์โหลด: http://blog.alivate.com.au/poppler-windows/
   - แตกไฟล์และเพิ่ม `bin` folder ใน PATH

#### **macOS:**

```bash
brew install tesseract tesseract-lang poppler
pip install pdf2image pytesseract Pillow
```

#### **Linux:**

```bash
sudo apt install tesseract-ocr tesseract-ocr-tha poppler-utils
pip install pdf2image pytesseract Pillow
```

---

## 💡 การใช้งาน

### **1. วิเคราะห์ข้อความ:**

```
1. พิมพ์ข้อความในกล่อง "หรือพิมพ์ข้อความ"
2. กดปุ่ม "ตรวจสอบคำซ้ำ"
3. ดูผลลัพธ์
```

### **2. อัปโหลดไฟล์:**

```
1. กด "เลือกไฟล์" ในส่วน "1. อัปโหลดไฟล์"
2. เลือกไฟล์ .txt หรือ .pdf
3. ระบบจะแปลงและวิเคราะห์อัตโนมัติ
```

### **3. ดูผลลัพธ์:**

- **สถิติ** - คำทั้งหมด, คำที่ไม่ซ้ำ
- **กราฟ** - ความถี่ของคำ (Top 10 หรือทั้งหมด)
- **หมวดหมู่** - คำจัดกลุ่มตามบริบทรัฐสภา
- **ตาราง** - รายการคำทั้งหมดพร้อม Pagination

### **4. ส่งออกข้อมูล:**

```
กดปุ่ม "ดาวน์โหลด CSV" เพื่อบันทึกผลลัพธ์
```

---

## 🏗️ โครงสร้างโปรเจค

```
duplicate-word-detector/
├── 📱 app.py                       # Flask Backend (main entry)
├── 📄 requirements.txt             # Python dependencies
├── 📖 README.md                    # คู่มือหลัก (คุณอยู่ที่นี่)
├── 🚀 QUICK_START.md              # เริ่มใช้งานด่วน
│
├── 🧠 core/                        # Core modules
│   ├── duplicate_word_detector.py  # ตัววิเคราะห์คำ
│   ├── word_categorizer.py         # ระบบจัดหมวดหมู่
│   ├── pdf_processor.py            # ประมวลผล PDF/OCR
│   └── performance_utils.py        # Performance tracking
│
├── ⚙️ config/                      # Configuration
│   └── config.py                   # ไฟล์การตั้งค่า
│
├── 🌐 templates/                   # HTML templates
│   └── dashboard.html              # Frontend UI
│
├── 🎨 static/                      # Static files
│   ├── style.css                   # Styles
│   ├── script.js                   # JavaScript
│   └── *.png                       # Charts (auto-generated)
│
├── 📚 docs/                        # Documentation
│   ├── INDEX.md                    # สารบัญเอกสาร
│   ├── PDF_OCR_SETUP_GUIDE.md     # คู่มือ PDF/OCR
│   ├── PARLIAMENT_CATEGORIZATION_FEATURE.md
│   └── ... (more docs)
│
├── 🔧 scripts/                     # Installation scripts
│   ├── install_windows.bat         # Windows installer
│   └── install_linux_mac.sh        # Linux/Mac installer
│
├── 📤 uploads/                     # Temp uploads (auto-created)
└── 💾 cache/                       # Cache files (auto-created)
```

👉 **ดูรายละเอียดเพิ่มเติม:** [docs/FOLDER_ORGANIZATION.md](docs/FOLDER_ORGANIZATION.md)

---

## 🎨 UI/UX Features

### **Sidebar (ซ้าย):**
```
┌─────────────────────────────┐
│ [รีเซ็ต] [ล้าง]             │ ← Quick Actions
│ [🔍 ตรวจสอบคำซ้ำ]          │ ← Primary Button
├─────────────────────────────┤
│ 1. อัปโหลดไฟล์              │
│ [เลือกไฟล์ .txt/.pdf]      │
├─────────────────────────────┤
│ หรือพิมพ์ข้อความ            │
│ [Textarea]                  │
├─────────────────────────────┤
│ [Progress Bar]              │
├─────────────────────────────┤
│ 💡 เคล็ดลับการใช้งาน       │
└─────────────────────────────┘
```

### **Main Content (ขวา):**
```
┌─────────────────────────────┐
│ [คำทั้งหมด] [คำที่ไม่ซ้ำ]  │ ← Stats
├─────────────────────────────┤
│ ✓ วิเคราะห์เสร็จ [📥 CSV]  │ ← Action Bar
├─────────────────────────────┤
│ 📊 กราฟความถี่ของคำ        │
│ [Interactive Chart]         │
├─────────────────────────────┤
│ 📂 หมวดหมู่คำที่พบ         │
│ [Accordion with Categories] │
├─────────────────────────────┤
│ 📋 รายการคำทั้งหมด         │
│ [Paginated Table]           │
└─────────────────────────────┘
```

---

## 🔧 API Documentation

### **POST /api/analyze**
วิเคราะห์ข้อความและตรวจสอบคำซ้ำ

**Request Body:**
```json
{
  "text": "ข้อความที่ต้องการวิเคราะห์",
  "filter_pos": true,
  "target_pos": null
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_words": 150,
    "unique_words": 75,
    "word_frequency": {...},
    "category_summary": [...],
    "top_words_by_category": {...}
  }
}
```

### **POST /api/upload**
อัปโหลดไฟล์ (.txt หรือ .pdf)

**Request:** FormData with file

**Response:**
```json
{
  "success": true,
  "data": {
    "filename": "document.pdf",
    "file_type": "PDF",
    "extraction_method": "pdfplumber",
    "content": "...",
    "total_words": 1234,
    ...
  }
}
```

### **GET /api/check-pdf-support**
ตรวจสอบการรองรับ PDF และ OCR

**Response:**
```json
{
  "success": true,
  "data": {
    "supported_methods": {
      "pypdf2": true,
      "pdfplumber": true,
      "ocr": false
    },
    "installation_instructions": {...}
  }
}
```

---

## 📝 ตัวอย่างการใช้งาน

### **Use Case 1: วิเคราะห์รายงานการประชุมสภา**

```
1. อัปโหลด: รายงานการประชุม.pdf
2. ระบบแปลง PDF → text อัตโนมัติ
3. วิเคราะห์คำซ้ำและจัดหมวดหมู่
4. ผลลัพธ์:
   - การเมือง: 45% (รัฐสภา, ส.ส., ญัตติ)
   - เศรษฐกิจ: 30% (งบประมาณ, การเงิน)
   - สังคม: 15% (สวัสดิการ, ประชาชน)
```

### **Use Case 2: เตรียมวาระการประชุม**

```
1. พิมพ์ข้อความวาระที่เตรียมไว้
2. กด "ตรวจสอบคำซ้ำ"
3. ดูว่าครอบคลุมหัวข้อใดบ้าง
4. ปรับปรุงเนื้อหาให้สมบูรณ์
```

### **Use Case 3: วิเคราะห์เอกสารนโยบาย**

```
1. อัปโหลด: นโยบายรัฐบาล.pdf
2. ดูหมวดหมู่ที่พบ
3. วิเคราะห์ว่าเน้นด้านใด
4. สรุปประเด็นหลักได้ทันที
```

---

## 📊 Screenshots

### **Welcome Screen:**
- อินเทอร์เฟซสะอาด เข้าใจง่าย
- แสดงฟีเจอร์หลักทั้งหมด
- คำแนะนำการใช้งาน

### **Results View:**
- Stats Cards แสดงเด่นชัด
- กราฟ Interactive
- Accordion สำหรับหมวดหมู่
- ตารางแบบ Paginated

---

## 🛠️ Tech Stack

### **Backend:**
- Flask 3.0
- PythaiNLP 4.0
- PyPDF2 & pdfplumber (PDF processing)
- Pytesseract (OCR)
- Matplotlib (Charts)
- Pandas & NumPy (Data processing)

### **Frontend:**
- Bootstrap 5.3
- Chart.js
- Font Awesome 6.4
- Vanilla JavaScript

---

## 📚 Documentation

- 📖 [PDF_OCR_SETUP_GUIDE.md](PDF_OCR_SETUP_GUIDE.md) - คู่มือติดตั้ง PDF/OCR
- 📖 [PARLIAMENT_CATEGORIZATION_FEATURE.md](PARLIAMENT_CATEGORIZATION_FEATURE.md) - คู่มือฟีเจอร์จัดหมวดหมู่
- 📖 [CATEGORIZATION_IMPROVEMENT.md](CATEGORIZATION_IMPROVEMENT.md) - การปรับปรุงอัลกอริทึม
- 📖 [WIDGET_IMPROVEMENTS.md](WIDGET_IMPROVEMENTS.md) - การปรับปรุง UI/UX

---

## 🔧 Configuration

### **ปรับแต่งหมวดหมู่:**

แก้ไขไฟล์ `word_categorizer.py`:

```python
self.categories = {
    'หมวดหมู่ใหม่': [
        'คำสำคัญ1', 'คำสำคัญ2', ...
    ]
}
```

### **ตั้งค่า Tesseract (Windows):**

เพิ่มใน `app.py` หรือ `pdf_processor.py`:

```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

---

## 📱 Responsive Design

### **รองรับทุกขนาดหน้าจอ:**

| Device | Layout | Chart Size |
|--------|--------|------------|
| Desktop (>1200px) | 2 columns | 450px |
| Tablet (768-992px) | 1 column | 350px |
| Mobile (576-768px) | Stack vertical | 280px |
| Small (<576px) | Compact | 220px |

---

## 🎯 Use Cases

### **สำหรับรัฐสภา:**

✅ วิเคราะห์รายงานการประชุม  
✅ ตรวจสอบวาระการประชุม  
✅ จัดหมวดหมู่เอกสาร  
✅ ติดตามประเด็นร้อน  
✅ สรุปเนื้อหาเอกสาร  
✅ วิเคราะห์แนวโน้มการพูดคุย  

---

## 🔍 How It Works

### **1. Text Input:**
```
User Input → Analyze → Word Count → Categorize → Display
```

### **2. PDF Text:**
```
Upload PDF → pdfplumber/PyPDF2 → Extract Text → Analyze → Display
```

### **3. PDF Image (OCR):**
```
Upload PDF → pdf2image → Images → Tesseract OCR → Text → Analyze → Display
```

---

## 📄 Supported File Types

| Type | Extension | Max Size | Processing Method |
|------|-----------|----------|-------------------|
| Text | .txt | 200MB* | Direct Read |
| PDF Text | .pdf | 200MB* | pdfplumber/PyPDF2 |
| PDF Image | .pdf | 200MB* | OCR (Tesseract) |
| Word Document | .doc, .docx | 200MB* | python-docx |

*สามารถปรับขนาดสูงสุดได้ผ่าน environment variable `MAX_FILE_SIZE_MB` (default: 200MB)

---

## 🧪 Testing

### **ทดสอบด้วยข้อความตัวอย่าง:**

```
วันนี้มีการประชุมสภาเพื่อพิจารณางบประมาณด้านการศึกษา 
โดยมีการหารือเรื่องการจัดสรรงบประมาณสำหรับโรงเรียน 
การพัฒนาคุณภาพครู และการจัดหาทุนการศึกษาให้กับนักเรียน 
นอกจากนี้ยังมีการพูดถึงเรื่องเศรษฐกิจและการค้าระหว่างประเทศด้วย
```

**ผลลัพธ์ที่คาดหวัง:**
- การศึกษา: งบประมาณ, โรงเรียน, ครู, นักเรียน
- เศรษฐกิจ: เศรษฐกิจ, การค้า
- การเมือง: ประชุมสภา

---

## ⚙️ System Requirements

- Python 3.8 หรือสูงกว่า
- RAM: 2GB ขึ้นไป (4GB แนะนำสำหรับ OCR)
- Disk Space: 500MB (รวม dependencies)
- Internet: สำหรับ CDN (Bootstrap, Chart.js)

---

## 🐛 Troubleshooting

### **ปัญหาที่พบบ่อย:**

#### 1. **"ไม่สามารถแปลง PDF ได้"**
```bash
# ตรวจสอบ libraries
python -c "import PyPDF2, pdfplumber; print('✅')"

# ถ้า error ให้ติดตั้งใหม่
pip install --upgrade PyPDF2 pdfplumber
```

#### 2. **"OCR ไม่ทำงาน"**
```bash
# ตรวจสอบ Tesseract
tesseract --version
tesseract --list-langs  # ต้องมี 'tha'

# ถ้าไม่มีภาษาไทย
# Windows: ติดตั้ง Tesseract ใหม่พร้อมเลือก Thai
# Linux: sudo apt install tesseract-ocr-tha
```

#### 3. **"pdf2image error"**
```bash
# ตรวจสอบ Poppler
pdftoppm -v

# ถ้า error
# Windows: ติดตั้ง Poppler และเพิ่ม PATH
# macOS: brew install poppler
# Linux: sudo apt install poppler-utils
```

#### 4. **"ไฟล์ใหญ่เกินไป"**
- ลดขนาดไฟล์ก่อนอัปโหลด
- แบ่งไฟล์ออกเป็นหลายส่วน
- เพิ่ม max file size ใน `app.py`

---

## 🚦 Status Indicators

### **File Upload:**
- 🟢 **Green Border** - อัปโหลดสำเร็จ
- 🔴 **Red Border** - อัปโหลดล้มเหลว

### **Progress Bar:**
- 10% - กำลังเริ่มต้น
- 30% - กำลังแปลง PDF
- 60% - กำลังวิเคราะห์
- 90% - กำลังสร้างกราฟ
- 100% - เสร็จสิ้น

### **Alerts:**
- 🔵 **Info** - ข้อมูลทั่วไป
- 🟢 **Success** - สำเร็จ
- 🟡 **Warning** - คำเตือน
- 🔴 **Danger** - ข้อผิดพลาด

---

## 🌟 Advanced Features

### **1. Word Categorization:**
- จัดกลุ่มคำอัตโนมัติ
- 16 หมวดหมู่สำหรับรัฐสภา
- แสดง Top 5 คำในแต่ละหมวด
- Accordion UI สำหรับดูรายละเอียด

### **2. PDF Processing:**
- รองรับทั้ง text-based และ image-based PDF
- Auto-detection ประเภท PDF
- Fallback mechanism (pdfplumber → PyPDF2 → OCR)
- Progress tracking

### **3. Export Features:**
- CSV with UTF-8 BOM (รองรับภาษาไทย)
- รวมข้อมูลหมวดหมู่
- เปิดใน Excel ได้เลย

---

## 🔐 Security

- ✅ ไฟล์ถูกลบทันทีหลังประมวลผล
- ✅ Validation ประเภทและขนาดไฟล์
- ✅ CORS enabled
- ✅ ไม่เก็บข้อมูลถาวร

---

## 📈 Performance

- **Text Analysis:** < 1 second
- **PDF Text Extraction:** 1-5 seconds
- **PDF OCR (per page):** 1-3 seconds
- **Chart Generation:** < 1 second

---

## 🤝 Contributing

ต้องการเพิ่มฟีเจอร์หรือปรับปรุง?

1. เพิ่มหมวดหมู่ใน `word_categorizer.py`
2. ปรับ UI ใน `templates/dashboard.html`
3. อัพเดท styles ใน `static/style.css`
4. Test และ commit

---

## 📄 License

MIT License - ใช้งานได้อย่างอิสระ

---

## 👥 Credits

**Developed for:** Thai Parliament  
**Version:** 4.0  
**Last Updated:** November 5, 2025  

---

## 🎓 Learn More

- [Flask Documentation](https://flask.palletsprojects.com/)
- [PythaiNLP](https://pythainlp.github.io/)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [Chart.js](https://www.chartjs.org/)

---

<div align="center">

**🏛️ สร้างเพื่อรัฐสภาไทย | Built for Thai Parliament 🏛️**

</div>
