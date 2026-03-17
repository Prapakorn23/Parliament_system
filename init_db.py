"""
Database Initialization Script
สร้างตาราง attendance ใน MariaDB (Database: meeting_attendance)
และเพิ่มข้อมูลตัวอย่าง
"""

import pymysql
from datetime import date

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',
    'charset': 'utf8mb4',
}

DB_NAME = 'meeting_attendance'


def get_connection(use_db=True):
    config = DB_CONFIG.copy()
    if use_db:
        config['database'] = DB_NAME
    return pymysql.connect(**config)


def create_database():
    conn = get_connection(use_db=False)
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        conn.commit()
        print(f"[OK] Database '{DB_NAME}' created / already exists.")
    finally:
        conn.close()


def create_table():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `attendance` (
                    `user_id`         INT AUTO_INCREMENT PRIMARY KEY COMMENT 'รหัสผู้ใช้งานในระบบ',
                    `person_code`     VARCHAR(50)  NOT NULL         COMMENT 'รหัสประจำตัวบุคลากร',
                    `name`            VARCHAR(255) NOT NULL         COMMENT 'ชื่อ-นามสกุล',
                    `id_no`           VARCHAR(20)  DEFAULT ''       COMMENT 'เลขบัตรประจำตัวประชาชน',
                    `card_no`         VARCHAR(50)  DEFAULT ''       COMMENT 'รหัสบัตรพนักงาน / RFID',
                    `mobile_no`       VARCHAR(20)  DEFAULT ''       COMMENT 'เบอร์โทรศัพท์มือถือ',
                    `punch_pwd`       VARCHAR(255) DEFAULT ''       COMMENT 'รหัสผ่านลงเวลา (encrypted)',
                    `department`      VARCHAR(255) DEFAULT ''       COMMENT 'หน่วยงาน / แผนก',
                    `person_type`     VARCHAR(100) DEFAULT ''       COMMENT 'ประเภทบุคลากร',
                    `register_date`   DATE         DEFAULT NULL     COMMENT 'วันที่ลงทะเบียน',
                    `entry_status`    VARCHAR(20)  DEFAULT 'Active' COMMENT 'สถานะการใช้งาน (Active/Inactive)',
                    `gender`          VARCHAR(10)  DEFAULT ''       COMMENT 'เพศ',
                    `position`        VARCHAR(255) DEFAULT ''       COMMENT 'ตำแหน่งงาน',
                    `degree`          VARCHAR(255) DEFAULT ''       COMMENT 'วุฒิการศึกษา',
                    `address`         TEXT                          COMMENT 'ที่อยู่',
                    `email`           VARCHAR(255) DEFAULT ''       COMMENT 'อีเมล',
                    `phone`           VARCHAR(20)  DEFAULT ''       COMMENT 'เบอร์โทรศัพท์ (บ้าน/สำนักงาน)',
                    `remark`          TEXT                          COMMENT 'หมายเหตุเพิ่มเติม',
                    `photo`           VARCHAR(500) DEFAULT ''       COMMENT 'รูปภาพโปรไฟล์ (file path)',
                    `app_token`       VARCHAR(500) DEFAULT ''       COMMENT 'Token สำหรับ Mobile App / Push',
                    `status`          VARCHAR(10)  DEFAULT 'ออก'    COMMENT 'สถานะเข้า/ออก (real-time)',
                    `created_at`      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    `updated_at`      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    UNIQUE KEY `uk_person_code` (`person_code`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
        conn.commit()
        print("[OK] Table 'attendance' created / already exists.")
    finally:
        conn.close()


def insert_sample_data():
    """เพิ่มข้อมูลตัวอย่าง 20 คน"""
    today = date.today().isoformat()

    # (person_code, name, id_no, card_no, mobile_no, punch_pwd,
    #  department, person_type, register_date, entry_status,
    #  gender, position, degree, address, email, phone,
    #  remark, photo, app_token, status)
    sample_data = [
        ('P001', 'นายสมชาย ใจดี',
         '1100100100001', 'RFID-0001', '081-111-1001', '',
         'สำนักงานเลขาธิการสภา', 'ข้าราชการ', today, 'Active',
         'ชาย', 'นักวิเคราะห์นโยบายและแผน ชำนาญการพิเศษ', 'ปริญญาโท',
         '123 ถ.สามเสน แขวงถนนนครไชยศรี เขตดุสิต กรุงเทพฯ 10300',
         'somchai.j@parliament.go.th', '02-111-1001', '', '', '', 'เข้า'),

        ('P002', 'นางสมหญิง รักงาน',
         '1100100100002', 'RFID-0002', '081-111-1002', '',
         'สำนักการประชุม', 'ข้าราชการ', today, 'Active',
         'หญิง', 'นักวิชาการ ชำนาญการ', 'ปริญญาตรี',
         '456 ถ.อู่ทองใน แขวงดุสิต เขตดุสิต กรุงเทพฯ 10300',
         'somying.r@parliament.go.th', '02-111-1002', '', '', '', 'เข้า'),

        ('P003', 'นายวิชัย เก่งมาก',
         '1100100100003', 'RFID-0003', '081-111-1003', '',
         'สำนักกฎหมาย', 'ข้าราชการ', today, 'Active',
         'ชาย', 'นิติกร ชำนาญการ', 'ปริญญาตรี',
         '789 ถ.ราชดำเนินนอก แขวงบ้านพานถม เขตพระนคร กรุงเทพฯ 10200',
         'wichai.k@parliament.go.th', '02-111-1003', '', '', '', 'ออก'),

        ('P004', 'นางสาวปราณี สวยงาม',
         '1100100100004', 'RFID-0004', '081-111-1004', '',
         'สำนักงานเลขาธิการสภา', 'พนักงานราชการ', today, 'Active',
         'หญิง', 'เจ้าพนักงานธุรการ ชำนาญงาน', 'ปริญญาตรี',
         '101 ถ.สามเสน แขวงถนนนครไชยศรี เขตดุสิต กรุงเทพฯ 10300',
         'pranee.s@parliament.go.th', '02-111-1004', '', '', '', 'เข้า'),

        ('P005', 'นายประเสริฐ มั่นคง',
         '1100100100005', 'RFID-0005', '081-111-1005', '',
         'สำนักการคลังและงบประมาณ', 'ข้าราชการ', today, 'Active',
         'ชาย', 'นักวิชาการเงินและบัญชี ชำนาญการ', 'ปริญญาโท',
         '202 ถ.อู่ทองใน แขวงดุสิต เขตดุสิต กรุงเทพฯ 10300',
         'prasert.m@parliament.go.th', '02-111-1005', '', '', '', 'ออก'),

        ('P006', 'นางมาลี สุขสันต์',
         '1100100100006', 'RFID-0006', '081-111-1006', '',
         'สำนักการประชุม', 'ข้าราชการ', today, 'Active',
         'หญิง', 'นักวิชาการ ชำนาญการพิเศษ', 'ปริญญาโท',
         '303 ถ.สามเสน แขวงถนนนครไชยศรี เขตดุสิต กรุงเทพฯ 10300',
         'malee.s@parliament.go.th', '02-111-1006', '', '', '', 'เข้า'),

        ('P007', 'นายดำรงค์ พัฒนา',
         '1100100100007', 'RFID-0007', '081-111-1007', '',
         'สำนักกฎหมาย', 'ข้าราชการ', today, 'Active',
         'ชาย', 'นิติกร ปฏิบัติการ', 'ปริญญาตรี',
         '404 ถ.ราชดำเนินนอก แขวงบ้านพานถม เขตพระนคร กรุงเทพฯ 10200',
         'damrong.p@parliament.go.th', '02-111-1007', '', '', '', 'เข้า'),

        ('P008', 'นางสาวจิราภรณ์ วิไล',
         '1100100100008', 'RFID-0008', '081-111-1008', '',
         'สำนักงานเลขาธิการสภา', 'พนักงานราชการ', today, 'Active',
         'หญิง', 'เจ้าหน้าที่บริหารงานทั่วไป', 'ปริญญาตรี',
         '505 ถ.อู่ทองใน แขวงดุสิต เขตดุสิต กรุงเทพฯ 10300',
         'jiraporn.w@parliament.go.th', '02-111-1008', '', '', '', 'ออก'),

        ('P009', 'นายสมศักดิ์ ดีมาก',
         '1100100100009', 'RFID-0009', '081-111-1009', '',
         'สำนักการคลังและงบประมาณ', 'ข้าราชการ', today, 'Active',
         'ชาย', 'นักวิชาการเงินและบัญชี ชำนาญการพิเศษ', 'ปริญญาโท',
         '606 ถ.สามเสน แขวงถนนนครไชยศรี เขตดุสิต กรุงเทพฯ 10300',
         'somsak.d@parliament.go.th', '02-111-1009', '', '', '', 'เข้า'),

        ('P010', 'นางสาวกมลชนก สุขใจ',
         '1100100100010', 'RFID-0010', '081-111-1010', '',
         'สำนักการประชุม', 'ข้าราชการ', today, 'Active',
         'หญิง', 'นักวิชาการ ปฏิบัติการ', 'ปริญญาตรี',
         '707 ถ.ราชดำเนินนอก แขวงบ้านพานถม เขตพระนคร กรุงเทพฯ 10200',
         'kamolchanok.s@parliament.go.th', '02-111-1010', '', '', '', 'เข้า'),

        ('P011', 'นายวีระ เกียรติสูง',
         '1100100100011', 'RFID-0011', '081-111-1011', '',
         'สำนักกฎหมาย', 'ข้าราชการ', today, 'Active',
         'ชาย', 'นิติกร ชำนาญการพิเศษ', 'ปริญญาโท',
         '808 ถ.อู่ทองใน แขวงดุสิต เขตดุสิต กรุงเทพฯ 10300',
         'weera.k@parliament.go.th', '02-111-1011', '', '', '', 'ออก'),

        ('P012', 'นางอรทัย ใจกว้าง',
         '1100100100012', 'RFID-0012', '081-111-1012', '',
         'สำนักงานเลขาธิการสภา', 'ข้าราชการ', today, 'Active',
         'หญิง', 'นักวิเคราะห์นโยบายและแผน ชำนาญการ', 'ปริญญาตรี',
         '909 ถ.สามเสน แขวงถนนนครไชยศรี เขตดุสิต กรุงเทพฯ 10300',
         'orathai.j@parliament.go.th', '02-111-1012', '', '', '', 'เข้า'),

        ('P013', 'นายธนพล มีดี',
         '1100100100013', 'RFID-0013', '081-111-1013', '',
         'สำนักการคลังและงบประมาณ', 'พนักงานราชการ', today, 'Active',
         'ชาย', 'นักวิชาการเงินและบัญชี ปฏิบัติการ', 'ปริญญาตรี',
         '111 ถ.ราชดำเนินนอก แขวงบ้านพานถม เขตพระนคร กรุงเทพฯ 10200',
         'thanapon.m@parliament.go.th', '02-111-1013', '', '', '', 'เข้า'),

        ('P014', 'นางสาวสิรินาถ รักความจริง',
         '1100100100014', 'RFID-0014', '081-111-1014', '',
         'สำนักการประชุม', 'ข้าราชการ', today, 'Active',
         'หญิง', 'นักวิชาการ ชำนาญการ', 'ปริญญาโท',
         '222 ถ.อู่ทองใน แขวงดุสิต เขตดุสิต กรุงเทพฯ 10300',
         'sirinat.r@parliament.go.th', '02-111-1014', '', '', '', 'ออก'),

        ('P015', 'นายนพพล สุขุม',
         '1100100100015', 'RFID-0015', '081-111-1015', '',
         'สำนักกฎหมาย', 'ข้าราชการ', today, 'Active',
         'ชาย', 'นิติกร ปฏิบัติการ', 'ปริญญาตรี',
         '333 ถ.สามเสน แขวงถนนนครไชยศรี เขตดุสิต กรุงเทพฯ 10300',
         'noppon.s@parliament.go.th', '02-111-1015', '', '', '', 'เข้า'),

        ('P016', 'นางปรีดา อนันต์',
         '1100100100016', 'RFID-0016', '081-111-1016', '',
         'สำนักงานเลขาธิการสภา', 'ข้าราชการ', today, 'Active',
         'หญิง', 'เจ้าพนักงานธุรการ ชำนาญงาน', 'ปริญญาตรี',
         '444 ถ.ราชดำเนินนอก แขวงบ้านพานถม เขตพระนคร กรุงเทพฯ 10200',
         'preeda.a@parliament.go.th', '02-111-1016', '', '', '', 'เข้า'),

        ('P017', 'นายชาญวิทย์ เก่งมาก',
         '1100100100017', 'RFID-0017', '081-111-1017', '',
         'สำนักการคลังและงบประมาณ', 'พนักงานราชการ', today, 'Active',
         'ชาย', 'นักวิชาการเงินและบัญชี ปฏิบัติการ', 'ปริญญาตรี',
         '555 ถ.อู่ทองใน แขวงดุสิต เขตดุสิต กรุงเทพฯ 10300',
         'chanwit.k@parliament.go.th', '02-111-1017', '', '', '', 'ออก'),

        ('P018', 'นางสาวปนัดดา ใจเย็น',
         '1100100100018', 'RFID-0018', '081-111-1018', '',
         'สำนักการประชุม', 'ข้าราชการ', today, 'Active',
         'หญิง', 'นักวิชาการ ปฏิบัติการ', 'ปริญญาตรี',
         '666 ถ.สามเสน แขวงถนนนครไชยศรี เขตดุสิต กรุงเทพฯ 10300',
         'panadda.j@parliament.go.th', '02-111-1018', '', '', '', 'เข้า'),

        ('P019', 'นายอภิชัย มั่นคง',
         '1100100100019', 'RFID-0019', '081-111-1019', '',
         'สำนักกฎหมาย', 'ข้าราชการ', today, 'Active',
         'ชาย', 'นิติกร ชำนาญการ', 'ปริญญาโท',
         '777 ถ.ราชดำเนินนอก แขวงบ้านพานถม เขตพระนคร กรุงเทพฯ 10200',
         'apichai.m@parliament.go.th', '02-111-1019', '', '', '', 'เข้า'),

        ('P020', 'นางสาวนิตยา สุขสำราญ',
         '1100100100020', 'RFID-0020', '081-111-1020', '',
         'สำนักงานเลขาธิการสภา', 'พนักงานราชการ', today, 'Inactive',
         'หญิง', 'เจ้าหน้าที่บริหารงานทั่วไป', 'ปริญญาตรี',
         '888 ถ.อู่ทองใน แขวงดุสิต เขตดุสิต กรุงเทพฯ 10300',
         'nittaya.s@parliament.go.th', '02-111-1020', '', '', '', 'ออก'),
    ]

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM attendance")
            count = cursor.fetchone()[0]
            if count > 0:
                print(f"[SKIP] Table already has {count} rows. Skipping insert.")
                return

            sql = """
                INSERT INTO attendance (
                    person_code, name, id_no, card_no, mobile_no, punch_pwd,
                    department, person_type, register_date, entry_status,
                    gender, position, degree, address, email, phone,
                    remark, photo, app_token, status
                ) VALUES (
                    %s,%s,%s,%s,%s,%s,
                    %s,%s,%s,%s,
                    %s,%s,%s,%s,%s,%s,
                    %s,%s,%s,%s
                )
            """
            cursor.executemany(sql, sample_data)
        conn.commit()
        print(f"[OK] Inserted {len(sample_data)} sample records.")
    finally:
        conn.close()


if __name__ == '__main__':
    print("=" * 50)
    print("Meeting Attendance - Database Initialization")
    print("=" * 50)
    create_database()
    create_table()
    insert_sample_data()
    print("=" * 50)
    print("Done!")
