import streamlit as st
import sqlite3
import socket
import requests
from datetime import datetime

st.set_page_config(page_title="Smart Hostel Bed-Check", page_icon="🛏️", layout="centered")

st.title("🛏️ Smart Hostel Bed-Check System")
st.markdown("---")

# Session state
if 'step' not in st.session_state:
    st.session_state.step = 'matric'
if 'student_data' not in st.session_state:
    st.session_state.student_data = None

def get_local_ip():
    # Try to get from Streamlit headers (works if behind a proxy or on Streamlit Cloud)
    try:
        if hasattr(st, 'context') and hasattr(st.context, 'headers'):
            headers = st.context.headers
            if 'X-Forwarded-For' in headers:
                return headers['X-Forwarded-For'].split(',')[0]
            if 'X-Real-IP' in headers:
                return headers['X-Real-IP']
    except:
        pass

    # Fallback to socket for local machine IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


def get_student_by_matric(matric_number):
    conn = sqlite3.connect('hostel.db')
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

def has_checked_in_today(matric_number):
    conn = sqlite3.connect('hostel.db')
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
    """Check if current IP starts with expected subnet"""
    if expected_subnet is None:
        return False, "❌ Subnet error: No subnet defined for this hostel in the database."
    if current_ip.startswith(expected_subnet):
        return True, f"✅ IP verified: {current_ip} is in {expected_subnet}x subnet"
    else:
        return False, f"❌ IP check failed: {current_ip} is NOT in {expected_subnet}x subnet"

# ============================================
# STEP 1: Matric Number
# ============================================
if st.session_state.step == 'matric':
    st.subheader("Step 1: Enter Matric Number")
    
    matric_number = st.text_input("Matric Number", placeholder="e.g., BUI/001")
    
    if st.button("Verify Identity"):
        if not matric_number:
            st.error("Please enter matric number.")
        else:
            student = get_student_by_matric(matric_number.upper())
            
            if student is None:
                st.error("❌ Matric number not found.")
            elif has_checked_in_today(matric_number.upper()):
                st.warning("⚠️ Already checked in today.")
            else:
                st.success(f"✅ Welcome, {student['name']}!")
                st.session_state.student_data = student
                st.session_state.step = 'location'
                st.rerun()

# ============================================
# STEP 2: Subnet IP Check (Gate A)
# ============================================
elif st.session_state.step == 'location':
    st.subheader("Step 2: Network Verification (Gate A)")
    
    student = st.session_state.student_data
    
    st.write(f"**Student:** {student['name']}")
    st.write(f"**Hostel:** {student['hostel']}")
    st.write(f"**Room:** {student['room_number']}")
    st.write(f"**Expected Subnet:** `{student['subnet']}x`")
    
    st.markdown("---")
    
    # Get current computer IP
    current_ip = get_local_ip()
    st.write(f"**Your Current IP Address:** `{current_ip}`")
    
    # Check if IP matches
    passed, message = check_subnet_ip(student['subnet'], current_ip)
    
    if passed:
        st.success(message)
        st.markdown("---")
        st.write("✅ **Gate A passed!** You are on the correct network.")
        
        if st.button("Continue to Next Step"):
            st.session_state.step = 'gps'
            st.rerun()
    else:
        st.error(message)
        st.markdown("---")
        st.warning("""
        **To pass this check:**
        - Connect to the Wi-Fi network that matches your hostel
        - For Mark Hostel, your IP should start with `{expected_subnet}`
        """)
        
        if st.button("Try Again (Switch Network)"):
            st.rerun()
        if st.button("Back to Start"):
            st.session_state.step = 'matric'
            st.session_state.student_data = None
            st.rerun()
    