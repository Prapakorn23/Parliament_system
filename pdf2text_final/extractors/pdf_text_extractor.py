import fitz  # PyMuPDF
from typing import List, Tuple
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image, ImageEnhance, ImageFilter
import io
import re
import os
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# Poppler configuration
POPPLER_PATH = os.getenv('POPPLER_PATH', None)

# Common Poppler installation paths on Windows
COMMON_POPPLER_PATHS = [
    r'C:\Program Files\poppler\Library\bin',
    r'C:\Program Files (x86)\poppler\Library\bin',
    r'C:\poppler\Library\bin',
    r'C:\Users\Public\poppler\Library\bin',
]

# Tesseract configuration
TESSERACT_PATH = os.getenv('TESSERACT_PATH', None)

# Common Tesseract installation paths on Windows
COMMON_TESSERACT_PATHS = [
    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    r'C:\Tesseract-OCR\tesseract.exe',
    r'C:\Users\Public\Tesseract-OCR\tesseract.exe',
]

def find_poppler_path():
    """Auto-detect Poppler installation path"""
    if POPPLER_PATH:
        return POPPLER_PATH
    
    for path in COMMON_POPPLER_PATHS:
        if os.path.exists(path) and os.path.exists(os.path.join(path, 'pdfinfo.exe')):
            return path
    
    return None

def find_tesseract_path():
    """Auto-detect Tesseract installation path"""
    if TESSERACT_PATH:
        return TESSERACT_PATH
    
    for path in COMMON_TESSERACT_PATHS:
        if os.path.exists(path):
            return path
    
    return None

# Configure Tesseract path
tesseract_exe = find_tesseract_path()
if tesseract_exe:
    pytesseract.pytesseract.tesseract_cmd = tesseract_exe
    try:
        print(f"✓ Tesseract found: {tesseract_exe}")
    except UnicodeEncodeError:
        print(f"[OK] Tesseract found: {tesseract_exe}")
    
    # Check for Thai language support
    try:
        available_langs = pytesseract.get_languages(config='')
        if 'tha' in available_langs:
            try:
                print(f"✓ Thai language (tha) available")
            except UnicodeEncodeError:
                print(f"[OK] Thai language (tha) available")
        else:
            try:
                print(f"⚠️  Thai language NOT found! Available: {', '.join(available_langs)}")
            except UnicodeEncodeError:
                print(f"[WARNING] Thai language NOT found! Available: {', '.join(available_langs)}")
            print(f"💡 Solution:")
            print(f"   1. Reinstall Tesseract and select 'Thai' language")
            print(f"   2. Or download tha.traineddata from:")
            print(f"      https://github.com/tesseract-ocr/tessdata/raw/main/tha.traineddata")
            print(f"   3. Copy to: C:\\Program Files\\Tesseract-OCR\\tessdata\\")
            print(f"   See: QUICK_SETUP_TESSERACT.md for details")
    except Exception as e:
        try:
            print(f"⚠️  Could not check Tesseract languages: {e}")
        except UnicodeEncodeError:
            print(f"[WARNING] Could not check Tesseract languages: {e}")
else:
    try:
        print("⚠️  Tesseract not found in common paths. OCR will not work.")
    except UnicodeEncodeError:
        print("[WARNING] Tesseract not found in common paths. OCR will not work.")
    print("💡 Install from: https://github.com/UB-Mannheim/tesseract/wiki")
    print("   Or set TESSERACT_PATH in .env")


