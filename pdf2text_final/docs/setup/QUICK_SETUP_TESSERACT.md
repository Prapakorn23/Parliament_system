# 🔍 Quick Setup - Tesseract OCR

## ⚠️ ปัญหา

เมื่ออัปโหลด PDF ที่ต้องการ OCR จะเห็น error:
```
OCR error on page 0: tesseract is not installed or it's not in your PATH
```

## 📌 Tesseract OCR คืออะไร?

**Tesseract OCR** คือ engine สำหรับแปลงรูปภาพเป็นข้อความ (Optical Character Recognition)

จำเป็นสำหรับ:
- ✅ แปลง PDF ที่เป็นภาพสแกน → ข้อความ
- ✅ แปลงไฟล์รูปภาพ (JPG, PNG) → ข้อความ
- ✅ รองรับภาษาไทยและภาษาอื่นๆ มากกว่า 100 ภาษา

**หมายเหตุ:** Tesseract ทำงานร่วมกับ Poppler (ต้องติดตั้งทั้งคู่)

---

## 🚀 วิธีติดตั้ง Tesseract (Windows)

### วิธีที่ 1: ดาวน์โหลด Installer (แนะนำ) ⭐

#### ขั้นตอนที่ 1: ดาวน์โหลด Tesseract

1. ไปที่: https://github.com/UB-Mannheim/tesseract/wiki
2. คลิก: **"Tesseract at UB Mannheim"**
3. ดาวน์โหลด: `tesseract-ocr-w64-setup-X.X.X.XXXXXXXX.exe` (เวอร์ชัน 64-bit)
   - ตัวอย่าง: `tesseract-ocr-w64-setup-5.3.3.20231005.exe`
4. ขนาดไฟล์ประมาณ 50-60 MB

#### ขั้นตอนที่ 2: ติดตั้ง

1. **Run Installer** (double-click ไฟล์ `.exe`)
2. ที่หน้า **"Choose Components"**:
   - ✅ เลือก **"Additional language data (download)"**
   - ✅ เลือก **"Thai"** (ภาษาไทย)
   - ✅ เลือก **"English"** (อังกฤษ - default)
3. เลือก Installation Path:
   ```
   C:\Program Files\Tesseract-OCR
   ```
   (แนะนำใช้ path default)
4. คลิก **"Install"**
5. รอจนติดตั้งเสร็จ (อาจต้องดาวน์โหลด language data)
6. คลิก **"Finish"**

#### ขั้นตอนที่ 3: เพิ่มเข้า PATH (Optional)

**วิธีที่ 1: ผ่าน GUI**

1. กด `Windows + R`
2. พิมพ์: `sysdm.cpl` → Enter
3. แท็บ "Advanced" → "Environment Variables..."
4. ที่ "System variables" → เลือก "Path" → "Edit..."
5. "New" → เพิ่ม: `C:\Program Files\Tesseract-OCR`
6. OK ทั้งหมด
7. รีสตาร์ท Terminal/PowerShell

**วิธีที่ 2: ผ่าน PowerShell (Admin)**

```powershell
# เปิด PowerShell as Administrator
[Environment]::SetEnvironmentVariable(
    "Path",
    [Environment]::GetEnvironmentVariable("Path", "Machine") + ";C:\Program Files\Tesseract-OCR",
    "Machine"
)
```

**วิธีที่ 3: ระบุใน `.env` (ไม่ต้องแก้ PATH) - แนะนำ**

สร้าง/แก้ไขไฟล์ `.env`:

```env
# Tesseract Path
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
```

#### ขั้นตอนที่ 4: ตรวจสอบการติดตั้ง

เปิด **Terminal ใหม่**:

```bash
# ทดสอบ Tesseract
tesseract --version
```

**ผลลัพธ์ที่ถูกต้อง:**
```
tesseract 5.3.3
 leptonica-1.83.1
  libgif 5.2.1 : libjpeg 8d (libjpeg-turbo 2.1.5.1) : libpng 1.6.40 : libtiff 4.6.0 : zlib 1.3 : libwebp 1.3.2 : libopenjp2 2.5.0
 Found AVX2
 Found AVX
 Found FMA
 Found SSE4.1
 Found OpenMP 201511
```

