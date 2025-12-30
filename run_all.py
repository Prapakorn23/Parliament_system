"""
Script สำหรับรันทั้ง 3 แอปพลิเคชันพร้อมกัน
Run all Parliament services: Main Dashboard, TranText, and Duplicate
"""

import subprocess
import sys
import os
import time
from pathlib import Path

# กำหนด root directory (directory ที่มี run_all.py - main_Parliament/)
ROOT_DIR = Path(__file__).parent.absolute()

def run_service(name, command, cwd, env=None, port=None):
    """รัน service ใน subprocess"""
    print(f"\n[กำลังเริ่ม] {name}...")
    print(f"  Command: {' '.join(command)}")
    print(f"  Directory: {cwd}")
    if port:
        print(f"  Port: {port}")
    
    # สร้าง environment variables
    process_env = os.environ.copy()
    if env:
        process_env.update(env)
    if port:
        process_env['PORT'] = str(port)
    
    try:
        # รัน subprocess (ไม่ใช้ PIPE เพื่อให้เห็น output ใน console)
        # หมายเหตุ: ถ้าต้องการแยก output ของแต่ละ process อาจใช้ threading
        process = subprocess.Popen(
            command,
            cwd=cwd,
            env=process_env,
            shell=True
        )
        print(f"✅ {name} เริ่มต้นเรียบร้อย (PID: {process.pid})")
        return process
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการเริ่ม {name}: {e}")
        return None

def check_port_available(port):
    """ตรวจสอบว่า port ใช้งานได้หรือไม่ (optional check)"""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('localhost', port))
            return result != 0  # ถ้า result != 0 แสดงว่า port ว่าง
    except:
        return True  # ถ้าเช็คไม่ได้ให้ assume ว่าว่าง

def main():
    """Main function"""
    print("=" * 70)
    print("🏛️  Parliament Dashboard - Starting All Services")
    print("=" * 70)
    print()
    print("กำลังเริ่มต้นทั้ง 3 แอปพลิเคชัน...")
    print()
    print("📍 URLs:")
    print("  - Main Dashboard: http://localhost:5003")
    print("  - Document System: http://localhost:5001")
    print("  - Trend Analysis: http://localhost:5002")
    print()
    print("=" * 70)
    print()
    
    processes = []
    
    # 1. รัน Document System (PDF2Text) - port 5001
    trantext_cwd = ROOT_DIR / "pdf2text_final"
    if trantext_cwd.exists():
        trantext_process = run_service(
            "Document Recommendation System (TranText)",
            [sys.executable, "app.py"],
            str(trantext_cwd),
            env={},
            port=5001
        )
        if trantext_process:
            processes.append(("TranText", trantext_process))
            time.sleep(2)  # รอสักครู่ให้แอปเริ่มต้น
    else:
        print(f"⚠️  ไม่พบโฟลเดอร์: {trantext_cwd}")
        print(f"   ข้าม TranText...")
    
    # 2. รัน Trend Analysis (Duplicate) - port 5002
    duplicate_cwd = ROOT_DIR / "duplicate-word-detector_final"
    if duplicate_cwd.exists():
        duplicate_process = run_service(
            "Trend Analysis (Duplicate)",
            [sys.executable, "app.py"],
            str(duplicate_cwd),
            env={},
            port=5002
        )
        if duplicate_process:
            processes.append(("Duplicate", duplicate_process))
            time.sleep(2)  # รอสักครู่ให้แอปเริ่มต้น
    else:
        print(f"⚠️  ไม่พบโฟลเดอร์: {duplicate_cwd}")
        print(f"   ข้าม Duplicate...")
    
    # 3. รัน Main Dashboard (port 5003)
    main_cwd = ROOT_DIR
    if main_cwd.exists():
        main_process = run_service(
            "Main Dashboard",
            [sys.executable, "app.py"],
            str(main_cwd),
            env={},
            port=5003
        )
        if main_process:
            processes.append(("Main Dashboard", main_process))
            time.sleep(2)  # รอสักครู่ให้แอปเริ่มต้น
    else:
        print(f"⚠️  ไม่พบโฟลเดอร์: {main_cwd}")
        print(f"   ไม่สามารถรัน Main Dashboard ได้")
        return
    
    # แสดงสถานะ
    print()
    print("=" * 70)
    print("✅ ทั้งหมดเริ่มต้นเรียบร้อยแล้ว!")
    print("=" * 70)
    print()
    print("📍 เปิดเบราว์เซอร์ไปที่: http://localhost:5003")
    print()
    print("⚠️  กด Ctrl+C เพื่อหยุดทุกบริการ")
    print()
    print("=" * 70)
    print()
    
    # รอจนกว่าจะถูก interrupt
    try:
        while True:
            # ตรวจสอบว่า process ยังทำงานอยู่หรือไม่
            active_processes = []
            for name, process in processes:
                return_code = process.poll()
                if return_code is None:
                    # ยังทำงานอยู่
                    active_processes.append((name, process))
                else:
                    print(f"⚠️  {name} หยุดทำงาน (Exit code: {return_code})")
            
            processes = active_processes
            
            # ถ้าไม่มี process ที่ทำงานอยู่แล้ว ให้หยุด
            if not processes:
                print("\n⚠️  ไม่มี service ที่ทำงานอยู่แล้ว")
                break
            
            time.sleep(5)  # รอ 5 วินาทีก่อนเช็คอีกครั้ง
            
    except KeyboardInterrupt:
        print()
        print("=" * 70)
        print("🛑 กำลังหยุดทุกบริการ...")
        print("=" * 70)
        print()
        
        # หยุดทุก process
        for name, process in processes:
            try:
                print(f"  กำลังหยุด {name}...", end=" ")
                process.terminate()
                print("✅")
            except Exception as e:
                print(f"❌ ไม่สามารถหยุด {name}: {e}")
        
        # รอให้ process ปิดตัว (graceful shutdown)
        print("\n  รอให้ services ปิดตัว...")
        time.sleep(3)
        
        # Force kill ถ้ายังทำงานอยู่
        for name, process in processes:
            if process.poll() is None:
                try:
                    print(f"  Force kill {name}...", end=" ")
                    process.kill()
                    print("✅")
                except Exception as e:
                    print(f"❌ {e}")
        
        print()
        print("=" * 70)
        print("✅ หยุดทุกบริการเรียบร้อยแล้ว")
        print("=" * 70)
        print()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

