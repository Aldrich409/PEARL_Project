import streamlit as st
import pandas as pd
import plotly.express as px
from data_fetcher import fetch_history_data, fetch_devices, fetch_latest_data

def calculate_risk_score(temp, ph, turb):
    score = 0
    if temp < 26 or temp > 33: score += 40
    elif temp < 28 or temp > 31: score += 20
    
    if ph < 6.5 or ph > 9.0: score += 50
    elif ph < 7.0 or ph > 8.5: score += 20
    
    if turb > 100: score += 40
    elif turb > 80: score += 20
    
    return min(score, 100)

def render():
    st.title("📂 Telemetry Records & Analytics")
    
    # ==========================================
    # ADMIN VIEW: Ranking & Masterlist Exporter
    # ==========================================
    if st.session_state.role == "admin":
        devices = fetch_devices(st.session_state.user_id, st.session_state.role)
        
        # 1. FARMER RANKING (DANGER TO NORMAL)
        st.markdown("### 🚨 Farmer Risk Ranking (Danger to Normal)")
        st.markdown("<p style='color: #64748B; font-style: italic;'>Identify which farmers require immediate intervention based on latest sensor data.</p>", unsafe_allow_html=True)
        
        farmer_risks = []
        with st.spinner("Calculating current risk levels across the network..."):
            for dev in devices:
                latest = fetch_latest_data(dev['device_sn'])
                if latest:
                    risk = calculate_risk_score(latest.get('temperature', 0), latest.get('ph', 0), latest.get('turbidity', 0))
                    farmer_risks.append({
                        "Farmer": f"Farmer {dev['owner_id']} ({dev['pond_name']})",
                        "Risk Score": risk,
                        "Status": "Danger" if risk >= 50 else "Warning" if risk >= 20 else "Normal"
                    })
        
        if farmer_risks:
            # Sort so Danger (highest score) is at the top
            df_risk = pd.DataFrame(farmer_risks).sort_values(by="Risk Score", ascending=True)
            
            color_map = {"Danger": "#EF4444", "Warning": "#F59E0B", "Normal": "#10B981"}
            fig_risk = px.bar(
                df_risk, x="Risk Score", y="Farmer", color="Status",
                color_discrete_map=color_map, orientation='h', text="Status"
            )
            fig_risk.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                margin=dict(l=0, r=0, t=10, b=0), height=max(250, len(farmer_risks) * 40),
                xaxis=dict(range=[0, 100], title="Risk Severity (%)"), yaxis=dict(title="")
            )
            st.plotly_chart(fig_risk, use_container_width=True, key="records_risk_chart")
        
        st.markdown("---")
        
        # 2. RAW MASTERLIST EXPORTER
        st.markdown("### 📋 Raw Masterlist Exporter")
        all_history = []
        with st.spinner("Compiling global database records..."):
            for dev in devices:
                history = fetch_history_data(dev['device_sn'], limit=100)
                if history:
                    for record in history:
                        record['Owner'] = f"Farmer {dev['owner_id']}"
                        record['Pond Name'] = dev['pond_name']
                        all_history.append(record)
                        
        if all_history:
            df = pd.DataFrame(all_history)
            # Reorganize columns for Excel
            df = df[["timestamp", "Owner", "Pond Name", "temperature", "ph", "turbidity", "water_level_cm"]]
            df = df.sort_values(by="timestamp", ascending=False)
            
            # Export to Excel/CSV Button
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Masterlist (Excel/CSV)",
                data=csv,
                file_name='pearl_network_masterlist.csv',
                mime='text/csv',
                type="primary"
            )
            
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No historical logs found in the database.")
            
    # ==========================================
    # FARMER VIEW: Personal Records Exporter
    # ==========================================
    else:
        active_device = st.session_state.get("active_device_sn", "PEARL-ESP32-001")
        st.markdown("### 📋 Your Telemetry Records")
        
        history = fetch_history_data(active_device, limit=200)
        if history:
            df = pd.DataFrame(history)
            df = df[["timestamp", "temperature", "ph", "turbidity", "water_level_cm"]]
            
            # Export Button for Farmers
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Data (Excel/CSV)",
                data=csv,
                file_name=f'{active_device}_telemetry_log.csv',
                mime='text/csv',
                type="primary"
            )
            
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No historical logs found for your pond.")