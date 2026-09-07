from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from prophet import Prophet
import pandas as pd
import sqlite3
import datetime

app = FastAPI(title="PEARL API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def init_db():
    conn = sqlite3.connect('pearl_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT)''')
    # ADDED: location column to devices table
    cursor.execute('''CREATE TABLE IF NOT EXISTS devices (device_sn TEXT PRIMARY KEY, owner_id INTEGER, pond_name TEXT, location TEXT DEFAULT '', length REAL DEFAULT 25.0, width REAL DEFAULT 20.0, depth REAL DEFAULT 1.0, alert_phone TEXT DEFAULT '', alert_level TEXT DEFAULT 'Critical', sleep_interval INTEGER DEFAULT 30, ph_offset REAL DEFAULT 0.0, turb_offset REAL DEFAULT 0.0, fish_count INTEGER DEFAULT 0)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS telemetry (id INTEGER PRIMARY KEY AUTOINCREMENT, device_sn TEXT, ph REAL, temperature REAL, turbidity REAL, water_level_cm REAL DEFAULT 15.0, timestamp DATETIME)''')
    
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")
        for i in range(1, 11):
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, 'farmer')", (f"farmer_{i}", f"pass{i}"))
            cursor.execute("INSERT INTO devices (device_sn, owner_id, pond_name, location, length, width, depth, fish_count) VALUES (?, ?, ?, ?, 25.0, 20.0, 1.0, 500)", (f"PEARL-ESP32-00{i}", i + 1, f"Test Pond {i}", "Angono Rizal"))
    conn.commit()
    conn.close()

init_db()

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
    cursor.execute("INSERT INTO telemetry (device_sn, ph, temperature, turbidity, water_level_cm, timestamp) VALUES (?, ?, ?, ?, ?, ?)", 
                   (data.device_sn, data.ph, data.temperature, data.turbidity, data.water_level_cm, ts))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.get("/api/devices")
async def get_devices(user_id: int = 1, role: str = "admin"):
    conn = sqlite3.connect('pearl_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM devices" if role.lower() == 'admin' else f"SELECT * FROM devices WHERE owner_id={user_id}")
    rows = [{"device_sn": r[0], "owner_id": r[1], "pond_name": r[2], "location": r[3], "length": r[4], "width": r[5], "depth": r[6], "alert_phone": r[7], "alert_level": r[8], "sleep_interval": r[9], "ph_offset": r[10], "turb_offset": r[11], "fish_count": r[12]} for r in cursor.fetchall()]
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
    
    accounts = []
    for r in rows:
        accounts.append({
            "id": r[0], "username": r[1], "role": r[2], "device_sn": r[3],
            "pond_name": r[4], "location": r[5], "length": r[6], "width": r[7],
            "depth": r[8], "fish_count": r[9], "alert_phone": r[10]
        })
    return accounts

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
async def get_history(device_sn: str, limit: int = 30):
    conn = sqlite3.connect('pearl_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT temperature, ph, turbidity, water_level_cm, timestamp FROM telemetry WHERE device_sn = ? ORDER BY id DESC LIMIT ?", (device_sn, limit))
    rows = cursor.fetchall()
    conn.close()
    rows.reverse()
    return [{"temperature": r[0], "ph": r[1], "turbidity": r[2], "water_level_cm": r[3], "timestamp": r[4]} for r in rows]

# --- META PROPHET AI & BILINGUAL BIOLOGICAL DECISION ENGINE ---
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
            "NORMAL: Maganda ang kondisyon para sa pangitlog ng isda. Panatilihin ang dami ng pakain at huwag gaanong istorbohin ang palaisdaan."
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
        raise HTTPException(status_code=400, detail="Insufficient telemetry data (at least 10 historical records needed for Prophet).")

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