import sqlite3
import datetime
import math
import random
import os
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))

ROOT_DB_PATH = os.path.join(BASE_DIR, "pearl_data.db")
BACKEND_DB_PATH = os.path.join(BACKEND_DIR, "pearl_data.db")

DEFAULT_FISH_PROFILES = {
    "Tilapia": {
        "t_n_min": 26.0, "t_n_max": 33.0, "t_d_min": 24.0, "t_d_max": 35.0,
        "p_n_min": 7.0,  "p_n_max": 8.5,  "p_d_min": 6.5,  "p_d_max": 9.0,
        "tb_n_max": 80.0, "tb_d_max": 100.0,
        "suggestion": (
            "📘 BFAR / FAO Guide (Tilapia): Optimal growth and spawning occur at 26–33°C and pH 7.0–8.5. "
            "Water below 24°C halts feeding, while >35°C depletes dissolved oxygen rapidly. "
            "Keep turbidity ≤80 NTU; >100 NTU signals dense algal blooms or gill-clogging silt.\n"
            "🇵🇭 Gabay: Pinakamaganda ang paglaki at pangingitlog sa 26–33°C at pH 7.0–8.5. "
            "Kapag lumampas sa 100 NTU ang labo, senyales ito ng sobrang lumot na nakakaubos ng oxygen."
        )
    },
    "Bangus (Milkfish)": {
        "t_n_min": 25.0, "t_n_max": 32.0, "t_d_min": 22.0, "t_d_max": 35.0,
        "p_n_min": 7.0,  "p_n_max": 8.5,  "p_d_min": 6.5,  "p_d_max": 9.0,
        "tb_n_max": 85.0, "tb_d_max": 110.0,
        "suggestion": (
            "📘 BFAR / SEAFDEC Guide (Bangus): Milkfish thrive in 25–32°C and slightly alkaline water (pH 7.0–8.5). "
            "They are highly sensitive to sudden dissolved oxygen drops when temp exceeds 32°C or turbidity spikes above 110 NTU. "
            "Acidic water (<6.5 pH) causes gill acidosis and slow growth.\n"
            "🇵🇭 Gabay: Sensitibo ang Bangus sa biglaang pagbaba ng oxygen kapag mainit (>32°C) o malabo ang tubig (>110 NTU). "
            "Panatilihin ang pH sa 7.0–8.5."
        )
    },
    "Catfish (Hito)": {
        "t_n_min": 26.0, "t_n_max": 32.0, "t_d_min": 22.0, "t_d_max": 36.0,
        "p_n_min": 6.5,  "p_n_max": 8.0,  "p_d_min": 5.5,  "p_d_max": 9.0,
        "tb_n_max": 100.0, "tb_d_max": 140.0,
        "suggestion": (
            "📘 BFAR / FAO Guide (Catfish / Hito): Air-breathing labyrinth organs make Hito more tolerant of murky water (Normal up to 100 NTU, Danger >140 NTU) "
            "and slightly acidic pH (6.5–8.0). However, extreme pH (<5.5 or >9.0) or temp >36°C burns their scaleless skin and triggers bacterial ulcers.\n"
            "🇵🇭 Gabay: Mas matibay ang Hito sa malabong tubig (hanggang 100 NTU), ngunit delikado sa balat nila kapag bumaba sa 5.5 o lumampas sa 9.0 ang pH."
        )
    },
    "Carp (Karpa)": {
        "t_n_min": 24.0, "t_n_max": 30.0, "t_d_min": 20.0, "t_d_max": 34.0,
        "p_n_min": 7.0,  "p_n_max": 8.5,  "p_d_min": 6.0,  "p_d_max": 9.0,
        "tb_n_max": 90.0, "tb_d_max": 120.0,
        "suggestion": (
            "📘 FAO Guide (Common Carp / Karpa): Prefers slightly cooler tropical waters (24–30°C) and pH 7.0–8.5. "
            "Bottom-feeding habits naturally stir up sediment (Normal ≤90 NTU), but >120 NTU indicates excessive organic waste.\n"
            "🇵🇭 Gabay: Natural na nagpapalabo ng tubig ang Karpa dahil sa paghuhukay sa ilalim, ngunit huwag hayaang lumampas sa 120 NTU."
        )
    },
    "Freshwater Prawn (Ulang)": {
        "t_n_min": 28.0, "t_n_max": 31.0, "t_d_min": 24.0, "t_d_max": 34.0,
        "p_n_min": 7.0,  "p_n_max": 8.5,  "p_d_min": 6.5,  "p_d_max": 9.0,
        "tb_n_max": 60.0, "tb_d_max": 85.0,
        "suggestion": (
            "📘 BFAR Guide (Giant Freshwater Prawn / Ulang): Requires clean, well-oxygenated water (≤60 NTU) and pH 7.0–8.5 for proper shell molting. "
            "High turbidity (>85 NTU) or extreme pH causes molting failure and high mortality.\n"
            "🇵🇭 Gabay: Kailangan ng malinis na tubig (≤60 NTU) at tamang pH (7.0–8.5) para sa maayos na pagpapalit ng balat (molting) ng Ulang."
        )
    }
}

