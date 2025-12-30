-- ============================================
-- PDF2Text Database Schema for MariaDB
-- ============================================
-- This script creates the database and tables
-- for the PDF2Text application
-- ============================================

-- Create database
CREATE DATABASE IF NOT EXISTS `pdf2text`
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- Use the database
USE `pdf2text`;

-- ============================================
-- Table: extraction_records
-- ============================================
-- Stores information about file extraction operations
-- ============================================

CREATE TABLE IF NOT EXISTS `extraction_records` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    
    -- File information
    `filename` VARCHAR(255) NOT NULL,
    `file_type` VARCHAR(10) NOT NULL,
    `file_size` BIGINT NOT NULL,
    `file_hash` VARCHAR(64) UNIQUE,
    
    -- Original file data (เก็บไฟล์ original จริงๆ)
    `original_file_data` LONGBLOB NOT NULL,
    
    -- Extracted text information (เก็บข้อความเต็ม ไม่ใช่ preview)
    `extracted_text` LONGTEXT,
    `extracted_text_length` INT DEFAULT 0,
    
    -- Page and OCR information
    `total_pages` INT DEFAULT 0,
    `ocr_used` BOOLEAN DEFAULT FALSE,
    `ocr_pages` JSON,
    
    -- File paths and hashes
    `original_file_path` VARCHAR(500),
    `original_file_hash` VARCHAR(64),
    `extracted_text_path` VARCHAR(500),
    
    -- Request information
    `ip_address` VARCHAR(45),
    `user_agent` TEXT,
    `processing_time` DECIMAL(10,3),
    
    -- Status information
    `status` VARCHAR(20) DEFAULT 'success',
    `error_message` TEXT,
    
    -- Timestamps
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes for better query performance
    INDEX `idx_file_hash` (`file_hash`),
    INDEX `idx_status` (`status`),
    INDEX `idx_created_at` (`created_at`),
    INDEX `idx_file_type` (`file_type`)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- Table: summary_records
-- ============================================
-- Stores information about text summarization operations
-- ============================================

CREATE TABLE IF NOT EXISTS `summary_records` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    
    -- Foreign key to extraction_records
    `extraction_id` INT NOT NULL,
    
    -- Summary information (เก็บ summary เต็ม ไม่ใช่ preview)
    `summary` LONGTEXT,
    `summary_keywords` TEXT,
    
    -- File paths
    `original_text_path` VARCHAR(500),
    `summary_text_path` VARCHAR(500) NOT NULL,
    
    -- Text length information
    `original_text_length` INT DEFAULT 0,
    `summary_length` INT DEFAULT 0,
    `compression_ratio` DECIMAL(5,2),
    
    -- Processing information
    `processing_time` DECIMAL(10,3) NOT NULL,
    `language` VARCHAR(10) DEFAULT 'auto',
    `provider` VARCHAR(20) DEFAULT 'auto',
    `max_length` INT,
    `min_length` INT,
    
    -- Request information
    `ip_address` VARCHAR(45),
    `user_agent` TEXT,
    
    -- Status information
    `status` VARCHAR(20) DEFAULT 'success',
    `error_message` TEXT,
    
    -- Timestamp
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraint
    CONSTRAINT `fk_summary_extraction`
        FOREIGN KEY (`extraction_id`)
        REFERENCES `extraction_records` (`id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    
    -- Indexes for better query performance
    INDEX `idx_extraction_id` (`extraction_id`),
    INDEX `idx_status` (`status`),
    INDEX `idx_created_at` (`created_at`),
    INDEX `idx_provider` (`provider`)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- Script completed successfully
-- ============================================
-- To verify the tables were created, run:
-- SHOW TABLES;
-- DESCRIBE extraction_records;
-- DESCRIBE summary_records;
-- ============================================

