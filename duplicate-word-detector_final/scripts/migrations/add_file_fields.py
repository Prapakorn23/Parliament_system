#!/usr/bin/env python3
"""
Script สำหรับเพิ่มฟิลด์เก็บไฟล์ต้นฉบับในตาราง analyses
"""

import os
import sys
import pymysql
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = 'duplicate_word'
DB_CHARSET = 'utf8mb4'

def add_file_fields():
    """เพิ่มฟิลด์เก็บไฟล์ต้นฉบับ"""
    print("=" * 70)
    print("Add File Fields to analyses table")
    print("=" * 70)
    print(f"\nDatabase: {DB_NAME}")
    print(f"Host: {DB_HOST}:{DB_PORT}")
    print(f"User: {DB_USER}")
    
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset=DB_CHARSET
    )
    
    try:
        with conn.cursor() as cursor:
            # ตรวจสอบว่ามีฟิลด์อยู่แล้วหรือไม่
            cursor.execute("SHOW COLUMNS FROM `analyses` LIKE 'original_file_path'")
            has_original_file_path = cursor.fetchone() is not None
            
            cursor.execute("SHOW COLUMNS FROM `analyses` LIKE 'file_size'")
            has_file_size = cursor.fetchone() is not None
            
            cursor.execute("SHOW COLUMNS FROM `analyses` LIKE 'file_content'")
            has_file_content = cursor.fetchone() is not None
            
            if has_original_file_path and has_file_size and has_file_content:
                print("\n[INFO] ฟิลด์ทั้งหมดมีอยู่แล้ว ไม่ต้องเพิ่ม")
                return
            
            print("\n[ALTER] กำลังเพิ่มฟิลด์ใหม่...")
            
            # เพิ่มฟิลด์ original_file_path
            if not has_original_file_path:
                try:
                    cursor.execute("""
                        ALTER TABLE `analyses` 
                        ADD COLUMN `original_file_path` VARCHAR(500) NULL 
                        COMMENT 'path ของไฟล์ต้นฉบับ' 
                        AFTER `file_type`
                    """)
                    print("   [OK] เพิ่มฟิลด์: original_file_path")
                except Exception as e:
                    print(f"   [WARN] ไม่สามารถเพิ่ม original_file_path: {e}")
            
            # เพิ่มฟิลด์ file_size
            if not has_file_size:
                try:
                    cursor.execute("""
                        ALTER TABLE `analyses` 
                        ADD COLUMN `file_size` BIGINT NULL 
                        COMMENT 'ขนาดไฟล์ต้นฉบับ (bytes)' 
                        AFTER `original_file_path`
                    """)
                    print("   [OK] เพิ่มฟิลด์: file_size")
                except Exception as e:
                    print(f"   [WARN] ไม่สามารถเพิ่ม file_size: {e}")
            
            # เพิ่มฟิลด์ file_content
            if not has_file_content:
                try:
                    cursor.execute("""
                        ALTER TABLE `analyses` 
                        ADD COLUMN `file_content` LONGTEXT NULL 
                        COMMENT 'เนื้อหาไฟล์ต้นฉบับ (สำหรับไฟล์ข้อความ)' 
                        AFTER `file_size`
                    """)
                    print("   [OK] เพิ่มฟิลด์: file_content")
                except Exception as e:
                    print(f"   [WARN] ไม่สามารถเพิ่ม file_content: {e}")
            
            conn.commit()
            print("\n[SUCCESS] เพิ่มฟิลด์สำเร็จ!")
            
            # ตรวจสอบฟิลด์ทั้งหมด
            cursor.execute("SHOW COLUMNS FROM `analyses`")
            columns = cursor.fetchall()
            print("\n[VERIFY] ฟิลด์ในตาราง analyses:")
            for col in columns:
                print(f"   - {col[0]} ({col[1]})")
                
    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] เกิดข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        conn.close()

if __name__ == '__main__':
    add_file_fields()

