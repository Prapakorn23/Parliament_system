-- ============================================================
-- Database Schema for Duplicate Word Detector System
-- MariaDB Database (รองรับ MySQL ด้วย)
-- Database Name: duplicate_word
-- 
-- หมายเหตุ: 
-- - Schema นี้ใช้กับ MariaDB (แนะนำ)
-- - MariaDB เป็น fork ของ MySQL และมีความเข้ากันได้สูง
-- - ใช้ utf8mb4 character set เพื่อรองรับภาษาไทยและ emoji
-- - Schema แบบง่าย: เฉพาะความถี่และหมวดหมู่ (ไม่มีฟีเจอร์พยากรณ์)
-- ============================================================

-- ============================================================
-- Table: analyses
-- เก็บประวัติการวิเคราะห์ (แบบง่าย)
-- ============================================================
CREATE TABLE IF NOT EXISTS `analyses` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `title` VARCHAR(255) NULL COMMENT 'ชื่อ/หัวข้อการวิเคราะห์',
    `source_type` ENUM('text', 'file') NOT NULL COMMENT 'ประเภทแหล่งที่มา',
    `file_name` VARCHAR(255) NULL COMMENT 'ชื่อไฟล์ (สำหรับ source_type=file)',
    `file_type` VARCHAR(50) NULL COMMENT 'ประเภทไฟล์ (txt, pdf, doc, docx, หรือคำอธิบายเพิ่มเติม)',
    `original_file_path` VARCHAR(500) NULL COMMENT 'path ของไฟล์ต้นฉบับ',
    `file_size` BIGINT NULL COMMENT 'ขนาดไฟล์ต้นฉบับ (bytes)',
    `file_content` LONGTEXT NULL COMMENT 'เนื้อหาไฟล์ต้นฉบับ (สำหรับไฟล์ข้อความ)',
    
    -- สถิติการวิเคราะห์
    `total_words` INT NOT NULL DEFAULT 0 COMMENT 'จำนวนคำทั้งหมด',
    `unique_words` INT NOT NULL DEFAULT 0 COMMENT 'จำนวนคำที่ไม่ซ้ำ',
    `processing_time` DECIMAL(10,3) NULL COMMENT 'เวลาที่ใช้ในการประมวลผล (วินาที)',
    
    -- Metadata
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'วันที่สร้าง',
    
    -- Indexes
    INDEX `idx_analyses_source_type` (`source_type`),
    INDEX `idx_analyses_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='ตารางเก็บประวัติการวิเคราะห์';

-- ============================================================
-- Table: word_frequencies
-- เก็บความถี่ของคำในแต่ละการวิเคราะห์
-- ============================================================
CREATE TABLE IF NOT EXISTS `word_frequencies` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `analysis_id` INT NOT NULL,
    `word` VARCHAR(255) NOT NULL COMMENT 'คำ',
    `frequency` INT NOT NULL DEFAULT 0 COMMENT 'ความถี่',
    `pos_tag` VARCHAR(50) NULL COMMENT 'Part-of-Speech tag',
    
    FOREIGN KEY (`analysis_id`) REFERENCES `analyses`(`id`) ON DELETE CASCADE,
    
    -- Indexes
    INDEX `idx_word_freq_analysis_id` (`analysis_id`),
    INDEX `idx_word_freq_word` (`word`),
    INDEX `idx_word_freq_frequency` (`frequency` DESC),
    UNIQUE KEY `idx_word_freq_unique` (`analysis_id`, `word`, `pos_tag`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='ตารางเก็บความถี่ของคำ';

-- ============================================================
-- Table: categories
-- เก็บหมวดหมู่คำในแต่ละการวิเคราะห์
-- ============================================================
CREATE TABLE IF NOT EXISTS `categories` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `analysis_id` INT NOT NULL,
    `category_name` VARCHAR(100) NOT NULL COMMENT 'ชื่อหมวดหมู่',
    `unique_words_count` INT DEFAULT 0 COMMENT 'จำนวนคำเฉพาะในหมวดหมู่',
    `total_frequency` INT DEFAULT 0 COMMENT 'ความถี่รวม',
    
    FOREIGN KEY (`analysis_id`) REFERENCES `analyses`(`id`) ON DELETE CASCADE,
    
    -- Indexes
    INDEX `idx_categories_analysis_id` (`analysis_id`),
    INDEX `idx_categories_name` (`category_name`),
    UNIQUE KEY `idx_categories_unique` (`analysis_id`, `category_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='ตารางเก็บหมวดหมู่คำ';

-- ============================================================
-- Table: category_words
-- เก็บคำในแต่ละหมวดหมู่
-- ============================================================
CREATE TABLE IF NOT EXISTS `category_words` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `category_id` INT NOT NULL,
    `analysis_id` INT NOT NULL,
    `word` VARCHAR(255) NOT NULL COMMENT 'คำ',
    `frequency` INT NOT NULL DEFAULT 0 COMMENT 'ความถี่',
    `rank_in_category` INT NULL COMMENT 'อันดับในหมวดหมู่',
    
    FOREIGN KEY (`category_id`) REFERENCES `categories`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`analysis_id`) REFERENCES `analyses`(`id`) ON DELETE CASCADE,
    
    -- Indexes
    INDEX `idx_category_words_category_id` (`category_id`),
    INDEX `idx_category_words_analysis_id` (`analysis_id`),
    INDEX `idx_category_words_rank` (`category_id`, `rank_in_category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='ตารางเก็บคำในแต่ละหมวดหมู่';
