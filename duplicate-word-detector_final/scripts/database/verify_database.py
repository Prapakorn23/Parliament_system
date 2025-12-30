#!/usr/bin/env python3
"""
Script สำหรับตรวจสอบโครงสร้าง Database
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


def verify_database():
    """ตรวจสอบโครงสร้าง database"""
    print("=" * 70)
    print("Database Verification")
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
            # ตรวจสอบตาราง
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            table_names = [list(t.values())[0] for t in tables]
            
            print(f"\nFound {len(table_names)} tables:")
            for name in table_names:
                print(f"  - {name}")
            
            # ตรวจสอบโครงสร้างตาราง analyses
            print("\n" + "-" * 70)
            print("Table: analyses")
            print("-" * 70)
            cursor.execute("DESCRIBE analyses")
            columns = cursor.fetchall()
            for col in columns:
                field = col['Field']
                col_type = col['Type']
                null = col['Null']
                key = col['Key']
                default = col['Default'] or 'NULL'
                extra = col['Extra'] or ''
                print(f"  {field:25s} {str(col_type):30s} NULL={null:3s} Key={key:3s} Default={str(default):15s} {extra}")
            
            # ตรวจสอบโครงสร้างตาราง word_frequencies
            print("\n" + "-" * 70)
            print("Table: word_frequencies")
            print("-" * 70)
            cursor.execute("DESCRIBE word_frequencies")
            columns = cursor.fetchall()
            for col in columns:
                field = col['Field']
                col_type = col['Type']
                null = col['Null']
                key = col['Key']
                default = col['Default'] or 'NULL'
                extra = col['Extra'] or ''
                print(f"  {field:25s} {str(col_type):30s} NULL={null:3s} Key={key:3s} Default={str(default):15s} {extra}")
            
            # ตรวจสอบโครงสร้างตาราง categories
            print("\n" + "-" * 70)
            print("Table: categories")
            print("-" * 70)
            cursor.execute("DESCRIBE categories")
            columns = cursor.fetchall()
            for col in columns:
                field = col['Field']
                col_type = col['Type']
                null = col['Null']
                key = col['Key']
                default = col['Default'] or 'NULL'
                extra = col['Extra'] or ''
                print(f"  {field:25s} {str(col_type):30s} NULL={null:3s} Key={key:3s} Default={str(default):15s} {extra}")
            
            # ตรวจสอบโครงสร้างตาราง category_words
            print("\n" + "-" * 70)
            print("Table: category_words")
            print("-" * 70)
            cursor.execute("DESCRIBE category_words")
            columns = cursor.fetchall()
            for col in columns:
                field = col['Field']
                col_type = col['Type']
                null = col['Null']
                key = col['Key']
                default = col['Default'] or 'NULL'
                extra = col['Extra'] or ''
                print(f"  {field:25s} {str(col_type):30s} NULL={null:3s} Key={key:3s} Default={str(default):15s} {extra}")
            
            print("\n" + "=" * 70)
            print("[OK] Database structure verified successfully!")
            print("=" * 70)
        
        conn.close()
        
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    verify_database()

