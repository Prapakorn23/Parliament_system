"""
Configuration file for Parliament Duplicate Word Detector
ไฟล์การตั้งค่าสำหรับระบบตรวจจับคำซ้ำ
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Application Settings
APP_NAME = "Parliament Duplicate Word Detector"
APP_VERSION = "4.0.0"
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))

# File Upload Settings
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'
# ขนาดไฟล์สูงสุด (สามารถตั้งค่าได้ผ่าน environment variable)
MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', '200'))  # Default 200MB
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024  # แปลงเป็น bytes

# Supported File Types
ALLOWED_TEXT_EXTENSIONS = {'.txt', '.text'}
ALLOWED_PDF_EXTENSIONS = {'.pdf'}
ALLOWED_DOC_EXTENSIONS = {'.doc', '.docx'}
ALLOWED_EXTENSIONS = ALLOWED_TEXT_EXTENSIONS | ALLOWED_PDF_EXTENSIONS | ALLOWED_DOC_EXTENSIONS

# Chart Settings
CHART_DPI = 300
CHART_DEFAULT_TOP_N = 10
CHART_COLORS = [
    '#007BFF', '#FF5733', '#FFEB3B', '#4A90E2', '#FF8A65',
    '#FFD54F', '#212121', '#FF7043', '#FFC107', '#FF9800'
]

# Thai Font Settings for Matplotlib
THAI_FONT_CANDIDATES = [
    'Tahoma', 'Arial', 'Microsoft Sans Serif', 'Segoe UI',
    'Calibri', 'Times New Roman', 'Courier New'
]
DEFAULT_FONT = 'DejaVu Sans'

# Analysis Settings
DEFAULT_FILTER_POS = True
DEFAULT_TARGET_POS = None
# Tokenization Settings
# 'newmm': เร็ว ดีสำหรับข้อความทั่วไป (default)
# 'long': แยกวลียาวได้ดีกว่า เช่น "การศึกษาขั้นพื้นฐาน" เป็นคำเดียว (แนะนำ)
# 'deepcut': ใช้ deep learning (ต้องติดตั้ง deepcut)
# 'attacut': ใช้ transformer (ต้องติดตั้ง attacut, ช้าที่สุดแต่แม่นยำที่สุด)
TOKENIZE_ENGINE = os.getenv('TOKENIZE_ENGINE', 'long')  # Default: 'long' สำหรับแยกวลีได้ดีกว่า

# Pagination Settings
DEFAULT_ITEMS_PER_PAGE = 25
ITEMS_PER_PAGE_OPTIONS = [10, 25, 50, 100]

# PDF Processing Settings
PDF_EXTRACTION_TIMEOUT = 300  # seconds
OCR_LANGUAGE = 'tha+eng'
OCR_DPI = 200

# Tesseract Configuration (Windows)
TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Cache Settings
ENABLE_CACHE = True
CACHE_FOLDER = 'cache'

# Performance Settings
ENABLE_PERFORMANCE_TRACKING = True

# Export Settings
EXPORT_CSV_ENCODING = 'utf-8-sig'  # UTF-8 with BOM
EXPORT_TIMESTAMP_FORMAT = '%Y%m%d_%H%M%S'

# Database Configuration (MariaDB)
# MariaDB เป็น fork ของ MySQL และมีความเข้ากันได้สูง
# PyMySQL รองรับทั้ง MariaDB และ MySQL
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 3306))  # Port default ของ MariaDB
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'Duplicate_word')
DB_CHARSET = os.getenv('DB_CHARSET', 'utf8mb4')  # utf8mb4 รองรับ emoji และอักขระพิเศษ

# Session Settings
SECRET_KEY = os.getenv('SECRET_KEY', 'parliament-word-detector-secret-key-2025')

# Logging Settings
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# CORS Settings
CORS_ORIGINS = "*"

# UI Settings
NAVBAR_TITLE = "ระบบตรวจจับคำซ้ำ"
NAVBAR_SUBTITLE = "Duplicate Word Detector"

