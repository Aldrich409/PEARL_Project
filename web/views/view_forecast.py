import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from data_fetcher import fetch_ai_forecast, fetch_history_data

def fetch_7_day_weather():
    """Fetches a 7-day weather forecast for Angono, Rizal."""
    # Coordinates for Angono, Calabarzon, Philippines
    lat, lon = 14.5264, 121.1558 
    # Added precipitation_probability_max to the API request
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max&timezone=Asia%2FManila"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json().get("daily", {})
    except Exception:
        pass
    return None

def apply_dark_iot_css():
    st.markdown("""
        <style>
        /* 🚫 HIDE STREAMLIT DEPLOY BUTTON & TOOLBAR */
        .stAppDeployButton, .stDeployButton, [data-testid="stToolbar"] { 
            display: none !important; 
        }
        [data-testid="stHeader"] {
            background-color: transparent !important; 
        }
        
        /* 🌌 MODERN DARK IOT THEME */
        .stApp { 
            background-color: white; /* Deep dark purple-blue background */
        }
        
        /* 📉 NEON COMPACT METRIC CARDS */
        div[data-testid="stMetric"] {
            background-color: #F0F9FF; /* Soft neon blue background */
            border: 1px solid #2A2A4A; /* Subtle dark border */
            padding: 15px 20px;          
            border-radius: 12px;          
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }
        div[data-testid="stMetric"]:hover {
            transform: translateY(-3px);
            border-color: #8B5CF6; /* Neon purple hover glow */
            box-shadow: 0px 6px 15px rgba(139, 92, 246, 0.15);
        }
        div[data-testid="stMetricLabel"] > label {
            color: #F0F9FF !important; /* Muted light gray for labels */
            font-weight: 600 !important;
            font-size: 0.75rem !important; 
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        div[data-testid="stMetricValue"] > div {
            color: black !important; /* Crisp white numbers */
            font-weight: 800 !important;
            font-size: 1.6rem !important; 
        }
        
        /* HEADERS & DIVIDERS */
        h1, h2, h3, h4, h5 {
            color: black !important; /* White headers */
            font-weight: 800;
        }
        hr {
            border-color: #2A2A4A !important;
            margin: 1.5rem 0; 
        }
        
        /* ALERT BOXES */
        div[data-testid="stAlert"] {
            background-color: #e7e7e7;
            border: 1px solid #2A2A4A;
            color: gray;
        }
        </style>
    """, unsafe_allow_html=True)

