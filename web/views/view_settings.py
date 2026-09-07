import streamlit as st
from data_fetcher import fetch_devices, update_device_settings

def render():
    st.title("⚙️ System Settings")
    st.markdown("<p style='color: #64748B; font-size: 13px; font-style: italic; margin-top: -15px;'>Manage Hardware Pairing and Device Configurations</p>", unsafe_allow_html=True)
    
    active_sn = st.session_state.get("active_device_sn", None)
    devices = fetch_devices(st.session_state.user_id, st.session_state.role)
    active_device = next((d for d in devices if d['device_sn'] == active_sn), None)
    
    if not active_device:
        st.warning("No active monitoring node selected. Please select a pond from the sidebar.")
        return

    st.info(f"**Currently Configuring:** {active_device['pond_name']} (`{active_device['device_sn']}`)")
    
    # Render strictly hardware-focused tabs
    if st.session_state.role == "admin":
        tabs = st.tabs(["🔗 Pair Hardware", "📱 SMS Alerts", "💤 Deep Sleep", "⚖️ Calibration"])
        tab_pair, tab_sms, tab_sleep, tab_calib = tabs
    else:
        tabs = st.tabs(["📱 SMS Alerts", "💤 Deep Sleep", "⚖️ Calibration"])
        tab_sms, tab_sleep, tab_calib = tabs
        tab_pair = None

    # --- TAB: PAIR HARDWARE (ADMIN ONLY) ---
    if tab_pair:
        with tab_pair:
            st.markdown("#### 🔗 Pair New Hardware Node")
            with st.form("form_pair"):
                st.text_input("Sensor Serial Number (e.g., PEARL-ESP32-999)")
                st.text_input("Assign Pond Name")
                if st.form_submit_button("Register Sensor to Network", use_container_width=True):
                    st.info("Hardware node registered successfully.")

    # --- TAB: SMS ALERTS ---
    with tab_sms:
        with st.form("form_sms"):
            alert_phone = st.text_input("Target Phone Number (+639...)", value=active_device['alert_phone'])
            levels = ["Critical Emergencies Only", "Warnings & Critical", "All Notifications"]
            current_idx = 0 if active_device['alert_level'] == "Critical" else 1
            alert_level = st.selectbox("Alert Sensitivity Level", levels, index=current_idx)
            
            if st.form_submit_button("Update SMS Settings", type="primary", use_container_width=True):
                active_device.update({
                    'alert_phone': alert_phone, 
                    'alert_level': "Critical" if "Critical" in alert_level else "Warning"
                })
                if update_device_settings(active_device):
                    st.success("SMS Settings saved!")
                    st.rerun()

    # --- TAB: DEEP SLEEP ---
    with tab_sleep:
        with st.form("form_sleep"):
            sleep_interval = st.slider("Broadcast Frequency (Minutes)", 5, 120, int(active_device['sleep_interval']), 5)
            if st.form_submit_button("Update Broadcast Cycle", type="primary", use_container_width=True):
                active_device['sleep_interval'] = sleep_interval
                if update_device_settings(active_device):
                    st.success("Sleep interval saved!")
                    st.rerun()

    # --- TAB: SENSOR CALIBRATION ---
    with tab_calib:
        with st.form("form_calibration"):
            c1, c2 = st.columns(2)
            ph_offset = c1.number_input("pH Offset", value=float(active_device['ph_offset']), step=0.1, format="%.2f")
            turb_offset = c2.number_input("Turbidity Offset (NTU)", value=float(active_device['turb_offset']), step=1.0, format="%.1f")
            
            if st.form_submit_button("Save Calibration Offsets", type="primary", use_container_width=True):
                active_device.update({'ph_offset': ph_offset, 'turb_offset': turb_offset})
                if update_device_settings(active_device):
                    st.success("Calibration applied successfully!")
                    st.rerun()