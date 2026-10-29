import requests

API_BASE_URL = "http://127.0.0.1:8000"

def fetch_latest_data(device_sn):
    try:
        res = requests.get(f"{API_BASE_URL}/api/telemetry/latest?device_sn={device_sn}")
        return res.json() if res.status_code == 200 else None
    except:
        return None

def fetch_history_data(device_sn, limit=30):
    try:
        res = requests.get(f"{API_BASE_URL}/api/telemetry/history?device_sn={device_sn}&limit={limit}")
        return res.json() if res.status_code == 200 else []
    except:
        return []

def fetch_bio_audit(device_sn):
    try:
        res = requests.get(f"{API_BASE_URL}/api/telemetry/bio-audit?device_sn={device_sn}")
        return res.json() if res.status_code == 200 else None
    except:
        return None

def post_farmer_intervention(payload):
    try:
        res = requests.post(f"{API_BASE_URL}/api/interventions", json=payload)
        return res.status_code == 200
    except:
        return False

def fetch_farmer_interventions(device_sn, limit=20):
    try:
        res = requests.get(f"{API_BASE_URL}/api/interventions?device_sn={device_sn}&limit={limit}")
        return res.json() if res.status_code == 200 else []
    except:
        return []

def fetch_iso25010_performance(limit=200):
    try:
        res = requests.get(f"{API_BASE_URL}/api/admin/performance?limit={limit}")
        return res.json() if res.status_code == 200 else []
    except:
        return []