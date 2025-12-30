# 🔧 Quick Setup - Poppler (สำหรับ OCR)

## ⚠️ ปัญหา

เมื่ออัปโหลด PDF ที่ต้องการ OCR จะเห็น error:
```
OCR error on page 0: Unable to get page count. Is poppler installed and in PATH?
```

## 📌 Poppler คืออะไร?

**Poppler** คือ library สำหรับแปลง PDF เป็นรูปภาพ จำเป็นสำหรับ:
- ✅ แปลง PDF ที่เป็นภาพสแกน → ข้อความ (OCR)
- ✅ แปลงไฟล์รูปภาพ (JPG, PNG) → ข้อความ
- ✅ ทำ OCR ในกรณีที่ PDF ไม่มี text layer

**หมายเหตุ:** ถ้า PDF มี text อยู่แล้ว (ไม่ใช่ภาพสแกน) จะใช้งานได้ปกติ **ไม่จำเป็นต้องติดตั้ง Poppler**

## 🚀 วิธีติดตั้ง Poppler (Windows)

### วิธีที่ 1: ดาวน์โหลด Binary (แนะนำ) ⭐

#### ขั้นตอนที่ 1: ดาวน์โหลด Poppler

1. ไปที่: https://github.com/oschwartz10612/poppler-windows/releases/
2. ดาวน์โหลด **Release-XX.XX.X-0.zip** (เวอร์ชันล่าสุด)
   - ตัวอย่าง: `Release-24.08.0-0.zip`
3. ขนาดไฟล์ประมาณ 20-30 MB

#### ขั้นตอนที่ 2: แตกไฟล์

1. แตกไฟล์ ZIP ที่ดาวน์โหลดมา
2. คัดลอกโฟลเดอร์ `poppler-XX.XX.X` ไปวางที่:
   ```
   C:\Program Files\poppler
   ```
   
   หรือที่อื่นก็ได้ เช่น:
   - `C:\poppler`
   - `C:\Users\Public\poppler`
   - `D:\Tools\poppler`

3. โครงสร้างโฟลเดอร์จะเป็น:
   ```
   C:\Program Files\poppler\
   └── Library\
       └── bin\
           ├── pdfinfo.exe
           ├── pdftoppm.exe
           ├── pdfimages.exe
           └── ... (ไฟล์อื่นๆ)
   ```

#### ขั้นตอนที่ 3: เพิ่ม Poppler เข้า PATH

**วิธีที่ 1: ผ่าน GUI (ง่ายที่สุด)**

1. กด `Windows + R`
2. พิมพ์: `sysdm.cpl`
3. กด Enter
4. ไปที่แท็บ **"Advanced"**
5. คลิก **"Environment Variables..."**
6. ที่ส่วน **"System variables"** หา **"Path"**
7. คลิก **"Edit..."**
8. คลิก **"New"**
9. เพิ่ม: `C:\Program Files\poppler\Library\bin`
   - (ปรับตาม path ที่คุณแตกไฟล์)
10. คลิก **OK** ทั้งหมด
11. **รีสตาร์ท Terminal/PowerShell**

**วิธีที่ 2: ผ่าน PowerShell (รวดเร็ว)**

เปิด PowerShell **as Administrator**:

```powershell
# แก้ไข path ตามที่คุณแตกไฟล์
$popplerPath = "C:\Program Files\poppler\Library\bin"

# เพิ่มเข้า System PATH
[Environment]::SetEnvironmentVariable(
    "Path",
    [Environment]::GetEnvironmentVariable("Path", "Machine") + ";$popplerPath",
    "Machine"
)

Write-Host "✓ Poppler added to PATH successfully!" -ForegroundColor Green
Write-Host "Please restart your terminal/IDE" -ForegroundColor Yellow
```

**วิธีที่ 3: ระบุ Path ใน .env (ไม่ต้องแก้ PATH ระบบ)**

