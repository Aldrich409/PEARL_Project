import sys
import os
import base64
import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from PIL import Image

# Using the API modules and separated components/views
from api import auth_api, device_api 
from api.telemetry_api import fetch_latest_data
from components import sidebar
from views import (
    view_telemetry, 
    view_forecast, 
    view_records, 
    view_settings, 
    view_admin_overview, 
    view_account_management,
    view_system_health
)

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="PEARL Dashboard", 
    page_icon="🐟",  
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- LOAD GLOBAL CSS THEME ---
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "theme.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    else:
        # Fallback CSS if theme.css is missing
        st.markdown("""
        <style>
        .stApp { background-color: var(--background-color); }
        div[data-testid="stMetric"] {
            background-color: var(--secondary-background-color);
            border: 1px solid var(--border-color);
            padding: 16px 20px;
            border-radius: 12px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.05);
        }
        .tagalog-subtext {
            color: #64748B;
            font-size: 13px;
            font-style: italic;
            margin-top: -15px;
            margin-bottom: 20px;
        }
        </style>
        """, unsafe_allow_html=True)

load_css()

# --- SESSION STATE INITIALIZATION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.active_device_sn = "PEARL-ESP32-001"

if "current_page" not in st.session_state:
    st.session_state.current_page = "Live Telemetry"

def set_page(page_name):
    st.session_state.current_page = page_name

def handle_login(username, password):
    user_data = auth_api.authenticate_user(username, password) 
    if user_data:
        st.session_state.logged_in = True
        st.session_state.user_id = user_data["id"]
        st.session_state.username = user_data["username"]
        st.session_state.role = user_data["role"]
        st.session_state.current_page = "Live Telemetry"

        devices = device_api.fetch_devices(user_data["id"], user_data["role"]) 
        if devices:
            st.session_state.active_device_sn = devices[0]["device_sn"]
        st.rerun()
    else:
        st.error("Invalid credentials or backend offline. Please try again.")

def handle_logout():
    st.session_state.clear()
    st.rerun()

# Helper function to load local images safely in Streamlit via Base64
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return ""