def reset_and_seed_database():
    conn = sqlite3.connect(ROOT_DB_PATH)
    cursor = conn.cursor()

    print("1. Clearing old database tables...")
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS devices")
    cursor.execute("DROP TABLE IF EXISTS telemetry")
    cursor.execute("DROP TABLE IF EXISTS fish_profiles")

    print("2. Rebuilding tables with Fish Species Library & Threshold columns...")
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE fish_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fish_name TEXT UNIQUE,
            temp_norm_min REAL,
            temp_norm_max REAL,
            temp_danger_min REAL,
            temp_danger_max REAL,
            ph_norm_min REAL,
            ph_norm_max REAL,
            ph_danger_min REAL,
            ph_danger_max REAL,
            turb_norm_max REAL,
            turb_danger_max REAL,
            suggestion_text TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE devices (
            device_sn TEXT PRIMARY KEY,
            owner_id INTEGER,
            pond_name TEXT,
            location TEXT DEFAULT 'Angono, Rizal',
            length REAL DEFAULT 25.0,
            width REAL DEFAULT 20.0,
            depth REAL DEFAULT 1.0,
            alert_phone TEXT DEFAULT '',
            alert_level TEXT DEFAULT 'Critical',
            sleep_interval INTEGER DEFAULT 30,
            ph_offset REAL DEFAULT 0.0,
            turb_offset REAL DEFAULT 0.0,
            fish_count INTEGER DEFAULT 0,
            fish_type TEXT DEFAULT 'Tilapia',
            temp_norm_min REAL DEFAULT 26.0,
            temp_norm_max REAL DEFAULT 33.0,
            temp_danger_min REAL DEFAULT 24.0,
            temp_danger_max REAL DEFAULT 35.0,
            ph_norm_min REAL DEFAULT 7.0,
            ph_norm_max REAL DEFAULT 8.5,
            ph_danger_min REAL DEFAULT 6.5,
            ph_danger_max REAL DEFAULT 9.0,
            turb_norm_max REAL DEFAULT 80.0,
            turb_danger_max REAL DEFAULT 100.0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_sn TEXT,
            ph REAL,
            temperature REAL,
            turbidity REAL,
            water_level_cm REAL DEFAULT 15.0,
            timestamp DATETIME
        )
    ''')

    print("3. Seeding Default Fish Species Library...")
    for fish_name, p in DEFAULT_FISH_PROFILES.items():
        cursor.execute('''
            INSERT INTO fish_profiles (
                fish_name, temp_norm_min, temp_norm_max, temp_danger_min, temp_danger_max,
                ph_norm_min, ph_norm_max, ph_danger_min, ph_danger_max,
                turb_norm_max, turb_danger_max, suggestion_text
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            fish_name, p["t_n_min"], p["t_n_max"], p["t_d_min"], p["t_d_max"],
            p["p_n_min"], p["p_n_max"], p["p_d_min"], p["p_d_max"],
            p["tb_n_max"], p["tb_d_max"], p["suggestion"]
        ))

    print("4. Seeding 1 Admin and 10 Farmers with Normal, Warning, and Danger Pond Samples...")
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")
    
    profiles = {
        1:  {"pond": "North Pond",    "fish": "Tilapia",           "t_base": 29.5, "ph_base": 7.5, "tb_base": 40.0},  # Stable
        2:  {"pond": "South Pond",    "fish": "Bangus (Milkfish)", "t_base": 28.5, "ph_base": 7.8, "tb_base": 30.0},  # Stable
        3:  {"pond": "East Pond",     "fish": "Catfish (Hito)",    "t_base": 29.5, "ph_base": 7.2, "tb_base": 50.0},  # Stable
        4:  {"pond": "West Pond",     "fish": "Tilapia",           "t_base": 29.0, "ph_base": 8.0, "tb_base": 35.0},  # Stable
        5:  {"pond": "Shallow Pond",  "fish": "Bangus (Milkfish)", "t_base": 33.2, "ph_base": 7.5, "tb_base": 40.0},  # WARNING (Temp)
        6:  {"pond": "Acidic Pond",   "fish": "Tilapia",           "t_base": 29.5, "ph_base": 6.8, "tb_base": 40.0},  # WARNING (pH)
        7:  {"pond": "Muddy Pond",    "fish": "Catfish (Hito)",    "t_base": 29.5, "ph_base": 7.2, "tb_base": 120.0}, # WARNING (Turbidity)
        8:  {"pond": "Heatwave Pond", "fish": "Tilapia",           "t_base": 36.0, "ph_base": 6.2, "tb_base": 40.0},  # CRITICAL (Temp + pH)
        9:  {"pond": "Algae Pond",    "fish": "Bangus (Milkfish)", "t_base": 33.0, "ph_base": 7.5, "tb_base": 125.0}, # CRITICAL (Turb + Temp)
        10: {"pond": "Dead Zone",     "fish": "Catfish (Hito)",    "t_base": 37.0, "ph_base": 9.5, "tb_base": 160.0}  # CRITICAL (All)
    }

    for i in range(1, 11):
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, 'farmer')", (f"farmer_{i}", f"pass{i}"))
        device_sn = f"PEARL-ESP32-{i:03d}"
        prof = profiles[i]
        fish_type = prof["fish"]
        preset = DEFAULT_FISH_PROFILES[fish_type]

        cursor.execute('''
            INSERT INTO devices (
                device_sn, owner_id, pond_name, location, length, width, depth, fish_count,
                fish_type, temp_norm_min, temp_norm_max, temp_danger_min, temp_danger_max,
                ph_norm_min, ph_norm_max, ph_danger_min, ph_danger_max, turb_norm_max, turb_danger_max
            ) VALUES (?, ?, ?, 'Angono, Rizal', 25.0, 20.0, 1.0, 500, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            device_sn, i + 1, prof["pond"], fish_type,
            preset["t_n_min"], preset["t_n_max"], preset["t_d_min"], preset["t_d_max"],
            preset["p_n_min"], preset["p_n_max"], preset["p_d_min"], preset["p_d_max"],
            preset["tb_n_max"], preset["tb_d_max"]
        ))

    print("5. Seeding 30-day Telemetry Data for all 10 Devices...")
    now = datetime.datetime.now()
    records = []

    for i in range(1, 11):
        device_sn = f"PEARL-ESP32-{i:03d}"
        prof = profiles[i]
        
        for j in range(120, 0, -1):
            timestamp = (now - datetime.timedelta(hours=j * 6)).strftime("%Y-%m-%d %H:%M:%S")
            hour = (now - datetime.timedelta(hours=j * 6)).hour
            cycle = math.sin(math.pi * (hour - 6) / 12) 
            
            temp = round(prof["t_base"] + (0.4 * cycle) + random.uniform(-0.15, 0.15), 1)
            ph = round(prof["ph_base"] + (0.08 * cycle) + random.uniform(-0.04, 0.04), 2)
            turbidity = round(prof["tb_base"] + random.uniform(-3.0, 3.0), 1)
            water_level = round(15.0 + random.uniform(-0.5, 0.5), 1)
            
            records.append((device_sn, ph, temp, turbidity, water_level, timestamp))

    cursor.executemany(
        "INSERT INTO telemetry (device_sn, ph, temperature, turbidity, water_level_cm, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
        records
    )
    conn.commit()
    conn.close()

    if ROOT_DB_PATH != BACKEND_DB_PATH:
        shutil.copyfile(ROOT_DB_PATH, BACKEND_DB_PATH)

    print("✅ Database seeding complete! Fish species library and 10 pond profiles are ready.")

if __name__ == "__main__":
    reset_and_seed_database()