สร้างหรือแก้ไขไฟล์ `.env`:

```env
# Poppler Path (Windows)
POPPLER_PATH=C:\Program Files\poppler\Library\bin
```

#### ขั้นตอนที่ 4: ตรวจสอบการติดตั้ง

เปิด **Terminal ใหม่** (สำคัญ!):

```bash
# ทดสอบ Poppler
pdfinfo -v
```

**ผลลัพธ์ที่ถูกต้อง:**
```
pdfinfo version 24.08.0
Copyright 2005-2024 The Poppler Developers - http://poppler.freedesktop.org
Copyright 1996-2011 Glyph & Cog, LLC
```

**ถ้าได้ error:**
```
'pdfinfo' is not recognized as an internal or external command...
```
→ แสดงว่า PATH ยังไม่ถูกต้อง ลองใหม่อีกครั้งหรือรีสตาร์ทเครื่อง

#### ขั้นตอนที่ 5: รีสตาร์ท Flask App

```bash
# กด Ctrl+C ใน Terminal ที่รัน app.py
# รันใหม่
python app.py
```

#### ขั้นตอนที่ 6: ทดสอบ OCR

1. ไปที่ `http://localhost:5000`
2. อัปโหลด PDF ที่เป็นภาพสแกน
3. คลิก "แปลงไฟล์เป็นข้อความ"
4. ถ้าสำเร็จจะเห็น:
   - ✅ ข้อความที่แปลงได้
   - ✅ ไม่มี error `OCR error on page X`
   - ✅ มีไอคอน 🔍 แสดงว่าใช้ OCR

---

### วิธีที่ 2: ใช้ Conda (ถ้ามี Anaconda/Miniconda)

```bash
conda install -c conda-forge poppler
```

จากนั้นรีสตาร์ท Flask app

---

### วิธีที่ 3: ใช้ Scoop (Package Manager)

