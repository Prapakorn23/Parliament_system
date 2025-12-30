"""
Migration Script: Add original_file_data and extracted_text
Remove extracted_text_preview
"""

import os
import sys
from pathlib import Path

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from database.connection import get_db_connection

def migrate_database():
    """Migrate database to add original_file_data and extracted_text"""
    try:
        print("Starting database migration...")
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # ตรวจสอบว่ามีฟิลด์ original_file_data อยู่แล้วหรือไม่
            cursor.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'extraction_records' 
                AND COLUMN_NAME = 'original_file_data'
            """)
            
            has_original_file_data = cursor.fetchone() is not None
            
            if not has_original_file_data:
                print("Adding original_file_data column...")
                cursor.execute("""
                    ALTER TABLE extraction_records 
                    ADD COLUMN original_file_data LONGBLOB NULL AFTER file_hash
                """)
                print("✓ Added original_file_data column")
            else:
                print("✓ original_file_data column already exists")
            
            # ตรวจสอบว่ามีฟิลด์ extracted_text อยู่แล้วหรือไม่
            cursor.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'extraction_records' 
                AND COLUMN_NAME = 'extracted_text'
            """)
            
            has_extracted_text = cursor.fetchone() is not None
            
            if not has_extracted_text:
                print("Adding extracted_text column...")
                cursor.execute("""
                    ALTER TABLE extraction_records 
                    ADD COLUMN extracted_text LONGTEXT NULL AFTER original_file_data
                """)
                print("✓ Added extracted_text column")
                
                # ย้ายข้อมูลจาก extracted_text_preview ไป extracted_text (ถ้ามี)
                cursor.execute("""
                    SELECT COLUMN_NAME 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = 'extraction_records' 
                    AND COLUMN_NAME = 'extracted_text_preview'
                """)
                
                if cursor.fetchone():
                    print("Migrating data from extracted_text_preview to extracted_text...")
                    cursor.execute("""
                        UPDATE extraction_records 
                        SET extracted_text = extracted_text_preview 
                        WHERE extracted_text_preview IS NOT NULL AND extracted_text IS NULL
                    """)
                    print(f"✓ Migrated {cursor.rowcount} records")
            else:
                print("✓ extracted_text column already exists")
            
            # ลบฟิลด์ preview
            cursor.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'extraction_records' 
                AND COLUMN_NAME = 'extracted_text_preview'
            """)
            
            if cursor.fetchone():
                print("Removing extracted_text_preview column...")
                cursor.execute("""
                    ALTER TABLE extraction_records 
                    DROP COLUMN extracted_text_preview
                """)
                print("✓ Removed extracted_text_preview column")
            else:
                print("✓ extracted_text_preview column does not exist")
            
            # ลบฟิลด์ extracted_text_keywords
            cursor.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'extraction_records' 
                AND COLUMN_NAME = 'extracted_text_keywords'
            """)
            
            if cursor.fetchone():
                print("Removing extracted_text_keywords column...")
                cursor.execute("""
                    ALTER TABLE extraction_records 
                    DROP COLUMN extracted_text_keywords
                """)
                print("✓ Removed extracted_text_keywords column")
            else:
                print("✓ extracted_text_keywords column does not exist")
            
            # ตั้งค่า original_file_data เป็น NOT NULL (ถ้ายังไม่ใช่)
            if not has_original_file_data:
                print("Setting original_file_data to NOT NULL...")
                try:
                    cursor.execute("""
                        ALTER TABLE extraction_records 
                        MODIFY COLUMN original_file_data LONGBLOB NOT NULL
                    """)
                    print("✓ Set original_file_data to NOT NULL")
                except Exception as e:
                    print(f"⚠ Warning: Could not set original_file_data to NOT NULL: {e}")
                    print("  You may need to populate existing records first")
            
            # Update summary_records table
            cursor.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'summary_records' 
                AND COLUMN_NAME = 'summary'
            """)
            
            has_summary = cursor.fetchone() is not None
            
            if not has_summary:
                print("Adding summary column to summary_records...")
                cursor.execute("""
                    ALTER TABLE summary_records 
                    ADD COLUMN summary LONGTEXT NULL AFTER extraction_id
                """)
                print("✓ Added summary column")
                
                # ย้ายข้อมูลจาก summary_preview ไป summary (ถ้ามี)
                cursor.execute("""
                    SELECT COLUMN_NAME 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = 'summary_records' 
                    AND COLUMN_NAME = 'summary_preview'
                """)
                
                if cursor.fetchone():
                    print("Migrating data from summary_preview to summary...")
                    cursor.execute("""
                        UPDATE summary_records 
                        SET summary = summary_preview 
                        WHERE summary_preview IS NOT NULL AND summary IS NULL
                    """)
                    print(f"✓ Migrated {cursor.rowcount} summary records")
            else:
                print("✓ summary column already exists")
            
            # ลบฟิลด์ summary_preview
            cursor.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'summary_records' 
                AND COLUMN_NAME = 'summary_preview'
            """)
            
            if cursor.fetchone():
                print("Removing summary_preview column...")
                cursor.execute("""
                    ALTER TABLE summary_records 
                    DROP COLUMN summary_preview
                """)
                print("✓ Removed summary_preview column")
            else:
                print("✓ summary_preview column does not exist")
            
            conn.commit()
            print("\n✅ Database migration completed successfully!")
            
    except Exception as e:
        print(f"\n❌ Migration error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    migrate_database()

