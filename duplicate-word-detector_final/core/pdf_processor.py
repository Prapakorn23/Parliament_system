"""
PDF Processor with OCR Support + Image Enhancement
ระบบแปลงไฟล์ PDF เป็น text รองรับทั้ง PDF ข้อความและภาพ
เพิ่มระบบปรับปรุงคุณภาพภาพก่อน OCR สำหรับ PDF ที่เบลอ/คุณภาพต่ำ
"""

import os
from typing import Tuple, Optional, List
import io
import numpy as np

# PDF Processing Libraries
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

# OCR Libraries (for image-based PDFs)
try:
    from pdf2image import convert_from_path, convert_from_bytes
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False

try:
    import pytesseract
    from PIL import Image, ImageFilter, ImageEnhance, ImageOps
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

# OpenCV for advanced image preprocessing (optional but recommended)
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


# Auto-detect Poppler path on Windows
POPPLER_PATH = None
if os.name == 'nt':
    _candidates = [
        r'C:\Program Files\poppler-25.12.0\Library\bin',
        r'C:\Program Files\poppler\Library\bin',
        r'C:\Program Files\poppler\bin',
        os.path.expanduser(r'~\poppler-25.12.0\Library\bin'),
        os.path.expanduser(r'~\poppler\Library\bin'),
    ]
    for _p in _candidates:
        if os.path.isfile(os.path.join(_p, 'pdftoppm.exe')):
            POPPLER_PATH = _p
            break
    if POPPLER_PATH:
        print(f"✅ Poppler found: {POPPLER_PATH}")
    else:
        print("⚠️  Poppler not found — OCR for scanned PDF will not work")