ถ้ามี [Scoop](https://scoop.sh/) ติดตั้งอยู่แล้ว:

```bash
scoop install poppler
```

---

### วิธีที่ 4: ใช้ Chocolatey

ถ้ามี [Chocolatey](https://chocolatey.org/) ติดตั้งอยู่แล้ว:

```bash
choco install poppler
```

---

## 🔍 การตรวจสอบ

### ตรวจสอบว่า Poppler ทำงานหรือไม่

```bash
# ดูเวอร์ชัน
pdfinfo -v

# ดู PATH
echo $env:Path

# ตรวจสอบว่ามี pdfinfo.exe
where pdfinfo
```

### ตรวจสอบว่าโปรเจกต์เห็น Poppler

เพิ่ม debug code ใน Python:

```python
import os
import shutil

# ตรวจสอบ pdfinfo
poppler = shutil.which('pdfinfo')
if poppler:
    print(f"✓ Poppler found: {poppler}")
else:
    print("✗ Poppler not found in PATH")

# ตรวจสอบ POPPLER_PATH
poppler_path = os.getenv('POPPLER_PATH')
if poppler_path:
    print(f"✓ POPPLER_PATH set: {poppler_path}")
else:
    print("✗ POPPLER_PATH not set")
```

---

## 🐛 Troubleshooting

### ปัญหา 1: pdfinfo command not found

**สาเหตุ:**
- Poppler ไม่ได้ติดตั้ง
- หรือ PATH ไม่ถูกต้อง
- หรือยังไม่ได้รีสตาร์ท Terminal

**แก้ไข:**
1. เช็คว่าไฟล์ `pdfinfo.exe` มีอยู่ไหม:
   ```bash
   dir "C:\Program Files\poppler\Library\bin\pdfinfo.exe"
   ```

2. ถ้ามี → ปัญหาอยู่ที่ PATH
   - ลองเพิ่ม PATH อีกครั้ง
   - หรือใช้วิธีระบุใน `.env`

3. ถ้าไม่มี → ต้องดาวน์โหลด Poppler ใหม่

### ปัญหา 2: ยังเห็น OCR error แม้ติดตั้งแล้ว

**แก้ไข:**
1. **รีสตาร์ท Terminal** (สำคัญมาก!)
2. **รีสตาร์ท Flask app** (กด Ctrl+C แล้วรันใหม่)
3. **รีสตาร์ท IDE** (VSCode, PyCharm, etc.)
4. ถ้ายังไม่ได้ → **รีสตาร์ทเครื่อง**

### ปัญหา 3: Permission denied

**สาเหตุ:**
- ติดตั้งใน `C:\Program Files\` แต่ไม่มีสิทธิ์

**แก้ไข:**
- ติดตั้งที่อื่นแทน เช่น `C:\poppler` หรือ `C:\Users\YourName\poppler`
- หรือรัน PowerShell as Administrator

### ปัญหา 4: Path มีช่องว่าง (spaces)

**ปัญหา:**
```
C:\Program Files\poppler\Library\bin
```

**แก้ไข:**
- ใช้ quotes: `"C:\Program Files\poppler\Library\bin"`
- หรือย้ายไปที่ไม่มีช่องว่าง: `C:\poppler\Library\bin`

---

## 📊 เปรียบเทียบวิธีติดตั้ง

| วิธี | ข้อดี | ข้อเสีย |
|------|-------|---------|
| **Binary** | ✅ ควบคุมเวอร์ชันได้<br>✅ ไม่ต้องติดตั้งอะไรเพิ่ม | ❌ ต้องเพิ่ม PATH เอง |
| **Conda** | ✅ ง่ายที่สุด<br>✅ จัดการเวอร์ชันอัตโนมัติ | ❌ ต้องมี Conda |
| **Scoop** | ✅ อัปเดตง่าย | ❌ ต้องติดตั้ง Scoop ก่อน |
| **.env** | ✅ ไม่ต้องแก้ PATH ระบบ | ❌ ต้องระบุทุกโปรเจกต์ |

---

## ✅ Checklist

เช็คให้ครบก่อนใช้งาน:

- [ ] ดาวน์โหลด Poppler
- [ ] แตกไฟล์ไปที่ `C:\Program Files\poppler`
- [ ] เพิ่ม `C:\Program Files\poppler\Library\bin` เข้า PATH
- [ ] เปิด Terminal ใหม่
- [ ] ทดสอบ `pdfinfo -v` ได้ผลลัพธ์
- [ ] รีสตาร์ท Flask app
- [ ] ทดสอบอัปโหลด PDF → ไม่มี OCR error

---

## 💡 Tips

### สำหรับ Development

ใส่ใน `.env`:
```env
# ระบุ Poppler path (ไม่ต้องแก้ PATH ระบบ)
POPPLER_PATH=C:\Program Files\poppler\Library\bin
```

### สำหรับ Production

- **Windows Server**: ติดตั้ง Poppler แล้วเพิ่มเข้า System PATH
- **Linux**: `sudo apt-get install poppler-utils`
- **macOS**: `brew install poppler`
- **Docker**: เพิ่มใน Dockerfile:
  ```dockerfile
  RUN apt-get update && apt-get install -y poppler-utils
  ```

---

## 🔗 ลิงก์ที่เป็นประโยชน์

- **Poppler for Windows**: https://github.com/oschwartz10612/poppler-windows/releases/
- **Poppler Official**: https://poppler.freedesktop.org/
- **pdf2image Docs**: https://github.com/Belval/pdf2image

---

## 📞 ยังมีปัญหา?

ถ้ายังแก้ไม่ได้:

1. ดู Terminal logs อีกครั้ง
2. ตรวจสอบว่า pdfinfo.exe มีอยู่จริง
3. ลองใช้ `.env` method แทน
4. ติดต่อ: (อีเมล/GitHub issue)

---

**Happy OCR-ing! 🔍✨**


