import sqlite3
import datetime
import math
import random
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "pearl_data.db")

def reset_and_seed_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Clearing old database tables...")
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS devices")
    cursor.execute("DROP TABLE IF EXISTS telemetry")

    print("Rebuilding tables...")
    cursor.execute('''CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT)''')
    cursor.execute('''CREATE TABLE devices (device_sn TEXT PRIMARY KEY, owner_id INTEGER, pond_name TEXT, location TEXT DEFAULT 'Angono, Rizal', length REAL DEFAULT 25.0, width REAL DEFAULT 20.0, depth REAL DEFAULT 1.0, alert_phone TEXT DEFAULT '', alert_level TEXT DEFAULT 'Critical', sleep_interval INTEGER DEFAULT 30, ph_offset REAL DEFAULT 0.0, turb_offset REAL DEFAULT 0.0, fish_count INTEGER DEFAULT 0)''')
    cursor.execute('''CREATE TABLE telemetry (id INTEGER PRIMARY KEY AUTOINCREMENT, device_sn TEXT, ph REAL, temperature REAL, turbidity REAL, water_level_cm REAL DEFAULT 15.0, timestamp DATETIME)''')

    print("Seeding 1 Admin and 10 Farmers...")
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")
    
    # Define exact environmental profiles to trigger the UI Risk Scores
    profiles = {
        1: {"pond": "North Pond", "t_base": 29.5, "ph_base": 7.5, "tb_base": 40.0},  # Stable
        2: {"pond": "South Pond", "t_base": 28.5, "ph_base": 7.8, "tb_base": 30.0},  # Stable
        3: {"pond": "East Pond", "t_base": 30.0, "ph_base": 7.2, "tb_base": 50.0},   # Stable
        4: {"pond": "West Pond", "t_base": 29.0, "ph_base": 8.0, "tb_base": 35.0},   # Stable
        5: {"pond": "Shallow Pond", "t_base": 32.0, "ph_base": 7.5, "tb_base": 40.0},# WARNING (Temp)
        6: {"pond": "Acidic Pond", "t_base": 29.5, "ph_base": 6.8, "tb_base": 40.0}, # WARNING (pH)
        7: {"pond": "Muddy Pond", "t_base": 29.5, "ph_base": 7.5, "tb_base": 90.0},  # WARNING (Turbidity)
        8: {"pond": "Heatwave Pond", "t_base": 34.0, "ph_base": 6.2, "tb_base": 40.0},# CRITICAL (Temp + pH)
        9: {"pond": "Algae Pond", "t_base": 31.5, "ph_base": 7.5, "tb_base": 115.0}, # CRITICAL (Turb + Temp)
        10: {"pond": "Dead Zone", "t_base": 35.0, "ph_base": 9.5, "tb_base": 150.0}  # CRITICAL (All)
    }

    for i in range(1, 11):
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, 'farmer')", (f"farmer_{i}", f"pass{i}"))
        device_sn = f"PEARL-ESP32-{i:03d}"
        cursor.execute(
            "INSERT INTO devices (device_sn, owner_id, pond_name, length, width, depth, fish_count) VALUES (?, ?, ?, 25.0, 20.0, 1.0, 500)", 
            (device_sn, i + 1, profiles[i]["pond"])
        )

    print("Seeding 30-day Telemetry Data for all 10 Devices...")
    now = datetime.datetime.now()
    records = []

    for i in range(1, 11):
        device_sn = f"PEARL-ESP32-{i:03d}"
        prof = profiles[i]
        
        for j in range(120, 0, -1):
            timestamp = (now - datetime.timedelta(hours=j * 6)).strftime("%Y-%m-%d %H:%M:%S")
            hour = (now - datetime.timedelta(hours=j * 6)).hour
            cycle = math.sin(math.pi * (hour - 6) / 12) 
            
            # Constrain the amplitude so the statuses remain consistent
            temp = round(prof["t_base"] + (0.5 * cycle) + random.uniform(-0.2, 0.2), 1)
            ph = round(prof["ph_base"] + (0.1 * cycle) + random.uniform(-0.05, 0.05), 2)
            turbidity = round(prof["tb_base"] + random.uniform(-3.0, 3.0), 1)
            water_level = round(15.0 + random.uniform(-0.5, 0.5), 1)
            
            records.append((device_sn, ph, temp, turbidity, water_level, timestamp))

    cursor.executemany("INSERT INTO telemetry (device_sn, ph, temperature, turbidity, water_level_cm, timestamp) VALUES (?, ?, ?, ?, ?, ?)", records)
    conn.commit()
    conn.close()
    print("Database seeding complete! Data is now perfectly calibrated to trigger UI warnings.")

if __name__ == "__main__":
    reset_and_seed_database()