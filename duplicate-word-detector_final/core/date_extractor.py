"""
Date Extractor for Thai Documents
ระบบดึงวันที่จากเอกสารภาษาไทย (รองรับทั้งตัวเลขไทยและอารบิก)
"""

import re
from datetime import datetime, date
from typing import Optional, List, Tuple
import unicodedata


class ThaiDateExtractor:
    """Extract และ parse วันที่จากข้อความภาษาไทย"""
    
    def __init__(self):
        # Mapping ตัวเลขไทยเป็นตัวเลขอารบิก
        self.thai_digit_map = {
            '๐': '0', '๑': '1', '๒': '2', '๓': '3', '๔': '4',
            '๕': '5', '๖': '6', '๗': '7', '๘': '8', '๙': '9'
        }
        
        # ชื่อเดือนภาษาไทย
        self.thai_months = {
            'มกราคม': 1, 'ม.ค.': 1,
            'กุมภาพันธ์': 2, 'ก.พ.': 2,
            'มีนาคม': 3, 'มี.ค.': 3,
            'เมษายน': 4, 'เม.ย.': 4,
            'พฤษภาคม': 5, 'พ.ค.': 5,
            'มิถุนายน': 6, 'มิ.ย.': 6,
            'กรกฎาคม': 7, 'ก.ค.': 7,
            'สิงหาคม': 8, 'ส.ค.': 8,
            'กันยายน': 9, 'ก.ย.': 9,
            'ตุลาคม': 10, 'ต.ค.': 10,
            'พฤศจิกายน': 11, 'พ.ย.': 11,
            'ธันวาคม': 12, 'ธ.ค.': 12
        }
    
    def normalize_thai_digits(self, text: str) -> str:
        """แปลงตัวเลขไทยเป็นตัวเลขอารบิก"""
        result = []
        for char in text:
            if char in self.thai_digit_map:
                result.append(self.thai_digit_map[char])
            else:
                result.append(char)
        return ''.join(result)
    
    def extract_dates_from_text(self, text: str) -> List[Tuple[str, date]]:
        """
        ดึงวันที่ทั้งหมดจากข้อความ
        
        Returns:
            List[Tuple[str, date]] - รายการ (matched_text, parsed_date)
        """
        dates = []
        
        # Pattern 1: "2 เมษายน ๒๕๒๕" หรือ "๒ เมษายน ๒๕๒๕"
        # รองรับทั้งตัวเลขไทย (๐-๙) และตัวเลขอารบิก (0-9)
        pattern1 = r'([๐๑๒๓๔๕๖๗๘๙\d]{1,2})\s+(มกราคม|กุมภาพันธ์|มีนาคม|เมษายน|พฤษภาคม|มิถุนายน|กรกฎาคม|สิงหาคม|กันยายน|ตุลาคม|พฤศจิกายน|ธันวาคม|ม\.ค\.|ก\.พ\.|มี\.ค\.|เม\.ย\.|พ\.ค\.|มิ\.ย\.|ก\.ค\.|ส\.ค\.|ก\.ย\.|ต\.ค\.|พ\.ย\.|ธ\.ค\.)\s+([๐๑๒๓๔๕๖๗๘๙\d]{4})'
        
        for match in re.finditer(pattern1, text, re.IGNORECASE):
            day_str = match.group(1)
            month_str = match.group(2)
            year_str = match.group(3)
            
            try:
                # แปลงตัวเลขไทย
                day_str = self.normalize_thai_digits(day_str)
                year_str = self.normalize_thai_digits(year_str)
                
                # แปลงชื่อเดือน
                month = self.thai_months.get(month_str.lower(), None)
                if month is None:
                    continue
                
                day = int(day_str)
                year = int(year_str)
                
                # แปลงปี พ.ศ. เป็น ค.ศ. (ถ้าปีมากกว่า 2500 ให้ถือว่าเป็น พ.ศ.)
                if year > 2500:
                    year = year - 543
                
                parsed_date = date(year, month, day)
                dates.append((match.group(0), parsed_date))
                
            except (ValueError, KeyError):
                continue
        
        # Pattern 2: "2/4/2525" หรือ "๒/๔/๒๕๒๕" (วัน/เดือน/ปี)
        # รองรับทั้งตัวเลขไทยและอารบิก
        pattern2 = r'([๐๑๒๓๔๕๖๗๘๙\d]{1,2})[/\-\.]([๐๑๒๓๔๕๖๗๘๙\d]{1,2})[/\-\.]([๐๑๒๓๔๕๖๗๘๙\d]{4})'
        
        for match in re.finditer(pattern2, text):
            day_str = match.group(1)
            month_str = match.group(2)
            year_str = match.group(3)
            
            try:
                day_str = self.normalize_thai_digits(day_str)
                month_str = self.normalize_thai_digits(month_str)
                year_str = self.normalize_thai_digits(year_str)
                
                day = int(day_str)
                month = int(month_str)
                year = int(year_str)
                
                # แปลงปี พ.ศ. เป็น ค.ศ.
                if year > 2500:
                    year = year - 543
                
                parsed_date = date(year, month, day)
                dates.append((match.group(0), parsed_date))
                
            except ValueError:
                continue
        
        # Pattern 3: "2 เมษายน 2025" (ปี ค.ศ.)
        # รองรับตัวเลขไทยและอารบิกสำหรับวัน
        pattern3 = r'([๐๑๒๓๔๕๖๗๘๙\d]{1,2})\s+(มกราคม|กุมภาพันธ์|มีนาคม|เมษายน|พฤษภาคม|มิถุนายน|กรกฎาคม|สิงหาคม|กันยายน|ตุลาคม|พฤศจิกายน|ธันวาคม|ม\.ค\.|ก\.พ\.|มี\.ค\.|เม\.ย\.|พ\.ค\.|มิ\.ย\.|ก\.ค\.|ส\.ค\.|ก\.ย\.|ต\.ค\.|พ\.ย\.|ธ\.ค\.)\s+(19|20)\d{2}'
        
        for match in re.finditer(pattern3, text, re.IGNORECASE):
            day_str = match.group(1)
            month_str = match.group(2)
            year_str = match.group(3)
            
            try:
                day_str = self.normalize_thai_digits(day_str)
                month = self.thai_months.get(month_str.lower(), None)
                if month is None:
                    continue
                
                day = int(day_str)
                year = int(year_str)
                
                parsed_date = date(year, month, day)
                dates.append((match.group(0), parsed_date))
                
            except (ValueError, KeyError):
                continue
        
        return dates
    
    def extract_primary_date(self, text: str, prefer_circled: bool = True) -> Optional[date]:
        """
        ดึงวันที่หลักจากข้อความ (โดยเฉพาะวันที่ถูกวงกลมหรือเน้น)
        
        Args:
            text: ข้อความที่ต้องการค้นหา
            prefer_circled: ถ้า True จะพยายามหาวันที่ที่ถูกวงกลมหรือเน้นไว้
        
        Returns:
            date object หรือ None
        """
        dates = self.extract_dates_from_text(text)
        
        if not dates:
            return None
        
        # ถ้า prefer_circled ให้หาวันที่ที่อาจถูกวงกลม
        # (ในข้อความที่ OCR มา อาจมีรูปแบบพิเศษหรืออยู่ในตำแหน่งพิเศษ)
        if prefer_circled:
            # ตรวจสอบวันที่ที่อยู่ในบรรทัดแรกหรือบริเวณ header
            lines = text.split('\n')
            header_text = '\n'.join(lines[:10])  # 10 บรรทัดแรก
            
            header_dates = []
            for matched_text, parsed_date in dates:
                if matched_text in header_text:
                    header_dates.append((matched_text, parsed_date))
            
            if header_dates:
                # เลือกวันที่ที่อยู่ซ้ายสุด (มักจะเป็นวันที่เอกสาร)
                # หรือวันที่แรกสุดที่เจอ
                return header_dates[0][1]
        
        # ถ้าไม่เจอใน header หรือไม่ต้องการ prefer_circled
        # คืนค่าวันที่แรกที่เจอ
        return dates[0][1]
    
    def extract_document_date(self, text: str) -> Optional[date]:
        """
        ดึงวันที่เอกสารจากข้อความ (วันที่ใน header/meta area)
        มักจะอยู่ในบรรทัดแรกๆ ของเอกสาร
        """
        # แบ่งเป็นบรรทัด
        lines = text.split('\n')
        
        # ตรวจสอบ 15 บรรทัดแรก (มักจะมีวันที่เอกสาร)
        header_text = '\n'.join(lines[:15])
        
        # หาวันที่ทั้งหมดใน header
        dates = self.extract_dates_from_text(header_text)
        
        if not dates:
            return None
        
        # คืนค่าวันที่แรกที่เจอ (มักจะเป็นวันที่เอกสาร)
        return dates[0][1]


# Singleton instance
_date_extractor = None

def get_date_extractor() -> ThaiDateExtractor:
    """Get singleton instance of ThaiDateExtractor"""
    global _date_extractor
    if _date_extractor is None:
        _date_extractor = ThaiDateExtractor()
    return _date_extractor

