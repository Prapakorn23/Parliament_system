#!/usr/bin/env python3
"""
Test script for ThaiDateExtractor
ทดสอบการ extract วันที่จากข้อความภาษาไทย
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.date_extractor import ThaiDateExtractor
from datetime import date

def test_date_extraction():
    """ทดสอบการ extract วันที่"""
    extractor = ThaiDateExtractor()
    
    # Test cases
    test_cases = [
        # (input_text, expected_date, description)
        ("2 เมษายน ๒๕๒๕", date(1982, 4, 2), "วันที่ไทยแบบเต็ม (ตัวเลขไทย)"),
        ("๒ เมษายน ๒๕๒๕", date(1982, 4, 2), "วันที่ไทยแบบเต็ม (ตัวเลขไทย 2)"),
        ("2 เมษายน 2567", date(2024, 4, 2), "วันที่ไทยแบบเต็ม (ตัวเลขอารบิก)"),
        ("15 มกราคม 2567", date(2024, 1, 15), "วันที่ 15 มกราคม"),
        ("2/4/2525", date(1982, 4, 2), "วันที่แบบสั้น (พ.ศ.)"),
        ("2/4/2024", date(2024, 4, 2), "วันที่แบบสั้น (ค.ศ.)"),
        ("ที่ นร ๐๕๐๓/๒\n2 เมษายน ๒๕๒๕\nสำนักงานเลขาธิการ", date(1982, 4, 2), "วันที่ในเอกสาร (แบบมี header)"),
        ("2 เม.ย. 2567", date(2024, 4, 2), "เดือนแบบย่อ"),
    ]
    
    print("=" * 70)
    print("🧪 Testing ThaiDateExtractor")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for input_text, expected_date, description in test_cases:
        print(f"\n📝 Test: {description}")
        print(f"   Input: {input_text}")
        print(f"   Expected: {expected_date}")
        
        extracted_date = extractor.extract_primary_date(input_text)
        
        if extracted_date == expected_date:
            print(f"   ✅ PASSED - Extracted: {extracted_date}")
            passed += 1
        else:
            print(f"   ❌ FAILED - Extracted: {extracted_date}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"📊 Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return failed == 0

def test_multiple_dates():
    """ทดสอบการ extract วันที่หลายวันที่"""
    extractor = ThaiDateExtractor()
    
    text = """
    ที่ นร ๐๕๐๓/๒
    2 เมษายน ๒๕๒๕
    อ้างถึง หนังสือสำนักงานเลขาธิการสภาผู้แทนราษฎร ด่วนที่สุด ที่ สม ๐๐๑๔/๕๘๐๓ 
    ลงวันที่ ๓๐ สิงหาคม ๒๕๒๔
    สิ่งที่ส่งมาด้วย สำเนาหนังสือกระทรวงยุติธรรม ด่วนที่สุด ที่ ยะ ๑๑๐๒.๐๑/๒๘๘๔๒ 
    ลงวันที่ ๘ พฤศจิกายน ๒๕๖๔
    """
    
    print("\n" + "=" * 70)
    print("🧪 Testing Multiple Dates Extraction")
    print("=" * 70)
    
    dates = extractor.extract_dates_from_text(text)
    
    print(f"\n📅 Found {len(dates)} dates:")
    for matched_text, parsed_date in dates:
        print(f"   - {matched_text} -> {parsed_date}")
    
    # Test extract_document_date (should get first date in header)
    doc_date = extractor.extract_document_date(text)
    print(f"\n📄 Document date (first in header): {doc_date}")
    
    if doc_date == date(1982, 4, 2):
        print("   ✅ PASSED")
        return True
    else:
        print("   ❌ FAILED")
        return False

if __name__ == '__main__':
    success1 = test_date_extraction()
    success2 = test_multiple_dates()
    
    if success1 and success2:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)

