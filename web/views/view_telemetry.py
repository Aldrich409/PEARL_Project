import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import base64
import os
import requests

from api.telemetry_api import (
    fetch_latest_data,
    fetch_history_data,
    fetch_bio_audit,
    post_farmer_intervention,
    fetch_farmer_interventions,
)
from api.device_api import fetch_devices

# =========================================================
# HELPER FUNCTIONS
# =========================================================
def fetch_current_weather():
    """Fetches real-time weather matching the mobile app."""
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=14.5264&longitude=121.1558&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m&timezone=Asia%2FManila"
        res = requests.get(url)
        if res.status_code == 200:
            return res.json().get('current')
    except Exception as e:
        print(f"Weather fetch error: {e}")
    return None

def evaluate_environment(temp, ph, turb):
    if turb > 100:
        return "error", "CLASSIFICATION: High Algal Bloom Risk (PANGANIB: Sobrang Labo ng Tubig / Lumot Risk)"
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

def generate_harvest_certificate_html(audit_data):
    ha = audit_data["harvest_audit"]
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=140x140&data={ha['certificate_id']}-{audit_data['device_sn']}-Score:{ha['compliance_score_pct']}pct"
    
    logo_b64 = ""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    
    search_paths = [
        os.path.join(parent_dir, "assets", "pearl_logo(1).png"),
        "web/assets/pearl_logo(1).png",
        "assets/pearl_logo(1).png",
        "pearl_logo(1).png"
    ]
    
    for path in search_paths:
        if os.path.exists(path):
            with open(path, "rb") as f:
                logo_b64 = base64.b64encode(f.read()).decode("utf-8")
            break
            
    logo_tag = f'<img src="data:image/png;base64,{logo_b64}" style="height: 80px; vertical-align: middle; margin-right: 12px;" />' if logo_b64 else ''

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>PEARL Clean Water Harvest Certificate - {ha['certificate_id']}</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f1f5f9; padding: 30px; }}
            .cert-box {{ max-width: 750px; margin: auto; background: white; padding: 40px; border: 6px double #0284c7; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }}
            .header {{ text-align: center; border-bottom: 2px solid #e2e8f0; padding-bottom: 20px; }}
            .badge {{ display: inline-block; background: #10b981; color: white; padding: 6px 16px; border-radius: 20px; font-weight: bold; margin-top: 8px; }}
            .grid {{ display: flex; justify-content: space-between; align-items: stretch; margin-top: 25px; }}
            .metrics {{ width: 66%; }}
            .metrics table {{ width: 100%; border-collapse: collapse; }}
            .metrics td {{ padding: 8px 4px; border-bottom: 1px solid #f1f5f9; font-size: 14px; }}
            .qr-panel {{ width: 28%; text-align: center; border: 1px solid #cbd5e1; border-radius: 8px; padding: 12px; display: flex; flex-direction: column; justify-content: center; align-items: center; }}
            .qr-panel img {{ max-width: 140px; height: auto; display: block; margin: 0 auto; }}
            .footer {{ margin-top: 30px; font-size: 12px; color: #64748b; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="cert-box">
            <div class="header">
                <h1 style="margin:0; color:#0f172a; display: flex; align-items: center; justify-content: center;">
                    {logo_tag} P.E.A.R.L. AQUACULTURE QUALITY AUDIT
                </h1>
                <p style="margin:4px 0; color:#475569;">Predictive Environmental Analytics for Real-Time Logging</p>
                <div class="badge">{ha['grade']}</div>
            </div>
            <div class="grid">
                <div class="metrics">
                    <table>
                        <tr><td><b>Certificate ID:</b></td><td>{ha['certificate_id']}</td></tr>
                        <tr><td><b>Pond Name & Node:</b></td><td>{audit_data['pond_name']} ({audit_data['device_sn']})</td></tr>
                        <tr><td><b>Location:</b></td><td>{audit_data['location']}</td></tr>
                        <tr><td><b>Audit Date:</b></td><td>{ha['audit_date']} ({ha['records_audited']} Telemetry Cycles Verified)</td></tr>
                        <tr><td><b>14-Day Avg Turbidity:</b></td><td>{ha['avg_turbidity_ntu']} NTU (Threshold: &le; 80.0 NTU)</td></tr>
                        <tr><td><b>14-Day Avg pH & Temp:</b></td><td>pH {ha['avg_ph']} | {ha['avg_temp_c']} &deg;C</td></tr>
                        <tr><td><b>Clean-Water Compliance:</b></td><td><b>{ha['compliance_score_pct']}% Verified Off-Flavor Free</b></td></tr>
                    </table>
                </div>
                <div class="qr-panel">
                    <img src="{qr_url}" alt="Verification QR" />
                    <p style="font-size:11px; color:#334155; margin:8px 0 0 0;"><b>Scan to Verify</b><br>{ha['certificate_id']}</p>
                </div>
            </div>
            <div class="footer">
                Certified by the P.E.A.R.L. Automated Water-Quality & Algal Bloom Prevention Engine.<br>
                This document verifies that cultured Nile Tilapia were raised in low-turbidity water free from geosmin/MIB algal blooms (<i>lasang lumot</i>).
            </div>
        </div>
    </body>
    </html>
    """

# =========================================================
# MAIN RENDER
# =========================================================
def render():
    st.title("📡 Live Telemetry Dashboard")
    st.markdown("<p class='tagalog-subtext' style='font-size: 12px; padding-bottom: 0px;'>Kasalukuyang Sukat ng Tubig sa Palaisdaan</p>", unsafe_allow_html=True)
    st.markdown("---")

    active_device_sn = st.session_state.get("active_device_sn", None)
    
    if not active_device_sn:
        st.warning("No active node selected in the sidebar.")
        return

    devices = fetch_devices(st.session_state.user_id, st.session_state.role)
    active_device = next((d for d in devices if d['device_sn'] == active_device_sn), None)
    
    if not active_device:
        st.error("Device configuration not found.")
        return

    latest = fetch_latest_data(active_device_sn)
    history = fetch_history_data(active_device_sn, limit=50)
    bio_audit = fetch_bio_audit(active_device_sn)
    interventions = fetch_farmer_interventions(active_device_sn, limit=10)

    # =========================================================
    # 0. LOCAL WEATHER BANNER
    # =========================================================
    weather = fetch_current_weather()
    if weather:
        location = active_device.get('location', 'Angono, Rizal')
        st.markdown(f"<h4 style='color: #0EA5E9; margin-bottom: 10px;'>🌤️ Local Weather ({location})</h4>", unsafe_allow_html=True)
        
        # Changed from 4 columns to 3 columns so they stretch to max width
        wc1, wc2, wc3 = st.columns(3)
        with wc1.container(border=True):
            st.metric("AIR TEMP", f"{weather.get('temperature_2m', '--')} °C")
        with wc2.container(border=True):
            st.metric("HUMIDITY", f"{weather.get('relative_humidity_2m', '--')} %")
        with wc3.container(border=True):
            st.metric("WIND", f"{weather.get('wind_speed_10m', '--')} km/h")
            
        st.markdown("<br>", unsafe_allow_html=True)

    # =========================================================
    # TOP ROW: HISTORICAL TRENDS (LEFT) + LIVE METRICS (RIGHT)
    # =========================================================
    top_col_chart, top_col_metrics = st.columns([2.5, 1.2])

    # LEFT: Historical Water Conditions Chart
    with top_col_chart:
        ch_h1, ch_h2 = st.columns([4, 1])
        ch_h1.markdown("<h3 style='font-size: 32px; margin-bottom: 0px; padding-bottom: 10px;'>📈 Historical water conditions</h3>", unsafe_allow_html=True)
        ch_h1.markdown("<p style='color: #64748B; font-size: 14px; font-weight: 600; margin-top: -15px; padding-left: 5px;'>Temperature and pH trends • dual-axis view</p>", unsafe_allow_html=True)
        ch_h2.markdown("<div style='text-align: right;'><span style='background-color: #EFF6FF; color: #1E40AF; padding: 4px 12px; border-radius: 12px; font-size: 13px; font-weight: 600;'>Last 50 Reads</span></div>", unsafe_allow_html=True)

        if history:
            df = pd.DataFrame(history)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            with st.container(border=True):
                fig_wq = make_subplots(specs=[[{"secondary_y": True}]])
                
                # Red solid line for Temperature
                fig_wq.add_trace(go.Scatter(
                    x=df['timestamp'], y=df['temperature'],
                    name='Temperature °C',
                    mode='lines+markers',
                    line=dict(color='#EF4444', width=2.5, shape='spline'),
                    marker=dict(size=5)
                ), secondary_y=False)
                
                # Blue solid line for pH
                fig_wq.add_trace(go.Scatter(
                    x=df['timestamp'], y=df['ph'],
                    name='pH Level',
                    mode='lines+markers',
                    line=dict(color='#0EA5E9', width=2.5, shape='spline'),
                    marker=dict(size=5),
                ), secondary_y=True)

                if interventions:
                    for act in interventions:
                        act_ts = pd.to_datetime(act.get("timestamp"))
                        if act_ts >= df['timestamp'].min() and act_ts <= df['timestamp'].max():
                            fig_wq.add_vline(x=act_ts.timestamp() * 1000, line_width=1.5, line_dash="dash", line_color="#A855F7")

                # --- COMPACT HEIGHT to align with metrics side ---
                fig_wq.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=10, r=10, t=10, b=10), height=210,
                    hovermode="x unified",
                    xaxis=dict(showgrid=True, gridcolor='#E2E8F0'),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
                )
                fig_wq.update_yaxes(title_text="", secondary_y=False, showgrid=True, gridcolor="#E2E8F0")
                fig_wq.update_yaxes(title_text="", secondary_y=True, showgrid=False)
                
                st.plotly_chart(fig_wq, use_container_width=True, key=f"wq_{active_device_sn}")

    # RIGHT: Live Sensor Metrics Cards (2x2 Grid Layout)
    with top_col_metrics:
        st.markdown("<div style='margin-top: 85px;'></div>", unsafe_allow_html=True) # Spacer to push down
        if latest:
            t_val = latest.get('temperature', 0)
            ph_val = latest.get('ph', 0)
            turb_val = latest.get('turbidity', 0)
            wl_val = latest.get('water_level_cm', 0)
            
            # Row 1 of metrics
            m1, m2 = st.columns(2)
            m1.metric("Temperature (°C)", f"{t_val:.1f}")
            m2.metric("pH Level", f"{ph_val:.2f}")
            
            st.markdown("<div style='margin-bottom: 5px;'></div>", unsafe_allow_html=True)
            
            # Row 2 of metrics
            m3, m4 = st.columns(2)
            m3.metric("Turbidity (NTU)", f"{turb_val:.1f}")
            m4.metric("Water Level (cm)", f"{wl_val:.1f}")


    # =========================================================
    # SECOND ROW: WATER QUALITY OVERVIEW (AREA CHART) & TURBIDITY
    # =========================================================
    if history:
        st.markdown("<br>", unsafe_allow_html=True)
        col_area, col_turb = st.columns([1, 1])
        
        with col_area:
            st.markdown("### 📊 Water quality risk trend")
            with st.container(border=True):
                # Calculate risk scores for each timestamp in history
                df['risk_score'] = df.apply(lambda row: calculate_risk_score(row['temperature'], row['ph'], row['turbidity']), axis=1)
                
                # Build an Area Chart plotting risk over time
                fig_area = go.Figure()
                
                # 1. ADD COLORED BACKGROUND ZONES
                fig_area.add_hrect(y0=0, y1=20, fillcolor="#10B981", opacity=0.15, line_width=0, annotation_text="Optimal", annotation_position="top left", annotation_font_color="#10B981")
                fig_area.add_hrect(y0=20, y1=50, fillcolor="#F59E0B", opacity=0.15, line_width=0, annotation_text="Warning", annotation_position="top left", annotation_font_color="#F59E0B")
                fig_area.add_hrect(y0=50, y1=100, fillcolor="#EF4444", opacity=0.15, line_width=0, annotation_text="Critical", annotation_position="top left", annotation_font_color="#EF4444")
                
                # 2. Add the actual risk trendline on top
                fig_area.add_trace(go.Scatter(
                    x=df['timestamp'], 
                    y=df['risk_score'],
                    mode='lines',
                    line=dict(color='#1E293B', width=2.5, shape='spline'),
                    name="Risk Score"
                ))
                
                fig_area.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=10, r=10, t=10, b=10), height=210,
                    xaxis=dict(showgrid=False, title=""),
                    yaxis=dict(showgrid=True, gridcolor='#E2E8F0', title="", range=[0, 100])
                )
                st.plotly_chart(fig_area, use_container_width=True, key=f"area_{active_device_sn}")

        with col_turb:
            st.markdown("### 🌊 Turbidity by day")
            with st.container(border=True):
                df['color'] = df['turbidity'].apply(lambda x: '#F59E0B' if x > 80 else '#93C5FD')
                
                fig_turb = go.Figure(data=[
                    go.Bar(
                        x=df['timestamp'], 
                        y=df['turbidity'], 
                        marker_color=df['color'],
                        name="Turbidity (NTU)"
                    )
                ])
                fig_turb.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=10, r=10, t=10, b=10), height=210,
                    xaxis=dict(showgrid=False, title=""), 
                    yaxis=dict(showgrid=True, gridcolor='#E2E8F0', title="")
                )
                st.plotly_chart(fig_turb, use_container_width=True, key=f"turb_{active_device_sn}")

   
   # =========================================================
    # 3. POND DIMENSIONS & VIRTUAL BIO-ESTIMATOR
    # =========================================================
    st.markdown("---")
    st.markdown("### 📏 Pond Specifications & Capacity (Sukat at Dami ng Isda)")
    length, width, depth = float(active_device['length']), float(active_device['width']), float(active_device['depth'])
    volume = length * width * depth
    fish_type = active_device.get('fish_type', 'Tilapia')
    
    # Custom HTML template to perfectly mimic Streamlit's metric box but with a controllable font size
   # Custom HTML template to perfectly mimic Streamlit's metric box with a hover effect
    def custom_metric_box(label, value):
        return f"""
        <style>
        .custom-metric-card {{
            background-color: #f7fdff; 
            border: 1px solid #b8ebfc; 
            border-radius: 8px; 
            padding: 16px;
            display: flex; 
            flex-direction: column;
            height: 100%;
            transition: border-color 0.2s ease;
        }}
        .custom-metric-card:hover {{
            border-color: #70e5ff; 
            transform: scale(1.03); 
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08); 
        }}
        </style>
        <div class="custom-metric-card">
            <span style="font-size: 14px; color: #64748B; margin-bottom: 4px;">{label}</span>
            <span style="font-size: 22px; font-weight: 600; color: #31333F; line-height: 1.2; word-wrap: break-word;">{value}</span>
        </div>
        """

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    
    with c1: st.markdown(custom_metric_box("Species", fish_type), unsafe_allow_html=True)
    with c2: st.markdown(custom_metric_box("Length", f"{length} m"), unsafe_allow_html=True)
    with c3: st.markdown(custom_metric_box("Width", f"{width} m"), unsafe_allow_html=True)
    with c4: st.markdown(custom_metric_box("Depth", f"{depth} m"), unsafe_allow_html=True)
    with c5: st.markdown(custom_metric_box("Volume", f"{volume:.1f} m³"), unsafe_allow_html=True)
    with c6: st.markdown(custom_metric_box("Fish Count", str(active_device['fish_count'])), unsafe_allow_html=True)
    if latest:
        if bio_audit and "virtual_bio" in bio_audit:
            vb = bio_audit["virtual_bio"]
            st.markdown("#### 🧪 Derived Chemical & Oxygen Stress Indicators (Emerson $pK_a$ & Henry's Law)")
            bc1, bc2, bc3 = st.columns(3)
            bc1.metric(
                "Un-ionized Ammonia (NH₃) Fraction",
                f"{vb['nh3_toxicity_percent']}% ({vb['estimated_nh3_mg_l']} mg/L)",
                delta=vb['nh3_status'],
                delta_color="inverse" if "Danger" in vb['nh3_status'] or "Warning" in vb['nh3_status'] else "normal"
            )
            bc2.metric(
                "Estimated Dissolved Oxygen (DO)",
                f"{vb['estimated_do_mg_l']} mg/L",
                delta=vb['do_status'],
                delta_color="inverse" if "Critical" in vb['do_status'] or "Stress" in vb['do_status'] else "normal"
            )
            dosage_summary = (
                f"{vb['recommended_apog_kg']} kg Apog" if vb['recommended_apog_kg'] > 0
                else f"{vb['recommended_water_exchange_m3']} m³ Water Flush" if vb['recommended_water_exchange_m3'] > 0
                else "No Dosage Needed"
            )
            bc3.metric(
                "Volumetric Remediation Dosage",
                dosage_summary,
                delta=f"Pond Volume: {vb['volume_m3']} m³"
            )

        st.markdown("#### 🤖 Meta Prophet AI Diagnostic Engine")
        status_type, msg = evaluate_environment(t_val, ph_val, turb_val)
        if status_type == "error": st.error(f"🚨 **{msg}**")
        elif status_type == "warning": st.warning(f"⚠️ **{msg}**")
        elif status_type == "success": st.success(f"✅ **{msg}**")
        else: st.info(f"ℹ️ **{msg}**")

        # =========================================================
        # 4. IPO FEEDBACK LOOP
        # =========================================================
        with st.expander("🛠️ IPO Feedback Loop: Log Farmer Remediation Action (Magtala ng Ginawang Aksyon)", expanded=(status_type in ["error", "warning"])):
            vb_data = bio_audit["virtual_bio"] if bio_audit else {"recommended_apog_kg": 75.0, "recommended_water_exchange_m3": 100.0, "volume_m3": volume}
            st.caption(
                f"Based on your **{vb_data['volume_m3']} m³** pond volume, logging an intervention records the exact timestamp of your remediation and tracks water recovery on the telemetry chart."
            )
            with st.form(f"intervention_form_{active_device_sn}"):
                ic1, ic2 = st.columns(2)
                action_options = [
                    f"Applied Agricultural Lime / Apog ({vb_data['recommended_apog_kg'] or round(volume*0.15, 1)} kg)",
                    f"Performed 20% Fresh Water Exchange ({vb_data['recommended_water_exchange_m3'] or round(volume*0.20, 1)} m³)",
                    "Reduced Fish Feeding Rate by 50% (Algal Bloom Control)",
                    "Activated Emergency Paddlewheel / Aerators",
                    "Installed Breeding Hapas / Spawning Nets"
                ]
                chosen_action = ic1.selectbox("Select Intervention Performed (Piniling Aksyon)", action_options)
                custom_notes = ic2.text_input("Exact Dosage / Notes (Tala ng Dami)", value=f"Auto-calculated for {volume:.1f} m³ pond")
                
                if st.form_submit_button("✅ Log Action Taken (I-save ang Aksyon)", type="primary", use_container_width=True):
                    payload = {
                        "device_sn": active_device_sn,
                        "username": st.session_state.get("username", "farmer"),
                        "action_taken": chosen_action,
                        "recommended_dosage": custom_notes,
                        "ph_at_action": float(ph_val),
                        "temp_at_action": float(t_val),
                        "turb_at_action": float(turb_val)
                    }
                    if post_farmer_intervention(payload):
                        st.success("Intervention logged! Vertical marker added to the telemetry chart.")
                        st.rerun()
                    else:
                        st.error("Failed to log intervention.")

            if interventions:
                st.markdown("##### 📋 Recent Remediation Feedback Logs")
                df_int = pd.DataFrame(interventions)[["timestamp", "username", "action_taken", "recommended_dosage", "ph_at_action", "temp_at_action", "turb_at_action"]]
                df_int.columns = ["Timestamp", "User", "Action Taken", "Dosage / Notes", "pH", "Temp (°C)", "Turbidity (NTU)"]
                st.dataframe(df_int, use_container_width=True, hide_index=True)

    # =========================================================
    # 5. OFF-FLAVOR (LUMOT) HARVEST READINESS TRACKER
    # =========================================================
    if bio_audit and "harvest_audit" in bio_audit:
        st.markdown("---")
        st.markdown("### 🏆 'Off-Flavor (*Lumot*) Free' Harvest Quality Audit & Buyer Certificate")
        ha = bio_audit["harvest_audit"]
        
        with st.container(border=True):
            hc1, hc2 = st.columns([7, 2])
            with hc1:
                if ha["is_off_flavor_free"]:
                    st.success(f"✅ **{ha['grade']}** — Certificate ID: `{ha['certificate_id']}`")
                else:
                    st.warning(f"⚠️ **{ha['grade']}** — Audit ID: `{ha['certificate_id']}`")
                
                st.markdown(
                    f"**14-Day Water Clarity Compliance:** `{ha['compliance_score_pct']}%` "
                    f"(Audited **{ha['records_audited']}** logs | Avg Turbidity: **{ha['avg_turbidity_ntu']} NTU** | Avg pH: **{ha['avg_ph']}**)"
                )
                st.caption(
                    "Buyers often lower farmgate prices due to skepticism over muddy taste (*lasang lumot*). "
                    "This certificate proves your Nile Tilapia were maintained below the 80 NTU algal threshold prior to harvest."
                )
                
                cert_html = generate_harvest_certificate_html(bio_audit)
                st.download_button(
                    label="📜 Download Printable Clean-Water Harvest Certificate",
                    data=cert_html.encode("utf-8"),
                    file_name=f"{ha['certificate_id']}_{active_device_sn}.html",
                    mime="text/html",
                    type="primary"
                )
            with hc2:
                qr_img_url = f"https://api.qrserver.com/v1/create-qr-code/?size=140x140&data={ha['certificate_id']}-{active_device_sn}-Score:{ha['compliance_score_pct']}pct"
                st.image(qr_img_url, caption=f"Verify: {ha['certificate_id']}", width=135)

    # =========================================================
    # 6. ADMIN NETWORK PRIORITY: FARMER RISK RANKINGS
    # =========================================================
    if st.session_state.role == "admin":
        st.markdown("---")
        st.markdown("### 🚨 Network Priority: Farmer Risk Rankings")
        farmer_risks = []
        for dev in devices:
            dev_latest = fetch_latest_data(dev['device_sn'])
            if dev_latest:
                risk = calculate_risk_score(dev_latest.get('temperature', 0), dev_latest.get('ph', 0), dev_latest.get('turbidity', 0))
                farmer_risks.append({
                    "Farmer": f"Farmer {dev['owner_id']} ({dev['pond_name']})",
                    "Risk Score": risk,
                    "Status": "Danger" if risk >= 50 else "Warning" if risk >= 20 else "Stable"
                })
        if farmer_risks:
            df_risk = pd.DataFrame(farmer_risks).sort_values(by="Risk Score", ascending=True)
            fig_risk = px.bar(
                df_risk, x="Risk Score", y="Farmer", color="Status",
                color_discrete_map={"Danger": "#EF4444", "Warning": "#F59E0B", "Stable": "#10B981"},
                orientation='h', text="Risk Score"
            )
            fig_risk.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=max(220, len(farmer_risks) * 35))
            st.plotly_chart(fig_risk, use_container_width=True, theme="streamlit", key="admin_farmer_risk_rank_bottom")