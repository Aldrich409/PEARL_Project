# ==============================================================================
# FILE 1: dashboard.py (Main Streamlit Entry Point)
# ==============================================================================
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import data_fetcher
import node_selector
from views import view_telemetry, view_forecast, view_records, view_settings, view_admin_overview, view_account_management

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="PEARL Dashboard", 
    page_icon="🐟", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- GLOBAL OCEAN THEME CSS (LIGHT/DARK COMPATIBLE) ---
st.markdown("""
    <style>
    /* 🛑 HIDE THE SIDEBAR CLOSE BUTTON TO PREVENT HIDING */
    [data-testid="stSidebarCollapseButton"] {
        display: none !important;
    }

    /* SIDEBAR TOGGLE (Visible only if auto-collapsed on mobile screens) */
    [data-testid="collapsedControl"] {
        background-color: #0284C7 !important; 
        border-radius: 50% !important;
        margin-top: 10px !important;
        margin-left: 10px !important;
        box-shadow: 0px 4px 10px rgba(2, 132, 199, 0.4) !important;
        z-index: 999999 !important;
    }
    [data-testid="collapsedControl"] svg {
        fill: #FFFFFF !important; 
    }

    /* METRIC CARDS - Transparent overlays adapt to Light/Dark automatically */
    div[data-testid="stMetric"] {
        background-color: rgba(14, 165, 233, 0.05) !important;
        border: 1px solid rgba(14, 165, 233, 0.2) !important;
        border-radius: 10px !important;
        padding: 15px !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05) !important;
        transition: transform 0.2s ease, border-color 0.2s ease !important;
    }
    div[data-testid="stMetric"]:hover { 
        transform: translateY(-2px); 
        border-color: rgba(14, 165, 233, 0.6) !important;
    }
    div[data-testid="stMetricLabel"] > label {
        font-weight: 700 !important;
        font-size: 0.75rem !important; 
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* CONTAINER BORDERS */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid rgba(14, 165, 233, 0.2) !important;
        border-radius: 12px !important;
        background-color: rgba(14, 165, 233, 0.01) !important;
    }

    /* UNIVERSAL SUBTEXT STYLING */
    .tagalog-subtext {
        color: #0EA5E9 !important;
        font-size: 13px !important; 
        font-style: italic !important;
        margin-top: -10px !important; 
        margin-bottom: 15px !important;
    }

    /* HIDE DEFAULT STREAMLIT TOOLBAR */
    .stAppDeployButton, .stDeployButton { display: none !important; }
    
    /* COMPACT SIDEBAR */
    [data-testid="stSidebar"] { padding-top: 0rem; border-right: 1px solid rgba(14, 165, 233, 0.2) !important; }
    [data-testid="stSidebar"] > div:first-child { padding-top: 2rem !important; padding-bottom: 1rem !important; }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.active_device_sn = "PEARL-ESP32-001"

if "current_page" not in st.session_state:
    st.session_state.current_page = "Live Telemetry"

def set_page(page_name):
    st.session_state.current_page = page_name

def handle_login(username, password):
    user_data = data_fetcher.authenticate_user(username, password)
    if user_data:
        st.session_state.logged_in = True
        st.session_state.user_id = user_data["id"]
        st.session_state.username = user_data["username"]
        st.session_state.role = user_data["role"]
        st.session_state.current_page = "Live Telemetry"

        devices = data_fetcher.fetch_devices(user_data["id"], user_data["role"])
        if devices:
            st.session_state.active_device_sn = devices[0]["device_sn"]
        st.rerun()
    else:
        st.error("Invalid credentials or backend offline. Please try again.")

def handle_logout():
    st.session_state.clear()
    st.rerun()

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)

    col_spacer1, col_box, col_spacer2 = st.columns([1, 1.5, 1])
    with col_box:
        if os.path.exists("pearl_logo(1).png"):
            # Nested columns to perfectly center the logo
            logo_left, logo_center, logo_right = st.columns([1, 2, 1])
            with logo_center:
                st.image("pearl_logo(1).png", use_container_width=True)
        else:
            st.markdown("<h1 style='text-align: center; font-size: 3rem;'>🐟</h1>", unsafe_allow_html=True)

        st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>P.E.A.R.L. System</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #0EA5E9;'>Predictive Environmental Analytics for Real-Time Aquaculture Logging</p>", unsafe_allow_html=True)

        with st.form("login_form"):
            st.subheader("Sign In")
            user_input = st.text_input("Username")
            pass_input = st.text_input("Password", type="password")

            if st.form_submit_button("Login to Dashboard", use_container_width=True):
                handle_login(user_input, pass_input)

# --- MAIN SECURE DASHBOARD ---
else:
    st.sidebar.title("PEARL System")
    st.sidebar.markdown(f"**User:** {st.session_state.username} ({st.session_state.role.capitalize()})")
    st.sidebar.markdown("---")

    st.sidebar.button("📊 Live Telemetry", on_click=set_page, args=("Live Telemetry",), use_container_width=True)
    st.sidebar.button("🤖 Breeding Forecast", on_click=set_page, args=("Breeding Forecast",), use_container_width=True)

    if st.session_state.role == "admin":
        st.sidebar.button("🌐 Network Overview", on_click=set_page, args=("Network Overview",), use_container_width=True)

    st.sidebar.button("📂 Telemetry Records", on_click=set_page, args=("Telemetry Records",), use_container_width=True)

    if st.session_state.role == "admin":
        st.sidebar.markdown("---")
        node_selector.render()

    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    st.sidebar.markdown("#### ⚙️ SYSTEM")

    st.sidebar.button("👥 Account Management", on_click=set_page, args=("Account Management",), use_container_width=True)
    st.sidebar.button("⚙️ System Settings", on_click=set_page, args=("System Settings",), use_container_width=True)
    st.sidebar.button("🚪 Logout", on_click=handle_logout, use_container_width=True, type="primary")

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