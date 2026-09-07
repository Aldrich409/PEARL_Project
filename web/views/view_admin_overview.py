import streamlit as st
from data_fetcher import fetch_devices, fetch_latest_data

def calculate_risk_score(temp, ph, turb):
    """Calculates the environmental risk score to determine Pond Standing."""
    score = 0
    if temp < 26 or temp > 33: score += 40
    elif temp < 28 or temp > 31: score += 20
    
    if ph < 6.5 or ph > 9.0: score += 50
    elif ph < 7.0 or ph > 8.5: score += 20
    
    if turb > 100: score += 40
    elif turb > 80: score += 20
    
    return min(score, 100)

def render():
    st.title("🌐 Network Overview")
    st.markdown("<p style='color: #64748B; font-size: 13px; font-style: italic; margin-top: -15px;'>Kabuuang estado ng lahat ng monitoring nodes</p>", unsafe_allow_html=True)
    
    # Fetch all devices for the Admin Master View
    devices = fetch_devices(st.session_state.get("user_id", 1), st.session_state.get("role", "admin"))
    
    if not devices:
        st.warning("No active devices found in the network.")
        return

    # Create the Header Row
    c1, c2, c3, c4, c5 = st.columns([1, 1.5, 2, 3, 2])
    c1.markdown("**Status**")
    c2.markdown("**Owner**")
    c3.markdown("**Pond Name**")
    c4.markdown("**Latest Readings**")
    c5.markdown("**Pond Standing**")
    st.divider()

    # Loop through devices and create an interactive row for each
    with st.spinner("Fetching telemetry across all nodes..."):
        for dev in devices:
            latest = fetch_latest_data(dev['device_sn'])
            
            c1, c2, c3, c4, c5 = st.columns([1, 1.5, 2, 3, 2])
            
            if latest:
                c1.markdown("🟢 **Online**")
                temp = latest.get('temperature', 0)
                ph = latest.get('ph', 0)
                turb = latest.get('turbidity', 0)
                
                # Display all 3 critical parameters in the readings column
                c4.markdown(f"**Temp:** {temp:.1f} °C | **pH:** {ph:.2f} | **Turb:** {turb:.1f} NTU")
                
                # Evaluate the Risk Score to determine Color Coding
                risk = calculate_risk_score(temp, ph, turb)
                if risk >= 50:
                    standing_html = """
                    <div style='background-color: #FEE2E2; color: #991B1B; padding: 6px 10px; border-radius: 6px; font-weight: 700; border: 1px solid #EF4444; text-align: center;'>
                        🚨 Danger
                    </div>
                    """
                elif risk >= 20:
                    standing_html = """
                    <div style='background-color: #FEF3C7; color: #92400E; padding: 6px 10px; border-radius: 6px; font-weight: 700; border: 1px solid #F59E0B; text-align: center;'>
                        ⚠️ Warning
                    </div>
                    """
                else:
                    standing_html = """
                    <div style='background-color: #D1FAE5; color: #065F46; padding: 6px 10px; border-radius: 6px; font-weight: 700; border: 1px solid #10B981; text-align: center;'>
                        ✅ Normal
                    </div>
                    """
            else:
                c1.markdown("🔴 **Offline**")
                c4.markdown("*No recent data*")
                standing_html = """
                <div style='background-color: #F1F5F9; color: #64748B; padding: 6px 10px; border-radius: 6px; font-weight: 700; border: 1px solid #CBD5E1; text-align: center;'>
                    Unknown
                </div>
                """
                
            c2.write(f"Farmer {dev['owner_id']}")
            c3.write(dev['pond_name'])
            
            # Display the color-coded standing badge instead of the button
            c5.markdown(standing_html, unsafe_allow_html=True)
            
            st.markdown("---")