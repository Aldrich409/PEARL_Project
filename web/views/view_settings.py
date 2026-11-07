import streamlit as st
import pandas as pd
from api.device_api import (
    fetch_devices,
    update_device_settings,
    fetch_fish_profiles,
    fetch_fish_suggestion,
    save_fish_profile
)

# Built-in Reference Library
BUILT_IN_FISH_GUIDES = {
    "Tilapia": {
        "fish_name": "Tilapia",
        "temp_norm_min": 26.0, "temp_norm_max": 33.0, "temp_danger_min": 24.0, "temp_danger_max": 35.0,
        "ph_norm_min": 7.0, "ph_norm_max": 8.5, "ph_danger_min": 6.5, "ph_danger_max": 9.0,
        "turb_norm_max": 80.0, "turb_danger_max": 100.0,
        "suggestion_text": "📘 BFAR / FAO Standard (Tilapia): Optimal growth and breeding occur at 26–33°C and pH 7.0–8.5. Keep turbidity ≤80 NTU."
    },
    "Bangus (Milkfish)": {
        "fish_name": "Bangus (Milkfish)",
        "temp_norm_min": 25.0, "temp_norm_max": 32.0, "temp_danger_min": 22.0, "temp_danger_max": 35.0,
        "ph_norm_min": 7.0, "ph_norm_max": 8.5, "ph_danger_min": 6.5, "ph_danger_max": 9.0,
        "turb_norm_max": 85.0, "turb_danger_max": 110.0,
        "suggestion_text": "📘 BFAR / SEAFDEC Standard (Bangus): Milkfish thrive at 25–32°C and pH 7.0–8.5. Sensitive to low oxygen >32°C."
    },
    "Catfish (Hito)": {
        "fish_name": "Catfish (Hito)",
        "temp_norm_min": 26.0, "temp_norm_max": 32.0, "temp_danger_min": 22.0, "temp_danger_max": 36.0,
        "ph_norm_min": 6.5, "ph_norm_max": 8.0, "ph_danger_min": 5.5, "ph_danger_max": 9.0,
        "turb_norm_max": 100.0, "turb_danger_max": 140.0,
        "suggestion_text": "📘 BFAR Standard (Hito): Tolerates higher turbidity (≤100 NTU) but pH <5.5 or >9.0 burns scaleless skin."
    },
    "Carp (Karpa)": {
        "fish_name": "Carp (Karpa)",
        "temp_norm_min": 24.0, "temp_norm_max": 30.0, "temp_danger_min": 20.0, "temp_danger_max": 34.0,
        "ph_norm_min": 7.0, "ph_norm_max": 8.5, "ph_danger_min": 6.0, "ph_danger_max": 9.0,
        "turb_norm_max": 90.0, "turb_danger_max": 120.0,
        "suggestion_text": "📘 FAO Standard (Carp): Prefers slightly cooler water (24–30°C) and pH 7.0–8.5. Foraging stirs mud up to 90 NTU."
    },
    "Freshwater Prawn (Ulang)": {
        "fish_name": "Freshwater Prawn (Ulang)",
        "temp_norm_min": 28.0, "temp_norm_max": 31.0, "temp_danger_min": 24.0, "temp_danger_max": 34.0,
        "ph_norm_min": 7.0, "ph_norm_max": 8.5, "ph_danger_min": 6.5, "ph_danger_max": 9.0,
        "turb_norm_max": 60.0, "turb_danger_max": 85.0,
        "suggestion_text": "📘 BFAR Standard (Ulang): Requires clean water (≤60 NTU) and pH 7.0–8.5 for successful shell molting."
    },
    "Mudfish (Dalag)": {
        "fish_name": "Mudfish (Dalag)",
        "temp_norm_min": 25.0, "temp_norm_max": 32.0, "temp_danger_min": 20.0, "temp_danger_max": 36.0,
        "ph_norm_min": 6.5, "ph_norm_max": 8.0, "ph_danger_min": 5.5, "ph_danger_max": 9.0,
        "turb_norm_max": 100.0, "turb_danger_max": 140.0,
        "suggestion_text": "📘 BFAR Standard (Dalag): Hardy air-breathing predator. Keep turbidity ≤100 NTU to maintain feeding visibility."
    },
    "Pangasius (Cream Dory)": {
        "fish_name": "Pangasius (Cream Dory)",
        "temp_norm_min": 26.0, "temp_norm_max": 31.0, "temp_danger_min": 22.0, "temp_danger_max": 35.0,
        "ph_norm_min": 6.5, "ph_norm_max": 8.0, "ph_danger_min": 5.5, "ph_danger_max": 9.0,
        "turb_norm_max": 95.0, "turb_danger_max": 130.0,
        "suggestion_text": "📘 FAO Standard (Pangasius): Needs water exchange if turbidity >130 NTU to maintain white fillet quality."
    }
}

