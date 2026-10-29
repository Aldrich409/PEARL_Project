import streamlit as st
import data_fetcher

def render():
    st.sidebar.markdown("📡 **ACTIVE MONITORING NODE**")
    devices = data_fetcher.fetch_devices(st.session_state.user_id, st.session_state.role)
    
    if devices:
        if st.session_state.role == "admin":
            # Admin sees the Farmer ID to easily identify pond ownership
            device_options = {f"Farmer {dev['owner_id']} - {dev['pond_name']}": dev['device_sn'] for dev in devices}
        else:
            # Regular farmer just sees their pond name and device serial
            device_options = {f"{dev['pond_name']} ({dev['device_sn']})": dev['device_sn'] for dev in devices}
            
        selected_label = st.sidebar.selectbox(
            "Select Pond Node (Pumili ng Palaisdaan):",
            list(device_options.keys()),
            key="node_selectbox"
        )
        st.session_state.active_device_sn = device_options[selected_label]
    else:
        st.sidebar.warning("No devices found.")