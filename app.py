"""
Flask Application สำหรับ Main Dashboard
Main Parliament Dashboard - Landing Page
"""

from flask import Flask, render_template
import os

app = Flask(__name__, static_folder="static", template_folder="templates")

@app.route('/')
def index():
    """หน้า Dashboard หลัก"""
    return render_template('index.html')

if __name__ == '__main__':
    # รันบน port 5003 (หรือปรับตามต้องการ)
    # หมายเหตุ: ให้ตรวจสอบว่า port นี้ไม่ชนกับแอปอื่น
    # - TranText: port 5001 (แนะนำ)
    # - Duplicate: port 5002 (แนะนำ)
    # - Main Dashboard: port 5003
    port = int(os.environ.get("PORT", 5003))
    app.run(debug=True, host='0.0.0.0', port=port)

