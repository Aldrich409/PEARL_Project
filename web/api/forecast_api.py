import requests

API_BASE_URL = "http://127.0.0.1:8000"

def fetch_ai_forecast(device_sn, days=7):
    try:
        res = requests.get(f"{API_BASE_URL}/api/forecast/breeding?device_sn={device_sn}&days_ahead={days}")
        return res.json().get("forecast", []) if res.status_code == 200 else []
    except:
        return []