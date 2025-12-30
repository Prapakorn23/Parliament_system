# คู่มือการติดตั้งฟีเจอร์ PDF และ OCR
## PDF & OCR Feature Installation Guide

---

## 🎯 ฟีเจอร์ใหม่

ระบบตรวจจับคำซ้ำสามารถ:
- ✅ รองรับไฟล์ PDF ที่เป็นข้อความ
- ✅ รองรับไฟล์ PDF ที่เป็นภาพ (สแกน) ด้วย OCR
- ✅ แปลงอัตโนมัติและวิเคราะห์คำซ้ำ
- ✅ จัดหมวดหมู่คำตามบริบทรัฐสภา

---

## 📦 การติดตั้ง

### **ขั้นตอนที่ 1: ติดตั้ง Python Libraries**

```bash
pip install -r requirements.txt
```

**Libraries ที่จำเป็น:**
- ✅ `PyPDF2` - สำหรับ PDF ข้อความ (พื้นฐาน)
- ✅ `pdfplumber` - สำหรับ PDF ข้อความ (แม่นยำกว่า)
- ✅ `pdf2image` - แปลง PDF เป็นรูปภาพ
- ✅ `pytesseract` - OCR engine wrapper
- ✅ `Pillow` - จัดการรูปภาพ

---

### **ขั้นตอนที่ 2: ติดตั้ง Tesseract-OCR (สำหรับ OCR)**

#### **Windows:**

1. **ดาวน์โหลด Tesseract-OCR:**
   - ไปที่: https://github.com/UB-Mannheim/tesseract/wiki
   - ดาวน์โหลด: `tesseract-ocr-w64-setup-v5.3.3.exe` (หรือเวอร์ชันล่าสุด)

2. **ติดตั้ง:**
   - รันไฟล์ installer
   - **สำคัญ**: ติ๊กเลือก "Thai language data" ระหว่างการติดตั้ง
   - หรือติดตั้งทุกภาษาเลย

3. **เพิ่ม Path:**
   - เพิ่ม `C:\Program Files\Tesseract-OCR` ใน System PATH
   - หรือตั้งค่าใน Python:
   
   ```python
   # ใน pdf_processor.py หรือ app.py
   import pytesseract
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

4. **ดาวน์โหลดข้อมูลภาษาไทย (ถ้ายังไม่มี):**
   - ไปที่: https://github.com/tesseract-ocr/tessdata
   - ดาวน์โหลด `tha.traineddata`
   - วางไว้ที่: `C:\Program Files\Tesseract-OCR\tessdata\`

#### **macOS:**

```bash
# ติดตั้งผ่าน Homebrew
brew install tesseract
brew install tesseract-lang  # รวมภาษาไทย
```

#### **Linux (Ubuntu/Debian):**

```bash
sudo apt update
sudo apt install tesseract-ocr
sudo apt install tesseract-ocr-tha  # ภาษาไทย
sudo apt install poppler-utils  # สำหรับ pdf2image
```

---

### **ขั้นตอนที่ 3: ติดตั้ง Poppler (สำหรับ pdf2image)**

#### **Windows:**

1. ดาวน์โหลด Poppler สำหรับ Windows:
   - ไปที่: http://blog.alivate.com.au/poppler-windows/
   - ดาวน์โหลด: `poppler-xx.xx.x_x86.7z` หรือ `x64` version

2. แตกไฟล์และเพิ่ม Path:
   - แตกไฟล์ไปที่ `C:\poppler\`
   - เพิ่ม `C:\poppler\Library\bin` ใน System PATH

#### **macOS:**

```bash
brew install poppler
```

#### **Linux:**

```bash
sudo apt install poppler-utils
```

---

## 🧪 ทดสอบการติดตั้ง

### **ทดสอบ Python Libraries:**

```python
python -c "import PyPDF2; import pdfplumber; import pdf2image; import pytesseract; print('✅ ทุก libraries พร้อมใช้งาน')"
```

### **ทดสอบ Tesseract:**

```bash
tesseract --version
tesseract --list-langs  # ตรวจสอบว่ามีภาษาไทย (tha)
```

**ผลลัพธ์ที่ต้องการ:**
```
List of available languages (2):
eng
tha  ← ต้องมี
```

### **ทดสอบผ่าน Python:**

```python
import pytesseract
from PIL import Image

