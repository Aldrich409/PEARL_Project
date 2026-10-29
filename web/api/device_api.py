import requests

API_BASE_URL = "http://127.0.0.1:8000"

def fetch_devices(user_id, role):
    try:
        res = requests.get(f"{API_BASE_URL}/api/devices?user_id={user_id}&role={role}")
        return res.json() if res.status_code == 200 else []
    except:
        return []

def update_device_settings(payload):
    try:
        res = requests.put(f"{API_BASE_URL}/api/devices/update", json=payload)
        return res.status_code == 200
    except:
        return False

def fetch_fish_profiles():
    # Returns built-in Nile Tilapia aquaculture parameters for settings presets
    return [
        {"fish_type": "Nile Tilapia (Standard)", "temp_min": 26.0, "temp_max": 30.0, "ph_min": 6.5, "ph_max": 8.5, "turb_max": 80.0},
        {"fish_type": "Nile Tilapia (Fingerlings)", "temp_min": 28.0, "temp_max": 32.0, "ph_min": 7.0, "ph_max": 8.0, "turb_max": 50.0}
    ]

def fetch_fish_suggestion(fish_name):
    # Simulates fetching an AI suggestion or matching a library preset
    fish_name_lower = fish_name.lower()
    
    if 'tilapia' in fish_name_lower:
        return {
            'fish_name': fish_name,
            'temp_norm_min': 26.0, 'temp_norm_max': 33.0, 'temp_danger_min': 24.0, 'temp_danger_max': 35.0,
            'ph_norm_min': 7.0, 'ph_norm_max': 8.5, 'ph_danger_min': 6.5, 'ph_danger_max': 9.0,
            'turb_norm_max': 80.0, 'turb_danger_max': 100.0,
            'suggestion_text': f'📘 BFAR/FAO Guide ({fish_name}): Optimal spawning and growth at 26–33°C, pH 7.0–8.5, and turbidity ≤80 NTU.'
        }
    elif 'bangus' in fish_name_lower or 'milkfish' in fish_name_lower:
        return {
            'fish_name': fish_name,
            'temp_norm_min': 25.0, 'temp_norm_max': 32.0, 'temp_danger_min': 22.0, 'temp_danger_max': 35.0,
            'ph_norm_min': 7.0, 'ph_norm_max': 8.5, 'ph_danger_min': 6.5, 'ph_danger_max': 9.0,
            'turb_norm_max': 85.0, 'turb_danger_max': 110.0,
            'suggestion_text': f'📘 BFAR/SEAFDEC Guide ({fish_name}): Thrives at 25–32°C and pH 7.0–8.5. Highly sensitive to DO drops when turbidity >110 NTU.'
        }
    elif 'catfish' in fish_name_lower or 'hito' in fish_name_lower:
        return {
            'fish_name': fish_name,
            'temp_norm_min': 26.0, 'temp_norm_max': 32.0, 'temp_danger_min': 22.0, 'temp_danger_max': 36.0,
            'ph_norm_min': 6.5, 'ph_norm_max': 8.0, 'ph_danger_min': 5.5, 'ph_danger_max': 9.0,
            'turb_norm_max': 100.0, 'turb_danger_max': 140.0,
            'suggestion_text': f'📘 BFAR Guide ({fish_name}): Tolerates murky water up to 100 NTU and pH 6.5–8.0. Extreme pH harms scaleless skin.'
        }
    elif 'carp' in fish_name_lower or 'karpa' in fish_name_lower:
        return {
            'fish_name': fish_name,
            'temp_norm_min': 24.0, 'temp_norm_max': 30.0, 'temp_danger_min': 20.0, 'temp_danger_max': 34.0,
            'ph_norm_min': 7.0, 'ph_norm_max': 8.5, 'ph_danger_min': 6.0, 'ph_danger_max': 9.0,
            'turb_norm_max': 90.0, 'turb_danger_max': 120.0,
            'suggestion_text': f'📘 FAO Guide ({fish_name}): Prefers 24–30°C and pH 7.0–8.5. Bottom feeding naturally stirs sediment.'
        }
    elif 'prawn' in fish_name_lower or 'ulang' in fish_name_lower:
        return {
            'fish_name': fish_name,
            'temp_norm_min': 28.0, 'temp_norm_max': 31.0, 'temp_danger_min': 24.0, 'temp_danger_max': 34.0,
            'ph_norm_min': 7.0, 'ph_norm_max': 8.5, 'ph_danger_min': 6.5, 'ph_danger_max': 9.0,
            'turb_norm_max': 60.0, 'turb_danger_max': 85.0,
            'suggestion_text': f'📘 BFAR Guide ({fish_name}): Needs clear water (≤60 NTU) and pH 7.0–8.5 for healthy shell molting.'
        }
    
    return {
        'fish_name': fish_name,
        'temp_norm_min': 26.0, 'temp_norm_max': 32.0, 'temp_danger_min': 23.0, 'temp_danger_max': 35.0,
        'ph_norm_min': 6.8, 'ph_norm_max': 8.5, 'ph_danger_min': 6.0, 'ph_danger_max': 9.0,
        'turb_norm_max': 80.0, 'turb_danger_max': 110.0,
        'suggestion_text': f'🤖 AI Guide ({fish_name}): Recommended tropical freshwater range is 26–32°C, pH 6.8–8.5, and turbidity ≤80 NTU.'
    }

def save_fish_profile(payload):
    try:
        res = requests.post(f"{API_BASE_URL}/api/fish-profiles", json=payload)
        return res.status_code == 200
    except:
        return False