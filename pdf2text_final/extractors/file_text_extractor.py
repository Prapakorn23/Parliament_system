import os
from typing import Optional, Tuple

from extractors.pdf_text_extractor import extract_text_from_pdf_bytes, fix_thai_spacing
from docx import Document
import chardet


def extract_text_from_upload(filename: str, file_bytes: bytes) -> Tuple[str, bool, Optional[list]]:
    """
    Extract text from uploaded file.
    Returns tuple of (extracted_text, is_ocr_used, pages_data)
    - pages_data จะเป็น None สำหรับไฟล์ที่ไม่ใช่ PDF
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".pdf":
        text, is_ocr, pages = extract_text_from_pdf_bytes(file_bytes)
        return text, is_ocr, pages
    if ext == ".docx":
        text = _extract_text_from_docx_bytes(file_bytes)
        return text, False, None
    if ext in (".txt", ".log", ".md"):
        text = _extract_text_from_plaintext_bytes(file_bytes)
        return text, False, None
    if ext in (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"):
        text = _extract_text_from_image_bytes(file_bytes)
        # For images, create single page data
        pages = [{'page_number': 1, 'text': text, 'ocr_used': True}]
        return text, True, pages
    raise ValueError(f"ไม่รองรับประเภทไฟล์: {ext}")


def _extract_text_from_docx_bytes(file_bytes: bytes) -> str:
    from io import BytesIO
    buf = BytesIO(file_bytes)
    doc = Document(buf)
    paragraphs = [p.text for p in doc.paragraphs]
    return "\n".join(p for p in paragraphs if p is not None)


def _extract_text_from_plaintext_bytes(file_bytes: bytes) -> str:
    # Detect encoding then decode
    detection = chardet.detect(file_bytes)
    encoding = detection.get("encoding") or "utf-8"
    try:
        return file_bytes.decode(encoding, errors="replace")
    except Exception:
        return file_bytes.decode("utf-8", errors="replace")


def _extract_text_from_image_bytes(file_bytes: bytes) -> str:
    """Extract text from image using OCR."""
    try:
        from PIL import Image
        import pytesseract
        from io import BytesIO
        
        # Load image from bytes
        image = Image.open(BytesIO(file_bytes))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Preprocess image for better OCR accuracy
        from extractors.pdf_text_extractor import preprocess_image_for_ocr
        processed_image = preprocess_image_for_ocr(image)
        
        # Use pytesseract for OCR with optimized config for Thai
        # PSM 6 = Uniform block of text
        ocr_config = r'--oem 3 --psm 6'
        
        try:
            text = pytesseract.image_to_string(
                processed_image, 
                lang='tha+eng',
                config=ocr_config
            )
        except Exception:
            try:
                # Fallback to English only
                text = pytesseract.image_to_string(
                    processed_image, 
                    lang='eng',
                    config=ocr_config
                )
            except Exception as e:
                raise ValueError(f"OCR failed: {str(e)}")
        
        # แก้ไขปัญหาช่องว่างระหว่างตัวอักษรไทย
        text = fix_thai_spacing(text.strip())
        
        return text
        
    except ImportError:
        raise ValueError("OCR libraries not installed. Please install: pip install Pillow pytesseract")
    except Exception as e:
        raise ValueError(f"OCR failed: {str(e)}")