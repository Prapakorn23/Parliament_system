#!/usr/bin/env python3
"""
Script สำหรับทดสอบการเชื่อมต่อ database
ใช้สำหรับ debug ปัญหา connection
"""

import sys
import os

# เพิ่ม path เพื่อ import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_config():
    """ทดสอบการโหลด config"""
    print("=" * 70)
    print("🔧 Testing Configuration")
    print("=" * 70)
    
    try:
        from config.config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, DB_CHARSET
        
        print(f"\n📝 Database Configuration:")
        print(f"   DB_HOST: {DB_HOST}")
        print(f"   DB_PORT: {DB_PORT}")
        print(f"   DB_USER: {DB_USER}")
        print(f"   DB_PASSWORD: {'*' * len(DB_PASSWORD) if DB_PASSWORD else '(empty)'}")
        print(f"   DB_NAME: {DB_NAME}")
        print(f"   DB_CHARSET: {DB_CHARSET}")
        
        # ตรวจสอบว่ามีค่าทั้งหมดหรือไม่
        issues = []
        if not DB_HOST:
            issues.append("DB_HOST is empty")
        if not DB_USER:
            issues.append("DB_USER is empty")
        if not DB_NAME:
            issues.append("DB_NAME is empty")
        
        if issues:
            print(f"\n⚠️  Configuration Issues:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        
        print("\n✅ Configuration looks good!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error loading configuration: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pymysql_import():
    """ทดสอบการ import PyMySQL"""
    print("\n" + "=" * 70)
    print("📦 Testing PyMySQL Import")
    print("=" * 70)
    
    try:
        import pymysql
        print(f"✅ PyMySQL imported successfully")
        print(f"   Version: {pymysql.__version__ if hasattr(pymysql, '__version__') else 'unknown'}")
        return True
    except ImportError as e:
        print(f"❌ Cannot import PyMySQL: {e}")
        print("💡 Install with: pip install PyMySQL")
        return False

def test_connection():
    """ทดสอบการเชื่อมต่อ database"""
    print("\n" + "=" * 70)
    print("🔌 Testing Database Connection")
    print("=" * 70)
    
    try:
        from config.config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, DB_CHARSET
        import pymysql
        
        print(f"\n🔗 Connecting to MySQL server at {DB_HOST}:{DB_PORT}...")
        
        # ทดสอบเชื่อมต่อโดยไม่ระบุ database
        config = {
            'host': DB_HOST,
            'port': int(DB_PORT),
            'user': DB_USER,
            'password': DB_PASSWORD or '',
            'charset': DB_CHARSET,
            'connect_timeout': 10
        }
        
        print(f"   Config: host={config['host']}, port={config['port']}, user={config['user']}")
        
        conn = pymysql.connect(**config)
        print("✅ Successfully connected to MySQL server!")
        
        # ทดสอบ database
        cursor = conn.cursor()
        cursor.execute(f"SHOW DATABASES LIKE '{DB_NAME}'")
        result = cursor.fetchone()
        
        if result:
            print(f"✅ Database '{DB_NAME}' exists")
        else:
            print(f"⚠️  Database '{DB_NAME}' does not exist")
            print(f"💡 Creating database...")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET {DB_CHARSET} COLLATE utf8mb4_unicode_ci")
            conn.commit()
            print(f"✅ Database '{DB_NAME}' created successfully")
        
        cursor.close()
        conn.close()
        
        return True
        
    except pymysql.err.OperationalError as e:
        error_msg = str(e)
        print(f"❌ Connection failed: {error_msg}")
        
        if "Access denied" in error_msg:
            print("\n💡 Access Denied - Check:")
            print("   1. DB_USER and DB_PASSWORD in .env file")
            print("   2. User exists in MySQL")
            print("   3. Try: mysql -h localhost -u root -p")
        elif "Can't connect" in error_msg:
            print("\n💡 Cannot Connect - Check:")
            print("   1. MySQL/MariaDB server is running")
            print("      - Windows: net start MySQL")
            print("      - Linux: sudo systemctl status mariadb")
            print("      - Mac: brew services list | grep mariadb")
            print("   2. DB_HOST and DB_PORT in .env file are correct")
        elif "Unknown database" in error_msg:
            print(f"\n💡 Database '{DB_NAME}' does not exist")
            print(f"   Create it manually or it will be created automatically")
        
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("\n" + "=" * 70)
    print("🧪 Database Connection Test")
    print("=" * 70)
    
    results = []
    
    # ทดสอบ config
    results.append(("Configuration", test_config()))
    
    # ทดสอบ PyMySQL
    results.append(("PyMySQL Import", test_pymysql_import()))
    
    # ทดสอบ connection (ถ้า config และ PyMySQL OK)
    if results[0][1] and results[1][1]:
        results.append(("Database Connection", test_connection()))
    
    # สรุปผล
    print("\n" + "=" * 70)
    print("📊 Test Results Summary")
    print("=" * 70)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    all_passed = all(r[1] for r in results)
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ All tests passed! Database connection is working.")
        print("=" * 70)
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("=" * 70)
        return 1

if __name__ == '__main__':
    sys.exit(main())

