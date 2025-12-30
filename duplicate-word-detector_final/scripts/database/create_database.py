#!/usr/bin/env python3
"""
Script สำหรับสร้าง Database และตารางตาม schema.sql
Create Database Script - สร้าง database ตาม schema ที่กำหนด
"""

import os
import sys
import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv

# โหลด environment variables
load_dotenv()

# กำหนดค่า database จาก .env หรือค่า default
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'Duplicate_word')
DB_CHARSET = os.getenv('DB_CHARSET', 'utf8mb4')


def get_raw_connection():
    """สร้าง connection โดยไม่ระบุ database เพื่อ drop/create database"""
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            charset=DB_CHARSET,
            cursorclass=DictCursor,
            autocommit=True
        )
        return conn
    except Exception as e:
        print(f"[ERROR] Error connecting to MariaDB server: {e}")
        print("   โปรดตรวจสอบว่า MariaDB server ทำงานอยู่ และข้อมูลใน .env ถูกต้อง")
        sys.exit(1)


def drop_database():
    """ลบ database ทิ้ง"""
    print(f"[DROP] กำลังลบ Database '{DB_NAME}' (ถ้ามี)...")
    conn = get_raw_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"DROP DATABASE IF EXISTS `{DB_NAME}`")
        print(f"[OK] ลบ Database '{DB_NAME}' สำเร็จ")
    except Exception as e:
        print(f"[ERROR] เกิดข้อผิดพลาดในการลบ Database: {e}")
        sys.exit(1)
    finally:
        conn.close()


def create_database():
    """สร้าง database ใหม่"""
    print(f"[CREATE] กำลังสร้าง Database '{DB_NAME}' ใหม่...")
    conn = get_raw_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET {DB_CHARSET} COLLATE utf8mb4_unicode_ci")
        print(f"[OK] สร้าง Database '{DB_NAME}' สำเร็จ")
    except Exception as e:
        print(f"[ERROR] เกิดข้อผิดพลาดในการสร้าง Database: {e}")
        sys.exit(1)
    finally:
        conn.close()


def execute_schema_file():
    """รัน schema.sql เพื่อสร้างตาราง"""
    schema_file = os.path.join(os.path.dirname(__file__), '..', '..', 'database', 'schema.sql')
    
    if not os.path.exists(schema_file):
        print(f"[ERROR] ไม่พบไฟล์ schema.sql ที่: {schema_file}")
        sys.exit(1)
    
    print(f"\n[SCHEMA] กำลังอ่านและรัน schema.sql...")
    
    # อ่านไฟล์ schema
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    # เชื่อมต่อกับ database ที่สร้างแล้ว
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset=DB_CHARSET,
        cursorclass=DictCursor,
        autocommit=False
    )
    
    try:
        with conn.cursor() as cursor:
            # แยก statements โดยใช้ semicolon
            # แบ่งเป็น statements แต่ละตัว
            statements = []
            current_statement = ""
            
            for line in schema_sql.split('\n'):
                # ข้าม comment lines ที่เป็นบรรทัดเดียว
                stripped = line.strip()
                if stripped.startswith('--') or not stripped:
                    continue
                
                current_statement += line + '\n'
                
                # ถ้าเจอ semicolon แสดงว่า statement เสร็จแล้ว
                if ';' in line:
                    # ตัดเฉพาะส่วนก่อน semicolon
                    parts = current_statement.split(';')
                    if len(parts) > 1:
                        statement = parts[0].strip()
                        if statement:
                            statements.append(statement)
                        current_statement = ';'.join(parts[1:])
            
            # Execute แต่ละ statement
            for i, statement in enumerate(statements, 1):
                if statement.strip():
                    try:
                        cursor.execute(statement)
                        # หาชื่อตารางจาก statement
                        if 'CREATE TABLE' in statement.upper():
                            table_name = statement.split('`')[1] if '`' in statement else 'unknown'
                            print(f"   [OK] สร้างตาราง: {table_name}")
                    except Exception as e:
                        print(f"   [WARN] Error executing statement {i}: {e}")
                        # แสดง statement ที่มีปัญหา (เฉพาะส่วนแรก)
                        preview = statement[:100] + '...' if len(statement) > 100 else statement
                        print(f"      Statement: {preview}")
            
            conn.commit()
            print(f"\n[OK] สร้างตารางทั้งหมดสำเร็จ ({len(statements)} statements)")
            
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] เกิดข้อผิดพลาดในการสร้างตาราง: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        conn.close()


