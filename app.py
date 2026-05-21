import streamlit as st
import sqlite3
import requests
from datetime import datetime

st.set_page_config(page_title="Smart Hostel Bed-Check", page_icon="🛏️", layout="centered")
st.title("HostelPal")
st.markdown("---")

# Session state
if 'step' not in st.session_state:
    st.session_state.step = 'matric'
if 'student_data' not in st.session_state:
    st.session_state.student_data = None


def get_public_ip():
    """
    Get the student's REAL public IP address from the browser client.
    Works on both local environments and deployed Streamlit Cloud.
    """
    # Method 1: Check Streamlit context headers for the proxy client IP
    try:
        if hasattr(st, 'context') and hasattr(st.context, 'headers'):
            headers = st.context.headers
            
            # Streamlit Cloud explicitly forwards the client IP through this header
            if 'X-Forwarded-For' in headers:
                # Can contain a comma-separated list of proxies; the first one is the student
                ip = headers['X-Forwarded-For'].split(',')[0].strip()
                if ip and ip != '127.0.0.1':
                    return ip
                    
            # Fallback headers commonly passed by various reverse proxies
            for header_name in ['X-Real-IP', 'X-Client-IP', 'Cf-Connecting-Ip']:
                if header_name in headers:
                    ip = headers[header_name].strip()
                    if ip and ip != '127.0.0.1':
                        return ip
    except Exception as e:
        # Silently catch context errors (useful if testing on an older Streamlit version)
        pass

    # Method 2: If we are running locally (localhost), your server and client are on the 
    # same machine, so requests.get works perfectly to find your local router's public IP.
    try:
        response = requests.get('https://api.ipify.org', timeout=3)
        if response.status_code == 200:
            ip = response.text.strip()
            if ip:
                return ip
    except:
        pass

    # Fallback default if completely offline/isolated
    return '127.0.0.1'

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
# STEP 2: Public IP Check (Gate A) with Loader
# ============================================
elif st.session_state.step == 'location':
    st.subheader("Step 2: Network Verification (Gate A)")
    
    student = st.session_state.student_data
    
    st.write(f"**Student:** {student['name']}")
    st.write(f"**Hostel:** {student['hostel']}")
    st.write(f"**Room:** {student['room_number']}")
    st.write(f"**Expected Subnet:** `{student['subnet']}x`")
    
    st.markdown("---")
    
    # Only run IP check if not already done
    if 'ip_checked' not in st.session_state:
        st.session_state.ip_checked = False
        st.session_state.ip_passed = False
        st.session_state.ip_message = ""
        st.session_state.current_ip = ""
    
    if not st.session_state.ip_checked:
        # Show loader while checking IP
        with st.spinner("Checking your network connection... Please wait."):
            current_ip = get_public_ip()
            passed, message = check_subnet_ip(student['subnet'], current_ip)
            
            st.session_state.current_ip = current_ip
            st.session_state.ip_passed = passed
            st.session_state.ip_message = message
            st.session_state.ip_checked = True
        
        st.rerun()
    
    # Show results (from saved session state)
    st.write(f"**Your Public IP Address:** `{st.session_state.current_ip}`")
    
    if st.session_state.ip_passed:
        st.success(st.session_state.ip_message)
        st.markdown("---")
        st.write("✅ **Gate A passed!** You are on the correct network.")
        
        if st.button("Continue to Next Step"):
            st.session_state.step = 'face'
            st.rerun()
    else:
        st.error(st.session_state.ip_message)
        if st.button("Try Again"):
            # Reset IP check so it runs again
            st.session_state.ip_checked = False
            st.rerun()
        if st.button("Back to Start"):
            st.session_state.step = 'matric'
            st.session_state.student_data = None
            # Clear IP check session data
            for key in ['ip_checked', 'ip_passed', 'ip_message', 'current_ip']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        

# ============================================
# STEP 3: Face Recognition (Coming)
# ============================================
elif st.session_state.step == 'face':
    st.subheader("Step 3: Face Verification")
    st.write("Face recognition with VGG-Face and EAR liveness will be added here.")
    st.write(f"**Student:** {st.session_state.student_data['name']}")
    
    if st.button("Back to Network Check"):
        st.session_state.step = 'location'
        st.rerun()