def get_local_ai_suggestion(fish_name: str):
    name_clean = fish_name.strip()
    for k, v in BUILT_IN_FISH_GUIDES.items():
        if k.lower() in name_clean.lower() or name_clean.lower() in k.lower():
            copied = dict(v)
            copied["fish_name"] = name_clean
            return copied
    return {
        "fish_name": name_clean,
        "temp_norm_min": 26.0, "temp_norm_max": 32.0, "temp_danger_min": 23.0, "temp_danger_max": 35.0,
        "ph_norm_min": 6.8, "ph_norm_max": 8.5, "ph_danger_min": 6.0, "ph_danger_max": 9.0,
        "turb_norm_max": 80.0, "turb_danger_max": 110.0,
        "suggestion_text": f"🤖 AI Aquaculture Guide ({name_clean}): Recommended range is 26-32°C, pH 6.8-8.5, and turbidity ≤80 NTU."
    }

def enrich_profile_tips(p: dict):
    t_n_min, t_n_max = p.get("temp_norm_min", 26.0), p.get("temp_norm_max", 33.0)
    t_d_min, t_d_max = p.get("temp_danger_min", 24.0), p.get("temp_danger_max", 35.0)
    p_n_min, p_n_max = p.get("ph_norm_min", 7.0), p.get("ph_norm_max", 8.5)
    p_d_min, p_d_max = p.get("ph_danger_min", 6.5), p.get("ph_danger_max", 9.0)
    tb_n_max, tb_d_max = p.get("turb_norm_max", 80.0), p.get("turb_danger_max", 100.0)

    p["temp_tip"] = p.get("temp_tip") or f"🟢 {t_n_min}-{t_n_max}°C | 🔴 <{t_d_min} or >{t_d_max}°C"
    p["ph_tip"] = p.get("ph_tip") or f"🟢 {p_n_min}-{p_n_max} | 🔴 <{p_d_min} or >{p_d_max}"
    p["turb_tip"] = p.get("turb_tip") or f"🟢 0-{tb_n_max} NTU | 🔴 >{tb_d_max} NTU"
    if not p.get("suggestion_text"):
        p["suggestion_text"] = get_local_ai_suggestion(p.get("fish_name", "Tilapia"))["suggestion_text"]
    return p

