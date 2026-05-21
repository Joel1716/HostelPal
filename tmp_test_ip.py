import requests

def get_public_ip_mock(headers=None):
    """Mock version of the app.py function for testing"""
    try:
        if headers:
            ip_headers = [
                'X-Forwarded-For', 
                'x-forwarded-for',
                'X-Real-IP', 
                'x-real-ip',
                'Cf-Connecting-Ip',
                'cf-connecting-ip'
            ]
            
            for header in ip_headers:
                if header in headers:
                    ip = headers[header].split(',')[0].strip()
                    if ip and ip != '127.0.0.1' and ip != '::1':
                        return ip
    except Exception:
        pass

    try:
        response = requests.get('https://api.ipify.org', timeout=5)
        if response.status_code == 200:
            ip = response.text.strip()
            if ip:
                return ip
    except Exception:
        pass

    return '127.0.0.1'

print("Testing with Streamlit Cloud header:")
print(f"Result: {get_public_ip_mock({'X-Forwarded-For': '1.2.3.4, 5.6.7.8'})}")

print("\nTesting with fallback (IPify):")
print(f"Result: {get_public_ip_mock({})}")
