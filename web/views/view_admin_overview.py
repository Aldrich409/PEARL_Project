import streamlit as st
import pandas as pd
import plotly.express as px

# Using the new API modules
from api.device_api import fetch_devices
from api.telemetry_api import fetch_latest_data

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
    elif ph < p_n_min or p_n_max < ph: score += 25
    
    if turb > tb_d_max: score += 50
    elif turb > tb_n_max: score += 25
    
    return min(score, 100)

def render():
    st.title("🌐 PEARL Network Command Center")
    st.markdown("Bird's-eye view of all registered nodes and their current operational status across the agricultural network.")

    devices = fetch_devices(st.session_state.get("user_id", 1), st.session_state.get("role", "admin"))
    if not devices:
        st.warning("No devices found on the network.")
        return
        
    # --- AGGREGATE NETWORK DATA ---
    network_data = []
    total_fish = 0
    total_volume = 0
    alerts_active = 0
    
    with st.spinner("Scanning active nodes..."):
        for dev in devices:
            latest = fetch_latest_data(dev['device_sn'])
            total_fish += dev.get('fish_count', 0)
            
            # Calculate Volume (L x W x D)
            length = float(dev.get('length', 0))
            width = float(dev.get('width', 0))
            depth = float(dev.get('depth', 0))
            total_volume += (length * width * depth)
            
            if latest:
                temp = latest.get('temperature', 0)
                ph = latest.get('ph', 0)
                turb = latest.get('turbidity', 0)
                
                risk = calculate_risk_score(temp, ph, turb, dev)
                
                status = "Stable"
                color = "🟢"
                if risk >= 50:
                    status = "Danger"
                    color = "🔴"
                    alerts_active += 1
                elif risk >= 20:
                    status = "Warning"
                    color = "🟠"
                    alerts_active += 1
                    
                network_data.append({
                    "Indicator": color,
                    "Farmer": f"Farmer {dev['owner_id']}",
                    "Pond Name": dev['pond_name'],
                    "Location": dev.get('location', 'N/A'),
                    "Device SN": dev['device_sn'],
                    "Temp (°C)": temp,
                    "pH": ph,
                    "Turbidity": turb,
                    "Status": status
                })
            else:
                 network_data.append({
                    "Indicator": "⚪",
                    "Farmer": f"Farmer {dev['owner_id']}",
                    "Pond Name": dev['pond_name'],
                    "Location": dev.get('location', 'N/A'),
                    "Device SN": dev['device_sn'],
                    "Temp (°C)": None, "pH": None, "Turbidity": None,
                    "Status": "Offline"
                })

    # --- TOP LEVEL METRICS ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Active Nodes", f"{len([d for d in network_data if d['Status'] != 'Offline'])} / {len(devices)}")
    c2.metric("Total Managed Volume", f"{total_volume:,.1f} m³")
    c3.metric("Total Monitored Fish", f"{total_fish:,}")
    c4.metric("Active Alerts", str(alerts_active), delta_color="inverse", delta=f"{alerts_active} Attention Needed" if alerts_active > 0 else "Normal")

    st.divider()

    # --- VISUALIZATIONS ---
    if network_data:
        df = pd.DataFrame(network_data)
        
        col_chart1, col_chart2 = st.columns([1, 1])
        
        with col_chart1:
            st.markdown("### 📊 Network Health Status")
            health_counts = df['Status'].value_counts().reset_index()
            health_counts.columns = ['Status', 'Count']
            color_map = {"Stable": "#10B981", "Warning": "#F59E0B", "Danger": "#EF4444", "Offline": "#94A3B8"}
            
            fig = px.pie(health_counts, values='Count', names='Status', hole=0.6, color='Status', color_discrete_map=color_map)
            fig.update_layout(margin=dict(l=0, r=0, t=20, b=0), height=300, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
            
        with col_chart2:
            st.markdown("### 🌡️ Temperature vs pH Scatter Plot")
            active_df = df[df['Status'] != 'Offline']
            if not active_df.empty:
                fig_scatter = px.scatter(active_df, x='Temp (°C)', y='pH', color='Status', 
                                         hover_name='Farmer', hover_data=['Pond Name', 'Device SN'],
                                         color_discrete_map=color_map, size_max=60)
                # Add default optimal ranges box
                fig_scatter.add_shape(type="rect", x0=26, y0=7.0, x1=33, y1=8.5, line=dict(color="green", width=2, dash="dash"), fillcolor="rgba(16, 185, 129, 0.1)")
                fig_scatter.update_layout(margin=dict(l=0, r=0, t=20, b=0), height=300)
                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.info("No active data for scatter plot.")

        st.markdown("### 🗃️ Active Nodes Data Matrix")
        st.dataframe(df, use_container_width=True, hide_index=True)