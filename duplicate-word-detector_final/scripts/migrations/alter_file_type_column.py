#!/usr/bin/env python3
"""
Script สำหรับแก้ไขขนาด column file_type จาก VARCHAR(10) เป็น VARCHAR(50)
"""

import os
import sys
import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv

# โหลด environment variables
load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'Duplicate_word')
DB_CHARSET = os.getenv('DB_CHARSET', 'utf8mb4')


def alter_file_type_column():
    """แก้ไขขนาด column file_type"""
    print("=" * 70)
    print("Alter file_type column from VARCHAR(10) to VARCHAR(50)")
    print("=" * 70)
    
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset=DB_CHARSET,
            cursorclass=DictCursor
        )
        
        with conn.cursor() as cursor:
            # ตรวจสอบขนาดปัจจุบัน
            cursor.execute("DESCRIBE analyses")
            columns = cursor.fetchall()
            current_file_type = None
            for col in columns:
                if col['Field'] == 'file_type':
                    current_file_type = col['Type']
                    print(f"\nCurrent file_type column type: {current_file_type}")
                    break
            
            if current_file_type and 'varchar(10)' in current_file_type.lower():
                print("\n[ALTER] กำลังแก้ไข file_type column จาก VARCHAR(10) เป็น VARCHAR(50)...")
                cursor.execute("""
                    ALTER TABLE `analyses` 
                    MODIFY COLUMN `file_type` VARCHAR(50) NULL 
                    COMMENT 'ประเภทไฟล์ (txt, pdf, doc, docx, หรือคำอธิบายเพิ่มเติม)'
                """)
                conn.commit()
                print("[OK] แก้ไข file_type column สำเร็จ!")
                
                # ตรวจสอบอีกครั้ง
                cursor.execute("DESCRIBE analyses")
                columns = cursor.fetchall()
                for col in columns:
                    if col['Field'] == 'file_type':
                        print(f"\nNew file_type column type: {col['Type']}")
                        break
            elif current_file_type and 'varchar(50)' in current_file_type.lower():
                print("\n[OK] file_type column มีขนาด VARCHAR(50) อยู่แล้ว ไม่ต้องแก้ไข")
            else:
                print(f"\n[WARN] ไม่พบ file_type column หรือมีประเภทไม่ตรงกับที่คาดไว้: {current_file_type}")
        
        conn.close()
        print("\n" + "=" * 70)
        print("[SUCCESS] เสร็จสิ้น!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    alter_file_type_column()