# ==========================================
# UI ROUTING - LOGIN & DASHBOARD
# ==========================================

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    bg_path = os.path.join(current_dir, "assets", "Pearl_BG.jpg")
    logo_path = os.path.join(current_dir, "assets", "pearl_logo(1).png")
    
    bg_base64 = get_base64_image(bg_path)
    logo_base64 = get_base64_image(logo_path)
    
    bg_url = f"data:image/jpeg;base64,{bg_base64}" if bg_base64 else ""
    logo_url = f"data:image/png;base64,{logo_base64}" if logo_base64 else ""

    css_style = """
        <style>
        .stApp {
            background-image: url('BG_URL_PLACEHOLDER');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        header { visibility: hidden; }
        
        div[data-testid="column"]:nth-of-type(2) {
            background: rgba(255, 255, 255, 0.4);
            backdrop-filter: blur(6px);
            -webkit-backdrop-filter: blur(6px);
            border: 2px solid #7C3AED !important;
            border-radius: 12px;
            padding: 30px 20px 40px 20px;
            box-shadow: 0px 8px 30px rgba(0, 0, 0, 0.4);
            text-align: center;
            margin-top: 5vh;
        }

        div[data-testid="stForm"] {
            background: rgba(148, 163, 184, 0.85);
            border: 2px solid #0EA5E9 !important;
            border-radius: 12px;
            padding: 20px;
            box-shadow: inset 0 0 10px rgba(255,255,255,0.2);
            margin-top: 15px;
        }

        div.stTextInput > div > div > input {
            background-color: rgba(241, 245, 249, 0.95) !important;
            border-radius: 20px !important;
            border: 1px solid #CBD5E1 !important;
            padding-left: 15px !important;
            color: #0F172A !important;
        }
        
        div[data-testid="stFormSubmitButton"] > button {
            border-radius: 20px !important;
            background-color: #F8FAFC !important;
            color: #0F172A !important;
            border: 1px solid #CBD5E1 !important;
            font-weight: 700 !important;
            margin-top: 10px;
        }
        div[data-testid="stFormSubmitButton"] > button:hover {
            background-color: #0EA5E9 !important;
            color: white !important;
            border-color: #0EA5E9 !important;
        }

        .custom-form-header {
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            border-bottom: 2px solid #475569;
            padding-bottom: 12px;
            margin-bottom: 20px;
        }
        .sign-in-text {
            color: #0F172A;
            font-weight: 800;
            font-size: 18px;
        }
        </style>
    """
    
    css_style = css_style.replace("BG_URL_PLACEHOLDER", bg_url)
    st.markdown(css_style, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1.2, 1.6, 1.2])
    
    with col2:
        header_html = f"""<div style="text-align: center; margin-bottom: 10px;">
            <div style="text-align: center; margin-bottom: 5px;">
                <img src="{logo_url}" width="300" style="filter: drop-shadow(0px 8px 10px rgba(0,0,0,0.5)); margin-bottom: 20px;">
            </div>
        </div>"""
        st.markdown(header_html, unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown("""
                <div class="custom-form-header">
                    <span class="sign-in-text" style="color: #0F172A; font-weight: 800; font-size: 30px;">Sign In</span>
                </div>
            """, unsafe_allow_html=True)
            
            user_input = st.text_input("Username", placeholder="👤 Username", label_visibility="collapsed")
            pass_input = st.text_input("Password", type="password", placeholder="  🔒   Password", label_visibility="collapsed")
            
            if st.form_submit_button("Login", use_container_width=True):
                handle_login(user_input, pass_input)

# --- MAIN SECURE DASHBOARD ---
else:
    # ==========================================
    # TOP HEADER BAR: CLOCK, DATE & BATTERY STATUS (WITH BACKGROUND COLOR)
    # ==========================================
    now_str = datetime.datetime.now().strftime("%B %d, %Y | %I:%M:%S %p")
    
    st.markdown(f"""
        <div style="background-color: #80FFFF; border: 1px solid #E2E8F0; padding: 12px 20px; border-radius: 12px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0px 2px 4px rgba(0,0,0,0.02); margin-bottom: 20px;">
            <div style="color: #475569; font-size: 20px;">
                📅 <b>System Time:</b> {now_str}
            </div>
            <div>
                <span style="background-color: #DCFCE7; color: #166534; padding: 5px 12px; border-radius: 19px; font-size: 20px; font-weight: 600;">
                    🔋 Node Battery: 94% (Stable)
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- HEADER SMS NOTIFICATION SIMULATOR ---
    active_device_sn = st.session_state.get("active_device_sn")
    if active_device_sn:
        latest_data = fetch_latest_data(active_device_sn)
        if latest_data:
            temp = latest_data.get('temperature', 0)
            ph = latest_data.get('ph', 0)
            turb = latest_data.get('turbidity', 0)
            
            alert_messages = []
            if temp > 33 or temp < 26: alert_messages.append(f"Temperature ({temp}°C)")
            if ph > 9.0 or ph < 6.5: alert_messages.append(f"pH Level ({ph})")
            if turb > 100: alert_messages.append(f"Turbidity ({turb} NTU)")
            
            if alert_messages:
                st.error(f"📱 **SMS ALERT TRIGGERED:** Critical conditions detected in {', '.join(alert_messages)}! Please intervene immediately.", icon="🚨")
    # Render the separated sidebar component
    sidebar.render(set_page_callback=set_page, logout_callback=handle_logout)

    # Route the current page to the correct view
    page = st.session_state.current_page

    if page == "Live Telemetry": 
        view_telemetry.render()
    elif page in ["Breeding Forecast", "AI Breeding Forecast"]: 
        view_forecast.render()
    elif page == "Network Overview": 
        view_admin_overview.render()
    elif page == "System Health":
        view_system_health.render()
    elif page == "Account Management": 
        view_account_management.render()
    elif page == "Telemetry Records": 
        view_records.render()
    elif page == "System Settings": 
        view_settings.render()