"""
Database Connection Helper
จัดการการเชื่อมต่อฐานข้อมูล MariaDB/MySQL
"""

import os
import pymysql
from typing import Optional, Dict, Any
from contextlib import contextmanager

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


def parse_database_url(url: str) -> Dict[str, Any]:
    """
    Parse DATABASE_URL format: mysql+pymysql://user:password@host:port/database
    """
    try:
        # ลบ mysql+pymysql://
        url = url.replace('mysql+pymysql://', '')
        
        # แยก user:password@host:port/database
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
        
        # แยก host:port/database
        if '/' in rest:
            host_port, database = rest.split('/', 1)
            if ':' in host_port:
                host, port = host_port.split(':', 1)
                port = int(port)
            else:
                host = host_port
                port = 3306
        else:
            host = rest.split(':')[0] if ':' in rest else rest
            port = 3306
            database = None
        
        return {
            'user': user,
            'password': password,
            'host': host,
            'port': port,
            'database': database
        }
    except Exception as e:
        raise ValueError(f"Error parsing DATABASE_URL: {e}")


def get_database_config() -> Optional[Dict[str, Any]]:
    """อ่าน database configuration จาก environment variable"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        return None
    
    try:
        return parse_database_url(database_url)
    except Exception as e:
        print(f"Warning: Could not parse DATABASE_URL: {e}")
        return None


@contextmanager
def get_db_connection():
    """
    Context manager สำหรับ database connection
    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ...")
    """
    config = get_database_config()
    
    if not config:
        raise ValueError("DATABASE_URL not configured. Please set DATABASE_URL in .env file")
    
    connection = None
    try:
        connection = pymysql.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database=config.get('database', 'pdf2text'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False
        )
        yield connection
        connection.commit()
    except Exception as e:
        if connection:
            connection.rollback()
        raise e
    finally:
        if connection:
            connection.close()


def test_connection() -> bool:
    """ทดสอบการเชื่อมต่อฐานข้อมูล"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False

