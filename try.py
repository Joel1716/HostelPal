# Create this file as get_my_public_ip.py
import requests

def get_router_ip():
    try:
        response = requests.get('https://api.ipify.org')
        print(f"\nYour Hostel Router's Public IP is: {response.text}")
        print("Copy this number and put it in your subnet.py file.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_router_ip()
