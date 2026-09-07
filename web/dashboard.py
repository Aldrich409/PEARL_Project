import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import data_fetcher
import node_selector
from views import view_telemetry, view_forecast, view_records, view_settings, view_admin_overview, view_account_management

# =========================================================
# --- PAGE CONFIGURATION ---
# =========================================================
st.set_page_config(page_title="PEARL Dashboard", page_icon="🐟", layout="wide")

# =========================================================
# --- SESSION STATE INITIALIZATION ---
# =========================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.active_device_sn = "PEARL-ESP32-001"
    
if "current_page" not in st.session_state:
    st.session_state.current_page = "Live Telemetry"

def set_page(page_name):
    """Callback function to handle sidebar navigation routing."""
    st.session_state.current_page = page_name

def handle_login(username, password):
    """Authenticates the user via the FastAPI backend."""
    user_data = data_fetcher.authenticate_user(username, password)
    if user_data:
        st.session_state.logged_in = True
        st.session_state.user_id = user_data["id"]
        st.session_state.username = user_data["username"]
        st.session_state.role = user_data["role"]
        st.session_state.current_page = "Live Telemetry"
        
        # Fetch devices to set the initial active node
        devices = data_fetcher.fetch_devices(user_data["id"], user_data["role"])
        if devices:
            st.session_state.active_device_sn = devices[0]["device_sn"]
        st.rerun()
    else:
        st.error("Invalid credentials or backend offline. Please try again.")

def handle_logout():
    """Clears session state and returns to the login screen."""
    st.session_state.clear()
    st.rerun()

# =========================================================
# --- LOGIN SCREEN ---
# =========================================================
if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col_spacer1, col_box, col_spacer2 = st.columns([1, 1.5, 1])
    with col_box:
        # Load the pearls_logo.png if it exists, otherwise fallback to an emoji
        if os.path.exists("pearls_logo.png"):
            st.image("pearls_logo.png", width=80)
        else:
            st.markdown("<h1 style='text-align: center; font-size: 3rem;'>🐟</h1>", unsafe_allow_html=True)
            
        st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>P.E.A.R.L. System</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748B;'>Predictive Environmental Analytics for Real-Time Aquaculture Logging</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.subheader("Sign In")
            user_input = st.text_input("Username")
            pass_input = st.text_input("Password", type="password")
            
            if st.form_submit_button("Login to Dashboard", use_container_width=True):
                handle_login(user_input, pass_input)

# =========================================================
# --- MAIN SECURE DASHBOARD ---
# =========================================================
else:
    # --- SIDEBAR: HEADER ---
    st.sidebar.title("🐟 PEARL System")
    st.sidebar.markdown(f"**User:** {st.session_state.username} ({st.session_state.role.capitalize()})")
    st.sidebar.markdown("---")

    # --- SIDEBAR: TOP NAVIGATION ---
    st.sidebar.button("📊 Live Telemetry", on_click=set_page, args=("Live Telemetry",), use_container_width=True)
    st.sidebar.button("🤖 Breeding Forecast", on_click=set_page, args=("Breeding Forecast",), use_container_width=True)
    
    if st.session_state.role == "admin":
        st.sidebar.button("🌐 Network Overview", on_click=set_page, args=("Network Overview",), use_container_width=True)
        
    st.sidebar.button("📂 Telemetry Records", on_click=set_page, args=("Telemetry Records",), use_container_width=True)

    # --- SIDEBAR: MIDDLE NODE SELECTOR ---
    if st.session_state.role == "admin":
        st.sidebar.markdown("---")
        node_selector.render()

    # --- SIDEBAR: BOTTOM UTILITIES ---
    st.sidebar.markdown("<br>" * 8, unsafe_allow_html=True)
    st.sidebar.markdown("---")
    st.sidebar.markdown("#### ⚙️ SYSTEM")
    
    # Account Management is now accessible to EVERYONE (Farmers see profile edits, Admins see full manager)
    st.sidebar.button("👥 Account Management", on_click=set_page, args=("Account Management",), use_container_width=True)
    st.sidebar.button("⚙️ System Settings", on_click=set_page, args=("System Settings",), use_container_width=True)
    st.sidebar.button("🚪 Logout", on_click=handle_logout, use_container_width=True, type="primary")

    # =========================================================
    # --- PAGE ROUTING CONTROLLER ---
    # =========================================================
    page = st.session_state.current_page
    
    if page == "Live Telemetry": 
        view_telemetry.render()
    elif page == "Breeding Forecast": 
        view_forecast.render()
    elif page == "Network Overview": 
        view_admin_overview.render()
    elif page == "Account Management": 
        view_account_management.render()
    elif page == "Telemetry Records": 
        view_records.render()
    elif page == "System Settings": 
        view_settings.render()