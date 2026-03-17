"""
Flask Application สำหรับ Main Dashboard
Main Parliament Dashboard - Landing Page
พร้อม API + WebSocket (Flask-SocketIO) สำหรับข้อมูลผู้เข้าประชุม
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from datetime import datetime, date
import os
import pymysql

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'parliament-secret-key')

socketio = SocketIO(app, cors_allowed_origins="*")

# ============================================
# Database Configuration
# ============================================
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', 'meeting_attendance'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
}


def get_db():
    return pymysql.connect(**DB_CONFIG)


def serialize_row(row):
    """แปลง date/datetime ใน dict ให้เป็น string สำหรับ JSON"""
    if not row:
        return row
    out = {}
    for k, v in row.items():
        if isinstance(v, (datetime, date)):
            out[k] = v.isoformat()
        else:
            out[k] = v
    return out


def _fetch_all_attendees():
    """ดึงข้อมูลผู้เข้าประชุมทั้งหมด (ใช้ร่วมกันระหว่าง API และ WebSocket)"""
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT user_id, person_code, name, department,
                       position, person_type, gender, entry_status, status
                FROM attendance
                ORDER BY user_id ASC
            """)
            participants = [serialize_row(r) for r in cursor.fetchall()]

        present_count = sum(1 for p in participants if p['status'] == 'เข้า')
        absent_count = len(participants) - present_count

        return {
            'success': True,
            'participants': participants,
            'summary': {
                'total': len(participants),
                'present': present_count,
                'absent': absent_count,
            },
            'timestamp': datetime.now().isoformat(),
        }
    finally:
        conn.close()


# ============================================
# Page Routes
# ============================================
@app.route('/')
def index():
    """หน้า Dashboard หลัก"""
    return render_template('index.html')


# ============================================
# API Routes - Attendance
# ============================================
@app.route('/api/attendees')
def get_attendees():
    """ดึงรายชื่อผู้เข้าประชุมทั้งหมดพร้อมสถานะ"""
    try:
        return jsonify(_fetch_all_attendees())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/attendees/<int:user_id>')
def get_attendee(user_id):
    """ดึงข้อมูลผู้เข้าประชุมรายบุคคล (ครบทุกฟิลด์)"""
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM attendance WHERE user_id = %s", (user_id,))
            participant = cursor.fetchone()

        if not participant:
            return jsonify({'success': False, 'error': 'ไม่พบข้อมูล'}), 404

        return jsonify({'success': True, 'participant': serialize_row(participant)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/api/attendees/<int:user_id>/status', methods=['PUT'])
def update_attendee_status(user_id):
    """อัพเดทสถานะ เข้า/ออก ของผู้เข้าประชุม แล้ว broadcast ผ่าน WebSocket"""
    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({'success': False, 'error': 'กรุณาระบุ status'}), 400

    new_status = data['status']
    if new_status not in ('เข้า', 'ออก'):
        return jsonify({'success': False, 'error': 'status ต้องเป็น "เข้า" หรือ "ออก"'}), 400

    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE attendance SET status = %s WHERE user_id = %s",
                (new_status, user_id)
            )
            if cursor.rowcount == 0:
                return jsonify({'success': False, 'error': 'ไม่พบข้อมูล'}), 404
        conn.commit()

        # Broadcast ข้อมูลใหม่ไปยังทุก client ที่เชื่อมต่ออยู่
        updated_data = _fetch_all_attendees()
        socketio.emit('attendance_updated', updated_data)

        return jsonify({
            'success': True,
            'message': f'อัพเดทสถานะเป็น "{new_status}" เรียบร้อย',
            'user_id': user_id,
            'new_status': new_status,
        })
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()


# ============================================
# WebSocket Events
# ============================================
@socketio.on('connect')
def handle_connect():
    """เมื่อ client เชื่อมต่อ ส่งข้อมูลล่าสุดให้ทันที"""
    try:
        data = _fetch_all_attendees()
        emit('attendance_updated', data)
    except Exception as e:
        emit('error', {'message': str(e)})


@socketio.on('request_refresh')
def handle_refresh():
    """client ขอ refresh ข้อมูลด้วยตัวเอง"""
    try:
        data = _fetch_all_attendees()
        emit('attendance_updated', data)
    except Exception as e:
        emit('error', {'message': str(e)})


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5003))
    socketio.run(app, debug=True, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
