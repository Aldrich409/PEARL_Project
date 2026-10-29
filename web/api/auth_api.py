import requests

API_BASE_URL = "http://127.0.0.1:8000"

def authenticate_user(username, password):
    try:
        res = requests.post(f"{API_BASE_URL}/api/login", json={"username": username, "password": password})
        return res.json() if res.status_code == 200 else None
    except:
        return None

def fetch_all_accounts():
    try:
        res = requests.get(f"{API_BASE_URL}/api/admin/accounts")
        return res.json() if res.status_code == 200 else []
    except:
        return []

def admin_create_account(payload):
    try:
        res = requests.post(f"{API_BASE_URL}/api/admin/accounts/create", json=payload)
        return res.status_code == 200
    except:
        return False

def admin_delete_account(user_id):
    try:
        res = requests.delete(f"{API_BASE_URL}/api/admin/accounts/{user_id}")
        return res.status_code == 200
    except:
        return False