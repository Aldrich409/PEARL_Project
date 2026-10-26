from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from prophet import Prophet
import pandas as pd
import sqlite3
import datetime
import time
import math
import hashlib

app = FastAPI(title="PEARL API Gateway")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# --- DATABASE INITIALIZATION (WITH NEW UPGRADE TABLES) ---
# =========================================================
def init_db():
    conn = sqlite3.connect('pearl_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS devices (
        device_sn TEXT PRIMARY KEY, owner_id INTEGER, pond_name TEXT, location TEXT DEFAULT '', 
        length REAL DEFAULT 25.0, width REAL DEFAULT 20.0, depth REAL DEFAULT 1.0, 
        alert_phone TEXT DEFAULT '', alert_level TEXT DEFAULT 'Critical', 
        sleep_interval INTEGER DEFAULT 30, ph_offset REAL DEFAULT 0.0, 
        turb_offset REAL DEFAULT 0.0, fish_count INTEGER DEFAULT 0)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS telemetry (
        id INTEGER PRIMARY KEY AUTOINCREMENT, device_sn TEXT, ph REAL, temperature REAL, 
        turbidity REAL, water_level_cm REAL DEFAULT 15.0, timestamp DATETIME)''')

    # NEW TABLE 1: IPO Feedback Loop - Farmer Interventions Log
    cursor.execute('''CREATE TABLE IF NOT EXISTS interventions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_sn TEXT,
        username TEXT,
        action_taken TEXT,
        recommended_dosage TEXT,
        ph_at_action REAL,
        temp_at_action REAL,
        turb_at_action REAL,
        timestamp DATETIME
    )''')

    # NEW TABLE 2: ISO/IEC 25010 Performance Efficiency Telemetry Log
    cursor.execute('''CREATE TABLE IF NOT EXISTS performance_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        endpoint TEXT,
        method TEXT,
        operation_category TEXT,
        execution_time_ms REAL,
        status_code INTEGER,
        timestamp DATETIME
    )''')
    
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")
        for i in range(1, 11):
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, 'farmer')", (f"farmer_{i}", f"pass{i}"))
            cursor.execute(
                "INSERT INTO devices (device_sn, owner_id, pond_name, location, length, width, depth, fish_count) VALUES (?, ?, ?, ?, 25.0, 20.0, 1.0, 500)", 
                (f"PEARL-ESP32-{i:03d}", i + 1, f"Test Pond {i}", "Angono, Rizal")
            )
    conn.commit()
    conn.close()

init_db()

# =========================================================
# --- ISO/IEC 25010 PERFORMANCE EFFICIENCY MIDDLEWARE ---
# =========================================================
@app.middleware("http")
async def log_iso25010_performance(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    execution_ms = round((time.perf_counter() - start_time) * 1000, 2)
    
    path = request.url.path
    if path.startswith("/api") and path != "/api/admin/performance":
        if "telemetry" in path and request.method == "POST":
            category = "IoT Telemetry Ingestion"
        elif "forecast" in path:
            category = "Prophet AI Prediction"
        elif "bio-audit" in path:
            category = "Virtual Bio & Harvest Audit"
        elif "interventions" in path:
            category = "IPO Feedback Action Log"
        else:
            category = "Dashboard Data Retrieval"
            
        try:
            conn = sqlite3.connect('pearl_data.db')
            cursor = conn.cursor()
            ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "INSERT INTO performance_logs (endpoint, method, operation_category, execution_time_ms, status_code, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                (path, request.method, category, execution_ms, response.status_code, ts)
            )
            conn.commit()
            conn.close()
        except Exception:
            pass
            
    response.headers["X-Process-Time-Ms"] = str(execution_ms)
    return response

# =========================================================
# --- PYDANTIC SCHEMAS ---
# =========================================================
class LoginData(BaseModel):
    username: str
    password: str

class SensorData(BaseModel):
    device_sn: str
    ph: float
    temperature: float
    turbidity: float
    water_level_cm: float = 15.0

class DeviceSettings(BaseModel):
    device_sn: str
    pond_name: str
    location: str = ""
    length: float
    width: float
    depth: float
    fish_count: int
    alert_phone: str
    alert_level: str
    sleep_interval: int
    ph_offset: float
    turb_offset: float

class AccountData(BaseModel):
    username: str
    password: str
    role: str = "farmer"
    pond_name: str = "Main Pond"
    location: str = ""
    length: float = 25.0
    width: float = 20.0
    depth: float = 1.0
    fish_count: int = 500
    alert_phone: str = ""

class InterventionData(BaseModel):
    device_sn: str
    username: str
    action_taken: str
    recommended_dosage: str
    ph_at_action: float
    temp_at_action: float
    turb_at_action: float

# =========================================================
# --- BIOLOGICAL & CHEMICAL ESTIMATION ENGINE ---
# =========================================================
def compute_virtual_bio_indicators(temp_c: float, ph: float, turb_ntu: float, length: float = 25.0, width: float = 20.0, depth: float = 1.0):
    """
    1. Emerson et al. Formula for Un-ionized Ammonia (NH3) Fraction:
       pKa = 0.09018 + (2729.92 / (273.15 + Temp_C))
       nh3_fraction = 1 / (10^(pKa - pH) + 1)
    2. Theoretical Dissolved Oxygen (DO) Saturation & Algal Respiration Stress:
       Approximates freshwater DO saturation (mg/L) from temperature and deducts nocturnal algal demand from high turbidity.
    3. Volumetric Remediation Math (L x W x D).
    """
    temp_k = 273.15 + max(temp_c, 0.0)
    pka = 0.09018 + (2729.92 / temp_k)
    nh3_fraction = 1.0 / (math.pow(10, (pka - ph)) + 1.0)
    nh3_percent = round(nh3_fraction * 100, 2)
    
    # Assuming a typical stocked pond Total Ammonia Nitrogen (TAN) of 1.5 mg/L:
    estimated_toxic_nh3_mg_l = round(1.5 * nh3_fraction, 3)
    if estimated_toxic_nh3_mg_l >= 0.05 or nh3_percent >= 10.0:
        nh3_status = "Danger (Toxic NH3 Spike)"
    elif estimated_toxic_nh3_mg_l >= 0.02 or nh3_percent >= 3.0:
        nh3_status = "Warning (Elevated NH3 Conversion)"
    else:
        nh3_status = "Safe (Ionized NH4+ Dominant)"

    # Freshwater DO saturation baseline (14.62 mg/L at 0C, decreasing with heat & algal turbidity)
    do_saturation = 14.62 - (0.3898 * temp_c) + (0.006969 * (temp_c ** 2)) - (0.00005897 * (temp_c ** 3))
    turbidity_oxygen_penalty = max(0.0, (turb_ntu - 40.0) * 0.025)
    estimated_do_mg_l = round(max(1.0, do_saturation - turbidity_oxygen_penalty), 2)
    
    if estimated_do_mg_l < 4.0:
        do_status = "Critical Hypoxia Risk (Buksan ang Aerator)"
    elif estimated_do_mg_l < 5.5:
        do_status = "Moderate Oxygen Stress"
    else:
        do_status = "Optimal Oxygen Saturation"

    # Volumetric Dosage Calculations
    volume_m3 = round(length * width * depth, 1)
    apog_kg = round(volume_m3 * 0.15, 1) if ph < 6.5 else 0.0
    water_exchange_m3 = round(volume_m3 * 0.20, 1) if (ph < 6.5 or ph > 9.0 or turb_ntu > 80 or temp_c > 33.0) else 0.0

    return {
        "nh3_toxicity_percent": nh3_percent,
        "estimated_nh3_mg_l": estimated_toxic_nh3_mg_l,
        "nh3_status": nh3_status,
        "estimated_do_mg_l": estimated_do_mg_l,
        "do_status": do_status,
        "volume_m3": volume_m3,
        "recommended_apog_kg": apog_kg,
        "recommended_water_exchange_m3": water_exchange_m3
    }

# =========================================================
# --- STANDARD AUTH, TELEMETRY & DEVICE ENDPOINTS ---
# =========================================================
@app.post("/api/login")
async def login(data: LoginData):
    conn = sqlite3.connect('pearl_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users WHERE username=? AND password=?", (data.username, data.password))
    user = cursor.fetchone()
    conn.close()
    if user:
        return {"id": user[0], "username": user[1], "role": user[2]}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/api/telemetry")
async def receive_data(data: SensorData):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect('pearl_data.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO telemetry (device_sn, ph, temperature, turbidity, water_level_cm, timestamp) VALUES (?, ?, ?, ?, ?, ?)", 
        (data.device_sn, data.ph, data.temperature, data.turbidity, data.water_level_cm, ts)
    )
    conn.commit()
    conn.close()
    return {"status": "success", "timestamp": ts}

@app.get("/api/devices")
async def get_devices(user_id: int = 1, role: str = "admin"):
    conn = sqlite3.connect('pearl_data.db')
    cursor = conn.cursor()
    if role.lower() == 'admin':
        cursor.execute("SELECT device_sn, owner_id, pond_name, location, length, width, depth, alert_phone, alert_level, sleep_interval, ph_offset, turb_offset, fish_count FROM devices")
    else:
        cursor.execute("SELECT device_sn, owner_id, pond_name, location, length, width, depth, alert_phone, alert_level, sleep_interval, ph_offset, turb_offset, fish_count FROM devices WHERE owner_id=?", (user_id,))
    rows = [{
        "device_sn": r[0], "owner_id": r[1], "pond_name": r[2], "location": r[3],
        "length": r[4], "width": r[5], "depth": r[6], "alert_phone": r[7],
        "alert_level": r[8], "sleep_interval": r[9], "ph_offset": r[10],
        "turb_offset": r[11], "fish_count": r[12]
    } for r in cursor.fetchall()]
    conn.close()
    return rows

@app.put("/api/devices/update")
async def update_device(data: DeviceSettings):
    conn = sqlite3.connect('pearl_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE devices 
        SET pond_name=?, location=?, length=?, width=?, depth=?, fish_count=?, 
            alert_phone=?, alert_level=?, sleep_interval=?, ph_offset=?, turb_offset=?
        WHERE device_sn=?
    ''', (data.pond_name, data.location, data.length, data.width, data.depth, data.fish_count,
          data.alert_phone, data.alert_level, data.sleep_interval, 
          data.ph_offset, data.turb_offset, data.device_sn))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.get("/api/admin/accounts")
