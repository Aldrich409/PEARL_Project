import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
from data_fetcher import fetch_latest_data, fetch_history_data, fetch_devices
import os

def fetch_current_weather():
    lat, lon = 14.5264, 121.1558 
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m&timezone=Asia%2FManila"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json().get("current", {})
    except Exception:
        pass
    return None

def get_weather_description(code):
    if code == 0: return "Clear sky (Maaliwalas)"
    if code in [1, 2, 3]: return "Partly cloudy (Maulap)"
    if code in [45, 48]: return "Fog/Rime (Makapal na Ulap)"
    if code in [51, 53, 55, 56, 57]: return "Drizzle (Ambon)"
    if code in [61, 63, 65, 66, 67]: return "Rain (Ulan)"
    if code in [80, 81, 82]: return "Showers (Paiba-ibang Ulan)"
    if code in [95, 96, 99]: return "Thunderstorm (Kumikidlat)"
    return "Overcast (Maulap)"

def evaluate_environment(temp, ph, turb):
    if turb > 100:
        return "error", "CLASSIFICATION: High Algal Bloom Risk (PANGANIB: Sobrang Labo ng Tubig)"
    if ph < 6.5 or ph > 9.0:
        return "error", "CLASSIFICATION: Critical Water Warning (PANGANIB: Mataas na Asido o Lason sa Tubig)"
    if temp < 24 or temp > 35:
        return "error", "CLASSIFICATION: Extreme Temperature (PANGANIB: Sobrang Init o Lamig ng Tubig)"

    if turb > 80:
        return "warning", "CLASSIFICATION: Approaching High Turbidity (BABALA: Nagsisimulang Lumabo ang Tubig)"
    if ph < 7.0 or ph > 8.5:
        return "warning", "CLASSIFICATION: pH Level Imbalance (BABALA: Nagbabago ang Antas ng pH)"
    if temp < 26 or temp > 33:
        return "warning", "CLASSIFICATION: Temperature Stress (BABALA: Hindi Maganda ang Temperatura)"

    if 28 <= temp <= 31 and 7.0 <= ph <= 8.5 and turb <= 80:
        return "success", "CLASSIFICATION: Optimal Breeding (Magandang Panahon sa Pagpaparami)"

    return "info", "CLASSIFICATION: System Stable (Maayos ang Kalagayan ng Tubig)"

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
    active_device_sn = st.session_state.get("active_device_sn", None)
    if not active_device_sn:
        st.warning("No active node selected in the sidebar.")
        return

    devices = fetch_devices(st.session_state.user_id, st.session_state.role)
    active_device = next((d for d in devices if d['device_sn'] == active_device_sn), None)

    latest = fetch_latest_data(active_device_sn)
    history = fetch_history_data(active_device_sn, limit=50)

    if not active_device:
        st.error("Device configuration not found.")
        return

    col_logo, col_title = st.columns([1, 6])
    with col_logo:
        if os.path.exists("pearl_logo(1).png"):
            st.image("pearl_logo(1).png", width=110)
        else:
            st.markdown("<h1 style='text-align: center; font-size: 2.5rem; margin-top: 0;'>🐟</h1>", unsafe_allow_html=True)

    with col_title:
       with col_title:
        # #0284C7 is a deep Ocean Blue for the main title
        st.markdown(f"<h2 style='margin-bottom: 0px; color: #0284C7;'>P.E.A.R.L. System Dashboard</h2>", unsafe_allow_html=True)
        
        # #0EA5E9 is a lighter Tropical Ocean Blue for the subtext
        st.markdown(f"<p class='tagalog-subtext' style='color: #0EA5E9; font-weight: 500;'>Predictive Environmental Analytics for Real-Time Aquaculture Logging</p>", unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### 🌤️ Local Weather Update: **Angono, Rizal**")
    st.markdown("<p class='tagalog-subtext'>Kasalukuyang Panahon sa Labas ng Palaisdaan</p>", unsafe_allow_html=True)

    weather_data = fetch_current_weather()
    if weather_data:
        t_air = weather_data.get('temperature_2m', '--')
        hum = weather_data.get('relative_humidity_2m', '--')
        wind = weather_data.get('wind_speed_10m', '--')
        w_code = weather_data.get('weather_code', 0)
        cond = get_weather_description(w_code)

        w1, w2, w3, w4 = st.columns(4)
        w1.metric("Air Temp (Temperatura)", f"{t_air} °C")
        w2.metric("Condition (Panahon)", cond.split(" (")[0])
        w3.metric("Humidity (Alinsangan)", f"{hum} %")
        w4.metric("Wind Speed (Hangin)", f"{wind} km/h")
    else:
        st.info("No weather data available right now.")

    st.markdown("---")

    col_chart, col_live = st.columns([1.6, 1])

    with col_chart:
        with st.container(border=True):
            st.markdown(f"### 📈 Environmental Trend Analytics: **{active_device['pond_name']}**")
            st.markdown("<p class='tagalog-subtext'>Kasaysayan ng Datos ng Palaisdaan</p>", unsafe_allow_html=True)

            if history:
                df = pd.DataFrame(history)
                df['timestamp'] = pd.to_datetime(df['timestamp'])

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df['timestamp'], y=df['temperature'], name='Temp (°C)', fill='tozeroy', mode='lines', line=dict(color='rgba(245, 158, 11, 0.8)', width=2, shape='spline')))
                fig.add_trace(go.Scatter(x=df['timestamp'], y=df['turbidity'], name='Turbidity (NTU)', fill='tozeroy', mode='lines', line=dict(color='rgba(2, 132, 199, 0.8)', width=2, shape='spline')))
                fig.add_trace(go.Scatter(x=df['timestamp'], y=df['water_level_cm'], name='Level (cm)', fill='tozeroy', mode='lines', line=dict(color='rgba(14, 165, 233, 0.8)', width=2, shape='spline')))
                fig.add_trace(go.Scatter(x=df['timestamp'], y=df['ph'], name='pH Level', fill='tozeroy', mode='lines', line=dict(color='rgba(16, 185, 129, 0.8)', width=2, shape='spline')))

                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', 
                    plot_bgcolor='rgba(0,0,0,0)', 
                    margin=dict(l=0, r=0, t=10, b=0), height=300,
                    hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig, use_container_width=True, theme="streamlit", key=f"trend_{active_device_sn}")
            else:
                st.info("No historical data available for this node.")

    with col_live:
        with st.container(border=True):
            st.markdown("### 📡 Live Sensor Readings & AI Engine")

            if latest:
                t_val = latest.get('temperature', 0)
                ph_val = latest.get('ph', 0)
                turb_val = latest.get('turbidity', 0)
                wl_val = latest.get('water_level_cm', 0)

                sc1, sc2 = st.columns(2)
                sc1.metric("Water Temp (°C)", f"{t_val:.1f}")
                sc2.metric("pH Level", f"{ph_val:.2f}")

                sc3, sc4 = st.columns(2)
                sc3.metric("Turbidity (NTU)", f"{turb_val:.1f}")
                sc4.metric("Water Level (cm)", f"{wl_val:.1f}")

                st.markdown("#### 🤖 Meta Prophet AI Diagnostic Engine")
                status_type, msg = evaluate_environment(t_val, ph_val, turb_val)

                if status_type == "error":
                    st.error(f"🚨 **{msg}**")
                elif status_type == "warning":
                    st.warning(f"⚠️ **{msg}**")
                elif status_type == "success":
                    st.success(f"✅ **{msg}**")
                else:
                    st.info(f"ℹ️ **{msg}**")
            else:
                st.warning("No live data currently being received from this node.")

    st.markdown("---")

    with st.container(border=True):
        st.markdown("### 📏 Pond Dimensions & Capacity")

        length = float(active_device['length'])
        width = float(active_device['width'])
        depth = float(active_device['depth'])
        fish_count = int(active_device.get('fish_count', 0))
        volume = length * width * depth
        pond_area = length * width

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Length", f"{length} m")
        c2.metric("Width", f"{width} m")
        c3.metric("Depth", f"{depth} m")
        c4.metric("Volume (Capacity)", f"{volume:.1f} m³")
        c5.metric("Fish Count", str(fish_count))

        stocking_density = fish_count / pond_area if pond_area > 0 else 0
        if stocking_density == 0:
            st.info("🐟 **Pond is currently empty.** Add fish in Pond Settings to calculate stocking density.")
        elif stocking_density <= 8:
            st.success(f"✅ **Healthy Stocking Density:** {stocking_density:.1f} fish per square meter. (Standard limit is 5-8 fish/m²).")
        else:
            st.warning(f"⚠️ **Overcrowding Risk:** {stocking_density:.1f} fish per square meter. (You exceed 8 fish/m². Ensure paddlewheel aerators are running to maintain oxygen levels!)")

    if st.session_state.role == "admin":
        st.markdown("---")
        with st.container(border=True):
            st.markdown("### 🚨 Network Priority: Farmer Risk Rankings")
            st.markdown("<p class='tagalog-subtext'>Listahan ng mga palaisdaan na nangangailangan ng agarang pansin</p>", unsafe_allow_html=True)

            farmer_risks = []
            with st.spinner("Analyzing network-wide risk scores..."):
                for dev in devices:
                    dev_latest = fetch_latest_data(dev['device_sn'])
                    if dev_latest:
                        risk = calculate_risk_score(dev_latest.get('temperature', 0), dev_latest.get('ph', 0), dev_latest.get('turbidity', 0))
                        farmer_risks.append({
                            "Farmer": f"Farmer {dev['owner_id']} ({dev['pond_name']})",
                            "Risk Score": risk,
                            "Status": "Critical" if risk >= 50 else "Warning" if risk >= 20 else "Stable"
                        })

            if farmer_risks:
                df_risk = pd.DataFrame(farmer_risks).sort_values(by="Risk Score", ascending=True)
                color_map = {"Critical": "#EF4444", "Warning": "#F59E0B", "Stable": "#10B981"}

                fig_risk = px.bar(
                    df_risk, x="Risk Score", y="Farmer", color="Status",
                    color_discrete_map=color_map, orientation='h', text="Risk Score"
                )
                fig_risk.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                    margin=dict(l=0, r=0, t=10, b=0), height=max(200, len(farmer_risks) * 35),
                    xaxis=dict(range=[0, 100], title="Risk Score (%)"), yaxis=dict(title="")
                )
                st.plotly_chart(fig_risk, use_container_width=True, theme="streamlit", key="admin_farmer_risk_rank_bottom")