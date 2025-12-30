import os
import sys
import time
import gc
import psutil
import hashlib
from datetime import datetime
from flask import Flask, render_template, request, send_file, jsonify
from io import BytesIO
import json

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from extractors.file_text_extractor import extract_text_from_upload
from summarizers.text_summarizer import summarize_text

# Load .env if present (for TYPHOON_API_KEY etc.)
try:
	from dotenv import load_dotenv  # type: ignore
	load_dotenv()
except Exception:
	pass
def create_app() -> Flask:
    app = Flask(__name__, static_folder="static", template_folder="templates")
    
    # Add memory management utilities
    def check_memory_usage():
        """Check current memory usage and trigger cleanup if needed."""
        try:
            memory_percent = psutil.virtual_memory().percent
            if memory_percent > 80:
                gc.collect()  # Force garbage collection
                return True  # Indicate cleanup was performed
        except:
            pass
        return False
    
    def optimize_for_large_text(text_length):
        """Optimize system for large text processing."""
        if text_length > 50000:
            gc.collect()  # Clean up memory before processing large text
            return True
        return False
    
    # Database helper functions
    def save_extraction_to_db(filename, file_bytes, extracted_text, ocr_used, pages_data, processing_time):
        """บันทึกข้อมูลการแปลงไฟล์ลง database (extraction_records)"""
        try:
            from database.connection import get_db_connection
            
            file_ext = os.path.splitext(filename)[1][1:].lower() if '.' in filename else 'unknown'
            file_size = len(file_bytes)
            extracted_text_length = len(extracted_text)
            
            # คำนวณ file hash
            file_hash = hashlib.sha256(file_bytes).hexdigest()
            
            # เก็บ original_file_path
            original_file_path = filename
            
            # คำนวณ original_file_hash (ถ้าต้องการ)
            original_file_hash = file_hash  # ใช้ hash เดียวกัน
            
            # จำนวนหน้า
            total_pages = len(pages_data) if pages_data else 0
            
            # OCR pages เป็น JSON
            ocr_pages_json = None
            if pages_data and ocr_used:
                # สร้าง list ของหน้าเลขที่ใช้ OCR
                ocr_pages_list = [page.get('page_num', i+1) for i, page in enumerate(pages_data) if page.get('ocr_used', False)]
                if ocr_pages_list:
                    ocr_pages_json = json.dumps(ocr_pages_list)
            
            # ข้อมูล request
            ip_address = request.remote_addr if request else None
            user_agent = request.headers.get('User-Agent') if request else None
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # บันทึกลงตาราง extraction_records (เก็บไฟล์ original และข้อความเต็ม)
                cursor.execute("""
                    INSERT INTO extraction_records (
                        filename, file_type, file_size, file_hash,
                        original_file_data, extracted_text, extracted_text_length,
                        total_pages, ocr_used, ocr_pages,
                        original_file_path, original_file_hash,
                        ip_address, user_agent, processing_time, status
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    filename,
                    file_ext,
                    file_size,
                    file_hash,
                    file_bytes,  # เก็บไฟล์ original จริงๆ
                    extracted_text,  # เก็บข้อความเต็ม
                    extracted_text_length,
                    total_pages,
                    ocr_used,
                    ocr_pages_json,
                    original_file_path,
                    original_file_hash,
                    ip_address,
                    user_agent,
                    processing_time,
                    'success'
                ))
                
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"Error saving extraction to database: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def save_summary_to_db(original_file, extracted_text, summary, processing_time, text_length, summary_length, extraction_id=None, lang='auto', provider='auto', max_length=None, min_length=None):
        """บันทึกข้อมูลการสรุปลง database (summary_records)"""
        try:
            from database.connection import get_db_connection
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # ถ้าไม่มี extraction_id ให้หาจาก filename
                if not extraction_id:
                    if original_file and original_file != "unknown":
                        cursor.execute("""
                            SELECT id 
                            FROM extraction_records 
                            WHERE filename = %s
                            ORDER BY created_at DESC 
                            LIMIT 1
                        """, (original_file,))
                        result = cursor.fetchone()
                        if result:
                            extraction_id = result['id']
                
                # ถ้ายังไม่มี extraction_id ให้ใช้ข้อมูลล่าสุด
                if not extraction_id:
                    cursor.execute("""
                        SELECT id 
                        FROM extraction_records 
                        ORDER BY created_at DESC 
                        LIMIT 1
                    """)
                    result = cursor.fetchone()
                    if result:
                        extraction_id = result['id']
                
                # ถ้ายังไม่มี extraction_id แสดงว่าไม่มีข้อมูล extraction
                if not extraction_id:
                    print("Warning: No extraction record found for summary. Skipping database save.")
                    return False
                
                # คำนวณ compression ratio
                compression_ratio = None
                if text_length > 0:
                    compression_ratio = round((1 - (summary_length / text_length)) * 100, 2)
                
                # สร้าง summary_text_path (required field)
                # ใช้ชื่อไฟล์เดิม + _summary.txt
                summary_text_path = f"{original_file}_summary.txt" if original_file != "unknown" else "summary.txt"
                
                # ข้อมูล request
                ip_address = request.remote_addr if request else None
                user_agent = request.headers.get('User-Agent') if request else None
                
                # บันทึกลงตาราง summary_records (เก็บ summary เต็ม)
                cursor.execute("""
                    INSERT INTO summary_records (
                        extraction_id,
                        summary,
                        original_text_length, summary_length,
                        compression_ratio,
                        summary_text_path,
                        processing_time, language, provider,
                        max_length, min_length,
                        ip_address, user_agent, status
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    extraction_id,
                    summary,  # เก็บ summary เต็ม
                    text_length,     # original_text_length
                    summary_length,  # summary_length
                    compression_ratio,
                    summary_text_path,
                    processing_time,
                    lang,
                    provider,
                    max_length,
                    min_length,
                    ip_address,
                    user_agent,
                    'success'
                ))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error saving summary to database: {e}")
            import traceback
            traceback.print_exc()
            return False

    # Limit upload size to 50MB for better large text handling
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

    @app.errorhandler(413)
    def request_entity_too_large(e):  # type: ignore
        return render_template("index.html", extracted_text=None, filename=None, error_message="ขนาดไฟล์เกิน 50MB กรุณาเลือกไฟล์ที่เล็กกว่า", summary=None), 413
    
    @app.errorhandler(500)
    def internal_server_error(e):  # type: ignore
        return render_template("index.html", extracted_text=None, filename=None, error_message="เกิดข้อผิดพลาดภายในเซิร์ฟเวอร์ กรุณาลองใหม่อีกครั้ง", summary=None), 500
    
    @app.errorhandler(404)
    def not_found_error(e):  # type: ignore
        return render_template("index.html", extracted_text=None, filename=None, error_message="ไม่พบหน้าที่ต้องการ", summary=None), 404
    
    @app.errorhandler(408)
    def timeout_error(e):  # type: ignore
        return render_template("index.html", extracted_text=None, filename=None, error_message="การประมวลผลใช้เวลานานเกินไป กรุณาลองใหม่อีกครั้ง", summary=None), 408

    @app.route("/", methods=["GET"]) 
    def index():
        return render_template("index.html", extracted_text=None, filename=None, error_message=None, summary=None)
    
    @app.route("/extract", methods=["POST"])
    def extract():
        # Accept multiple file types (.pdf, .docx, .txt)
        field_name = "file"
        if field_name not in request.files:
            # Backward compatibility with older field name
            if "pdf_file" in request.files:
                field_name = "pdf_file"
            else:
                return render_template("index.html", extracted_text=None, filename=None, error_message="ไม่พบไฟล์ที่อัปโหลด", summary=None)

        file = request.files[field_name]
        if file.filename == "":
            return render_template("index.html", extracted_text=None, filename=None, error_message="กรุณาเลือกไฟล์ (.pdf, .docx, .txt)", summary=None)

        try:
            # ตรวจสอบว่ามี flag from_search หรือไม่
            from_search = request.form.get("from_search") == "true"
            extraction_id = request.form.get("extraction_id")
            
            file_bytes = file.read()
            if not file_bytes:
                return render_template("index.html", extracted_text=None, filename=None, error_message="ไฟล์ว่างหรือไม่สามารถอ่านได้", summary=None, ocr_used=False)

            # เริ่มจับเวลาการประมวลผล
            start_time = time.time()
            extracted_text, ocr_used, pages_data = extract_text_from_upload(file.filename, file_bytes)
            processing_time = time.time() - start_time

            # บันทึกข้อมูลลง database เฉพาะเมื่อไม่ใช่จาก search
            if not from_search:
                try:
                    save_extraction_to_db(file.filename, file_bytes, extracted_text, ocr_used, pages_data, processing_time)
                except Exception as db_error:
                    print(f"Warning: Could not save to database: {db_error}")
            else:
                # ถ้ามาจาก search ให้ใช้ extraction_id ที่มีอยู่
                print(f"File loaded from search (extraction_id: {extraction_id}), skipping database save")

            if request.form.get("download") == "1":
                download_name = os.path.splitext(file.filename)[0] + ".txt"
                output = BytesIO(extracted_text.encode("utf-8"))
                output.seek(0)
                return send_file(
                    output,
                    mimetype="text/plain; charset=utf-8",
                    as_attachment=True,
                    download_name=download_name,
                )

            # ส่งข้อมูลทีละหน้าไปยัง template
            return render_template("index.html", 
                                 extracted_text=extracted_text, 
                                 filename=file.filename, 
                                 error_message=None, 
                                 summary=None, 
                                 ocr_used=ocr_used,
                                 pages_data=pages_data,
                                 total_pages=len(pages_data) if pages_data else 0,
                                 from_search=from_search,
                                 extraction_id=extraction_id)
        except ValueError as ve:
            return render_template("index.html", extracted_text=None, filename=None, error_message=str(ve), summary=None)
        except MemoryError:
            return render_template("index.html", extracted_text=None, filename=None, error_message="ไฟล์ใหญ่เกินไป กรุณาเลือกไฟล์ที่เล็กกว่า", summary=None)
        except TimeoutError:
            return render_template("index.html", extracted_text=None, filename=None, error_message="การประมวลผลไฟล์ใช้เวลานานเกินไป กรุณาลองใหม่อีกครั้ง", summary=None)
        except Exception as exc:  # pylint: disable=broad-except
            error_msg = str(exc)
            if "corrupted" in error_msg.lower() or "invalid" in error_msg.lower():
                return render_template("index.html", extracted_text=None, filename=None, error_message="ไฟล์เสียหายหรือไม่ถูกต้อง กรุณาเลือกไฟล์อื่น", summary=None)
            elif "permission" in error_msg.lower() or "access" in error_msg.lower():
                return render_template("index.html", extracted_text=None, filename=None, error_message="ไม่สามารถเข้าถึงไฟล์ได้ กรุณาตรวจสอบสิทธิ์การเข้าถึง", summary=None)
            else:
                return render_template("index.html", extracted_text=None, filename=None, error_message=f"เกิดข้อผิดพลาด: {exc}", summary=None)

    @app.route("/api/extract", methods=["POST"])
    def extract_api():
        """
        API endpoint สำหรับอัปโหลดและแปลงไฟล์
        ส่งกลับ JSON response
        """
        field_name = "file"
        if field_name not in request.files:
            if "pdf_file" in request.files:
                field_name = "pdf_file"
            else:
                return jsonify({"error": "ไม่พบไฟล์ที่อัปโหลด"}), 400

        file = request.files[field_name]
        if file.filename == "":
            return jsonify({"error": "กรุณาเลือกไฟล์ (.pdf, .docx, .txt, รูปภาพ)"}), 400

        try:
            # ตรวจสอบว่ามี flag from_search หรือไม่
            from_search = request.form.get("from_search") == "true" or request.headers.get("X-From-Search") == "true"
            extraction_id = request.form.get("extraction_id")
            
            file_bytes = file.read()
            if not file_bytes:
                return jsonify({"error": "ไฟล์ว่างหรือไม่สามารถอ่านได้"}), 400

            # เริ่มจับเวลาการประมวลผล
            start_time = time.time()
            extracted_text, ocr_used, pages_data = extract_text_from_upload(file.filename, file_bytes)
            processing_time = time.time() - start_time

            file_ext = os.path.splitext(file.filename)[1][1:].lower() if '.' in file.filename else 'unknown'

            # บันทึกข้อมูลลง database เฉพาะเมื่อไม่ใช่จาก search
            record_id = None
            if not from_search:
                try:
                    record_id = save_extraction_to_db(file.filename, file_bytes, extracted_text, ocr_used, pages_data, processing_time)
                except Exception as db_error:
                    print(f"Warning: Could not save to database: {db_error}")
            else:
                print(f"File loaded from search (extraction_id: {extraction_id}), skipping database save")

            return jsonify({
                "success": True,
                "filename": file.filename,
                "file_type": file_ext,
                "extracted_text_length": len(extracted_text),
                "total_pages": len(pages_data) if pages_data else 0,
                "ocr_used": ocr_used,
                "processing_time": f"{processing_time:.2f} วินาที",
                "record_id": record_id,
                "from_search": from_search,
                "extraction_id": extraction_id,
                "message": f"อัปโหลดและแปลงข้อความสำเร็จ: {file.filename}"
            })
            
        except ValueError as ve:
            return jsonify({"error": str(ve)}), 400
        except MemoryError:
            return jsonify({"error": "ไฟล์ใหญ่เกินไป กรุณาเลือกไฟล์ที่เล็กกว่า"}), 413
        except TimeoutError:
            return jsonify({"error": "การประมวลผลไฟล์ใช้เวลานานเกินไป กรุณาลองใหม่อีกครั้ง"}), 408
        except Exception as exc:
            error_msg = str(exc)
            if "corrupted" in error_msg.lower() or "invalid" in error_msg.lower():
                return jsonify({"error": "ไฟล์เสียหายหรือไม่ถูกต้อง กรุณาเลือกไฟล์อื่น"}), 400
            elif "permission" in error_msg.lower() or "access" in error_msg.lower():
                return jsonify({"error": "ไม่สามารถเข้าถึงไฟล์ได้ กรุณาตรวจสอบสิทธิ์การเข้าถึง"}), 403
            else:
                return jsonify({"error": f"เกิดข้อผิดพลาด: {exc}"}), 500

    @app.route("/summarize", methods=["POST"])
    def summarize():
        try:
            data = request.get_json()
            text = data.get("text", "")
            lang = data.get("lang", "auto")
            provider = data.get("provider", "auto")
            max_length = data.get("max_length", None)
            min_length = data.get("min_length", None)
            
            if not text:
                return jsonify({"error": "ไม่พบข้อความที่จะสรุป"}), 400
            
            # เริ่มจับเวลาการประมวลผล
            start_time = time.time()
            
            # Check memory and optimize for large text processing
            text_length = len(text)
            check_memory_usage()
            optimize_for_large_text(text_length)
            
            # ใช้พารามิเตอร์ที่ปรับปรุงแล้วสำหรับการสรุปข้อความยาว
            summary = summarize_text(
                text, 
                lang=lang, 
                provider=provider,
                max_length=max_length,
                min_length=min_length
            )
            
            end_time = time.time()
            
            # Clean up memory after processing
            if text_length > 20000:
                gc.collect()
            
            # คำนวณเวลาการประมวลผล
            processing_time = end_time - start_time
            
            # Calculate compression ratio
            compression_ratio = ((len(text) - len(summary)) / len(text) * 100) if len(text) > 0 else 0
            
            # บันทึกข้อมูลสรุปลง database
            # ใช้ filename จาก request ถ้ามี หรือใช้ค่า default
            original_file = data.get("filename", "unknown")
            extraction_id = data.get("extraction_id", None)  # ถ้ามี extraction_id จาก extraction
            from_search = data.get("from_search", False)  # ตรวจสอบ flag
            
            # บันทึกข้อมูลสรุปลง database เฉพาะเมื่อไม่ใช่จาก search bar
            # ถ้ามาจาก search bar ไม่ต้องบันทึก (เพราะมีอยู่ใน database อยู่แล้ว)
            if not from_search:
                try:
                    save_summary_to_db(
                        original_file=original_file,
                        extracted_text=text,
                        summary=summary,
                        processing_time=processing_time,
                        text_length=len(text),
                        summary_length=len(summary),
                        extraction_id=extraction_id,
                        lang=lang,
                        provider=provider,
                        max_length=max_length,
                        min_length=min_length
                    )
                except Exception as db_error:
                    print(f"Warning: Could not save summary to database: {db_error}")
            else:
                print(f"Summary from search (extraction_id: {extraction_id}), skipping database save")
            
            return jsonify({
                "summary": summary,
                "processing_time": f"{processing_time:.2f} วินาที",
                "text_length": len(text),
                "summary_length": len(summary),
                "compression_ratio": f"{compression_ratio:.1f}%"
            })
            
        except Exception as exc:
            # Enhanced error handling with more specific error messages
            error_message = str(exc)
            if "timeout" in error_message.lower() or "timed out" in error_message.lower():
                return jsonify({"error": "การประมวลผลใช้เวลานานเกินไป กรุณาลองใหม่อีกครั้ง"}), 408
            elif "memory" in error_message.lower() or "out of memory" in error_message.lower():
                return jsonify({"error": "ข้อความยาวเกินไป กรุณาลดขนาดข้อความแล้วลองใหม่อีกครั้ง"}), 413
            elif "connection" in error_message.lower() or "network" in error_message.lower():
                return jsonify({"error": "เกิดปัญหาการเชื่อมต่อ กรุณาลองใหม่อีกครั้ง"}), 503
            else:
                return jsonify({"error": f"เกิดข้อผิดพลาดในการสรุป: {exc}"}), 500

    @app.route("/download_summary", methods=["POST"])
    def download_summary():
        try:
            data = request.get_json()
            summary = data.get("summary", "")
            filename = data.get("filename", "summary")
            
            if not summary:
                return jsonify({"error": "ไม่พบข้อความที่จะดาวน์โหลด"}), 400
            
            download_name = f"{filename}_summary.txt"
            output = BytesIO(summary.encode("utf-8"))
            output.seek(0)
            return send_file(
                output,
                mimetype="text/plain; charset=utf-8",
                as_attachment=True,
                download_name=download_name,
            )
            
        except Exception as exc:
            error_msg = str(exc)
            if "memory" in error_msg.lower() or "out of memory" in error_msg.lower():
                return jsonify({"error": "เนื้อหายาวเกินไป กรุณาลดขนาดข้อความแล้วลองใหม่อีกครั้ง"}), 413
            elif "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                return jsonify({"error": "การดาวน์โหลดใช้เวลานานเกินไป กรุณาลองใหม่อีกครั้ง"}), 408
            else:
                return jsonify({"error": f"เกิดข้อผิดพลาดในการดาวน์โหลด: {exc}"}), 500

    @app.route("/api/search", methods=["POST"])
    def search_files():
        """API endpoint สำหรับค้นหาไฟล์"""
        try:
            data = request.get_json()
            query = data.get("query", "").strip()
            file_type = data.get("file_type", "")
            date_from = data.get("date_from", "")
            date_to = data.get("date_to", "")
            page = int(data.get("page", 1))
            per_page = int(data.get("per_page", 10))
            
            if not query or len(query) < 1:
                return jsonify({
                    "success": False,
                    "error": "กรุณาระบุคำค้นหาอย่างน้อย 1 ตัวอักษร"
                }), 400
            
            # จำกัด per_page
            per_page = min(per_page, 50)
            
            # ตรวจสอบว่ามี database connection หรือไม่
            try:
                from database.connection import get_db_connection
                
                # สร้าง search conditions
                conditions = []
                params = []
                
                # ค้นหาจากชื่อไฟล์ (filename) ใน extraction_records
                conditions.append("(e.filename LIKE %s)")
                params.append(f"%{query}%")
                
                # Filter by file type
                if file_type:
                    conditions.append("e.file_type = %s")
                    params.append(file_type)
                
                # Filter by date
                if date_from:
                    conditions.append("DATE(e.created_at) >= %s")
                    params.append(date_from)
                
                if date_to:
                    conditions.append("DATE(e.created_at) <= %s")
                    params.append(date_to)
                
                # สร้าง WHERE clause
                where_clause = " AND ".join(conditions)
                
                # Query สำหรับนับจำนวนทั้งหมด
                count_sql = f"""
                    SELECT COUNT(DISTINCT e.id) as total
                    FROM extraction_records e
                    WHERE {where_clause}
                """
                
                # Query สำหรับดึงข้อมูล (ไม่ดึง original_file_data และ extracted_text เต็ม เพราะใหญ่เกินไป)
                offset = (page - 1) * per_page
                
                # สร้าง patterns สำหรับ ORDER BY
                starts_with_query = f"{query}%"
                starts_with_first_char = f"{query[0]}%" if len(query) > 0 else "%"
                contains_query = f"%{query}%"
                
                search_sql = f"""
                    SELECT DISTINCT
                        e.id,
                        e.filename,
                        e.file_type,
                        e.file_size,
                        LEFT(e.extracted_text, 1000) as extracted_text_preview,
                        e.extracted_text_length,
                        e.total_pages,
                        e.ocr_used,
                        e.original_file_path,
                        e.processing_time,
                        e.created_at,
                        e.updated_at,
                        e.file_hash,
                        (SELECT COUNT(*) FROM summary_records s WHERE s.extraction_id = e.id) as summary_count
                    FROM extraction_records e
                    WHERE {where_clause}
                    ORDER BY 
                        CASE 
                            WHEN e.filename LIKE %s THEN 1
                            WHEN e.filename LIKE %s THEN 2
                            WHEN e.filename LIKE %s THEN 3
                            ELSE 4
                        END,
                        e.created_at DESC
                    LIMIT %s OFFSET %s
                """
                
                # Execute queries
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Count total
                    cursor.execute(count_sql, tuple(params))
                    total_result = cursor.fetchone()
                    total = total_result['total'] if total_result else 0
                    
                    # Get results - เพิ่ม parameters สำหรับ ORDER BY
                    cursor.execute(search_sql, tuple(params + [starts_with_query, starts_with_first_char, contains_query, per_page, offset]))
                    results = cursor.fetchall()
                    
                    # Format results
                    formatted_results = []
                    for result in results:
                        formatted_results.append({
                            "id": result['id'],
                            "filename": result['filename'],
                            "file_type": result['file_type'],
                            "file_size": result['file_size'],
                            "extracted_text_preview": result['extracted_text_preview'],
                            "extracted_text_length": result['extracted_text_length'],
                            "total_pages": result['total_pages'],
                            "ocr_used": bool(result['ocr_used']),
                            "has_summary": bool(result['summary_count'] and result['summary_count'] > 0),
                            "created_at": result['created_at'].isoformat() if result['created_at'] else None,
                            "updated_at": result['updated_at'].isoformat() if result['updated_at'] else None,
                            "original_file_path": result['original_file_path'],
                            "file_hash": result['file_hash'],
                            "processing_time": float(result['processing_time']) if result['processing_time'] else None
                        })
                    
                    # Calculate pagination
                    total_pages = (total + per_page - 1) // per_page if total > 0 else 0
                    
                    return jsonify({
                        "success": True,
                        "query": query,
                        "results": formatted_results,
                        "total": total,
                        "page": page,
                        "per_page": per_page,
                        "pages": total_pages
                    })
            
            except ImportError:
                # ถ้ายังไม่มี database module ให้ return mock data
                return jsonify({
                    "success": True,
                    "query": query,
                    "results": [],
                    "total": 0,
                    "page": page,
                    "per_page": per_page,
                    "pages": 0,
                    "message": "Database not configured. Please set up database connection."
                })
            except Exception as db_error:
                print(f"Database error: {db_error}")
                return jsonify({
                    "success": False,
                    "error": f"เกิดข้อผิดพลาดในการค้นหา: {str(db_error)}"
                }), 500
        
        except Exception as e:
            print(f"Search error: {e}")
            return jsonify({
                "success": False,
                "error": f"เกิดข้อผิดพลาดในการค้นหา: {str(e)}"
            }), 500

    @app.route("/api/search/suggestions", methods=["GET"])
    def search_suggestions():
        """API endpoint สำหรับ autocomplete suggestions"""
        try:
            query = request.args.get("q", "").strip()
            
            if not query or len(query) < 1:
                return jsonify({
                    "success": True,
                    "suggestions": []
                })
            
            try:
                from database.connection import get_db_connection
                
                # ค้นหาชื่อไฟล์ที่ขึ้นต้นด้วย query หรือมี query อยู่ (case-insensitive)
                # เรียงลำดับให้พิจารณาตัวอักษรแรกที่พิมพ์
                # 1. ไฟล์ที่ขึ้นต้นด้วย query ทั้งหมด
                # 2. ไฟล์ที่ขึ้นต้นด้วยตัวอักษรแรกของ query
                # 3. ไฟล์ที่มี query อยู่ที่อื่น
                sql = """
                    SELECT DISTINCT e.filename, e.file_type, e.id
                    FROM extraction_records e
                    WHERE e.filename LIKE %s
                    ORDER BY 
                        CASE 
                            WHEN e.filename LIKE %s THEN 1
                            WHEN e.filename LIKE %s THEN 2
                            WHEN e.filename LIKE %s THEN 3
                            ELSE 4
                        END,
                        e.created_at DESC
                    LIMIT 10
                """
                
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    # สร้าง patterns สำหรับ ORDER BY
                    search_pattern = f"%{query}%"
                    starts_with_query = f"{query}%"
                    starts_with_first_char = f"{query[0]}%" if len(query) > 0 else "%"
                    contains_query = f"%{query}%"
                    cursor.execute(sql, (search_pattern, starts_with_query, starts_with_first_char, contains_query))
                    results = cursor.fetchall()
                    
                    suggestions = []
                    for result in results:
                        suggestions.append({
                            "filename": result['filename'],
                            "file_type": result['file_type'],
                            "id": result['id']
                        })
                    
                    return jsonify({
                        "success": True,
                        "suggestions": suggestions
                    })
            
            except ImportError:
                return jsonify({
                    "success": True,
                    "suggestions": []
                })
            except Exception as db_error:
                # ตรวจสอบว่าเป็น error เกี่ยวกับ table ไม่มีหรือไม่
                error_str = str(db_error)
                if "doesn't exist" in error_str.lower() or "1146" in error_str:
                    # ตารางยังไม่มี - ไม่ต้องแสดง error log
                    pass
                else:
                    # Error อื่นๆ - แสดง log
                    print(f"Suggestions error: {db_error}")
                return jsonify({
                    "success": True,
                    "suggestions": []
                })
        
        except Exception as e:
            print(f"Suggestions error: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route("/api/tags/popular", methods=["GET"])
    def get_popular_tags():
        """API endpoint สำหรับดึง tags ที่ใช้บ่อย"""
        try:
            limit = int(request.args.get("limit", 10))
            limit = min(limit, 50)
            
            try:
                from database.connection import get_db_connection
                
                sql = """
                    SELECT id, name, slug, color, category, usage_count
                    FROM tags
                    ORDER BY usage_count DESC, name ASC
                    LIMIT %s
                """
                
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(sql, (limit,))
                    tags = cursor.fetchall()
                    
                    return jsonify({
                        "success": True,
                        "tags": tags
                    })
            
            except ImportError:
                # ถ้ายังไม่มี database module ให้ return empty
                return jsonify({
                    "success": True,
                    "tags": []
                })
            except Exception as db_error:
                # ตรวจสอบว่าเป็น error เกี่ยวกับ table ไม่มีหรือไม่
                error_str = str(db_error)
                if "doesn't exist" in error_str.lower() or "1146" in error_str:
                    # ตารางยังไม่มี - ไม่ต้องแสดง error log
                    pass
                else:
                    # Error อื่นๆ - แสดง log
                    print(f"Database error: {db_error}")
                return jsonify({
                    "success": True,
                    "tags": []
                })
        
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route("/api/extractions/<int:extraction_id>/download", methods=["GET"])
    def download_extraction(extraction_id):
        """API endpoint สำหรับดาวน์โหลดไฟล์ที่แปลงแล้ว"""
        try:
            from database.connection import get_db_connection
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT extracted_text, filename
                    FROM extraction_records
                    WHERE id = %s
                """, (extraction_id,))
                
                result = cursor.fetchone()
                
                if not result or not result['extracted_text']:
                    return jsonify({"error": "ไม่พบข้อมูล"}), 404
                
                # ใช้ extracted_text โดยตรง
                content = result['extracted_text']
                
                output = BytesIO(content.encode("utf-8"))
                output.seek(0)
                
                download_name = os.path.splitext(result['filename'])[0] + ".txt"
                
                return send_file(
                    output,
                    mimetype="text/plain; charset=utf-8",
                    as_attachment=True,
                    download_name=download_name,
                )
        
        except ImportError:
            return jsonify({"error": "Database not configured"}), 503
        except Exception as e:
            print(f"Download error: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/extractions/<int:extraction_id>/load", methods=["GET"])
    def load_extraction(extraction_id):
        """API endpoint สำหรับโหลดไฟล์ original จาก database เพื่อแสดงและวิเคราะห์"""
        try:
            from database.connection import get_db_connection
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        id, filename, file_type, file_size, file_hash,
                        extracted_text, extracted_text_length,
                        total_pages, ocr_used, ocr_pages,
                        original_file_path, original_file_hash,
                        created_at
                    FROM extraction_records
                    WHERE id = %s
                """, (extraction_id,))
                
                result = cursor.fetchone()
                
                if not result:
                    return jsonify({"error": "ไม่พบข้อมูล"}), 404
                
                # ส่งข้อมูลกลับ (ไม่ส่ง original_file_data ผ่าน JSON เพราะใหญ่เกินไป)
                # จะส่งผ่าน endpoint แยก
                return jsonify({
                    "success": True,
                    "extraction_id": result['id'],
                    "filename": result['filename'],
                    "file_type": result['file_type'],
                    "file_size": result['file_size'],
                    "file_hash": result['file_hash'],
                    "extracted_text": result['extracted_text'],  # ข้อความเต็ม
                    "extracted_text_length": result['extracted_text_length'],
                    "total_pages": result['total_pages'],
                    "ocr_used": bool(result['ocr_used']),
                    "ocr_pages": json.loads(result['ocr_pages']) if result['ocr_pages'] else None,
                    "original_file_path": result['original_file_path'],
                    "created_at": result['created_at'].isoformat() if result['created_at'] else None,
                    "from_search": True  # Flag เพื่อบอกว่าไฟล์มาจาก search
                })
        
        except ImportError:
            return jsonify({"error": "Database not configured"}), 503
        except Exception as e:
            print(f"Load extraction error: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/extractions/<int:extraction_id>/original-file", methods=["GET"])
    def get_original_file(extraction_id):
        """API endpoint สำหรับดาวน์โหลดไฟล์ original จาก database"""
        try:
            from database.connection import get_db_connection
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT original_file_data, filename, file_type
                    FROM extraction_records
                    WHERE id = %s
                """, (extraction_id,))
                
                result = cursor.fetchone()
                
                if not result or not result['original_file_data']:
                    return jsonify({"error": "ไม่พบไฟล์"}), 404
                
                # ส่งไฟล์กลับ
                file_bytes = result['original_file_data']
                filename = result['filename']
                file_type = result['file_type']
                
                # กำหนด MIME type
                mime_types = {
                    'pdf': 'application/pdf',
                    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'txt': 'text/plain',
                    'jpg': 'image/jpeg',
                    'jpeg': 'image/jpeg',
                    'png': 'image/png',
                    'gif': 'image/gif'
                }
                mimetype = mime_types.get(file_type.lower(), 'application/octet-stream')
                
                output = BytesIO(file_bytes)
                output.seek(0)
                
                return send_file(
                    output,
                    mimetype=mimetype,
                    as_attachment=True,
                    download_name=filename
                )
        
        except ImportError:
            return jsonify({"error": "Database not configured"}), 503
        except Exception as e:
            print(f"Get original file error: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/extractions/<int:extraction_id>/re-extract", methods=["POST"])
    def re_extract_from_search(extraction_id):
        """API endpoint สำหรับแปลงไฟล์ใหม่จาก search results (ไม่บันทึกซ้ำ)"""
        try:
            from database.connection import get_db_connection
            from extractors.file_text_extractor import extract_text_from_upload
            
            # ดึงข้อมูล extraction record พร้อมไฟล์ original
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT filename, file_type, original_file_data, extracted_text
                    FROM extraction_records
                    WHERE id = %s
                """, (extraction_id,))
                
                result = cursor.fetchone()
                
                if not result:
                    return jsonify({"error": "ไม่พบข้อมูล"}), 404
                
                # ใช้ไฟล์ original ที่เก็บไว้
                file_bytes = result['original_file_data']
                filename = result['filename']
                
                # แปลงไฟล์ใหม่
                start_time = time.time()
                extracted_text, ocr_used, pages_data = extract_text_from_upload(filename, file_bytes)
                processing_time = time.time() - start_time
                
                # ไม่บันทึกซ้ำ (เพราะมีอยู่แล้ว)
                # แค่ return ข้อมูลกลับไป
                
                return jsonify({
                    "success": True,
                    "filename": filename,
                    "extracted_text": extracted_text,
                    "extracted_text_length": len(extracted_text),
                    "total_pages": len(pages_data) if pages_data else 0,
                    "ocr_used": ocr_used,
                    "pages_data": pages_data,
                    "processing_time": f"{processing_time:.2f} วินาที",
                    "from_search": True,
                    "extraction_id": extraction_id
                })
        
        except ImportError:
            return jsonify({"error": "Database not configured"}), 503
        except Exception as e:
            print(f"Re-extract error: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/extraction/<int:extraction_id>", methods=["GET"])
    def view_extraction(extraction_id):
        """แสดงหน้า extraction detail และโหลดไฟล์ original"""
        try:
            from database.connection import get_db_connection
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT filename, file_type, original_file_data, extracted_text,
                           total_pages, ocr_used, ocr_pages, extracted_text_length
                    FROM extraction_records
                    WHERE id = %s
                """, (extraction_id,))
                
                result = cursor.fetchone()
                
                if not result:
                    return render_template("index.html", 
                                         extracted_text=None, 
                                         filename=None, 
                                         error_message="ไม่พบข้อมูล", 
                                         summary=None)
                
                # ใช้ extracted_text ที่มีอยู่แล้ว
                extracted_text = result['extracted_text'] or ""
                filename = result['filename']
                total_pages = result['total_pages'] or 0
                ocr_used = bool(result['ocr_used'])
                
                # Parse pages_data จาก ocr_pages
                pages_data = []
                if result['ocr_pages']:
                    try:
                        ocr_pages_list = json.loads(result['ocr_pages'])
                        # สร้าง pages_data จาก extracted_text
                        if extracted_text and total_pages > 0:
                            text_length = len(extracted_text)
                            text_per_page = text_length // total_pages if total_pages > 0 else text_length
                            for i in range(total_pages):
                                start = i * text_per_page
                                end = (i + 1) * text_per_page if i < total_pages - 1 else text_length
                                page_text = extracted_text[start:end]
                                pages_data.append({
                                    'page_num': i + 1,
                                    'text': page_text,
                                    'ocr_used': (i + 1) in ocr_pages_list if ocr_pages_list else False
                                })
                    except Exception as e:
                        print(f"Error parsing pages_data: {e}")
                        # ถ้า parse ไม่ได้ ให้สร้าง pages_data แบบง่าย
                        if extracted_text:
                            pages_data.append({
                                'page_num': 1,
                                'text': extracted_text,
                                'ocr_used': ocr_used
                            })
                elif extracted_text:
                    # ถ้าไม่มี ocr_pages ให้สร้าง pages_data แบบง่าย
                    pages_data.append({
                        'page_num': 1,
                        'text': extracted_text,
                        'ocr_used': ocr_used
                    })
                
                # ส่งข้อมูลไปยัง template
                return render_template("index.html", 
                                     extracted_text=extracted_text, 
                                     filename=filename, 
                                     error_message=None, 
                                     summary=None, 
                                     ocr_used=ocr_used,
                                     pages_data=pages_data,
                                     total_pages=total_pages,
                                     from_search=True,
                                     extraction_id=extraction_id)
        
        except ImportError:
            return render_template("index.html", 
                                 extracted_text=None, 
                                 filename=None, 
                                 error_message="Database not configured", 
                                 summary=None)
        except Exception as e:
            print(f"View extraction error: {e}")
            import traceback
            traceback.print_exc()
            return render_template("index.html", 
                                 extracted_text=None, 
                                 filename=None, 
                                 error_message=f"เกิดข้อผิดพลาด: {str(e)}", 
                                 summary=None)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)