def preprocess_image_for_ocr(image: Image.Image) -> Image.Image:
    """
    ประมวลผลภาพก่อน OCR เพื่อเพิ่มความแม่นยำสำหรับเอกสารภาษาไทย:
    1. แปลงเป็นขาว-ดำ (Grayscale) - ลดข้อมูลที่ไม่จำเป็น
    2. เพิ่ม Contrast - ทำให้ตัวอักษรชัดขึ้น
    3. ปรับ Brightness - ทำให้ภาพสว่างพอเหมาะ
    4. เพิ่ม Sharpness - ทำให้ขอบตัวอักษรคมชัด
    5. ลบ Noise - ลดจุดรบกวน (ใช้เฉพาะเมื่อจำเป็น)
    """
    # ขั้นที่ 1: แปลงเป็นขาว-ดำ (Grayscale)
    if image.mode != 'L':
        image = image.convert('L')
    
    # ขั้นที่ 2: เพิ่ม Contrast (ทำให้ตัวอักษรชัดขึ้น)
    # สำหรับเอกสารที่สแกนมา อาจต้องเพิ่ม contrast มากกว่า
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(3.0)  # เพิ่ม contrast เป็น 3.0 เท่า (เดิม 2.5)
    
    # ขั้นที่ 3: ปรับ Brightness (ถ้าภาพมืดเกินไป)
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(1.2)  # เพิ่ม brightness เป็น 20% (เดิม 15%)
    
    # ขั้นที่ 4: Threshold - แปลงเป็น binary (ขาว-ดำ) เพื่อความชัดเจน
    # ใช้ threshold เพื่อแยกขาว-ดำให้ชัดเจน
    if HAS_NUMPY:
        try:
            img_array = np.array(image)
            # ใช้ threshold ที่ 128 (ค่ากลาง) เพื่อแยกขาว-ดำ
            threshold = 128
            img_array = np.where(img_array > threshold, 255, 0).astype(np.uint8)
            image = Image.fromarray(img_array, mode='L')
        except Exception:
            # ถ้า numpy มีปัญหา ให้ข้ามขั้นตอนนี้
            pass
    
    # ขั้นที่ 5: เพิ่ม Sharpness (ทำให้ขอบตัวอักษรคมชัด)
    # สำคัญมากสำหรับภาษาไทยที่มีตัวอักษรซับซ้อน
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(2.5)  # เพิ่ม sharpness เป็น 2.5 เท่า (เดิม 2.0)
    
    # ขั้นที่ 6: ลบ Noise ด้วย Median Filter (ใช้เฉพาะเมื่อจำเป็น)
    # ลดขนาด filter เพื่อไม่ให้ทำให้ตัวอักษรเบลอ
    image = image.filter(ImageFilter.MedianFilter(size=3))
    
    return image


def fix_thai_spacing(text: str) -> str:
    """
    แก้ไขปัญหาช่องว่างระหว่างตัวอักษรไทยที่เกิดจาก OCR
    เช่น "ก า ร ป ร ะ ชุ ม" -> "การประชุม"
    
    ฟังก์ชันนี้จะ:
    1. ลบช่องว่างระหว่างอักษรไทย (พยัญชนะ, สระ, วรรณยุกต์)
    2. ลบช่องว่างระหว่างตัวเลข
    3. จัดรูปแบบเครื่องหมายวรรคตอนให้เหมาะสม
    4. แก้ไขปัญหาการอ่านผิดพลาดจาก OCR
    """
    if not text:
        return text
    
    # ลบช่องว่างระหว่างอักษรไทย (Unicode range: \u0E00-\u0E7F)
    # รวมพยัญชนะ, สระ, วรรณยุกต์, เลขไทย
    # ทำซ้ำหลายรอบเพื่อให้แน่ใจว่าได้ลบช่องว่างทั้งหมด
    for _ in range(15):  # เพิ่มจาก 10 เป็น 15 รอบ
        text = re.sub(r'([\u0E00-\u0E7F])\s+([\u0E00-\u0E7F])', r'\1\2', text)
    
    # ลบช่องว่างระหว่างตัวเลข (รวมเลขอารบิกและเลขไทย)
    for _ in range(5):
        text = re.sub(r'(\d)\s+(\d)', r'\1\2', text)
        text = re.sub(r'([\u0E50-\u0E59])\s+([\u0E50-\u0E59])', r'\1\2', text)
    
    # แก้ไขปัญหาการอ่านผิดพลาดจาก OCR
    # ลบตัวอักษรแปลกๆ ที่ไม่ใช่ภาษาไทยหรืออังกฤษ
    # เก็บเฉพาะตัวอักษรไทย, อังกฤษ, ตัวเลข, และเครื่องหมายวรรคตอน
    # แต่ต้องระวังไม่ให้ลบตัวอักษรที่ถูกต้อง
    
    # แก้ไขช่องว่างรอบๆ วงเล็บ
    text = re.sub(r'\s*\(\s*', ' (', text)
    text = re.sub(r'\s*\)\s*', ') ', text)
    
    # แก้ไขช่องว่างรอบๆ เครื่องหมายอัญประกาศ
    text = re.sub(r'\s*"\s*', ' "', text)
    text = re.sub(r'\s*"\s*', '" ', text)
    text = re.sub(r"\s*'\s*", " '", text)
    
    # แก้ไขช่องว่างหลังเครื่องหมายวรรคตอน
    text = re.sub(r'\s*,\s*', ', ', text)
    text = re.sub(r'\s*\.\s+', '. ', text)
    
    # แก้ไขปัญหาการอ่านผิดพลาด: ลบช่องว่างที่มากเกินไป
    # เช่น "Q.) .d .d" -> "Q.)"
    text = re.sub(r'([A-Za-z0-9\u0E00-\u0E7F])\s+\.\s+([A-Za-z0-9\u0E00-\u0E7F])', r'\1.\2', text)
    
    # ลบช่องว่างที่เกินไประหว่างคำ (เหลือเพียง 1 ช่องว่าง)
    text = re.sub(r'\s+', ' ', text)
    
    # ลบช่องว่างที่ต้นและท้ายบรรทัด
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(line for line in lines if line)
    
    return text.strip()


