import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# Using the new API modules
from api.telemetry_api import fetch_history_data, fetch_latest_data, fetch_iso25010_performance
from api.device_api import fetch_devices

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
    
    if st.session_state.role == "admin":
        tab_telemetry, tab_iso = st.tabs(["📊 Pond Telemetry Masterlist", "⚡ ISO/IEC 25010 Performance Efficiency Logs"])
    else:
        tab_telemetry = st.container()
        tab_iso = None

    with tab_telemetry:
        # --- COMMON DATE FILTER ---
        st.markdown("### 📅 Filter Data by Date")
        col_date1, col_date2 = st.columns(2)
        start_date = col_date1.date_input("Start Date", datetime.date.today() - datetime.timedelta(days=7))
        end_date = col_date2.date_input("End Date", datetime.date.today())
        
        start_str = start_date.strftime("%Y-%m-%d 00:00:00")
        end_str = end_date.strftime("%Y-%m-%d 23:59:59")
        st.markdown("---")

        if st.session_state.role == "admin":
            devices = fetch_devices(st.session_state.user_id, st.session_state.role)
            st.markdown("### 🚨 Farmer Risk Ranking (Danger to Normal)")
            
            farmer_risks = []
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
                df_risk = pd.DataFrame(farmer_risks).sort_values(by="Risk Score", ascending=True)
                fig_risk = px.bar(
                    df_risk, x="Risk Score", y="Farmer", color="Status",
                    color_discrete_map={"Danger": "#EF4444", "Warning": "#F59E0B", "Normal": "#10B981"},
                    orientation='h', text="Status"
                )
                fig_risk.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=10, b=0), height=max(250, len(farmer_risks) * 40))
                st.plotly_chart(fig_risk, use_container_width=True, key="records_risk_chart")
            
            st.markdown("---")
            st.markdown("### 📋 Raw Masterlist Exporter")
            all_history = []
            
            with st.spinner("Compiling and filtering masterlist..."):
                for dev in devices:
                    history = fetch_history_data(dev['device_sn'], limit=500) # Increased limit for better exporting
                    if history:
                        for record in history:
                            record['Owner'] = f"Farmer {dev['owner_id']}"
                            record['Pond Name'] = dev['pond_name']
                            all_history.append(record)
                        
            if all_history:
                df = pd.DataFrame(all_history)
                df = df[["timestamp", "Owner", "Pond Name", "temperature", "ph", "turbidity", "water_level_cm"]].sort_values(by="timestamp", ascending=False)
                
                # Apply Date Filter
                mask = (df['timestamp'] >= start_str) & (df['timestamp'] <= end_str)
                filtered_df = df.loc[mask]

                if not filtered_df.empty:
                    csv = filtered_df.to_csv(index=False).encode('utf-8')
                    st.download_button(label="📥 Download Filtered Masterlist (CSV)", data=csv, file_name=f'pearl_network_masterlist_{start_date}_to_{end_date}.csv', mime='text/csv', type="primary")
                    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
                else:
                    st.info("No records found in the selected date range.")
                    
        else:
            active_device = st.session_state.get("active_device_sn", "PEARL-ESP32-001")
            st.markdown(f"### Data for Node: `{active_device}`")
            history = fetch_history_data(active_device, limit=500)
            
            if history:
                df = pd.DataFrame(history)[["timestamp", "temperature", "ph", "turbidity", "water_level_cm"]]
                
                # Apply Date Filter
                mask = (df['timestamp'] >= start_str) & (df['timestamp'] <= end_str)
                filtered_df = df.loc[mask]

                if not filtered_df.empty:
                    csv = filtered_df.to_csv(index=False).encode('utf-8')
                    st.download_button(label="📥 Export Filtered Data (CSV)", data=csv, file_name=f'{active_device}_telemetry_{start_date}_to_{end_date}.csv', mime='text/csv', type="primary")
                    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
                else:
                    st.info("No records found in the selected date range.")

    # =========================================================
    # ADMIN TAB 2: ISO/IEC 25010 PERFORMANCE EFFICIENCY LOGS
    # =========================================================
    if tab_iso is not None:
        with tab_iso:
            # (Keep your existing ISO tab code here exactly as it was)
            st.markdown("### ⚡ ISO/IEC 25010 Performance Efficiency Empirical Logs")
            st.caption(
                "Automatically captures real-time millisecond (`ms`) response latency across IoT ingestion, "
                "Prophet AI forecasting, Virtual Bio-Audits, and Dashboard queries for Chapter 4 statistical evaluation."
            )
            perf_logs = fetch_iso25010_performance(limit=300)
            if perf_logs:
                df_perf = pd.DataFrame(perf_logs)
                
                avg_overall = df_perf["execution_time_ms"].mean()
                df_ingest = df_perf[df_perf["operation_category"] == "IoT Telemetry Ingestion"]
                df_ai = df_perf[df_perf["operation_category"] == "Prophet AI Prediction"]
                df_dash = df_perf[df_perf["operation_category"] == "Dashboard Data Retrieval"]

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Overall Mean Response", f"{avg_overall:.2f} ms")
                m2.metric("Dashboard Query Latency", f"{df_dash['execution_time_ms'].mean():.2f} ms" if not df_dash.empty else "N/A")
                m3.metric("IoT Ingestion Latency", f"{df_ingest['execution_time_ms'].mean():.2f} ms" if not df_ingest.empty else "N/A")
                m4.metric("Prophet AI Forecast Latency", f"{df_ai['execution_time_ms'].mean():.2f} ms" if not df_ai.empty else "N/A")

                csv_perf = df_perf.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Export ISO/IEC 25010 Performance Benchmark Table (CSV)",
                    data=csv_perf,
                    file_name="iso25010_performance_efficiency_logs.csv",
                    mime="text/csv",
                    type="primary"
                )
                st.dataframe(df_perf, use_container_width=True, hide_index=True)
            else:
                st.info("Performance logs will populate automatically as you navigate the dashboard.")