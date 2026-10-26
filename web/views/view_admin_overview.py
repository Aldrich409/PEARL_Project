import streamlit as st
from data_fetcher import fetch_devices, fetch_latest_data

def calculate_risk_score(temp, ph, turb, dev=None):
    """Calculates the environmental risk score using the device's dynamic fish thresholds."""
    t_n_min = float(dev.get("temp_norm_min", 26.0)) if dev else 26.0
    t_n_max = float(dev.get("temp_norm_max", 33.0)) if dev else 33.0
    t_d_min = float(dev.get("temp_danger_min", 24.0)) if dev else 24.0
    t_d_max = float(dev.get("temp_danger_max", 35.0)) if dev else 35.0

    p_n_min = float(dev.get("ph_norm_min", 7.0)) if dev else 7.0
    p_n_max = float(dev.get("ph_norm_max", 8.5)) if dev else 8.5
    p_d_min = float(dev.get("ph_danger_min", 6.5)) if dev else 6.5
    p_d_max = float(dev.get("ph_danger_max", 9.0)) if dev else 9.0

    tb_n_max = float(dev.get("turb_norm_max", 80.0)) if dev else 80.0
    tb_d_max = float(dev.get("turb_danger_max", 100.0)) if dev else 100.0

    score = 0
    if temp < t_d_min or temp > t_d_max: score += 50
    elif temp < t_n_min or temp > t_n_max: score += 25
    
    if ph < p_d_min or ph > p_d_max: score += 50
    elif ph < p_n_min or ph > p_n_max: score += 25
    
    if turb > tb_d_max: score += 50
    elif turb > tb_n_max: score += 25
    
    return min(score, 100)

def render():
    st.title("🌐 Network Overview")
    st.markdown("<p style='color: #64748B; font-size: 13px; font-style: italic; margin-top: -15px;'>Kabuuang estado ng lahat ng monitoring nodes</p>", unsafe_allow_html=True)
    
    devices = fetch_devices(st.session_state.get("user_id", 1), st.session_state.get("role", "admin"))
    
    if not devices:
        st.warning("No active devices found in the network.")
        return

    # Header Row
    c1, c2, c3, c4, c5 = st.columns([1, 1.5, 2.2, 3, 2])
    c1.markdown("**Status**")
    c2.markdown("**Owner**")
    c3.markdown("**Pond & Species**")
    c4.markdown("**Latest Readings**")
    c5.markdown("**Pond Standing**")
    st.divider()

    with st.spinner("Fetching telemetry across all nodes..."):
        for dev in devices:
            latest = fetch_latest_data(dev['device_sn'])
            fish_type = dev.get('fish_type', 'Tilapia')
            
            c1, c2, c3, c4, c5 = st.columns([1, 1.5, 2.2, 3, 2])
            
            if latest:
                c1.markdown("🟢 **Online**")
                temp = latest.get('temperature', 0)
                ph = latest.get('ph', 0)
                turb = latest.get('turbidity', 0)
                
                c4.markdown(f"**Temp:** {temp:.1f} °C | **pH:** {ph:.2f} | **Turb:** {turb:.1f} NTU")
                
                risk = calculate_risk_score(temp, ph, turb, dev)
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
            c3.write(f"{dev['pond_name']} ({fish_type})")
            c5.markdown(standing_html, unsafe_allow_html=True)
            
            st.markdown("---")