def fix_thai_vowel_spacing(text: str) -> str:
    """
    แก้ไขปัญหาการแยกสระ -ำ ที่มีช่องว่างเพิ่ม (เก็บไว้เพื่อ backward compatibility)
    เช่น "จ านวน" -> "จำนวน"
    
    หมายเหตุ: ฟังก์ชันนี้ถูกแทนที่ด้วย fix_thai_spacing() ที่ครอบคลุมกว่า
    """
    # แก้ไขกรณีเฉพาะของคำ "จำนวน" ที่มักพบปัญหา
    # "จ า น ว น" -> "จำนวน"
    text = re.sub(r'จ\s+า\s+น\s+ว\s+น', 'จำนวน', text)
    text = re.sub(r'จ\s+า\s+น\s+ว\s+น\s+ร', 'จำนวนร', text)
    
    # แก้ไขกรณี "จ านวน" -> "จำนวน" (ไม่มีช่องว่างระหว่างพยัญชนะอื่นๆ)
    text = re.sub(r'จ\s+า\s*น\s*ว\s*น', 'จำนวน', text)
    text = re.sub(r'จ\s+า\s*น\s*ว\s*น\s*ร', 'จำนวนร', text)
    
    # แก้ไขกรณีทั่วไป: [พยัญชนะ] [า] [พยัญชนะ] -> [พยัญชนะ][ำ][พยัญชนะ]
    # เช่น "ข าว" -> "ข้าว", "ป าน" -> "ป่าน"
    text = re.sub(r'([ก-๙])\s+า\s+([ก-๙])', r'\1ำ\2', text)
    
    # แก้ไขกรณีที่มีพยัญชนะมากกว่า 1 ตัวหลังสระ า
    text = re.sub(r'([ก-๙])\s+า\s*([ก-๙])\s*([ก-๙])', r'\1ำ\2\3', text)
    
    # แก้ไขกรณีที่มีพยัญชนะมากกว่า 2 ตัวหลังสระ า
    text = re.sub(r'([ก-๙])\s+า\s*([ก-๙])\s*([ก-๙])\s*([ก-๙])', r'\1ำ\2\3\4', text)
    
    # แก้ไขกรณีที่มีพยัญชนะมากกว่า 3 ตัวหลังสระ า
    text = re.sub(r'([ก-๙])\s+า\s*([ก-๙])\s*([ก-๙])\s*([ก-๙])\s*([ก-๙])', r'\1ำ\2\3\4\5', text)
    
    # แก้ไขช่องว่างหลายช่องให้เป็นช่องว่างเดียว
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> Tuple[str, bool, List[dict]]:
    """Extract text from a PDF given as bytes using PyMuPDF.
    
    This function first tries to extract text directly. If no text is found,
    it converts pages to images and uses OCR to extract text.
    
    Returns tuple of (extracted_text, is_ocr_used, pages_data)
    - extracted_text: รวมข้อความทุกหน้า
    - is_ocr_used: ใช้ OCR หรือไม่
    - pages_data: ข้อมูลทีละหน้า [{'page_number': 1, 'text': '...', 'ocr_used': False}, ...]
    """
    text_chunks: List[str] = []
    pages_data: List[dict] = []
    any_ocr_used = False
    
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page_index in range(doc.page_count):
            page = doc.load_page(page_index)
            page_text = page.get_text("text").strip()
            page_ocr_used = False
            
            # If no text found, use OCR
            if not page_text:
                page_text = extract_text_with_ocr(pdf_bytes, page_index)
                if page_text:
                    page_ocr_used = True
                    any_ocr_used = True
            
            # แก้ไขปัญหาช่องว่างระหว่างตัวอักษรไทยสำหรับแต่ละหน้า
            page_text = fix_thai_spacing(page_text)
            
            text_chunks.append(page_text)
            pages_data.append({
                'page_number': page_index + 1,  # เริ่มต้นที่ 1
                'text': page_text,
                'ocr_used': page_ocr_used
            })
    
    # Join pages with separator
    full_text = "\n\n".join(chunk for chunk in text_chunks if chunk)
    
    return full_text, any_ocr_used, pages_data