def render():
    apply_dark_iot_css()
    
    st.title("🤖 Breeding Forecast")
    # Updated subtext color to neon purple to match theme
    st.markdown("<p style='color: #372b53; font-style: italic;'>Suriin ang nakaraang 1 buwan at asahan ang susunod na 7 araw</p>", unsafe_allow_html=True)
    
    active_device = st.session_state.get("active_device_sn", "PEARL-ESP32-001")
    with st.spinner("Analyzing historical trends and generating 7-day forecast..."):
        history = fetch_history_data(active_device, limit=120) 
        forecasts = fetch_ai_forecast(active_device, days=7)
        weather_daily = fetch_7_day_weather()
        
    if history and forecasts:
        df_hist = pd.DataFrame(history)
        df_hist['timestamp'] = pd.to_datetime(df_hist['timestamp'])
        
        df_fore = pd.DataFrame(forecasts)
        df_fore['date'] = pd.to_datetime(df_fore['date'])

        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.markdown("### 📊 Past 30 Days / Nakaraang Buwan")
            fig_hist = make_subplots(specs=[[{"secondary_y": True}]])
            # Neon Purple and Neon Green for history
            fig_hist.add_trace(go.Scatter(x=df_hist['timestamp'], y=df_hist['temperature'], mode='lines', name='Temp (°C)', line=dict(color='#8B5CF6', width=2)), secondary_y=False)
            fig_hist.add_trace(go.Scatter(x=df_hist['timestamp'], y=df_hist['ph'], mode='lines', name='pH Level', line=dict(color='#10B981', width=2)), secondary_y=True)
            fig_hist.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#94A3B8'),
                margin=dict(l=20, r=20, t=20, b=20), height=300,
                xaxis=dict(showgrid=True, gridcolor='#2A2A4A')
            )
            fig_hist.update_yaxes(title_text="Temp (°C)", secondary_y=False, showgrid=True, gridcolor='#2A2A4A')
            fig_hist.update_yaxes(title_text="pH Level", secondary_y=True, showgrid=False)
            st.plotly_chart(fig_hist, use_container_width=True)

        with chart_col2:
            st.markdown("### 🔮 Forecast Next 7 Days / Susunod na 7 Araw")
            fig_fore = make_subplots(specs=[[{"secondary_y": True}]])
            # Neon Orange and Neon Blue for forecast
            fig_fore.add_trace(go.Scatter(x=df_fore['date'], y=df_fore['predicted_temperature'], mode='lines+markers', name='Pred Temp', line=dict(color='#F59E0B', width=2, dash='dash')), secondary_y=False)
            fig_fore.add_trace(go.Scatter(x=df_fore['date'], y=df_fore['predicted_ph'], mode='lines+markers', name='Pred pH', line=dict(color='#0EA5E9', width=2, dash='dash')), secondary_y=True)
            fig_fore.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#94A3B8'),
                margin=dict(l=20, r=20, t=20, b=20), height=300,
                xaxis=dict(showgrid=True, gridcolor='#2A2A4A')
            )
            fig_fore.update_yaxes(title_text="Temp (°C)", secondary_y=False, showgrid=True, gridcolor='#2A2A4A')
            fig_fore.update_yaxes(title_text="pH Level", secondary_y=True, showgrid=False)
            st.plotly_chart(fig_fore, use_container_width=True)

        st.divider()
        
        # --- NEW: 7-DAY WEATHER FORECAST & RAIN PROBABILITY (SIDE BY SIDE) ---
        if weather_daily and 'time' in weather_daily:
            st.markdown("### 🌤️ 7-Day Surface Weather & Rain Forecast / Pagtatantiya ng Panahon")
            st.markdown("<p style='color: #372b53; font-size: 13px; font-style: italic;'>External weather directly impacts pond water temperature and turbidity.</p>", unsafe_allow_html=True)
            
            df_weather = pd.DataFrame(weather_daily)
            
            # Create two columns for the side-by-side layout
            weather_col1, weather_col2 = st.columns(2)
            
            with weather_col1:
                st.markdown("<h5 style='text-align: center; color: #64748B; font-size: 14px;'>Temperature & Rainfall Amount</h5>", unsafe_allow_html=True)
                fig_weather = make_subplots(specs=[[{"secondary_y": True}]])
                
                # Precipitation (Rain) in bars
                fig_weather.add_trace(go.Bar(x=df_weather['time'], y=df_weather['precipitation_sum'], name='Rainfall (mm)', marker_color='#0EA5E9', opacity=0.6), secondary_y=True)
                
                # Max & Min Temperatures in lines
                fig_weather.add_trace(go.Scatter(x=df_weather['time'], y=df_weather['temperature_2m_max'], mode='lines+markers', name='Max Temp (°C)', line=dict(color='#EF4444', width=2)), secondary_y=False)
                fig_weather.add_trace(go.Scatter(x=df_weather['time'], y=df_weather['temperature_2m_min'], mode='lines+markers', name='Min Temp (°C)', line=dict(color='#F59E0B', width=2)), secondary_y=False)
                
                fig_weather.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#94A3B8'),
                    margin=dict(l=20, r=20, t=20, b=20), height=320,
                    xaxis=dict(showgrid=True, gridcolor='#2A2A4A'),
                    hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
                )
                fig_weather.update_yaxes(title_text="Air Temp (°C)", secondary_y=False, showgrid=True, gridcolor='#2A2A4A')
                fig_weather.update_yaxes(title_text="Rainfall (mm)", secondary_y=True, showgrid=False)
                st.plotly_chart(fig_weather, use_container_width=True)

            with weather_col2:
                st.markdown("<h5 style='text-align: center; color: #64748B; font-size: 14px;'>Rain Probability Risk</h5>", unsafe_allow_html=True)
                fig_rain_prob = go.Figure()
                
                # Rain Probability Area Chart
                fig_rain_prob.add_trace(go.Scatter(
                    x=df_weather['time'], 
                    y=df_weather.get('precipitation_probability_max', [0]*len(df_weather['time'])), 
                    mode='lines+markers',
                    name='Chance of Rain (%)', 
                    fill='tozeroy',
                    line=dict(color='#8B5CF6', width=2), # Neon purple to match theme
                    marker=dict(size=6)
                ))
                
                fig_rain_prob.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#94A3B8'),
                    margin=dict(l=20, r=20, t=20, b=20), height=320,
                    xaxis=dict(showgrid=True, gridcolor='#2A2A4A'),
                    yaxis=dict(title="Probability (%)", range=[0, 100], showgrid=True, gridcolor='#2A2A4A'),
                    hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
                )
                st.plotly_chart(fig_rain_prob, use_container_width=True)
            
            st.divider()

        # --- 7-DAY ACTION PLAN SECTION ---
        st.markdown("### 📋 7-Day Action Plan / Plano para sa Susunod na Linggo")
        
        for day in forecasts:
            status = day['status']
            action = day['action_required']
            action_parts = action.split("\n")
            eng_action = action_parts[0] if len(action_parts) > 0 else ""
            tag_action = action_parts[1] if len(action_parts) > 1 else ""
            msg_type = "success" if "Optimal" in status or "Stable" in status else "warning" if "Warning" in status or "Risk" in status else "error"
                
            with st.container():
                st.subheader(f"📅 Date / Petsa: {day['date']}")
                cA, cB, cC = st.columns(3)
                cA.metric("Predicted Temp / Temperatura", f"{day['predicted_temperature']} °C")
                cB.metric("Predicted pH / Antas ng pH", f"{day['predicted_ph']}")
                cC.metric("Predicted Turbidity / Labo", f"{day['predicted_turbidity']} NTU")
                
                # --- CUSTOM HTML ACTION PLAN CARDS ---
                if msg_type == "success":
                    st.markdown(f"""
                    <div style="background-color: #D1FAE5; color: #065F46; padding: 15px; border-radius: 8px; border: 1px solid #10B981;">
                        <strong>{status}</strong><br><br>🇬🇧 {eng_action}<br><br>🇵🇭 <em>{tag_action}</em>
                    </div>
                    """, unsafe_allow_html=True)
                elif msg_type == "warning":
                    st.markdown(f"""
                    <div style="background-color: #FEF3C7; color: #92400E; padding: 15px; border-radius: 8px; border: 1px solid #F59E0B;">
                        <strong>{status}</strong><br><br>🇬🇧 {eng_action}<br><br>🇵🇭 <em>{tag_action}</em>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background-color: #FEE2E2; color: #991B1B; padding: 15px; border-radius: 8px; border: 1px solid #EF4444;">
                        <strong>{status}</strong><br><br>🇬🇧 {eng_action}<br><br>🇵🇭 <em>{tag_action}</em>
                    </div>
                    """, unsafe_allow_html=True)
                    
                st.divider()
    else:
        st.info("Insufficient telemetry records for Meta Prophet forecasting / Kulang pa ang datos para sa hula ng AI.")