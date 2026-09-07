import requests

API_BASE_URL = "http://127.0.0.1:8000"
DEFAULT_DEVICE = "PEARL-ESP32-001"

def authenticate_user(username, password):
    try:
        res = requests.post(f"{API_BASE_URL}/api/login", json={"username": username, "password": password})
        return res.json() if res.status_code == 200 else None
    except: return None

def fetch_latest_data(device_sn):
    try:
        res = requests.get(f"{API_BASE_URL}/api/telemetry/latest?device_sn={device_sn}")
        return res.json() if res.status_code == 200 else None
    except: return None

def fetch_history_data(device_sn, limit=20):
    try:
        res = requests.get(f"{API_BASE_URL}/api/telemetry/history?device_sn={device_sn}&limit={limit}")
        return res.json() if res.status_code == 200 else []
    except: return []

def fetch_ai_forecast(device_sn, days=3):
    try:
        res = requests.get(f"{API_BASE_URL}/api/forecast/breeding?device_sn={device_sn}&days_ahead={days}")
        return res.json().get("forecast", []) if res.status_code == 200 else []
    except: return []

def fetch_devices(user_id, role):
    try:
        res = requests.get(f"{API_BASE_URL}/api/devices?user_id={user_id}&role={role}")
        return res.json() if res.status_code == 200 else []
    except: return []
def update_device_settings(settings_data):
    try:
        res = requests.put(f"{API_BASE_URL}/api/devices/update", json=settings_data)
        return res.status_code == 200
    except: 
        return False   
def create_new_user(username, password, role):
    try:
        res = requests.post(f"{API_BASE_URL}/api/users/create", json={"username": username, "password": password, "role": role})
        return res.status_code == 200
    except:
        return False

def fetch_all_accounts():
    try:
        res = requests.get(f"{API_BASE_URL}/api/admin/accounts")
        return res.json() if res.status_code == 200 else []
    except: return []

def admin_create_account(payload):
    try:
        res = requests.post(f"{API_BASE_URL}/api/admin/accounts/create", json=payload)
        return res.status_code == 200
    except: return False

def admin_delete_account(user_id):
    try:
        res = requests.delete(f"{API_BASE_URL}/api/admin/accounts/{user_id}")
        return res.status_code == 200
    except: return False
def fetch_all_accounts():
    try:
        res = requests.get(f"{API_BASE_URL}/api/admin/accounts")
        return res.json() if res.status_code == 200 else []
    except: return []

def admin_create_account(payload):
    try:
        res = requests.post(f"{API_BASE_URL}/api/admin/accounts/create", json=payload)
        return res.status_code == 200
    except: return False

def admin_delete_account(user_id):
    try:
        res = requests.delete(f"{API_BASE_URL}/api/admin/accounts/{user_id}")
        return res.status_code == 200
    except: return False

def update_device_settings(payload):
    try:
        res = requests.put(f"{API_BASE_URL}/api/devices/update", json=payload)
        return res.status_code == 200
    except: return False