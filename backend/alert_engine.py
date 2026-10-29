import sqlite3
import time
from datetime import datetime

DB_PATH = 'pearl_data.db'

def check_thresholds(temp, ph, turb):
    """Evaluates biological thresholds and returns SMS alert messages if breached."""
    alerts = []
    # Algal Bloom & Turbidity Rules
    if turb > 100: alerts.append(f"CRITICAL: Lumot Risk! Turbidity is {turb} NTU.")
    elif turb > 80: alerts.append(f"WARNING: Tubig ay lumalabo ({turb} NTU).")
    
    # pH Rules
    if ph < 6.5: alerts.append(f"CRITICAL: Mataas na Asido! pH is {ph}.")
    elif ph > 9.0: alerts.append(f"CRITICAL: Nakakalason na Alkalinity! pH is {ph}.")
    
    # Temp Rules
    if temp > 33: alerts.append(f"CRITICAL: Sobrang Init! Temp is {temp}°C.")
    elif temp < 26: alerts.append(f"WARNING: Malamig ang tubig ({temp}°C).")
    
    return alerts

def send_sms(phone, pond_name, message):
    """Mock function to simulate GSM/Twilio SMS Dispatch"""
    print(f"\n" + "="*50)
    print(f"📱 SMS DISPATCH INITIATED")
    print(f"📍 Target: {phone} ({pond_name})")
    print(f"✉️ Message: P.E.A.R.L. ALERT - {message} Please check dashboard.")
    print(f"✓ Status: DELIVERED at {datetime.now().strftime('%H:%M:%S')}")
    print("="*50 + "\n")
    # Note for Panel: In production, this uses Twilio API or AT Commands to SIM800L

def run_alert_engine():
    print("🚀 PEARL Autonomous SMS Alert Engine is running...")
    print("👀 Monitoring pearl_data.db for critical anomalies every 10 seconds...\n")
    
    # Keep track of the last processed telemetry ID to avoid spamming the same alert
    last_processed_ids = {}

    while True:
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Fetch all devices to monitor
            cursor.execute("SELECT device_sn, pond_name, alert_phone, alert_level FROM devices")
            devices = cursor.fetchall()
            
            for dev in devices:
                sn, pond_name, phone, alert_level = dev
                
                # Fetch the latest telemetry for this device
                cursor.execute("SELECT id, temperature, ph, turbidity FROM telemetry WHERE device_sn = ? ORDER BY id DESC LIMIT 1", (sn,))
                latest = cursor.fetchone()
                
                if latest:
                    record_id, temp, ph, turb = latest
                    
                    # Only process if this is a NEW record we haven't checked yet
                    if sn not in last_processed_ids or last_processed_ids[sn] < record_id:
                        
                        alerts = check_thresholds(temp, ph, turb)
                        
                        if alerts:
                            combined_message = " | ".join(alerts)
                            send_sms(phone if phone else "09XXXXXXXXX", pond_name, combined_message)
                        
                        # Update the tracker so we don't alert for this exact record again
                        last_processed_ids[sn] = record_id
                        
            conn.close()
        except Exception as e:
            print(f"Database error: {e}")
            
        time.sleep(10) # Wait 10 seconds before checking again

if __name__ == "__main__":
    run_alert_engine()