def verify_tables():
    """ตรวจสอบว่าตารางถูกสร้างครบหรือไม่"""
    print(f"\n[VERIFY] กำลังตรวจสอบตารางที่สร้าง...")
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset=DB_CHARSET,
        cursorclass=DictCursor
    )
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            if tables:
                table_names = [list(table.values())[0] for table in tables]
                print(f"[OK] พบ {len(table_names)} ตาราง:")
                for name in table_names:
                    print(f"   - {name}")
                
                # ตรวจสอบตารางที่ควรมี
                expected_tables = ['analyses', 'word_frequencies', 'categories', 'category_words']
                missing_tables = [t for t in expected_tables if t not in table_names]
                
                if missing_tables:
                    print(f"\n[WARN] ตารางที่ยังไม่พบ: {', '.join(missing_tables)}")
                else:
                    print(f"\n[OK] ตารางทั้งหมดถูกสร้างครบถ้วน!")
            else:
                print("[ERROR] ไม่พบตารางใดๆ ใน Database!")
                sys.exit(1)
                
    except Exception as e:
        print(f"[ERROR] เกิดข้อผิดพลาดในการตรวจสอบตาราง: {e}")
        sys.exit(1)
    finally:
        conn.close()


def main():
    """ฟังก์ชันหลัก"""
    print("=" * 70)
    print("Database Creation Script for MariaDB")
    print("=" * 70)
    print(f"\nConfiguration:")
    print(f"   Host: {DB_HOST}:{DB_PORT}")
    print(f"   User: {DB_USER}")
    print(f"   Database: {DB_NAME}")
    print(f"   Charset: {DB_CHARSET}")
    
    # ตรวจสอบว่ามี flag --yes หรือไม่
    auto_yes = '--yes' in sys.argv or '-y' in sys.argv
    
    if not auto_yes:
        # ถามยืนยัน
        print("\n[WARN] คำเตือน: การดำเนินการนี้จะ:")
        print(f"   1. ลบ Database '{DB_NAME}' (ถ้ามี)")
        print(f"   2. สร้าง Database '{DB_NAME}' ใหม่")
        print(f"   3. สร้างตารางทั้งหมดจาก schema.sql")
        
        try:
            response = input("\n   ต้องการดำเนินการต่อหรือไม่? (yes/no): ").strip().lower()
            if response not in ['yes', 'y', 'ย', 'ใช่']:
                print("\n[CANCEL] ยกเลิกการดำเนินการ")
                return
        except (EOFError, KeyboardInterrupt):
            print("\n[CANCEL] ยกเลิกการดำเนินการ")
            return
    
    try:
        # 1. ลบ database เดิม
        drop_database()
        
        # 2. สร้าง database ใหม่
        create_database()
        
        # 3. รัน schema.sql
        execute_schema_file()
        
        # 4. ตรวจสอบตาราง
        verify_tables()
        
        print("\n" + "=" * 70)
        print("[SUCCESS] สร้าง Database สำเร็จ!")
        print("=" * 70)
        print(f"\nDatabase: {DB_NAME}")
        print("   พร้อมใช้งานแล้ว!")
        print("\nคำแนะนำ:")
        print("   - สามารถเริ่มใช้งานระบบได้เลย")
        print("   - ตรวจสอบตารางด้วย: mysql -u root -p -e 'USE Duplicate_word; SHOW TABLES;'")
        
    except KeyboardInterrupt:
        print("\n\n[CANCEL] ยกเลิกโดยผู้ใช้")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] เกิดข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