async def get_all_accounts():
    conn = sqlite3.connect('pearl_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.id, u.username, u.role, d.device_sn, d.pond_name, d.location, d.length, d.width, d.depth, d.fish_count, d.alert_phone 
        FROM users u 
        LEFT JOIN devices d ON u.id = d.owner_id
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [{
        "id": r[0], "username": r[1], "role": r[2], "device_sn": r[3],
        "pond_name": r[4], "location": r[5], "length": r[6], "width": r[7],
        "depth": r[8], "fish_count": r[9], "alert_phone": r[10]
    } for r in rows]

@app.post("/api/admin/accounts/create")
async def create_account(data: AccountData):
    conn = sqlite3.connect('pearl_data.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (data.username, data.password, data.role))
        user_id = cursor.lastrowid
        if data.role == "farmer":
            device_sn = f"PEARL-ESP32-{user_id:03d}"
            cursor.execute('''
                INSERT INTO devices (device_sn, owner_id, pond_name, location, length, width, depth, fish_count, alert_phone)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (device_sn, user_id, data.pond_name, data.location, data.length, data.width, data.depth, data.fish_count, data.alert_phone))
        conn.commit()
        conn.close()
        return {"status": "success"}
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/admin/accounts/{user_id}")
async def delete_account(user_id: int):
    conn = sqlite3.connect('pearl_data.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    cursor.execute("DELETE FROM devices WHERE owner_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.get("/api/telemetry/latest")
async def get_latest(device_sn: str):
    conn = sqlite3.connect('pearl_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT temperature, ph, turbidity, water_level_cm, timestamp FROM telemetry WHERE device_sn = ? ORDER BY id DESC LIMIT 1", (device_sn,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"temperature": row[0], "ph": row[1], "turbidity": row[2], "water_level_cm": row[3], "timestamp": row[4]}
    raise HTTPException(status_code=404, detail="No data found")

@app.get("/api/telemetry/history")
async def get_history(device_sn: str, limit: int = 50):
    conn = sqlite3.connect('pearl_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT temperature, ph, turbidity, water_level_cm, timestamp FROM telemetry WHERE device_sn = ? ORDER BY id DESC LIMIT ?", (device_sn, limit))
    rows = cursor.fetchall()
    conn.close()
    rows.reverse()
    return [{"temperature": r[0], "ph": r[1], "turbidity": r[2], "water_level_cm": r[3], "timestamp": r[4]} for r in rows]

# =========================================================
# --- NEW ENDPOINT 1: VIRTUAL BIO-ESTIMATOR & LUMOT AUDIT ---
# =========================================================
@app.get("/api/telemetry/bio-audit")
async def get_bio_and_harvest_audit(device_sn: str):
    conn = sqlite3.connect('pearl_data.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT pond_name, location, length, width, depth, fish_count FROM devices WHERE device_sn = ?", (device_sn,))
    dev = cursor.fetchone()
    if not dev:
        conn.close()
        raise HTTPException(status_code=404, detail="Device not found")
    pond_name, location, length, width, depth, fish_count = dev

    # Fetch last 56 readings (~14 days of 6-hour logs) for the Off-Flavor (Lumot) Audit
    cursor.execute("SELECT temperature, ph, turbidity, water_level_cm, timestamp FROM telemetry WHERE device_sn = ? ORDER BY id DESC LIMIT 56", (device_sn,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail="No telemetry records found")

    latest_temp, latest_ph, latest_turb, latest_wl, latest_ts = rows[0]
    bio_metrics = compute_virtual_bio_indicators(latest_temp, latest_ph, latest_turb, length, width, depth)

    # Off-Flavor (Lumot) Harvest Readiness Audit across the 14-day window
    total_logs = len(rows)
    clean_turb_logs = sum(1 for r in rows if r[2] <= 80.0)
    stable_ph_logs = sum(1 for r in rows if 6.5 <= r[1] <= 8.8)
    avg_turb = round(sum(r[2] for r in rows) / total_logs, 1)
    avg_ph = round(sum(r[1] for r in rows) / total_logs, 2)
    avg_temp = round(sum(r[0] for r in rows) / total_logs, 1)

    compliance_score = round(((clean_turb_logs * 0.7) + (stable_ph_logs * 0.3)) / total_logs * 100, 1)
    is_harvest_ready = compliance_score >= 85.0 and latest_turb <= 80.0

    # Generate a unique cryptographic audit hash for the QR Harvest Certificate
    audit_date = datetime.datetime.now().strftime("%Y-%m-%d")
    raw_token = f"{device_sn}|{pond_name}|{compliance_score}|{audit_date}"
    cert_id = "PEARL-CERT-" + hashlib.sha256(raw_token.encode()).hexdigest()[:10].upper()

    return {
        "device_sn": device_sn,
        "pond_name": pond_name,
        "location": location or "Angono, Rizal",
        "fish_count": fish_count,
        "latest_timestamp": latest_ts,
        "virtual_bio": bio_metrics,
        "harvest_audit": {
            "records_audited": total_logs,
            "avg_turbidity_ntu": avg_turb,
            "avg_ph": avg_ph,
            "avg_temp_c": avg_temp,
            "compliance_score_pct": compliance_score,
            "is_off_flavor_free": is_harvest_ready,
            "grade": "GRADE A: Off-Flavor (Lumot) Free" if is_harvest_ready else "HOLD HARVEST: Depuration / Water Flushing Needed",
            "certificate_id": cert_id,
            "audit_date": audit_date
        }
    }

# =========================================================
# --- NEW ENDPOINT 2: FARMER INTERVENTION FEEDBACK LOOP ---
# =========================================================
@app.post("/api/interventions")
async def log_farmer_intervention(data: InterventionData):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect('pearl_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO interventions (device_sn, username, action_taken, recommended_dosage, ph_at_action, temp_at_action, turb_at_action, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data.device_sn, data.username, data.action_taken, data.recommended_dosage, data.ph_at_action, data.temp_at_action, data.turb_at_action, ts))
    conn.commit()
    conn.close()
    return {"status": "success", "timestamp": ts}

@app.get("/api/interventions")
async def get_farmer_interventions(device_sn: str, limit: int = 20):
    conn = sqlite3.connect('pearl_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, device_sn, username, action_taken, recommended_dosage, ph_at_action, temp_at_action, turb_at_action, timestamp
        FROM interventions
        WHERE device_sn = ?
        ORDER BY id DESC LIMIT ?
    ''', (device_sn, limit))
    rows = cursor.fetchall()
    conn.close()
    return [{
        "id": r[0], "device_sn": r[1], "username": r[2], "action_taken": r[3],
        "recommended_dosage": r[4], "ph_at_action": r[5], "temp_at_action": r[6],
        "turb_at_action": r[7], "timestamp": r[8]
    } for r in rows]

# =========================================================
# --- NEW ENDPOINT 3: ISO/IEC 25010 PERFORMANCE LOGS ---
# =========================================================
@app.get("/api/admin/performance")
async def get_iso25010_performance_logs(limit: int = 200):
    conn = sqlite3.connect('pearl_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, endpoint, method, operation_category, execution_time_ms, status_code, timestamp
        FROM performance_logs
        ORDER BY id DESC LIMIT ?
    ''', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [{
        "id": r[0], "endpoint": r[1], "method": r[2], "operation_category": r[3],
        "execution_time_ms": r[4], "status_code": r[5], "timestamp": r[6]
    } for r in rows]

# =========================================================
# --- PROPHET AI BREEDING FORECAST ENGINE ---
# =========================================================
def evaluate_tilapia_environment(temp: float, ph: float, turb: float):
    if turb > 100:
        return (
            "High Algal Bloom Risk / Panganib ng Mabilis na Pagdami ng Algae",
            "WARNING: Reduce feeding by 50% to cut nutrients. Increase aeration immediately.\n"
            "BABALA: Bawasan ang pakain ng 50% upang mabawasan ang dumi sa tubig. Paganahin agad ang aerator."
        )
    if ph < 6.5 or ph > 9.0:
        return (
            "Critical Water Warning / PANGANIB sa Kalidad ng Tubig",
            "DANGER: Immediate action required! Halt feeding, turn on all aerators, and prepare a 20% water exchange.\n"
            "PANGANIB: Kailangan ng agarang aksyon! Itigil ang pagpapakain, buksan ang lahat ng aerator, at magpalit ng 20% ng tubig."
        )
    if 28 <= temp <= 31 and 6.5 <= ph <= 9.0:
        return (
            "Optimal Breeding / Magandang Panahon sa Pagpaparami",
            "NORMAL: Conditions ideal for spawning. Maintain current feed rate and minimize pond disturbances.\n"
            "NORMAL: Maganda ang kondisyon para sa pangingitlog ng isda. Panatilihin ang dami ng pakain at huwag gaanong istorbohin ang palaisdaan."
        )
    return (
        "System Stable / Maayos ang Kalagayan ng Tubig",
        "NORMAL: Parameters are safe but not triggering breeding. Continue standard operations.\n"
        "NORMAL: Ligtas ang kalidad ng tubig ngunit hindi pa perpekto para sa pagpaparami. Ituloy ang karaniwang alaga."
    )

@app.get("/api/forecast/breeding")
async def get_breeding_forecast(device_sn: str, days_ahead: int = 3):
    conn = sqlite3.connect('pearl_data.db')
    df = pd.read_sql_query(f"SELECT timestamp as ds, temperature, ph, turbidity FROM telemetry WHERE device_sn='{device_sn}'", conn)
    conn.close()
    
    if len(df) < 10:
        raise HTTPException(status_code=400, detail="Insufficient telemetry data.")

    df['ds'] = pd.to_datetime(df['ds'])
    
    m_temp = Prophet(daily_seasonality=True).fit(df[['ds', 'temperature']].rename(columns={'temperature': 'y'}))
    forecast_temp = m_temp.predict(m_temp.make_future_dataframe(periods=days_ahead))[['ds', 'yhat']].tail(days_ahead)

    m_ph = Prophet(daily_seasonality=True).fit(df[['ds', 'ph']].rename(columns={'ph': 'y'}))
    forecast_ph = m_ph.predict(m_ph.make_future_dataframe(periods=days_ahead))[['ds', 'yhat']].tail(days_ahead)

    m_turb = Prophet(daily_seasonality=True).fit(df[['ds', 'turbidity']].rename(columns={'turbidity': 'y'}))
    forecast_turb = m_turb.predict(m_turb.make_future_dataframe(periods=days_ahead))[['ds', 'yhat']].tail(days_ahead)

    forecast_results = []
    for i in range(days_ahead):
        pred_temp = round(forecast_temp.iloc[i]['yhat'], 1)
        pred_ph = round(forecast_ph.iloc[i]['yhat'], 2)
        pred_turb = round(forecast_turb.iloc[i]['yhat'], 1)
        date_str = forecast_temp.iloc[i]['ds'].strftime('%Y-%m-%d')
        
        status, action = evaluate_tilapia_environment(pred_temp, pred_ph, pred_turb)
        
        forecast_results.append({
            "date": date_str,
            "predicted_temperature": pred_temp,
            "predicted_ph": pred_ph,
            "predicted_turbidity": pred_turb,
            "status": status,
            "action_required": action
        })

    return {"device_sn": device_sn, "forecast": forecast_results}