**ตรวจสอบภาษาที่ติดตั้ง:**
```bash
tesseract --list-langs
```

**ควรเห็น:**
```
List of available languages (3):
eng
osd
tha
```

#### ขั้นตอนที่ 5: รีสตาร์ท Flask App

```bash
# กด Ctrl+C ใน Terminal ที่รัน app.py
# รันใหม่
python app.py
```

ควรเห็น:
```
✓ Tesseract found: C:\Program Files\Tesseract-OCR\tesseract.exe
```

#### ขั้นตอนที่ 6: ทดสอบ OCR

1. ไปที่ `http://localhost:5000`
2. อัปโหลด PDF ที่เป็นภาพสแกน
3. คลิก "แปลงไฟล์เป็นข้อความ"
4. ถ้าสำเร็จจะเห็น:
   - ✅ ข้อความที่แปลงได้
   - ✅ ไม่มี error `tesseract is not installed`
   - ✅ มีไอคอน 🔍 แสดงว่าใช้ OCR

---

### วิธีที่ 2: ใช้ Conda (ถ้ามี Anaconda/Miniconda)

```bash
conda install -c conda-forge tesseract -y
```

จากนั้นรีสตาร์ท Flask app

---

### วิธีที่ 3: ใช้ Chocolatey

ถ้ามี [Chocolatey](https://chocolatey.org/) ติดตั้งอยู่แล้ว:

```bash
choco install tesseract -y
```

---

## 🔍 การตรวจสอบ

### ตรวจสอบว่า Tesseract ทำงานหรือไม่

```bash
# ดูเวอร์ชัน
tesseract --version

# ดูภาษาที่รองรับ
tesseract --list-langs

# ทดสอบ OCR (ถ้ามีรูปภาพ)
tesseract test.png output -l tha+eng
```

### ตรวจสอบว่าโปรเจกต์เห็น Tesseract

เพิ่ม debug code ใน Python:

```python
import pytesseract
import os

# ตรวจสอบ Tesseract command
try:
    version = pytesseract.get_tesseract_version()
    print(f"✓ Tesseract version: {version}")
except:
    print("✗ Tesseract not found")

# ตรวจสอบ TESSERACT_PATH
tesseract_path = os.getenv('TESSERACT_PATH')
if tesseract_path:
    print(f"✓ TESSERACT_PATH set: {tesseract_path}")
else:
    print("✗ TESSERACT_PATH not set")
```

---

## 🐛 Troubleshooting

### ปัญหา 1: tesseract command not found

**สาเหตุ:**
- Tesseract ไม่ได้ติดตั้ง
- หรือ PATH ไม่ถูกต้อง
- หรือยังไม่ได้รีสตาร์ท Terminal

**แก้ไข:**
1. เช็คว่าไฟล์ `tesseract.exe` มีอยู่ไหม:
   ```bash
   dir "C:\Program Files\Tesseract-OCR\tesseract.exe"
   ```

2. ถ้ามี → ใช้วิธีระบุใน `.env`:
   ```env
   TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
   ```

3. ถ้าไม่มี → ต้องติดตั้ง Tesseract ใหม่

### ปัญหา 2: ไม่มีภาษาไทย (tha)

**สาเหตุ:**
- ไม่ได้เลือก Thai language data ตอนติดตั้ง

**แก้ไข:**

**วิธีที่ 1: ติดตั้งใหม่** (แนะนำ)
- Uninstall Tesseract
- ติดตั้งใหม่ เลือก "Thai" ที่หน้า Components

**วิธีที่ 2: ดาวน์โหลด Language Data**
1. ดาวน์โหลด: https://github.com/tesseract-ocr/tessdata/raw/main/tha.traineddata
2. คัดลอกไปที่: `C:\Program Files\Tesseract-OCR\tessdata\`
3. รีสตาร์ท Flask app

### ปัญหา 3: OCR ได้แต่ไม่ถูกต้อง

**สาเหตุ:**
- รูปภาพคุณภาพต่ำ
- ขนาดตัวอักษรเล็กเกินไป
- มีเงาหรือสิ่งรบกวน

**แก้ไข:**
- ปรับความละเอียดของ PDF ให้สูงขึ้น (300 DPI)
- ใช้ภาพที่มีคอนทราสต์สูง
- แปลงเป็นขาวดำก่อน OCR

### ปัญหา 4: Permission denied

**สาเหตุ:**
- ไม่มีสิทธิ์ติดตั้งที่ `C:\Program Files\`

**แก้ไข:**
- Run Installer as Administrator
- หรือติดตั้งที่อื่น เช่น `C:\Tesseract-OCR`

---

## 📊 การตั้งค่าเพิ่มเติม

### ปรับแต่ง OCR Quality

ใน `extractors/pdf_text_extractor.py`:

```python
# Config ขั้นสูง
custom_config = r'--oem 3 --psm 6'
text = pytesseract.image_to_string(image, lang='tha+eng', config=custom_config)
```

**PSM Modes:**
- `3` = Fully automatic page segmentation (default)
- `6` = Uniform block of text
- `11` = Sparse text
- `13` = Raw line

**OEM Modes:**
- `0` = Legacy engine only
- `1` = Neural nets LSTM engine only
- `2` = Legacy + LSTM engines
- `3` = Default (Based on what is available)

### เพิ่มภาษาอื่น

ดาวน์โหลดจาก:
- https://github.com/tesseract-ocr/tessdata

Language codes:
- `tha` = ไทย
- `eng` = อังกฤษ
- `chi_sim` = จีนตัวย่อ
- `jpn` = ญี่ปุ่น
- `kor` = เกาหลี

---

## ✅ Checklist สำหรับ OCR

เช็คให้ครบก่อนใช้งาน:

- [ ] ติดตั้ง **Poppler** แล้ว (PDF → Image)
- [ ] ติดตั้ง **Tesseract** แล้ว (Image → Text)
- [ ] เลือกภาษาไทย (Thai) ตอนติดตั้ง
- [ ] ทดสอบ `tesseract --version` ได้ผลลัพธ์
- [ ] ทดสอบ `tesseract --list-langs` เห็น `tha`
- [ ] รีสตาร์ท Flask app
- [ ] เห็น `✓ Tesseract found:` ใน Terminal
- [ ] ทดสอบอัปโหลด PDF → ไม่มี OCR error

---

## 💡 Tips

### สำหรับ Development

ใส่ใน `.env`:
```env
# Tesseract path (ไม่ต้องแก้ PATH ระบบ)
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe

# Poppler path
POPPLER_PATH=C:\Program Files\poppler\Library\bin
```

### สำหรับ Production

- **Windows Server**: ติดตั้ง Tesseract แล้วเพิ่มเข้า System PATH
- **Linux**: 
  ```bash
  sudo apt-get install tesseract-ocr tesseract-ocr-tha
  ```
- **macOS**: 
  ```bash
  brew install tesseract tesseract-lang
  ```
- **Docker**: เพิ่มใน Dockerfile:
  ```dockerfile
  RUN apt-get update && apt-get install -y \
      tesseract-ocr \
      tesseract-ocr-tha \
      libtesseract-dev
  ```

---

## 🔗 ลิงก์ที่เป็นประโยชน์

- **Tesseract for Windows**: https://github.com/UB-Mannheim/tesseract/wiki
- **Tesseract Official**: https://github.com/tesseract-ocr/tesseract
- **Language Data**: https://github.com/tesseract-ocr/tessdata
- **pytesseract Docs**: https://github.com/madmaze/pytesseract

---

## 📞 ยังมีปัญหา?

ถ้ายังแก้ไม่ได้:

1. ตรวจสอบว่า `tesseract.exe` มีอยู่จริง
2. ตรวจสอบว่ามี `tha.traineddata` ใน `tessdata/`
3. ลองใช้ `.env` method
4. ดู Terminal logs อีกครั้ง

---

## 🎯 สรุป: ต้องติดตั้งทั้งคู่

สำหรับ OCR ต้องมี:

1. **Poppler** → แปลง PDF เป็นรูปภาพ
2. **Tesseract** → แปลงรูปภาพเป็นข้อความ

```
PDF → [Poppler] → Image → [Tesseract] → Text
```

---

**Happy OCR-ing! 🔍✨**


