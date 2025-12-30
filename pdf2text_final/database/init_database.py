"""
Database Initialization Script
สคริปต์สำหรับสร้างฐานข้อมูลและตารางตาม schema.sql
"""

import os
import sys
import pymysql
from pathlib import Path

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


def read_sql_file(file_path: str) -> str:
    """อ่านไฟล์ SQL และคืนค่าเป็น string"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def execute_sql_script(connection, sql_script: str):
    """รัน SQL script โดยแยกคำสั่งตาม semicolon"""
    cursor = connection.cursor()
    
    # แยกคำสั่ง SQL โดยละเว้น comment และคำสั่งว่าง
    statements = []
    current_statement = []
    
    for line in sql_script.split('\n'):
        line = line.strip()
        
        # ข้าม comment และบรรทัดว่าง
        if not line or line.startswith('--'):
            continue
        
        current_statement.append(line)
        
        # ถ้าบรรทัดจบด้วย semicolon ให้เพิ่ม statement
        if line.endswith(';'):
            statement = ' '.join(current_statement)
            if statement.strip():
                statements.append(statement)
            current_statement = []
    
    # รันแต่ละ statement
    for i, statement in enumerate(statements, 1):
        try:
            print(f"Executing statement {i}/{len(statements)}...")
            cursor.execute(statement)
            connection.commit()
        except Exception as e:
            print(f"Error executing statement {i}: {e}")
            print(f"Statement: {statement[:100]}...")
            raise


def init_database():
    """สร้างฐานข้อมูลและตารางตาม schema"""
    # อ่าน database config
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("Error: DATABASE_URL not found in environment variables")
        print("Please set DATABASE_URL in .env file")
        print("Format: mysql+pymysql://user:password@host:port/database")
        sys.exit(1)
    
    # Parse database URL
    try:
        url = database_url.replace('mysql+pymysql://', '')
        
        if '@' in url:
            auth_part, rest = url.split('@', 1)
            if ':' in auth_part:
                user, password = auth_part.split(':', 1)
            else:
                user = auth_part
                password = ''
        else:
            user = 'root'
            password = ''
            rest = url
        
        if '/' in rest:
            host_port, _ = rest.split('/', 1)
            if ':' in host_port:
                host, port = host_port.split(':', 1)
                port = int(port)
            else:
                host = host_port
                port = 3306
        else:
            host = rest.split(':')[0] if ':' in rest else rest
            port = 3306
        
    except Exception as e:
        print(f"Error parsing DATABASE_URL: {e}")
        sys.exit(1)
    
    # เชื่อมต่อฐานข้อมูล (ไม่ระบุ database เพื่อสร้าง database ใหม่)
    try:
        print(f"Connecting to MariaDB at {host}:{port}...")
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            charset='utf8mb4',
            autocommit=False
        )
        print("Connected successfully!")
        
        # อ่าน SQL schema file
        script_dir = Path(__file__).parent
        schema_file = script_dir / 'schema.sql'
        
        if not schema_file.exists():
            print(f"Error: schema.sql not found at {schema_file}")
            sys.exit(1)
        
        print(f"Reading schema file: {schema_file}")
        sql_script = read_sql_file(str(schema_file))
        
        # รัน SQL script
        print("\nExecuting SQL schema...")
        execute_sql_script(connection, sql_script)
        
        print("\n✅ Database initialization completed successfully!")
        print("\nTables created:")
        print("  - extraction_records")
        print("  - summary_records")
        
        connection.close()
        
    except pymysql.Error as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    init_database()