def extract_text_with_ocr(pdf_bytes: bytes, page_index: int) -> str:
    """Extract text from a specific page using OCR with image preprocessing."""
    try:
        # Find Poppler path
        poppler_path = find_poppler_path()
        
        # Convert PDF page to image with higher DPI for better quality
        # สำหรับเอกสารภาษาไทย ควรใช้ DPI สูงเพื่อความแม่นยำ
        dpi = 400  # เพิ่ม DPI เป็น 400 (เดิม 300) สำหรับความละเอียดสูงสุด
        
        if poppler_path:
            images = convert_from_bytes(
                pdf_bytes, 
                first_page=page_index + 1, 
                last_page=page_index + 1,
                poppler_path=poppler_path,
                dpi=dpi
            )
        else:
            # Try without poppler_path (might work if in system PATH)
            images = convert_from_bytes(
                pdf_bytes, 
                first_page=page_index + 1, 
                last_page=page_index + 1,
                dpi=dpi
            )
        
        if not images:
            return ""
        
        # Preprocess image for better OCR accuracy
        # แปลงเป็นขาว-ดำ + ปรับ contrast/sharpness
        processed_image = preprocess_image_for_ocr(images[0])
        
        # Extract text using Tesseract OCR with preprocessed image
        # ใช้ OCR config ที่เหมาะสมสำหรับเอกสารภาษาไทย
        # PSM modes สำหรับเอกสารภาษาไทย:
        # PSM 6 = Assume a single uniform block of text (เหมาะสำหรับเอกสารที่มีข้อความเป็นบล็อก)
        # PSM 11 = Sparse text (เหมาะสำหรับเอกสารที่มีข้อความกระจัดกระจาย)
        # PSM 3 = Fully automatic page segmentation (default)
        # PSM 1 = Automatic page segmentation with OSD (Orientation and Script Detection)
        # OEM 3 = Default engine (LSTM neural nets) - ดีที่สุดสำหรับภาษาไทย
        
        # ลองใช้ config หลายแบบ โดยเรียงตามความเหมาะสม
        # สำหรับเอกสารภาษาไทยที่เป็นภาพ (scanned document)
        ocr_configs = [
            (r'--oem 3 --psm 6', 'tha+eng'),   # Uniform block + Thai+English (เหมาะที่สุด)
            (r'--oem 3 --psm 6', 'tha'),       # Uniform block + Thai only
            (r'--oem 3 --psm 11', 'tha+eng'),  # Sparse text + Thai+English
            (r'--oem 3 --psm 11', 'tha'),      # Sparse text + Thai only
            (r'--oem 3 --psm 3', 'tha+eng'),   # Fully automatic + Thai+English
            (r'--oem 3 --psm 3', 'tha'),       # Fully automatic + Thai only
            (r'--oem 3 --psm 1', 'tha+eng'),   # Auto OSD + Thai+English
        ]
        
        text = ""
        best_text = ""
        best_thai_count = 0
        
        for config, lang in ocr_configs:
            try:
                # ลองใช้ภาษาไทย
                current_text = pytesseract.image_to_string(
                    processed_image, 
                    lang=lang,
                    config=config
                )
                
                # ตรวจสอบว่าผลลัพธ์มีตัวอักษรไทยหรือไม่
                thai_chars = sum(1 for c in current_text if '\u0E00' <= c <= '\u0E7F')
                
                # ตรวจสอบว่ามีตัวอักษรแปลกๆ หรือไม่ (เช่น ~, ', Q, .d)
                # ถ้ามีตัวอักษรแปลกๆ มากเกินไป แสดงว่าอ่านผิดพลาด
                weird_chars = sum(1 for c in current_text if c in "~'Q.dVl€")
                total_chars = len(current_text.strip())
                weird_ratio = weird_chars / total_chars if total_chars > 0 else 0
                
                # ถ้ามีตัวอักษรไทยมากกว่า best และไม่มีตัวอักษรแปลกๆ มากเกินไป ให้อัพเดท
                if thai_chars > best_thai_count and weird_ratio < 0.3:  # ถ้ามีตัวอักษรแปลกๆ น้อยกว่า 30%
                    best_text = current_text
                    best_thai_count = thai_chars
                
                # ถ้ามีตัวอักษรไทยมากกว่า 20 ตัว และไม่มีตัวอักษรแปลกๆ มากเกินไป แสดงว่าอ่านได้ดีแล้ว
                if thai_chars > 20 and weird_ratio < 0.2:  # ถ้ามีตัวอักษรแปลกๆ น้อยกว่า 20%
                    text = current_text
                    print(f"[SUCCESS] Page {page_index + 1}: Found {thai_chars} Thai characters (config: {config}, lang: {lang})")
                    break
                    
            except Exception as e:
                error_msg = str(e).lower()
                # ถ้าไม่มีภาษาไทย ให้ข้ามไป config ถัดไป
                if "tha" in error_msg or "language" in error_msg or "tessdata" in error_msg:
                    if config == ocr_configs[0][0] and lang == ocr_configs[0][1]:
                        print(f"[WARNING] Page {page_index + 1}: Thai language (tha) not available!")
                        print(f"[ERROR] {e}")
                        print(f"[TIP] Please install Thai language for Tesseract:")
                        print(f"     1. Download: https://github.com/tesseract-ocr/tessdata/raw/main/tha.traineddata")
                        print(f"     2. Copy to: C:\\Program Files\\Tesseract-OCR\\tessdata\\")
                        print(f"     3. Or reinstall Tesseract and select 'Thai' language")
                        print(f"     4. Check available languages: tesseract --list-langs")
                    continue
                else:
                    # Error อื่นๆ ให้ข้ามไป
                    continue
        
        # ถ้ายังไม่มีผลลัพธ์ที่ดี ให้ใช้ best_text
        if not text and best_text:
            text = best_text
            if best_thai_count > 0:
                print(f"[INFO] Page {page_index + 1}: Found {best_thai_count} Thai characters")
        
        # ถ้ายังไม่มีผลลัพธ์เลย ให้ลองใช้ English only
        if not text:
            try:
                text = pytesseract.image_to_string(
                    processed_image, 
                    lang='eng',
                    config=r'--oem 3 --psm 6'
                )
                print(f"[WARNING] Page {page_index + 1}: Using English only (no Thai detected)")
            except Exception as e2:
                print(f"[ERROR] OCR failed on page {page_index + 1}: {e2}")
                text = ""
        
        # แก้ไขปัญหาช่องว่างระหว่างตัวอักษรไทย
        text = fix_thai_spacing(text.strip())
        
        return text
    except Exception as e:
        error_msg = str(e)
        if "poppler" in error_msg.lower() or "unable to get page count" in error_msg.lower():
            print(f"⚠️  OCR error on page {page_index}: Poppler not found!")
            print(f"💡 Solution:")
            print(f"   1. Download Poppler: https://github.com/oschwartz10612/poppler-windows/releases/")
            print(f"   2. Extract to: C:\\Program Files\\poppler")
            print(f"   3. Add to PATH: C:\\Program Files\\poppler\\Library\\bin")
            print(f"   4. Or set POPPLER_PATH in .env")
            print(f"   See: QUICK_SETUP_POPPLER.md for details")
        elif "tesseract" in error_msg.lower():
            print(f"⚠️  OCR error on page {page_index}: Tesseract not found!")
            print(f"💡 Solution:")
            print(f"   1. Download Tesseract: https://github.com/UB-Mannheim/tesseract/wiki")
            print(f"   2. Install to: C:\\Program Files\\Tesseract-OCR")
            print(f"   3. Or set TESSERACT_PATH in .env")
            print(f"   See: QUICK_SETUP_TESSERACT.md for details")
        else:
            print(f"OCR error on page {page_index}: {e}")
        return ""