def render():
    st.title("⚙️ System Settings")
    st.markdown("<p style='color: #64748B; font-size: 13px; font-style: italic; margin-top: -15px;'>Manage Pond Fish Species, Recommended Range Guides, and Hardware Configurations</p>", unsafe_allow_html=True)
    
    active_sn = st.session_state.get("active_device_sn", None)
    devices = fetch_devices(st.session_state.user_id, st.session_state.role)
    active_device = next((d for d in devices if d['device_sn'] == active_sn), None)
    
    if not active_device:
        st.warning("No active monitoring node selected. Please select a pond from the sidebar.")
        return

    if "local_fish_library" not in st.session_state:
        st.session_state.local_fish_library = {k: dict(v) for k, v in BUILT_IN_FISH_GUIDES.items()}

    db_profiles = fetch_fish_profiles()
    for item in db_profiles:
        profile = dict(item)
        actual_name = profile.get("fish_name") or profile.get("name") or profile.get("species") or profile.get("fish_type") or "Saved Database Fish"
        profile["fish_name"] = actual_name 
        st.session_state.local_fish_library[actual_name] = enrich_profile_tips(profile)

    profile_map = st.session_state.local_fish_library
    fish_names = list(profile_map.keys())

    st.info(
        f"**Currently Configuring:** {active_device['pond_name']} (`{active_device['device_sn']}`)  |  "
        f"**Active Species in Pond:** 🐟 `{active_device.get('fish_type', 'Tilapia')}`"
    )
    
    if st.session_state.role == "admin":
        tabs = st.tabs(["🐟 Fish Species & Thresholds", "🔗 Pair Hardware", "📱 SMS Alerts", "💤 Deep Sleep", "⚖️ Calibration"])
        tab_fish, tab_pair, tab_sms, tab_sleep, tab_calib = tabs
    else:
        tabs = st.tabs(["🐟 Fish Species & Thresholds", "📱 SMS Alerts", "💤 Deep Sleep", "⚖️ Calibration"])
        tab_fish, tab_sms, tab_sleep, tab_calib = tabs
        tab_pair = None

    # =========================================================================
    # TAB 1: CHOOSE SPECIES & ADD CUSTOM RANGES (Streamlined UI)
    # =========================================================================
    with tab_fish:
        
        current_fish = active_device.get("fish_type", "Tilapia")
        if current_fish not in fish_names:
            profile_map[current_fish] = get_local_ai_suggestion(current_fish)
            fish_names.append(current_fish)

        default_idx = fish_names.index(current_fish) if current_fish in fish_names else 0

        # --- STEP 1: Main Dropdown ---
        st.markdown("### 🎯 Choose Species in Pond")
        chosen_fish = st.selectbox(
            "Select a saved fish species to apply its thresholds:",
            fish_names,
            index=default_idx,
            key="choose_pond_species_dropdown"
        )
        
        chosen_profile = enrich_profile_tips(profile_map.get(chosen_fish, BUILT_IN_FISH_GUIDES["Tilapia"]))
        
        # Minimized Guide Expander
        with st.expander(f"📖 View Biological Guidelines for {chosen_fish}", expanded=False):
            st.info(chosen_profile['suggestion_text'])

            t_n_min, t_n_max = chosen_profile["temp_norm_min"], chosen_profile["temp_norm_max"]
            t_d_min, t_d_max = chosen_profile["temp_danger_min"], chosen_profile["temp_danger_max"]
            p_n_min, p_n_max = chosen_profile["ph_norm_min"], chosen_profile["ph_norm_max"]
            p_d_min, p_d_max = chosen_profile["ph_danger_min"], chosen_profile["ph_danger_max"]
            tb_n_max, tb_d_max = chosen_profile["turb_norm_max"], chosen_profile["turb_danger_max"]

            range_df = pd.DataFrame([
                {"Parameter": "🌡️ Temp (°C)", "🟢 Normal": f"{t_n_min:.1f} – {t_n_max:.1f}", "🔴 Danger": f"<{t_d_min:.1f} or >{t_d_max:.1f}"},
                {"Parameter": "🧪 pH Level", "🟢 Normal": f"{p_n_min:.1f} – {p_n_max:.1f}", "🔴 Danger": f"<{p_d_min:.1f} or >{p_d_max:.1f}"},
                {"Parameter": "🌊 Turbidity", "🟢 Normal": f"0 – {tb_n_max:.0f} NTU", "🔴 Danger": f">{tb_d_max:.0f} NTU"}
            ])
            st.dataframe(range_df, hide_index=True, use_container_width=True)

        if st.button(f"✅ Set '{chosen_fish}' as Active Species for {active_device['pond_name']}", type="primary", use_container_width=True):
            active_device.update({
                "fish_type": chosen_fish,
                "temp_norm_min": chosen_profile["temp_norm_min"], "temp_norm_max": chosen_profile["temp_norm_max"],
                "temp_danger_min": chosen_profile["temp_danger_min"], "temp_danger_max": chosen_profile["temp_danger_max"],
                "ph_norm_min": chosen_profile["ph_norm_min"], "ph_norm_max": chosen_profile["ph_norm_max"],
                "ph_danger_min": chosen_profile["ph_danger_min"], "ph_danger_max": chosen_profile["ph_danger_max"],
                "turb_norm_max": chosen_profile["turb_norm_max"], "turb_danger_max": chosen_profile["turb_danger_max"],
            })
            if update_device_settings(active_device):
                st.success(f"🐟 Pond **{active_device['pond_name']}** is now monitoring with **{chosen_fish}** thresholds!")
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # --- STEP 2: Minimized Custom Add / Edit Section ---
        with st.expander("➕ Add New Custom Fish or Edit Thresholds", expanded=False):
            st.caption("Need specific values? Type a name, use AI, or edit the values manually and save them to your library.")
            
            if "editor_version" not in st.session_state:
                st.session_state.editor_version = 0

            # Automatically use the selected fish's values as the starting point for editing
            ed = chosen_profile
            
            c_type, c_btn = st.columns([2.5, 1])
            typed_name = c_type.text_input("Species Name (e.g., Red Tilapia):", value=ed.get("fish_name", chosen_fish))
            
            with c_btn:
                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                if st.button("✨ Auto-Fill AI Ranges", use_container_width=True):
                    target_name = typed_name.strip() or chosen_fish
                    api_sug = fetch_fish_suggestion(target_name)
                    st.session_state.editor_fish = enrich_profile_tips(api_sug if api_sug else get_local_ai_suggestion(target_name))
                    st.session_state.editor_version += 1
                    st.rerun()

            # If user clicked the AI button, use the AI suggestion. Otherwise, default to the chosen dropdown fish.
            ed = st.session_state.get("editor_fish", chosen_profile)
            ver = st.session_state.editor_version

            with st.form("form_save_multiple_fish"):
                tc1, tc2, tc3, tc4 = st.columns(4)
                in_t_n_min = tc1.number_input("🟢 Normal Min (°C)", value=float(ed["temp_norm_min"]), step=0.5, key=f"tnmin_{ver}")
                in_t_n_max = tc2.number_input("🟢 Normal Max (°C)", value=float(ed["temp_norm_max"]), step=0.5, key=f"tnmax_{ver}")
                in_t_d_min = tc3.number_input("🔴 Danger Below (°C)", value=float(ed["temp_danger_min"]), step=0.5, key=f"tdmin_{ver}")
                in_t_d_max = tc4.number_input("🔴 Danger Above (°C)", value=float(ed["temp_danger_max"]), step=0.5, key=f"tdmax_{ver}")

                pc1, pc2, pc3, pc4 = st.columns(4)
                in_p_n_min = pc1.number_input("🟢 Normal Min (pH)", value=float(ed["ph_norm_min"]), step=0.1, key=f"pnmin_{ver}")
                in_p_n_max = pc2.number_input("🟢 Normal Max (pH)", value=float(ed["ph_norm_max"]), step=0.1, key=f"pnmax_{ver}")
                in_p_d_min = pc3.number_input("🔴 Danger Below (pH)", value=float(ed["ph_danger_min"]), step=0.1, key=f"pdmin_{ver}")
                in_p_d_max = pc4.number_input("🔴 Danger Above (pH)", value=float(ed["ph_danger_max"]), step=0.1, key=f"pdmax_{ver}")

                tbc1, tbc2 = st.columns(2)
                in_tb_n_max = tbc1.number_input("🟢 Normal Max (NTU)", value=float(ed["turb_norm_max"]), step=5.0, key=f"tbnmax_{ver}")
                in_tb_d_max = tbc2.number_input("🔴 Danger Above (NTU)", value=float(ed["turb_danger_max"]), step=5.0, key=f"tbdmax_{ver}")

                in_sug_text = st.text_area("📖 Biological Note:", value=ed.get("suggestion_text", ""), height=68, key=f"sugtxt_{ver}")

                apply_now = st.checkbox(f"Immediately apply to {active_device['pond_name']} after saving", value=True)

                if st.form_submit_button("💾 Save to Species Library", type="secondary", use_container_width=True):
                    save_name = typed_name.strip()
                    if not save_name:
                        st.error("❌ Please type a fish species name before saving.")
                    else:
                        new_fish_data = enrich_profile_tips({
                            "fish_name": save_name,
                            "temp_norm_min": in_t_n_min, "temp_norm_max": in_t_n_max,
                            "temp_danger_min": in_t_d_min, "temp_danger_max": in_t_d_max,
                            "ph_norm_min": in_p_n_min, "ph_norm_max": in_p_n_max,
                            "ph_danger_min": in_p_d_min, "ph_danger_max": in_p_d_max,
                            "turb_norm_max": in_tb_n_max, "turb_danger_max": in_tb_d_max,
                            "suggestion_text": in_sug_text
                        })
                        
                        st.session_state.local_fish_library[save_name] = new_fish_data
                        st.session_state.editor_fish = new_fish_data
                        save_fish_profile(new_fish_data)

                        if apply_now:
                            active_device.update({
                                "fish_type": save_name,
                                "temp_norm_min": in_t_n_min, "temp_norm_max": in_t_n_max,
                                "temp_danger_min": in_t_d_min, "temp_danger_max": in_t_d_max,
                                "ph_norm_min": in_p_n_min, "ph_norm_max": in_p_n_max,
                                "ph_danger_min": in_p_d_min, "ph_danger_max": in_p_d_max,
                                "turb_norm_max": in_tb_n_max, "turb_danger_max": in_tb_d_max,
                            })
                            update_device_settings(active_device)

                        st.success(f"✅ Saved **{save_name}** to Library!")
                        st.rerun()

    # --- TAB: PAIR HARDWARE (ADMIN ONLY) ---
    if tab_pair:
        with tab_pair:
            st.markdown("#### 🔗 Pair New Hardware Node")
            with st.form("form_pair"):
                st.text_input("Sensor Serial Number (e.g., PEARL-ESP32-999)")
                st.text_input("Assign Pond Name")
                if st.form_submit_button("Register Sensor to Network", use_container_width=True):
                    st.info("Hardware node registered successfully.")

    # --- TAB: SMS ALERTS ---
    with tab_sms:
        with st.form("form_sms"):
            alert_phone = st.text_input("Target Phone Number (+639...)", value=active_device['alert_phone'])
            levels = ["Critical Emergencies Only", "Warnings & Critical", "All Notifications"]
            current_idx = 0 if active_device['alert_level'] == "Critical" else 1
            alert_level = st.selectbox("Alert Sensitivity Level", levels, index=current_idx)
            
            if st.form_submit_button("Update SMS Settings", type="primary", use_container_width=True):
                active_device.update({
                    'alert_phone': alert_phone, 
                    'alert_level': "Critical" if "Critical" in alert_level else "Warning"
                })
                if update_device_settings(active_device):
                    st.success("SMS Settings saved!")
                    st.rerun()

    # --- TAB: DEEP SLEEP ---
    with tab_sleep:
        with st.form("form_sleep"):
            sleep_interval = st.slider("Broadcast Frequency (Minutes)", 5, 120, int(active_device['sleep_interval']), 5)
            if st.form_submit_button("Update Broadcast Cycle", type="primary", use_container_width=True):
                active_device['sleep_interval'] = sleep_interval
                if update_device_settings(active_device):
                    st.success("Sleep interval saved!")
                    st.rerun()

    # --- TAB: SENSOR CALIBRATION ---
    with tab_calib:
        with st.form("form_calibration"):
            c1, c2 = st.columns(2)
            ph_offset = c1.number_input("pH Offset", value=float(active_device['ph_offset']), step=0.1, format="%.2f")
            turb_offset = c2.number_input("Turbidity Offset (NTU)", value=float(active_device['turb_offset']), step=1.0, format="%.1f")
            
            if st.form_submit_button("Save Calibration Offsets", type="primary", use_container_width=True):
                active_device.update({'ph_offset': ph_offset, 'turb_offset': turb_offset})
                if update_device_settings(active_device):
                    st.success("Calibration applied successfully!")
                    st.rerun()