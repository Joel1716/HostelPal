import sqlite3
import os
from datetime import datetime

# Consolidated verification script for Bed-Check
DB_PATH = 'verify_hostel.db'

def setup_test_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Create tables
    cursor.execute('CREATE TABLE students (matric_number TEXT PRIMARY KEY, name TEXT, hostel TEXT, room_number TEXT, enrolled INTEGER, subnet TEXT)')
    cursor.execute('CREATE TABLE attendance_log (id INTEGER PRIMARY KEY AUTOINCREMENT, matric_number TEXT, name TEXT, hostel TEXT, room_number TEXT, timestamp TEXT)')
    
    # 2. Insert test data
    students = [
        ('BUI/001', 'John Doe', 'Mark Hostel', '101', 0, '192.168.110.'),
        ('BUI/002', 'Jane Smith', 'Luke Hostel', '201', 0, '172.20.10.')
    ]
    cursor.executemany('INSERT INTO students VALUES (?, ?, ?, ?, ?, ?)', students)
    
    conn.commit()
    conn.close()
    print("Test database setup complete.")

def get_student_by_matric(matric_number):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT matric_number, name, hostel, room_number, enrolled, subnet FROM students WHERE matric_number = ?', (matric_number,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {'matric_number': result[0], 'name': result[1], 'hostel': result[2], 'room_number': result[3], 'enrolled': result[4], 'subnet': result[5]}
    return None

def has_checked_in_today(matric_number):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    today_date = datetime.now().strftime("%Y-%m-%d")
    cursor.execute('SELECT id FROM attendance_log WHERE matric_number = ? AND timestamp LIKE ?', (matric_number, f"{today_date}%"))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def check_subnet_ip(expected_subnet, current_ip):
    return current_ip.startswith(expected_subnet)

def run_tests():
    setup_test_db()
    
    print("\n--- Running Logic Tests ---")
    
    # Test 1: Student not in database
    print("Test 1: Check non-existent student (BUI/999)...")
    assert get_student_by_matric('BUI/999') is None
    print("✅ Pass: Non-existent student handled.")
    
    # Test 2: Student in database
    print("Test 2: Check existent student (BUI/001)...")
    student = get_student_by_matric('BUI/001')
    assert student is not None
    assert student['name'] == 'John Doe'
    print(f"✅ Pass: Found student {student['name']}.")
    
    # Test 3: Check-in check (None)
    print("Test 3: Check if already checked in (False expected)...")
    assert not has_checked_in_today('BUI/001')
    print("✅ Pass: Correctly identifies no previous check-in.")
    
    # Test 4: IP validation (Match)
    print(f"Test 4: IP check for {student['name']} (Expected Subnet: {student['subnet']})...")
    test_ip_match = '192.168.110.15'
    assert check_subnet_ip(student['subnet'], test_ip_match)
    print(f"✅ Pass: IP {test_ip_match} correctly matches subnet {student['subnet']}.")
    
    # Test 5: IP validation (Mismatch)
    print(f"Test 5: IP check for {student['name']} with wrong IP...")
    test_ip_wrong = '10.0.0.1'
    assert not check_subnet_ip(student['subnet'], test_ip_wrong)
    print(f"✅ Pass: IP {test_ip_wrong} correctly fails subnet {student['subnet']}.")
    
    print("\nALL SYSTEM LOGIC VERIFIED!")

if __name__ == "__main__":
    run_tests()
