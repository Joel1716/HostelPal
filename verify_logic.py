import sqlite3
from datetime import datetime
import os

# Import functions from app.py
# Note: Since app.py has streamlit calls at top level, we might need to mock streamlit
# or just copy the functions here for pure logic testing.
# For simplicity, I'll copy the logic here to verify it works as intended.

def get_student_by_matric(matric_number, db_path='hostel.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
    SELECT matric_number, name, hostel, room_number, enrolled, subnet
    FROM students WHERE matric_number = ?
    ''', (matric_number,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'matric_number': result[0],
            'name': result[1],
            'hostel': result[2],
            'room_number': result[3],
            'enrolled': result[4],
            'subnet': result[5]
        }
    return None

def has_checked_in_today(matric_number, db_path='hostel.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    today_date = datetime.now().strftime("%Y-%m-%d")
    cursor.execute('''
    SELECT id FROM attendance_log 
    WHERE matric_number = ? AND timestamp LIKE ?
    ''', (matric_number, f"{today_date}%"))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def check_subnet_ip(expected_subnet, current_ip):
    if current_ip.startswith(expected_subnet):
        return True, f"✅ IP verified: {current_ip} is in {expected_subnet}x subnet"
    else:
        return False, f"❌ IP check failed: {current_ip} is NOT in {expected_subnet}x subnet"

def test_logic():
    print("Starting verification...")
    
    # 1. Test student existence
    print("Testing student lookup...")
    student = get_student_by_matric('BUI/001')
    if student:
        print(f"Found student: {student['name']} in {student['hostel']}")
        assert student['name'] == 'John Doe'
    else:
        print("Student BUI/001 not found. Make sure to run insert_students.py first.")
        return

    # 2. Test check-in status
    print("Testing check-in status...")
    checked_in = has_checked_in_today('BUI/001')
    print(f"Already checked in today? {checked_in}")
    # Default should be False if we just reset the DB

    # 3. Test IP validation
    print("Testing IP validation...")
    # John Doe is in Mark Hostel -> subnet 192.168.110.
    passed, msg = check_subnet_ip(student['subnet'], '192.168.110.45')
    print(f"Test case 1 (Match): {passed}, {msg}")
    assert passed == True

    passed, msg = check_subnet_ip(student['subnet'], '172.20.10.5')
    print(f"Test case 2 (Mismatch): {passed}, {msg}")
    assert passed == False

    print("Logic verification PASSED!")

if __name__ == "__main__":
    test_logic()