# ทดสอบ OCR ภาษาไทย
print(pytesseract.get_languages())  # ต้องมี 'tha'
```

---

## 🚀 การใช้งาน

### **1. รันเซิร์ฟเวอร์:**

```bash
python app.py
```

### **2. เปิดเบราว์เซอร์:**

```
http://localhost:5000
```

### **3. อัปโหลดไฟล์:**

#### **กรณี PDF ข้อความ:**
- เลือกไฟล์ PDF
- ระบบจะใช้ `pdfplumber` หรือ `PyPDF2` แปลงเป็น text
- เร็วมาก (ไม่กี่วินาที)

#### **กรณี PDF ภาพ (สแกน):**
- เลือกไฟล์ PDF ที่เป็นภาพ
- ระบบจะใช้ OCR (Tesseract) อ่านข้อความจากภาพ
- ช้ากว่า (ขึ้นกับจำนวนหน้า)
- แสดง progress bar ระหว่างประมวลผล

#### **กรณีไฟล์ .txt:**
- เลือกไฟล์ text ธรรมดา
- อ่านและแสดงผลทันที

---

## 🔍 ระบบเลือกวิธีการแปลงอัตโนมัติ

ระบบจะลองใช้วิธีการตามลำดับ:

```
1. pdfplumber (แม่นยำที่สุด)
   ↓ ถ้าไม่สำเร็จ
2. PyPDF2 (เร็วกว่า)
   ↓ ถ้าไม่สำเร็จ หรือได้ text น้อยมาก
3. OCR (Tesseract) - สำหรับ PDF ภาพ
```

---

## 📊 ผลลัพธ์ที่ได้รับ

หลังจากแปลง PDF สำเร็จ ระบบจะแสดง:

1. **ข้อความที่แปลงได้** - ใน textarea
2. **สถิติคำ** - คำทั้งหมด, คำที่ไม่ซ้ำ
3. **กราฟความถี่** - Top 10 หรือทั้งหมด
4. **หมวดหมู่คำ** - จัดกลุ่มตามบริบทรัฐสภา
5. **ตารางรายละเอียด** - ทุกคำพร้อมความถี่
6. **วิธีการแปลง** - บอกว่าใช้วิธีใด (pdfplumber/PyPDF2/OCR)

---

## ⚠️ ข้อควรระวัง

### **สำหรับ OCR:**
- ⏱️ ใช้เวลานานกว่า (1-3 วินาทีต่อหน้า)
- 📊 ความแม่นยำขึ้นกับคุณภาพภาพ
- 🔤 ฟอนต์ที่ชัดเจนจะให้ผลลัพธ์ดีกว่า
- 📐 ภาพที่เอียงหรือมืดอาจให้ผลลัพธ์ไม่ดี

### **ขนาดไฟล์:**
- 📄 ไฟล์ .txt: สูงสุด 200MB (default, ปรับได้ผ่าน .env)
- 📕 ไฟล์ .pdf: สูงสุด 200MB (default, ปรับได้ผ่าน .env)
- 📝 ไฟล์ .doc/.docx: สูงสุด 200MB (default, ปรับได้ผ่าน .env)
- 📑 PDF หลายหน้า: อาจใช้เวลานาน

---

## 🛠️ Troubleshooting

### **ปัญหา: "ไม่สามารถแปลง PDF ได้"**

**วิธีแก้:**
1. ตรวจสอบว่าติดตั้ง libraries ครบ:
   ```bash
   pip list | grep -E "PyPDF2|pdfplumber|pdf2image|pytesseract"
   ```

2. ตรวจสอบ Tesseract:
   ```bash
   tesseract --version
   ```

3. ตรวจสอบ Poppler:
   ```bash
   pdftoppm -v
   ```

### **ปัญหา: OCR ไม่รู้จักภาษาไทย**

**วิธีแก้:**
```bash
tesseract --list-langs
# ต้องมี 'tha' ในรายการ

