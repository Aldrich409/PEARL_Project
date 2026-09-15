import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from data_fetcher import fetch_ai_forecast, fetch_history_data

def fetch_7_day_weather():
    lat, lon = 14.5264, 121.1558 
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max&timezone=Asia%2FManila"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json().get("daily", {})
    except Exception:
        pass
    return None

def render():
    st.title("🤖 Breeding Forecast")
    st.markdown("<p class='tagalog-subtext'>Suriin ang nakaraang 1 buwan at asahan ang susunod na 7 araw</p>", unsafe_allow_html=True)

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
            fig_hist.add_trace(go.Scatter(x=df_hist['timestamp'], y=df_hist['temperature'], mode='lines', name='Temp (°C)', line=dict(color='#0284C7', width=2)), secondary_y=False)
            fig_hist.add_trace(go.Scatter(x=df_hist['timestamp'], y=df_hist['ph'], mode='lines', name='pH Level', line=dict(color='#10B981', width=2)), secondary_y=True)

            fig_hist.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=20, b=20), height=300
            )
            fig_hist.update_yaxes(title_text="Temp (°C)", secondary_y=False)
            fig_hist.update_yaxes(title_text="pH Level", secondary_y=True, showgrid=False)
            st.plotly_chart(fig_hist, use_container_width=True, theme="streamlit")

        with chart_col2:
            st.markdown("### 🔮 Forecast Next 7 Days / Susunod na 7 Araw")
            fig_fore = make_subplots(specs=[[{"secondary_y": True}]])
            fig_fore.add_trace(go.Scatter(x=df_fore['date'], y=df_fore['predicted_temperature'], mode='lines+markers', name='Pred Temp', line=dict(color='#F59E0B', width=2, dash='dash')), secondary_y=False)
            fig_fore.add_trace(go.Scatter(x=df_fore['date'], y=df_fore['predicted_ph'], mode='lines+markers', name='Pred pH', line=dict(color='#0EA5E9', width=2, dash='dash')), secondary_y=True)

            fig_fore.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=20, b=20), height=300
            )
            fig_fore.update_yaxes(title_text="Temp (°C)", secondary_y=False)
            fig_fore.update_yaxes(title_text="pH Level", secondary_y=True, showgrid=False)
            st.plotly_chart(fig_fore, use_container_width=True, theme="streamlit")

        st.divider()

        if weather_daily and 'time' in weather_daily:
            st.markdown("### 🌤️ 7-Day Surface Weather & Rain Forecast / Pagtatantiya ng Panahon")
            st.markdown("<p class='tagalog-subtext'>External weather directly impacts pond water temperature and turbidity.</p>", unsafe_allow_html=True)

            df_weather = pd.DataFrame(weather_daily)
            weather_col1, weather_col2 = st.columns(2)

            with weather_col1:
                st.markdown("<h5 style='text-align: center; font-size: 14px;'>Temperature & Rainfall Amount</h5>", unsafe_allow_html=True)
                fig_weather = make_subplots(specs=[[{"secondary_y": True}]])
                fig_weather.add_trace(go.Bar(x=df_weather['time'], y=df_weather['precipitation_sum'], name='Rainfall (mm)', marker_color='#0EA5E9', opacity=0.6), secondary_y=True)
                fig_weather.add_trace(go.Scatter(x=df_weather['time'], y=df_weather['temperature_2m_max'], mode='lines+markers', name='Max Temp (°C)', line=dict(color='#EF4444', width=2)), secondary_y=False)
                fig_weather.add_trace(go.Scatter(x=df_weather['time'], y=df_weather['temperature_2m_min'], mode='lines+markers', name='Min Temp (°C)', line=dict(color='#F59E0B', width=2)), secondary_y=False)

                fig_weather.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=20, r=20, t=20, b=20), height=320,
                    hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
                )
                fig_weather.update_yaxes(title_text="Air Temp (°C)", secondary_y=False)
                fig_weather.update_yaxes(title_text="Rainfall (mm)", secondary_y=True, showgrid=False)
                st.plotly_chart(fig_weather, use_container_width=True, theme="streamlit")

            with weather_col2:
                st.markdown("<h5 style='text-align: center; font-size: 14px;'>Rain Probability Risk</h5>", unsafe_allow_html=True)
                fig_rain_prob = go.Figure()
                fig_rain_prob.add_trace(go.Scatter(
                    x=df_weather['time'], 
                    y=df_weather.get('precipitation_probability_max', [0]*len(df_weather['time'])), 
                    mode='lines+markers',
                    name='Chance of Rain (%)', 
                    fill='tozeroy',
                    line=dict(color='#0284C7', width=2), 
                    marker=dict(size=6)
                ))

                fig_rain_prob.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=20, r=20, t=20, b=20), height=320,
                    yaxis=dict(title="Probability (%)", range=[0, 100]),
                    hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
                )
                st.plotly_chart(fig_rain_prob, use_container_width=True, theme="streamlit")

            st.divider()

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

                if msg_type == "success":
                    st.markdown(f"""
                    <div style="background-color: rgba(16, 185, 129, 0.15); color: inherit; padding: 15px; border-radius: 8px; border-left: 4px solid #10B981;">
                        <strong>{status}</strong><br><br>🇬🇧 {eng_action}<br><br>🇵🇭 <em>{tag_action}</em>
                    </div>
                    """, unsafe_allow_html=True)
                elif msg_type == "warning":
                    st.markdown(f"""
                    <div style="background-color: rgba(245, 158, 11, 0.15); color: inherit; padding: 15px; border-radius: 8px; border-left: 4px solid #F59E0B;">
                        <strong>{status}</strong><br><br>🇬🇧 {eng_action}<br><br>🇵🇭 <em>{tag_action}</em>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background-color: rgba(239, 68, 68, 0.15); color: inherit; padding: 15px; border-radius: 8px; border-left: 4px solid #EF4444;">
                        <strong>{status}</strong><br><br>🇬🇧 {eng_action}<br><br>🇵🇭 <em>{tag_action}</em>
                    </div>
                    """, unsafe_allow_html=True)

                st.divider()
    else:
        st.info("Insufficient telemetry records for Meta Prophet forecasting / Kulang pa ang datos para sa hula ng AI.")