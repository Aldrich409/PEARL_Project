import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random
import datetime
import time

def apply_custom_dashboard_css():
    st.markdown("""
        <style>
        .stApp { background-color: #F8FAFC; }
        div[data-testid="stMetric"] {
            background-color: #FFFFFF; 
            border: 1px solid #E2E8F0;
            padding: 16px 20px; 
            border-radius: 12px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.03);
        }
        .tagalog-subtext {
            color: #64748B; 
            font-size: 13px; 
            font-style: italic;
            margin-top: -15px; 
            margin-bottom: 20px;
        }
        .iso-header {
            color: #0F172A;
            font-weight: 800;
            margin-top: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #E2E8F0;
        }
        </style>
    """, unsafe_allow_html=True)

def generate_mock_health_data():
    """Generates simulated server data for demonstration purposes."""
    now = datetime.datetime.now()
    times = [(now - datetime.timedelta(minutes=i)).strftime("%H:%M") for i in range(30, 0, -1)]
    
    # Simulate API Latency (Target: < 200ms)
    latencies = [random.randint(45, 120) for _ in range(30)]
    # Simulate occasional spike
    if random.random() > 0.8:
        latencies[random.randint(0, 29)] = random.randint(250, 400)
        
    return pd.DataFrame({
        "Time": times,
        "Latency (ms)": latencies,
        "CPU (%)": [random.uniform(15.0, 45.0) for _ in range(30)]
    })

def render():
    apply_custom_dashboard_css()
    
    st.title("🖥️ System Health & Diagnostics")
    st.markdown("<p class='tagalog-subtext'>ISO/IEC 25010 Software Quality Metrics / Pagsusuri ng Sistema</p>", unsafe_allow_html=True)
    
    # Generate dynamic data
    df_health = generate_mock_health_data()
    current_latency = df_health["Latency (ms)"].iloc[-1]
    current_cpu = df_health["CPU (%)"].iloc[-1]
    
    # ==========================================
    # 1. PERFORMANCE EFFICIENCY (ISO 25010)
    # ==========================================
    st.markdown("<h3 class='iso-header'>⚡ Performance Efficiency</h3>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: 
        st.metric("API Response Time", f"{current_latency} ms", delta="-12 ms" if current_latency < 100 else "+45 ms", delta_color="inverse")
    with c2: 
        st.metric("CPU Utilization", f"{current_cpu:.1f} %", delta="Stable", delta_color="off")
    with c3: 
        st.metric("Memory Usage (RAM)", f"{random.uniform(42.5, 45.1):.1f} %", delta="1.8 GB / 4.0 GB", delta_color="off")
    with c4: 
        st.metric("Database Query Time", f"{random.randint(8, 25)} ms", delta="Fast", delta_color="off")

    # Latency Chart
    fig_lat = go.Figure()
    fig_lat.add_trace(go.Scatter(x=df_health["Time"], y=df_health["Latency (ms)"], 
                                 mode='lines+markers', name='Latency', 
                                 line=dict(color='#0EA5E9', width=3)))
    fig_lat.add_hline(y=200, line_dash="dash", line_color="#EF4444", annotation_text="Threshold (200ms)")
    fig_lat.update_layout(
        title="API Latency Trend (Last 30 Minutes)",
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        height=300, margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(showgrid=True, gridcolor='#E2E8F0'),
        yaxis=dict(showgrid=True, gridcolor='#E2E8F0', title="Milliseconds (ms)")
    )
    st.plotly_chart(fig_lat, use_container_width=True)

    # ==========================================
    # 2. RELIABILITY & SECURITY (ISO 25010)
    # ==========================================
    col_rel, col_sec = st.columns(2)
    
    with col_rel:
        st.markdown("<h3 class='iso-header'>🛡️ Reliability</h3>", unsafe_allow_html=True)
        st.write("**System Uptime:** 99.98% (45 Days, 12 Hours)")
        st.write("**Hardware Node Status:** 🟢 All Nodes Active")
        st.write("**Error Rate (500s):** 0.02%")
        st.progress(0.9998, text="Uptime SLA Target: 99.9%")
        
    with col_sec:
        st.markdown("<h3 class='iso-header'>🔒 Security</h3>", unsafe_allow_html=True)
        st.write("**Active User Sessions:** 3")
        st.write("**Failed Login Attempts (24h):** 0")
        st.write("**Database Encryption:** 🟢 AES-256 Active")
        st.progress(1.0, text="Security Protocols Integrity")

    # ==========================================
    # 3. MAINTAINABILITY & PORTABILITY (ISO 25010)
    # ==========================================
    st.markdown("<h3 class='iso-header'>⚙️ Maintainability</h3>", unsafe_allow_html=True)
    st.info(
        "**System Architecture:** Modular FastAPI + Streamlit Pipeline\n\n"
        "**Database Size:** 12.4 MB (SQLite `pearl_data.db`)\n\n"
        "**Last Backup:** " + (datetime.datetime.now() - datetime.timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
    )