# ถ้าไม่มี ให้ดาวน์โหลด tha.traineddata
# และวางไว้ใน tessdata folder
```

### **ปัญหา: PDF ภาพให้ผลลัพธ์ไม่ดี**

**วิธีแก้:**
1. ลองปรับคุณภาพภาพก่อน scan
2. ใช้ DPI สูงกว่า (300 DPI ขึ้นไป)
3. ตรวจสอบว่าข้อความชัดเจน ไม่เอียง

### **ปัญหา: ใช้เวลานาน**

**วิธีแก้:**
- PDF ข้อความ: ควรเร็ว (1-5 วินาที)
- PDF ภาพ: ปกติ (1-3 วินาที/หน้า)
- ถ้าช้าเกินไป ลดขนาดไฟล์หรือจำนวนหน้า

---

## 📝 ตัวอย่างการใช้งาน

### **ตัวอย่างที่ 1: PDF รายงานการประชุมสภา**

```
1. อัปโหลด: รายงานการประชุมสภา.pdf
2. ระบบแปลง: ใช้ pdfplumber
3. ผลลัพธ์:
   - คำทั้งหมด: 1,245
   - คำที่ไม่ซ้ำ: 487
   - หมวดหมู่พบ: การเมือง, งบประมาณ, การศึกษา
```

### **ตัวอย่างที่ 2: PDF ที่สแกนจากกระดาษ**

```
1. อัปโหลด: เอกสารสแกน.pdf (ภาพ)
2. ระบบแปลง: ใช้ OCR (Tesseract)
3. แสดง Progress: "กำลังแปลง PDF เป็น text... 50%"
4. ผลลัพธ์: แสดงข้อความพร้อมวิเคราะห์
```

---

## 🎨 UI Features

### **File Upload Interface:**

```
┌─────────────────────────────────┐
│ 1. อัปโหลดไฟล์                  │
│                                 │
│ [เลือกไฟล์]  ชื่อไฟล์.pdf      │
│                                 │
│ 📄 รองรับ .txt, .pdf, .doc     │
│    (สูงสุด 200MB*)              │
│                                 │
│ ✨ รองรับ PDF ทั้งข้อความและ   │
│    ภาพ (OCR อัตโนมัติ)         │
└─────────────────────────────────┘
```

### **Progress Indicator สำหรับ PDF:**

```
┌─────────────────────────────────┐
│ กำลังแปลง PDF เป็น text...     │
│ ████████████░░░░░░░░ 60%        │
└─────────────────────────────────┘
```

### **Success Message:**

```
✅ แปลง PDF "เอกสาร.pdf" สำเร็จ (pdfplumber)
```

---

## 💻 Code Examples

### **ทดสอบ PDF Processor:**

```python
from pdf_processor import PDFProcessor

processor = PDFProcessor()

# ตรวจสอบ libraries ที่ใช้งานได้
print(processor.supported_methods)
# {'pypdf2': True, 'pdfplumber': True, 'ocr': True}

# แปลง PDF
success, text, method = processor.extract_text_from_pdf('document.pdf')
print(f"สำเร็จ: {success}")
print(f"วิธีการ: {method}")
print(f"ข้อความ: {text[:200]}...")
```

### **ตรวจสอบประเภท PDF:**

```python
pdf_type = processor.check_pdf_type('document.pdf')
print(f"PDF Type: {pdf_type}")  # 'text' หรือ 'image'
```

---

## 🔧 Advanced Configuration

### **ปรับแต่ง Tesseract (ถ้าต้องการ):**

สร้างไฟล์ `tesseract_config.py`:

```python
import pytesseract

# Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# macOS/Linux (ปกติไม่ต้องตั้งค่า)
# pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'