class PDFProcessor:
    """ประมวลผลไฟล์ PDF และแปลงเป็น text พร้อมระบบปรับปรุงคุณภาพภาพ"""

    def __init__(self, ocr_dpi: int = 300):
        self.ocr_dpi = ocr_dpi
        self.poppler_path = POPPLER_PATH
        self.supported_methods = self._check_available_libraries()

    def _check_available_libraries(self) -> dict:
        """ตรวจสอบ libraries ที่สามารถใช้งานได้"""
        ocr_ready = PDF2IMAGE_AVAILABLE and PYTESSERACT_AVAILABLE
        if os.name == 'nt' and not self.poppler_path:
            ocr_ready = False
        return {
            'pypdf2': PYPDF2_AVAILABLE,
            'pdfplumber': PDFPLUMBER_AVAILABLE,
            'ocr': ocr_ready,
            'cv2_enhance': CV2_AVAILABLE,
            'poppler_path': self.poppler_path,
        }
    
    def extract_text_from_pdf(self, pdf_path: str) -> Tuple[bool, str, str]:
        """
        แปลง PDF เป็น text โดยลองใช้หลายวิธี
        
        Args:
            pdf_path: path ของไฟล์ PDF
            
        Returns:
            Tuple of (success, text, method_used)
        """
        # ตรวจสอบว่าไฟล์มีอยู่จริง
        if not os.path.exists(pdf_path):
            return False, "", "ไม่พบไฟล์"
        
        # ลองใช้ pdfplumber ก่อน (แม่นยำที่สุด)
        if self.supported_methods['pdfplumber']:
            success, text = self._extract_with_pdfplumber(pdf_path)
            if success and text.strip():
                return True, text, "pdfplumber"
        
        # ลองใช้ PyPDF2
        if self.supported_methods['pypdf2']:
            success, text = self._extract_with_pypdf2(pdf_path)
            if success and text.strip():
                return True, text, "PyPDF2"
        
        # ถ้าไม่สามารถดึง text ได้ ให้ลอง OCR
        if self.supported_methods['ocr']:
            success, text = self._extract_with_ocr(pdf_path)
            if success and text.strip():
                return True, text, "OCR (Tesseract)"
        
        # ถ้า text extraction ได้ข้อความเปล่า และ OCR ไม่พร้อม/ล้มเหลว
        if not self.supported_methods['ocr']:
            return False, "", "PDF นี้เป็นไฟล์สแกน (ภาพ) ต้องใช้ OCR แต่ยังไม่ได้ติดตั้ง กรุณาติดตั้ง: pip install pdf2image pytesseract และ Tesseract-OCR"
        return False, "", "ไม่สามารถแปลง PDF ได้ กรุณาติดตั้ง libraries ที่จำเป็น"
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> Tuple[bool, str]:
        """แปลง PDF ด้วย pdfplumber"""
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return True, text
        except Exception as e:
            print(f"pdfplumber error: {e}")
            return False, ""
    
    def _extract_with_pypdf2(self, pdf_path: str) -> Tuple[bool, str]:
        """แปลง PDF ด้วย PyPDF2"""
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return True, text
        except Exception as e:
            print(f"PyPDF2 error: {e}")
            return False, ""
    
    def _extract_with_ocr(self, pdf_path: str) -> Tuple[bool, str]:
        """แปลง PDF ด้วย OCR พร้อมปรับปรุงคุณภาพภาพก่อน"""
        try:
            convert_kwargs = {'pdf_path': pdf_path, 'dpi': self.ocr_dpi}
            if self.poppler_path:
                convert_kwargs['poppler_path'] = self.poppler_path

            images = convert_from_path(**convert_kwargs)

            text = ""
            total = len(images)
            for i, image in enumerate(images):
                enhanced = self._enhance_image(image)
                page_text = pytesseract.image_to_string(
                    enhanced, lang='tha+eng',
                    config='--oem 3 --psm 6'
                )
                text += page_text + "\n"
                print(f"OCR (enhanced) หน้า {i+1}/{total} เสร็จสิ้น")

            if not text.strip():
                print("OCR enhanced ไม่พบข้อความ ลองแบบ raw...")
                text = ""
                for i, image in enumerate(images):
                    page_text = pytesseract.image_to_string(image, lang='tha+eng')
                    text += page_text + "\n"

            return True, text
        except Exception as e:
            print(f"OCR error: {e}")
            return False, ""

    # ================================================================
    # Image Enhancement Pipeline
    # ================================================================

    def _enhance_image(self, image: 'Image.Image') -> 'Image.Image':
        """
        Pipeline ปรับปรุงคุณภาพภาพก่อน OCR:
        1. แปลงเป็น Grayscale
        2. Upscale ถ้าภาพเล็ก
        3. Denoise (ลด noise)
        4. เพิ่ม Contrast & Sharpness
        5. Binarize (Adaptive threshold)
        6. Deskew (แก้ภาพเอียง)
        """
        if CV2_AVAILABLE:
            return self._enhance_with_cv2(image)
        return self._enhance_with_pillow(image)

    def _enhance_with_cv2(self, image: 'Image.Image') -> 'Image.Image':
        """ปรับปรุงคุณภาพด้วย OpenCV (ผลลัพธ์ดีที่สุด)"""
        img = np.array(image)

        # 1. Grayscale
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        else:
            gray = img

        # 2. Upscale ถ้าภาพเล็กเกินไป (ความสูง < 2000px)
        h, w = gray.shape[:2]
        if h < 2000:
            scale = 2000 / h
            gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

        # 3. Denoise
        denoised = cv2.fastNlMeansDenoising(gray, None, h=15, templateWindowSize=7, searchWindowSize=21)

        # 4. Contrast enhancement (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        contrast = clahe.apply(denoised)

        # 5. Sharpen
        sharpen_kernel = np.array([[-1, -1, -1],
                                    [-1,  9, -1],
                                    [-1, -1, -1]])
        sharpened = cv2.filter2D(contrast, -1, sharpen_kernel)

        # 6. Adaptive threshold (binarization)
        binary = cv2.adaptiveThreshold(
            sharpened, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            blockSize=31, C=10
        )

        # 7. Deskew (แก้ภาพเอียง)
        binary = self._deskew_cv2(binary)

        # 8. Morphological cleaning (ลบ noise จุดเล็กๆ)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

        return Image.fromarray(cleaned)

    def _deskew_cv2(self, image: np.ndarray) -> np.ndarray:
        """แก้ภาพเอียงอัตโนมัติ"""
        try:
            coords = np.column_stack(np.where(image < 128))
            if len(coords) < 100:
                return image
            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
            if abs(angle) < 0.5:
                return image
            h, w = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(
                image, M, (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE
            )
            return rotated
        except Exception:
            return image

    def _enhance_with_pillow(self, image: 'Image.Image') -> 'Image.Image':
        """ปรับปรุงคุณภาพด้วย Pillow (fallback เมื่อไม่มี OpenCV)"""
        # 1. Grayscale
        img = image.convert('L')

        # 2. Upscale ถ้าเล็ก
        w, h = img.size
        if h < 2000:
            scale = 2000 / h
            new_w, new_h = int(w * scale), int(h * scale)
            img = img.resize((new_w, new_h), Image.LANCZOS)

        # 3. Contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)

        # 4. Sharpness
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(2.5)

        # 5. Brightness balance
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.2)

        # 6. Median filter (denoise)
        img = img.filter(ImageFilter.MedianFilter(size=3))

        # 7. Binarize (simple threshold)
        img = img.point(lambda x: 255 if x > 140 else 0, '1')
        img = img.convert('L')

        return img
    
    def extract_text_from_bytes(self, pdf_bytes: bytes) -> Tuple[bool, str, str]:
        """
        แปลง PDF จาก bytes เป็น text
        
        Args:
            pdf_bytes: PDF data เป็น bytes
            
        Returns:
            Tuple of (success, text, method_used)
        """
        try:
            # ลอง pdfplumber ก่อน
            if self.supported_methods['pdfplumber']:
                try:
                    text = ""
                    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                        for page in pdf.pages:
                            page_text = page.extract_text()
                            if page_text:
                                text += page_text + "\n"
                    if text.strip():
                        return True, text, "pdfplumber"
                except:
                    pass
            
            # ลอง PyPDF2
            if self.supported_methods['pypdf2']:
                try:
                    text = ""
                    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    if text.strip():
                        return True, text, "PyPDF2"
                except:
                    pass
            
            # ลอง OCR พร้อม image enhancement (สำหรับ PDF ที่เป็นภาพ)
            if self.supported_methods['ocr']:
                try:
                    convert_kwargs = {'pdf_file': pdf_bytes, 'dpi': self.ocr_dpi}
                    if self.poppler_path:
                        convert_kwargs['poppler_path'] = self.poppler_path
                    images = convert_from_bytes(**convert_kwargs)
                    text = ""
                    for i, image in enumerate(images):
                        enhanced = self._enhance_image(image)
                        page_text = pytesseract.image_to_string(
                            enhanced, lang='tha+eng',
                            config='--oem 3 --psm 6'
                        )
                        text += page_text + "\n"
                    if text.strip():
                        return True, text, "OCR (Tesseract + Enhanced)"
                except:
                    pass
            
            return False, "", "ไม่สามารถแปลง PDF ได้"
            
        except Exception as e:
            return False, "", f"เกิดข้อผิดพลาด: {str(e)}"
    
    def get_installation_instructions(self) -> dict:
        """คำแนะนำการติดตั้ง libraries"""
        instructions = {
            'basic': {
                'missing': [],
                'command': []
            },
            'ocr': {
                'missing': [],
                'command': []
            }
        }
        
        # ตรวจสอบ basic libraries
        if not PDFPLUMBER_AVAILABLE:
            instructions['basic']['missing'].append('pdfplumber')
        if not PYPDF2_AVAILABLE:
            instructions['basic']['missing'].append('PyPDF2')
        
        if instructions['basic']['missing']:
            instructions['basic']['command'] = f"pip install {' '.join(instructions['basic']['missing'])}"
        
        # ตรวจสอบ OCR libraries
        if not PDF2IMAGE_AVAILABLE:
            instructions['ocr']['missing'].append('pdf2image')
        if not PYTESSERACT_AVAILABLE:
            instructions['ocr']['missing'].append('pytesseract')
        
        if instructions['ocr']['missing']:
            instructions['ocr']['command'] = f"pip install {' '.join(instructions['ocr']['missing'])}"
            instructions['ocr']['note'] = "สำหรับ OCR ยังต้องติดตั้ง Tesseract-OCR: https://github.com/tesseract-ocr/tesseract"
        
        return instructions
    
    def check_pdf_type(self, pdf_path: str) -> str:
        """
        ตรวจสอบว่า PDF เป็นแบบ text หรือ image
        
        Returns:
            'text', 'image', หรือ 'unknown'
        """
        try:
            if PDFPLUMBER_AVAILABLE:
                with pdfplumber.open(pdf_path) as pdf:
                    if len(pdf.pages) > 0:
                        text = pdf.pages[0].extract_text()
                        if text and len(text.strip()) > 50:
                            return 'text'
                        else:
                            return 'image'
            return 'unknown'
        except:
            return 'unknown'

