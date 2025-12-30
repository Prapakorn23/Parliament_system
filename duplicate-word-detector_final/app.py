"""
Flask Backend API สำหรับระบบตรวจจับคำซ้ำอัตโนมัติ
Duplicate Word Detector - Automatic Word Frequency Analysis System
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import json
import os
import matplotlib
matplotlib.use('Agg')  # ใช้ backend ที่ไม่ต้องการ GUI
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from core.duplicate_word_detector import ThaiDuplicateWordDetector
from core.performance_utils import PerformanceTracker
from core.word_categorizer import ParliamentWordCategorizer
from core.pdf_processor import PDFProcessor
from core.doc_processor import DocProcessor
from core.database import get_db_manager
from core.date_extractor import get_date_extractor
from config.config import *
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ตั้งค่า matplotlib สำหรับฟอนต์ไทย
# หาฟอนต์ที่มีในระบบ
available_fonts = [f.name for f in fm.fontManager.ttflist]

# ลองหาฟอนต์ที่รองรับภาษาไทย
thai_font_candidates = [
    'Tahoma', 'Arial', 'Microsoft Sans Serif', 'Segoe UI', 
    'Calibri', 'Times New Roman', 'Courier New'
]

selected_font = 'DejaVu Sans'  # default
for font in thai_font_candidates:
    if font in available_fonts:
        selected_font = font
        break

plt.rcParams['font.family'] = selected_font
print(f"ใช้ฟอนต์: {selected_font}")

# สร้างโฟลเดอร์สำหรับเก็บไฟล์ชั่วคราว
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC_FOLDER'] = STATIC_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE  # ตั้งค่าผ่าน MAX_FILE_SIZE_MB ใน config

# ตัวแปรสำหรับเก็บข้อมูลการวิเคราะห์
analysis_data = {
    'detector': ThaiDuplicateWordDetector(tokenize_engine=TOKENIZE_ENGINE),
    'categorizer': ParliamentWordCategorizer(),
    'pdf_processor': PDFProcessor(),
    'doc_processor': DocProcessor(),
    'current_analysis': None,
    'performance_tracker': PerformanceTracker()
}


# ฟังก์ชัน create_chart_image ถูกลบออกแล้ว
# เนื่องจาก frontend ใช้ Chart.js สร้างกราฟในฝั่ง client แล้ว
# ไม่จำเป็นต้องสร้างและบันทึกไฟล์ PNG ลง disk


@app.route('/')
def index():
    """หน้าแรกของ Dashboard"""
    return render_template('dashboard.html')


@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    """API สำหรับวิเคราะห์ข้อความ"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        filter_pos = data.get('filter_pos', True)
        target_pos = data.get('target_pos', None)
        
        # ข้อมูลไฟล์ต้นฉบับ (ถ้ามี)
        file_name = data.get('file_name')
        file_type = data.get('file_type')
        original_file_path = data.get('original_file_path')
        file_size = data.get('file_size')
        
        if not text:
            return jsonify({'error': 'ไม่มีข้อความที่ส่งมา'}), 400
        
        # วิเคราะห์ข้อความ
        detector = analysis_data['detector']
        categorizer = analysis_data['categorizer']
        result = detector.analyze_text(text, filter_pos=filter_pos, target_pos=target_pos)
        
        # สร้างกราฟ
        top_words_list = detector.get_most_frequent_words(15)
        # แปลง list of tuples เป็น dictionary สำหรับ JavaScript
        top_words = {word: freq for word, freq in top_words_list}
        
        # ไม่สร้างไฟล์ภาพ PNG แล้ว - frontend ใช้ Chart.js สร้างกราฟในฝั่ง client
        
        # จัดหมวดหมู่คำ
        word_freq_dict = dict(result['word_frequency'])
        categorized_words = categorizer.categorize_words(word_freq_dict)
        category_summary = categorizer.get_category_summary(categorized_words)
        top_words_by_category = categorizer.get_top_words_by_category(categorized_words, top_n=5)
        
        # บันทึกข้อมูลการวิเคราะห์ลง database
        try:
            db = get_db_manager()
            now = datetime.now()
            
            # กำหนด source_type ตามว่ามีไฟล์หรือไม่
            source_type = 'file' if file_name else 'text'
            
            analysis_id = db.create_analysis({
                'title': data.get('title', 'การวิเคราะห์ข้อความ'),
                'source_type': source_type,
                'file_name': file_name,
                'file_type': file_type,
                'original_file_path': original_file_path,
                'file_size': file_size,
                'file_content': text if source_type == 'text' else None,  # เก็บข้อความต้นฉบับสำหรับ text input
                'total_words': result['total_words'],
                'unique_words': result['unique_words'],
                'processing_time': result.get('processing_time')
            })
            
            # บันทึก word frequencies
            pos_tags_dict = {}
            for word, pos in result.get('filtered_words', []):
                pos_tags_dict[word] = pos
            
            db.save_word_frequencies(analysis_id, word_freq_dict, pos_tags_dict)
            
            # ไม่บันทึก POS frequencies แยก - POS tags เก็บใน word_frequencies.pos_tag แล้ว
            
            # บันทึก categories
            db.save_categories(analysis_id, categorized_words)
            
            print(f"✅ บันทึกข้อมูลการวิเคราะห์ลง database สำเร็จ (ID: {analysis_id})")
        except Exception as db_error:
            print(f"⚠️  ไม่สามารถบันทึกข้อมูลลง database: {db_error}")
            # ยังทำงานต่อได้ แค่ไม่บันทึกข้อมูล
        
        # บันทึกข้อมูลการวิเคราะห์
        analysis_data['current_analysis'] = {
            'text': text,
            'result': result,
            'top_words': top_words,
            'categorized_words': categorized_words,
            'category_summary': category_summary,
            'top_words_by_category': top_words_by_category
        }
        
        return jsonify({
            'success': True,
            'data': {
                'total_words': result['total_words'],
                'unique_words': result['unique_words'],
                'word_frequency': word_freq_dict,
                'top_words': top_words,
                'categorized_words': {k: dict(v) for k, v in categorized_words.items()},
                'category_summary': [{'category': cat, 'unique_words': unique, 'total_frequency': freq} 
                                    for cat, unique, freq in category_summary],
                'top_words_by_category': {k: list(v) for k, v in top_words_by_category.items()}
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'เกิดข้อผิดพลาด: {str(e)}'}), 500


# Note: compare_texts endpoint removed - functionality not implemented in current version
# สามารถใช้ /api/analyze หลายครั้งและเปรียบเทียบผลลัพธ์เอง


@app.route('/api/upload-config', methods=['GET'])
def get_upload_config():
    """API สำหรับดึงค่าการตั้งค่าการอัปโหลดไฟล์"""
    max_size_mb = MAX_FILE_SIZE / (1024 * 1024)
    return jsonify({
        'max_file_size': MAX_FILE_SIZE,
        'max_file_size_mb': max_size_mb,
        'allowed_extensions': list(ALLOWED_EXTENSIONS)
    })


@app.route('/api/upload-multiple', methods=['POST'])
def upload_multiple_files():
    """API สำหรับอัปโหลดไฟล์หลายไฟล์ (รองรับ .txt, .pdf, .doc, .docx)"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'ไม่มีไฟล์ที่ส่งมา'}), 400
        
        files = request.files.getlist('files')  # รับไฟล์หลายไฟล์
        if not files or len(files) == 0:
            return jsonify({'error': 'ไม่ได้เลือกไฟล์'}), 400
        
        # ตรวจสอบขนาดไฟล์ทั้งหมด
        for file in files:
            if file.filename == '':
                continue
            
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)  # Reset file pointer
            
            if file_size > MAX_FILE_SIZE:
                max_size_mb = MAX_FILE_SIZE / (1024 * 1024)
                return jsonify({'error': f'ไฟล์ {file.filename} ใหญ่เกินไป กรุณาเลือกไฟล์ที่มีขนาดไม่เกิน {max_size_mb:.0f}MB'}), 400
        
        # ประมวลผลไฟล์ทั้งหมด
        processed_files = []
        file_paths = []
        
        for file in files:
            if file.filename == '':
                continue
                
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            file_paths.append(filepath)
            
            
            content = ""
            file_type = ""
            extraction_method = ""
            
            filename_lower = filename.lower()
            
            try:
                # ตรวจสอบประเภทไฟล์
                if filename_lower.endswith('.pdf'):
                    # ประมวลผล PDF
                    pdf_processor = analysis_data['pdf_processor']
                    success, content, method = pdf_processor.extract_text_from_pdf(filepath)
                    
                    if not success:
                        processed_files.append({
                            'filename': filename,
                            'success': False,
                            'error': f'ไม่สามารถแปลง PDF เป็น text ได้: {method}',
                            'content': ''
                        })
                        continue
                    
                    file_type = "pdf"
                    extraction_method = method
                    
                elif filename_lower.endswith(('.doc', '.docx')):
                    # ประมวลผล Word Document
                    doc_processor = analysis_data['doc_processor']
                    success, content, method = doc_processor.extract_text_from_document(filepath)
                    
                    if not success:
                        error_msg = f'ไม่สามารถแปลงไฟล์ Word เป็น text ได้: {method}'
                        processed_files.append({
                            'filename': filename,
                            'success': False,
                            'error': error_msg,
                            'content': ''
                        })
                        continue
                    
                    if filename_lower.endswith('.docx'):
                        file_type = "docx"
                    else:
                        file_type = "doc"
                    extraction_method = method
                    
                else:
                    # อ่านไฟล์ text ธรรมดา
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        file_type = "txt"
                        extraction_method = "Direct Read"
                    except UnicodeDecodeError:
                        # ลองใช้ encoding อื่น
                        try:
                            with open(filepath, 'r', encoding='cp874') as f:
                                content = f.read()
                            file_type = "txt-tis620"
                            extraction_method = "Direct Read (TIS-620)"
                        except:
                            processed_files.append({
                                'filename': filename,
                                'success': False,
                                'error': 'ไม่สามารถอ่านไฟล์ได้ กรุณาตรวจสอบ encoding หรือประเภทไฟล์',
                                'content': ''
                            })
                            continue
                
                # เก็บข้อมูลไฟล์ต้นฉบับ
                file_size = os.path.getsize(filepath) if os.path.exists(filepath) else None
                
                # เพิ่มข้อมูลไฟล์ที่ประมวลผลสำเร็จ
                processed_files.append({
                    'filename': filename,
                    'file_type': file_type,
                    'extraction_method': extraction_method,
                    'content': content,  # ส่งข้อความเต็ม (frontend จะจัดการเอง)
                    'original_file_path': filepath,  # path ของไฟล์ต้นฉบับ
                    'file_size': file_size,  # ขนาดไฟล์ (bytes)
                    'success': True
                })
                
            except Exception as e:
                processed_files.append({
                    'filename': filename,
                    'success': False,
                    'error': f'เกิดข้อผิดพลาด: {str(e)}',
                    'content': ''
                })
        
        # ลบไฟล์ทั้งหมดหลังประมวลผลเสร็จ
        for filepath in file_paths:
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
            except:
                pass
        
        # คืนค่าผลลัพธ์
        return jsonify({
            'success': True,
            'data': processed_files,
            'total_files': len(processed_files),
            'successful_files': len([f for f in processed_files if f.get('success', False)])
        })
        
    except Exception as e:
        return jsonify({'error': f'เกิดข้อผิดพลาด: {str(e)}'}), 500


@app.route('/api/export', methods=['POST'])
def export_results():
    """API สำหรับส่งออกผลลัพธ์"""
    try:
        data = request.get_json()
        export_type = data.get('type', 'excel')
        filename = data.get('filename', 'analysis_results')
        
        if not analysis_data['current_analysis']:
            return jsonify({'error': 'ไม่มีข้อมูลการวิเคราะห์'}), 400
        
        detector = analysis_data['detector']
        
        if export_type == 'json':
            # ส่งออกเป็น JSON
            from datetime import datetime
            json_data = {
                'analysis_result': analysis_data['current_analysis']['result'],
                'top_words': analysis_data['current_analysis']['top_words'],
                'timestamp': datetime.now().isoformat()
            }
            
            json_path = os.path.join(app.config['STATIC_FOLDER'], f'{filename}.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            
            return jsonify({
                'success': True,
                'download_url': f'/static/{filename}.json'
            })
        
        else:
            return jsonify({'error': 'รูปแบบการส่งออกไม่ถูกต้อง'}), 400
        
    except Exception as e:
        return jsonify({'error': f'เกิดข้อผิดพลาด: {str(e)}'}), 500


@app.route('/api/reset', methods=['POST'])
def reset_analysis():
    """API สำหรับรีเซ็ตการวิเคราะห์"""
    try:
        detector = analysis_data['detector']
        detector.reset()
        analysis_data['current_analysis'] = None
        
        return jsonify({'success': True, 'message': 'รีเซ็ตการวิเคราะห์เรียบร้อยแล้ว'})
        
    except Exception as e:
        return jsonify({'error': f'เกิดข้อผิดพลาด: {str(e)}'}), 500


@app.route('/static/<filename>')
def static_files(filename):
    """ให้บริการไฟล์ static"""
    return send_from_directory(app.config['STATIC_FOLDER'], filename)


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """API สำหรับดึงสถิติการใช้งาน"""
    try:
        detector = analysis_data['detector']
        
        stats = {
            'total_texts_analyzed': len(detector.processed_texts),
            'total_words_processed': sum(text_data['total_words'] for text_data in detector.processed_texts),
            'total_unique_words': len(detector.word_frequency),
            'most_frequent_word': detector.word_frequency.most_common(1)[0] if detector.word_frequency else None
        }
        
        return jsonify({'success': True, 'data': stats})
        
    except Exception as e:
        return jsonify({'error': f'เกิดข้อผิดพลาด: {str(e)}'}), 500


@app.route('/api/performance', methods=['GET'])
def get_performance_stats():
    """API สำหรับดึงสถิติประสิทธิภาพ"""
    try:
        detector = analysis_data['detector']
        performance_stats = detector.get_performance_stats()
        
        return jsonify({'success': True, 'data': performance_stats})
        
    except Exception as e:
        return jsonify({'error': f'เกิดข้อผิดพลาด: {str(e)}'}), 500




@app.route('/api/check-pdf-support', methods=['GET'])
def check_pdf_support():
    """ตรวจสอบว่ารองรับ PDF และ OCR หรือไม่"""
    try:
        pdf_processor = analysis_data['pdf_processor']
        support_info = pdf_processor.supported_methods
        instructions = pdf_processor.get_installation_instructions()
        
        return jsonify({
            'success': True,
            'data': {
                'supported_methods': support_info,
                'installation_instructions': instructions
            }
        })
    except Exception as e:
        return jsonify({'error': f'เกิดข้อผิดพลาด: {str(e)}'}), 500


@app.route('/api/check-doc-support', methods=['GET'])
def check_doc_support():
    """ตรวจสอบว่ารองรับ Word Documents (.doc, .docx) หรือไม่"""
    try:
        doc_processor = analysis_data['doc_processor']
        support_info = doc_processor.supported_methods
        instructions = doc_processor.get_installation_instructions()
        
        return jsonify({
            'success': True,
            'data': {
                'supported_methods': support_info,
                'installation_instructions': instructions
            }
        })
    except Exception as e:
        return jsonify({'error': f'เกิดข้อผิดพลาด: {str(e)}'}), 500


@app.route('/api/cleanup-files', methods=['POST'])
def cleanup_files():
    """API สำหรับลบไฟล์ที่ไม่จำเป็น (ไฟล์เก่าใน uploads และ cache)"""
    try:
        import time
        from pathlib import Path
        
        deleted_files = []
        deleted_count = 0
        total_size_freed = 0
        
        # ลบไฟล์ใน uploads ที่เก่ากว่า 1 ชั่วโมง
        uploads_dir = Path(app.config['UPLOAD_FOLDER'])
        if uploads_dir.exists():
            current_time = time.time()
            for file_path in uploads_dir.iterdir():
                if file_path.is_file():
                    # ลบไฟล์ที่เก่ากว่า 1 ชั่วโมง
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > 3600:  # 1 ชั่วโมง = 3600 วินาที
                        try:
                            file_size = file_path.stat().st_size
                            file_path.unlink()
                            deleted_files.append(str(file_path.name))
                            deleted_count += 1
                            total_size_freed += file_size
                        except Exception as e:
                            print(f"⚠️  ไม่สามารถลบไฟล์ {file_path}: {e}")
        
        # ลบไฟล์ cache ที่เก่ากว่า 24 ชั่วโมง
        cache_dir = Path(CACHE_FOLDER)
        if cache_dir.exists():
            current_time = time.time()
            for file_path in cache_dir.iterdir():
                if file_path.is_file() and file_path.suffix == '.pkl':
                    # ลบไฟล์ cache ที่เก่ากว่า 24 ชั่วโมง
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > 86400:  # 24 ชั่วโมง = 86400 วินาที
                        try:
                            file_size = file_path.stat().st_size
                            file_path.unlink()
                            deleted_files.append(f"cache/{file_path.name}")
                            deleted_count += 1
                            total_size_freed += file_size
                        except Exception as e:
                            print(f"⚠️  ไม่สามารถลบไฟล์ cache {file_path}: {e}")
        
        size_mb = total_size_freed / (1024 * 1024)
        
        return jsonify({
            'success': True,
            'deleted_count': deleted_count,
            'deleted_files': deleted_files[:10],  # แสดงแค่ 10 ไฟล์แรก
            'total_size_freed_mb': round(size_mb, 2),
            'message': f'ลบไฟล์ {deleted_count} ไฟล์ (ประหยัดพื้นที่ {size_mb:.2f} MB)'
        })
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการลบไฟล์: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'เกิดข้อผิดพลาด: {str(e)}'
        }), 500


@app.route('/api/check-file-support', methods=['GET'])
def check_file_support():
    """ตรวจสอบการรองรับไฟล์ทั้งหมด (PDF, DOC, DOCX)"""
    try:
        pdf_processor = analysis_data['pdf_processor']
        doc_processor = analysis_data['doc_processor']
        
        return jsonify({
            'success': True,
            'data': {
                'pdf': {
                    'supported_methods': pdf_processor.supported_methods,
                    'installation_instructions': pdf_processor.get_installation_instructions()
                },
                'doc': {
                    'supported_methods': doc_processor.supported_methods,
                    'installation_instructions': doc_processor.get_installation_instructions()
                },
                'text': {
                    'supported': True,
                    'extensions': list(ALLOWED_TEXT_EXTENSIONS)
                }
            }
        })
    except Exception as e:
        return jsonify({'error': f'เกิดข้อผิดพลาด: {str(e)}'}), 500


def save_analysis_to_db(result, word_freq_dict, categorized_words, 
                        source_type='text', file_name=None, file_type=None, 
                        title=None, original_file_path=None, file_size=None, 
                        file_content=None):
    """
    Helper function สำหรับบันทึกข้อมูลการวิเคราะห์ลง database
    
    Args:
        result: ผลลัพธ์การวิเคราะห์
        word_freq_dict: dictionary ของความถี่คำ
        categorized_words: dictionary ของคำที่จัดหมวดหมู่
        source_type: ประเภทแหล่งที่มา ('text' หรือ 'file')
        file_name: ชื่อไฟล์
        file_type: ประเภทไฟล์
        title: หัวข้อการวิเคราะห์
        original_file_path: path ของไฟล์ต้นฉบับ
        file_size: ขนาดไฟล์ (bytes)
        file_content: เนื้อหาไฟล์ต้นฉบับ
    
    Returns:
        int: analysis_id ถ้าสำเร็จ, None ถ้าไม่สำเร็จ
    """
    try:
        db = get_db_manager()
        now = datetime.now()
        
        # Validate ข้อมูล
        if not result or 'total_words' not in result or 'unique_words' not in result:
            print("⚠️  ข้อมูล result ไม่ครบถ้วน")
            return None
        
        if not word_freq_dict:
            print("⚠️  ไม่มีข้อมูล word_frequency ที่จะบันทึก")
            return None
        
        # สร้าง analysis record
        analysis_id = db.create_analysis({
            'title': title or (file_name or 'การวิเคราะห์ข้อความ'),
            'source_type': source_type,
            'file_name': file_name,
            'file_type': file_type,
            'original_file_path': original_file_path,
            'file_size': file_size,
            'file_content': file_content,
            'total_words': result['total_words'],
            'unique_words': result['unique_words'],
            'processing_time': result.get('processing_time')
        })
        
        print(f"📝 สร้าง analysis record สำเร็จ (ID: {analysis_id})")
        
        # สร้าง pos_tags_dict
        pos_tags_dict = {}
        if 'filtered_words' in result:
            for word, pos in result.get('filtered_words', []):
                if word not in pos_tags_dict:
                    pos_tags_dict[word] = pos
        
        # บันทึก word frequencies
        db.save_word_frequencies(analysis_id, word_freq_dict, pos_tags_dict)
        print(f"✅ บันทึก word frequencies: {len(word_freq_dict)} คำ")
        
        # บันทึก POS frequencies
        # ไม่บันทึก POS frequencies แยก - POS tags เก็บใน word_frequencies.pos_tag แล้ว
        
        # บันทึก categories
        if categorized_words:
            db.save_categories(analysis_id, categorized_words)
            print(f"✅ บันทึก categories: {len(categorized_words)} หมวดหมู่")
        
        print(f"✅ บันทึกข้อมูลการวิเคราะห์ลง database สำเร็จ (Analysis ID: {analysis_id})")
        return analysis_id
        
    except Exception as e:
        import traceback
        print(f"❌ ไม่สามารถบันทึกข้อมูลลง database: {e}")
        traceback.print_exc()
        return None


if __name__ == '__main__':
    # สร้างโฟลเดอร์ templates
    os.makedirs('templates', exist_ok=True)
    
    # ตรวจสอบ PDF support
    pdf_processor = analysis_data['pdf_processor']
    support = pdf_processor.supported_methods
    
    print("=" * 70)
    print("🏛️  ระบบตรวจจับคำซ้ำอัตโนมัติสำหรับรัฐสภาไทย")
    print("    Duplicate Word Detector System for Thai Parliament")
    print("=" * 70)
    print("📊 เข้าใช้งานที่: http://localhost:5000")
    print("-" * 70)
    # ตรวจสอบ doc support
    doc_processor = analysis_data['doc_processor']
    doc_support = doc_processor.supported_methods
    
    print("📂 รองรับไฟล์:")
    print("   - Text Files (.txt)")
    print(f"   - PDF Files (.pdf) - Text: {'✅' if support['pdfplumber'] or support['pypdf2'] else '❌'}")
    print(f"   - PDF Files (.pdf) - Image (OCR): {'✅' if support['ocr'] else '❌'}")
    print(f"   - Word Documents (.docx): {'✅' if doc_support['python-docx'] else '❌'}")
    print(f"   - Word Documents (.doc): {'✅' if doc_support['textract'] else '⚠️  (ต้องติดตั้ง textract)'}")
    print("-" * 70)
    print("🔧 API Endpoints:")
    print("   Analysis:")
    print("   - POST /api/analyze              - วิเคราะห์ข้อความและตรวจสอบคำซ้ำ")
    print("   - POST /api/upload               - อัปโหลดไฟล์ (txt/pdf/doc/docx)")
    print("   - POST /api/export               - ส่งออกผลลัพธ์")
    print("   - GET  /api/check-file-support   - ตรวจสอบการรองรับไฟล์")
    print("=" * 70)
    
    # แสดงคำเตือนถ้าไม่มี libraries สำหรับ PDF
    if not (support['pdfplumber'] or support['pypdf2']):
        print("⚠️  คำเตือน: ไม่พบ PDF libraries")
        print("   ติดตั้ง: pip install PyPDF2 pdfplumber")
    
    if not support['ocr']:
        print("ℹ️  ข้อมูล: OCR ไม่พร้อมใช้งาน (สำหรับ PDF ภาพ)")
        print("   ติดตั้ง: pip install pdf2image pytesseract")
        print("   และติดตั้ง Tesseract-OCR: https://github.com/tesseract-ocr/tesseract")
    
    # แสดงคำเตือนถ้าไม่มี libraries สำหรับ Word Documents
    if not doc_support['python-docx']:
        print("⚠️  คำเตือน: ไม่พบ python-docx library")
        print("   ติดตั้ง: pip install python-docx")
    
    print("=" * 70)
    
    port = int(os.environ.get("PORT", 5002))
    app.run(debug=True, host='0.0.0.0', port=port)