# กำหนด config สำหรับ OCR
TESSERACT_CONFIG = '--psm 3 --oem 3'  # Page segmentation mode 3, OCR Engine Mode 3
```

### **ใช้ config ใน pdf_processor.py:**

```python
page_text = pytesseract.image_to_string(
    image, 
    lang='tha+eng',
    config='--psm 3 --oem 3'  # เพิ่มบรรทัดนี้
)
```

---

## 📈 Performance Tips

### **เพิ่มความเร็ว OCR:**

1. **ลด DPI:**
   ```python
   images = convert_from_path(pdf_path, dpi=200)  # แทน 300
   ```

2. **ประมวลผลแบบ Parallel:**
   - แยกหน้าประมวลผลพร้อมกัน
   - ใช้ multiprocessing

3. **Cache ผลลัพธ์:**
   - เก็บผลลัพธ์ของไฟล์ที่เคยแปลงแล้ว

### **ปรับคุณภาพ OCR:**

1. **Pre-processing ภาพ:**
   ```python
   from PIL import ImageEnhance
   
   # เพิ่มความคมชัด
   enhancer = ImageEnhance.Contrast(image)
   image = enhancer.enhance(2.0)
   ```

2. **ใช้ PSM ที่เหมาะสม:**
   - PSM 3: Fully automatic page segmentation (default)
   - PSM 6: Uniform block of text
   - PSM 11: Sparse text

---

## 📋 Checklist

### **ก่อนใช้งาน:**

- [ ] ติดตั้ง Python libraries (`pip install -r requirements.txt`)
- [ ] ติดตั้ง Tesseract-OCR
- [ ] ดาวน์โหลดข้อมูลภาษาไทย (tha.traineddata)
- [ ] ติดตั้ง Poppler (สำหรับ pdf2image)
- [ ] ทดสอบว่า Tesseract รู้จักภาษาไทย
- [ ] ทดสอบแปลง PDF ตัวอย่าง

### **การใช้งาน:**

- [ ] อัปโหลดไฟล์ PDF
- [ ] ตรวจสอบ Progress Bar
- [ ] ตรวจสอบข้อความที่แปลงได้
- [ ] ดูผลการวิเคราะห์คำซ้ำ
- [ ] ดูหมวดหมู่คำ
- [ ] ส่งออก CSV

---

## 🎯 Supported File Types

| ประเภท | Extension | วิธีการแปลง | ความเร็ว | ความแม่นยำ |
|--------|-----------|-------------|----------|------------|
| Text File | .txt, .text | Direct Read | ⚡⚡⚡ | ✅✅✅ |
| PDF Text | .pdf | pdfplumber/PyPDF2 | ⚡⚡ | ✅✅✅ |
| PDF Image | .pdf | OCR (Tesseract) | ⚡ | ✅✅ |

---

## 📞 Support

### **ถ้าติดตั้งไม่สำเร็จ:**

1. ตรวจสอบ error message ใน terminal
2. ตรวจสอบว่า Tesseract อยู่ใน PATH หรือไม่
3. ลองรัน `tesseract --version` ใน command line
4. ตรวจสอบว่ามีไฟล์ `tha.traineddata` ใน tessdata folder

### **ทดสอบแบบ Step-by-Step:**

```bash
# 1. ทดสอบ Import
python -c "from pdf_processor import PDFProcessor; print('✅')"

# 2. ทดสอบ Tesseract
tesseract --list-langs

# 3. ทดสอบแปลง PDF
python -c "from pdf_processor import PDFProcessor; p = PDFProcessor(); print(p.supported_methods)"
```

---

## 🌟 ตัวอย่าง Output

### **Success Message:**

```
✅ แปลง PDF "รายงานการประชุม.pdf" สำเร็จ (pdfplumber)

📊 ผลการวิเคราะห์:
- คำทั้งหมด: 2,456
- คำที่ไม่ซ้ำ: 892
- หมวดหมู่พบ: การเมือง (45%), เศรษฐกิจ (30%), สังคม (15%)
```

---

**วันที่สร้าง**: November 5, 2025  
**เวอร์ชัน**: 4.0 - PDF & OCR Support  
**ผู้พัฒนา**: Parliament IT Team

