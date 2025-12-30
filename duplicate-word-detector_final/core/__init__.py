"""
Core modules for Parliament Duplicate Word Detector
โมดูลหลักสำหรับระบบตรวจจับคำซ้ำรัฐสภา
"""

from .duplicate_word_detector import ThaiDuplicateWordDetector
from .word_categorizer import ParliamentWordCategorizer
from .pdf_processor import PDFProcessor
from .performance_utils import PerformanceTracker, CacheManager, ParallelProcessor, get_performance_summary

__all__ = [
    'ThaiDuplicateWordDetector',
    'ParliamentWordCategorizer',
    'PDFProcessor',
    'PerformanceTracker',
    'CacheManager',
    'ParallelProcessor',
    'get_performance_summary'
]

__version__ = '4.1.0'

