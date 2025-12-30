"""
Database Models and Operations for MariaDB
โมเดลฐานข้อมูลและการจัดการข้อมูลสำหรับ MariaDB

หมายเหตุ: 
- MariaDB เป็น fork ของ MySQL และมีความเข้ากันได้สูง
- ใช้ PyMySQL เป็น database connector (รองรับทั้ง MariaDB และ MySQL)
- SQL syntax และ features ส่วนใหญ่ใช้ได้เหมือนกัน
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pymysql
from pymysql.cursors import DictCursor
from pymysql.err import OperationalError, IntegrityError
from config.config import (
    DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, DB_CHARSET
)


class DatabaseManager:
    """จัดการการเชื่อมต่อและ operations กับฐานข้อมูล MariaDB/MySQL"""
    
    def __init__(self):
        """เริ่มต้น Database Manager"""
        # ตรวจสอบและเตรียม configuration
        self._validate_config()
        
        self.db_config = {
            'host': DB_HOST,
            'port': int(DB_PORT),
            'user': DB_USER,
            'password': DB_PASSWORD or '',  # ให้เป็น empty string ถ้าเป็น None
            'charset': DB_CHARSET,
            'cursorclass': DictCursor,
            'autocommit': False,
            'connect_timeout': 10
        }
        self._ensure_database_exists()
        # ตรวจสอบและอัปเดต schema ถ้าจำเป็น
        self._migrate_schema()
        # สร้างตารางถ้ายังไม่มี
        self._initialize_database()
    
    def _validate_config(self):
        """ตรวจสอบว่า configuration ถูกต้อง"""
        if not DB_HOST:
            raise ValueError("DB_HOST is not set in .env file")
        if not DB_USER:
            raise ValueError("DB_USER is not set in .env file")
        if not DB_NAME:
            raise ValueError("DB_NAME is not set in .env file")
        print(f"Database config (MariaDB): host={DB_HOST}, port={DB_PORT}, user={DB_USER}, database={DB_NAME}")
    
    def _ensure_database_exists(self):
        """
        ตรวจสอบว่าฐานข้อมูลมีอยู่หรือไม่ ถ้าไม่มีให้สร้าง
        """
        # เชื่อมต่อโดยไม่ระบุ database เพื่อสร้างฐานข้อมูล
        config_no_db = self.db_config.copy()
        config_no_db.pop('database', None)
        
        try:
            conn = pymysql.connect(**config_no_db)
            cursor = conn.cursor()
            
            # สร้างฐานข้อมูลถ้ายังไม่มี (MariaDB syntax)
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET {DB_CHARSET} COLLATE {DB_CHARSET}_unicode_ci")
            conn.commit()
            cursor.close()
            conn.close()
            print(f"✅ Database '{DB_NAME}' ready (MariaDB)")
        except Exception as e:
            print(f"⚠️  Warning: Could not create database: {e}")
            print("   Make sure MariaDB is running and the database exists or create it manually")
    
    def _migrate_schema(self):
        """อัปเดต schema ถ้ามีการเปลี่ยนแปลง (ไม่มีการ migrate ใน schema แบบง่าย)"""
        # Schema แบบง่ายไม่ต้องการ migration
        pass
    
    def get_connection(self):
        """สร้าง database connection ไปยัง MariaDB"""
        # เพิ่ม database ลงใน config สำหรับการเชื่อมต่อปกติ
        connection_config = self.db_config.copy()
        connection_config['database'] = DB_NAME
        
        # เพิ่ม options สำหรับ MariaDB (ถ้าจำเป็น)
        # MariaDB รองรับ SQL_MODE และ options ต่างๆ เหมือน MySQL
        try:
            conn = pymysql.connect(**connection_config)
            # ตั้งค่า session สำหรับ MariaDB เพื่อให้รองรับ utf8mb4 และ strict mode
            cursor = conn.cursor()
            cursor.execute("SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci")
            cursor.execute("SET sql_mode = 'STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO'")
            cursor.close()
            return conn
        except OperationalError as e:
            error_msg = str(e)
            print(f"❌ Database connection error: {error_msg}")
            if "Unknown database" in error_msg:
                print(f"💡 Database '{DB_NAME}' does not exist. Run init script first.")
            elif "Access denied" in error_msg:
                print("💡 Check your DB_USER and DB_PASSWORD in .env file")
            raise
        except Exception as e:
            print(f"❌ Unexpected connection error: {e}")
            print(f"   Type: {type(e).__name__}")
            raise
    
    def execute_schema(self, schema_file: str = 'database/schema.sql'):
        """รัน SQL schema file เพื่อสร้างตาราง"""
        conn = None
        cursor = None
        try:
            import os
            schema_path = os.path.join(os.path.dirname(__file__), '..', schema_file)
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            # แยก statements โดยใช้ semicolon
            statements = [s.strip() for s in schema_sql.split(';') if s.strip() and not s.strip().startswith('--')]
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            for statement in statements:
                if statement.upper().startswith('CREATE TABLE'):
                    try:
                        cursor.execute(statement)
                        # หาชื่อตาราง
                        table_name = statement.split('`')[1] if '`' in statement else 'unknown'
                        print(f"   ✅ Created table: {table_name}")
                    except Exception as e:
                        if 'already exists' not in str(e).lower():
                            print(f"   ⚠️  Error creating table: {e}")
            
            conn.commit()
        except FileNotFoundError:
            print(f"⚠️  Schema file {schema_file} not found. Creating tables automatically...")
            self._initialize_database()
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"❌ Error executing schema: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def _initialize_database(self):
        """สร้างตารางทั้งหมดถ้ายังไม่มี"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # สร้างตาราง analyses (แบบง่าย - เฉพาะความถี่และหมวดหมู่)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `analyses` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `title` VARCHAR(255) NULL COMMENT 'ชื่อ/หัวข้อการวิเคราะห์',
                    `source_type` ENUM('text', 'file') NOT NULL COMMENT 'ประเภทแหล่งที่มา',
                    `file_name` VARCHAR(255) NULL COMMENT 'ชื่อไฟล์ (สำหรับ source_type=file)',
                    `file_type` VARCHAR(50) NULL COMMENT 'ประเภทไฟล์ (txt, pdf, doc, docx, หรือคำอธิบายเพิ่มเติม)',
                    `original_file_path` VARCHAR(500) NULL COMMENT 'path ของไฟล์ต้นฉบับ',
                    `file_size` BIGINT NULL COMMENT 'ขนาดไฟล์ต้นฉบับ (bytes)',
                    `file_content` LONGTEXT NULL COMMENT 'เนื้อหาไฟล์ต้นฉบับ (สำหรับไฟล์ข้อความ)',
                    `total_words` INT NOT NULL DEFAULT 0 COMMENT 'จำนวนคำทั้งหมด',
                    `unique_words` INT NOT NULL DEFAULT 0 COMMENT 'จำนวนคำที่ไม่ซ้ำ',
                    `processing_time` DECIMAL(10,3) NULL COMMENT 'เวลาที่ใช้ในการประมวลผล (วินาที)',
                    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'วันที่สร้าง',
                    INDEX `idx_analyses_source_type` (`source_type`),
                    INDEX `idx_analyses_created_at` (`created_at`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # สร้างตาราง word_frequencies
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `word_frequencies` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `analysis_id` INT NOT NULL,
                    `word` VARCHAR(255) NOT NULL,
                    `frequency` INT NOT NULL DEFAULT 0,
                    `pos_tag` VARCHAR(50) NULL,
                    FOREIGN KEY (`analysis_id`) REFERENCES `analyses`(`id`) ON DELETE CASCADE,
                    INDEX `idx_word_freq_analysis_id` (`analysis_id`),
                    INDEX `idx_word_freq_word` (`word`),
                    INDEX `idx_word_freq_frequency` (`frequency` DESC),
                    UNIQUE KEY `idx_word_freq_unique` (`analysis_id`, `word`, `pos_tag`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # สร้างตาราง categories
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `categories` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `analysis_id` INT NOT NULL,
                    `category_name` VARCHAR(100) NOT NULL,
                    `unique_words_count` INT DEFAULT 0,
                    `total_frequency` INT DEFAULT 0,
                    FOREIGN KEY (`analysis_id`) REFERENCES `analyses`(`id`) ON DELETE CASCADE,
                    INDEX `idx_categories_analysis_id` (`analysis_id`),
                    INDEX `idx_categories_name` (`category_name`),
                    UNIQUE KEY `idx_categories_unique` (`analysis_id`, `category_name`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # สร้างตาราง category_words
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `category_words` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `category_id` INT NOT NULL,
                    `analysis_id` INT NOT NULL,
                    `word` VARCHAR(255) NOT NULL,
                    `frequency` INT NOT NULL DEFAULT 0,
                    `rank_in_category` INT NULL,
                    FOREIGN KEY (`category_id`) REFERENCES `categories`(`id`) ON DELETE CASCADE,
                    FOREIGN KEY (`analysis_id`) REFERENCES `analyses`(`id`) ON DELETE CASCADE,
                    INDEX `idx_category_words_category_id` (`category_id`),
                    INDEX `idx_category_words_analysis_id` (`analysis_id`),
                    INDEX `idx_category_words_rank` (`category_id`, `rank_in_category`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # ไม่สร้างตาราง pos_frequencies - POS tags เก็บใน word_frequencies.pos_tag แล้ว
            
            # ไม่สร้างตารางต่อไปนี้ - ยังไม่มีการใช้งาน:
            # - topics, topic_analyses
            # - parliament_sessions, session_aggregated_data
            # - monthly_aggregated_data
            # - time_series_models, predictions
            # - notification_settings, notifications
            
            conn.commit()
            print("✅ Database tables created successfully")
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"❌ Error creating tables: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    # ============ CRUD Operations สำหรับ analyses ============
    
    def create_analysis(self, data: Dict) -> int:
        """สร้างการวิเคราะห์ใหม่และคืนค่า analysis_id (แบบง่าย)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO `analyses` (
                    `title`, `source_type`, `file_name`, `file_type`,
                    `original_file_path`, `file_size`, `file_content`,
                    `total_words`, `unique_words`, `processing_time`
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data.get('title'),
                data['source_type'],
                data.get('file_name'),
                data.get('file_type'),
                data.get('original_file_path'),
                data.get('file_size'),
                data.get('file_content'),
                data['total_words'],
                data['unique_words'],
                data.get('processing_time')
            ))
            
            analysis_id = cursor.lastrowid
            conn.commit()
            return analysis_id
        except Exception as e:
            conn.rollback()
            print(f"Error creating analysis: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_analysis(self, analysis_id: int) -> Optional[Dict]:
        """ดึงข้อมูลการวิเคราะห์"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM `analyses` WHERE `id` = %s", (analysis_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            cursor.close()
            conn.close()
    
    def list_analyses(self, limit: int = 50, offset: int = 0, 
                     source_type: Optional[str] = None) -> List[Dict]:
        """ดึงรายการการวิเคราะห์ทั้งหมด"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if source_type:
                cursor.execute("""
                    SELECT * FROM `analyses` 
                    WHERE `source_type` = %s
                    ORDER BY `created_at` DESC
                    LIMIT %s OFFSET %s
                """, (source_type, limit, offset))
            else:
                cursor.execute("""
                    SELECT * FROM `analyses` 
                    ORDER BY `created_at` DESC
                    LIMIT %s OFFSET %s
                """, (limit, offset))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            cursor.close()
            conn.close()
    
    def save_word_frequencies(self, analysis_id: int, word_freq_dict: Dict[str, int], 
                             pos_tags_dict: Optional[Dict[str, str]] = None):
        """บันทึกความถี่ของคำ"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            for word, frequency in word_freq_dict.items():
                pos_tag = pos_tags_dict.get(word) if pos_tags_dict else None
                cursor.execute("""
                    INSERT INTO `word_frequencies` (`analysis_id`, `word`, `frequency`, `pos_tag`)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE `frequency` = VALUES(`frequency`)
                """, (analysis_id, word, frequency, pos_tag))
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error saving word frequencies: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def save_categories(self, analysis_id: int, categorized_words: Dict[str, Dict[str, int]]):
        """บันทึกหมวดหมู่และคำในหมวดหมู่"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            for category_name, words_dict in categorized_words.items():
                unique_words_count = len(words_dict)
                total_frequency = sum(words_dict.values())
                
                # สร้าง category
                cursor.execute("""
                    INSERT INTO `categories` (`analysis_id`, `category_name`, `unique_words_count`, `total_frequency`)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                        `unique_words_count` = VALUES(`unique_words_count`),
                        `total_frequency` = VALUES(`total_frequency`)
                """, (analysis_id, category_name, unique_words_count, total_frequency))
                
                category_id = cursor.lastrowid
                if category_id == 0:  # ถ้าเป็น UPDATE จะได้ 0
                    cursor.execute("SELECT `id` FROM `categories` WHERE `analysis_id` = %s AND `category_name` = %s",
                                 (analysis_id, category_name))
                    row = cursor.fetchone()
                    category_id = row['id'] if row else None
                
                if category_id:
                    # บันทึกคำในหมวดหมู่
                    sorted_words = sorted(words_dict.items(), key=lambda x: x[1], reverse=True)
                    for rank, (word, frequency) in enumerate(sorted_words, 1):
                        cursor.execute("""
                            INSERT INTO `category_words` (`category_id`, `analysis_id`, `word`, `frequency`, `rank_in_category`)
                            VALUES (%s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE 
                                `frequency` = VALUES(`frequency`),
                                `rank_in_category` = VALUES(`rank_in_category`)
                        """, (category_id, analysis_id, word, frequency, rank))
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error saving categories: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_categories(self, analysis_id: int) -> Dict[str, Dict[str, int]]:
        """ดึงหมวดหมู่และคำทั้งหมด"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT c.`category_name`, cw.`word`, cw.`frequency`
                FROM `categories` c
                JOIN `category_words` cw ON c.`id` = cw.`category_id`
                WHERE c.`analysis_id` = %s
                ORDER BY c.`category_name`, cw.`rank_in_category`
            """, (analysis_id,))
            
            rows = cursor.fetchall()
            result = {}
            for row in rows:
                category_name = row['category_name']
                if category_name not in result:
                    result[category_name] = {}
                result[category_name][row['word']] = row['frequency']
            
            return result
        finally:
            cursor.close()
            conn.close()
    
    def get_statistics(self) -> Dict:
        """ดึงสถิติรวมของฐานข้อมูล"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT COUNT(*) as total FROM `analyses`")
            total_analyses = cursor.fetchone()['total']
            
            cursor.execute("SELECT SUM(`total_words`) as total FROM `analyses`")
            total_words = cursor.fetchone()['total'] or 0
            
            cursor.execute("SELECT COUNT(DISTINCT `word`) as total FROM `word_frequencies`")
            unique_words = cursor.fetchone()['total'] or 0
            
            return {
                'total_analyses': total_analyses,
                'total_words_analyzed': total_words,
                'unique_words': unique_words
            }
        finally:
            cursor.close()
            conn.close()
    
    # Methods ที่เกี่ยวข้องกับ parliament_sessions และ session_aggregated_data ถูกลบออกแล้ว
    # เพราะตารางเหล่านี้ถูกลบออกจาก schema (ยังไม่มีการใช้งาน)


# Singleton pattern สำหรับ DatabaseManager
_db_manager_instance = None

def get_db_manager() -> DatabaseManager:
    """Get singleton instance of DatabaseManager"""
    global _db_manager_instance
    if _db_manager_instance is None:
        _db_manager_instance = DatabaseManager()
    return _db_manager_instance
