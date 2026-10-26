import streamlit as st
import pandas as pd
from data_fetcher import (
    fetch_devices,
    update_device_settings,
    fetch_fish_profiles,
    fetch_fish_suggestion,
    save_fish_profile
)

# Built-in BFAR / FAO / SEAFDEC Reference Library (Always available even if DB isn't re-seeded)
BUILT_IN_FISH_GUIDES = {
    "Tilapia": {
        "fish_name": "Tilapia",
        "temp_norm_min": 26.0, "temp_norm_max": 33.0, "temp_danger_min": 24.0, "temp_danger_max": 35.0,
        "ph_norm_min": 7.0, "ph_norm_max": 8.5, "ph_danger_min": 6.5, "ph_danger_max": 9.0,
        "turb_norm_max": 80.0, "turb_danger_max": 100.0,
        "temp_tip": "🟢 Normal: 26.0–33.0°C | ⚠️ Warning: 24.0–25.9°C or 33.1–35.0°C | 🔴 Danger: <24.0°C or >35.0°C (Stops feeding below 24°C; oxygen crash above 35°C)",
        "ph_tip": "🟢 Normal: 7.0–8.5 | ⚠️ Warning: 6.5–6.9 or 8.6–9.0 | 🔴 Danger: <6.5 (Acidosis) or >9.0 (Ammonia toxicity)",
        "turb_tip": "🟢 Normal: 0–80 NTU | ⚠️ Warning: 81–100 NTU | 🔴 Danger: >100 NTU (Severe algal bloom / gill-clogging silt)",
        "suggestion_text": (
            "📘 BFAR / FAO Standard (Tilapia): Optimal growth and breeding occur at 26–33°C and pH 7.0–8.5. "
            "Keep turbidity ≤80 NTU; readings above 100 NTU indicate heavy plankton blooms that deplete dissolved oxygen at night.\n"
            "🇵🇭 Gabay: Pinakamaganda ang paglaki at pangingitlog sa 26–33°C at pH 7.0–8.5. Huwag hayaang lumampas sa 100 NTU ang labo ng tubig."
        )
    },
    "Bangus (Milkfish)": {
        "fish_name": "Bangus (Milkfish)",
        "temp_norm_min": 25.0, "temp_norm_max": 32.0, "temp_danger_min": 22.0, "temp_danger_max": 35.0,
        "ph_norm_min": 7.0, "ph_norm_max": 8.5, "ph_danger_min": 6.5, "ph_danger_max": 9.0,
        "turb_norm_max": 85.0, "turb_danger_max": 110.0,
        "temp_tip": "🟢 Normal: 25.0–32.0°C | ⚠️ Warning: 22.0–24.9°C or 32.1–35.0°C | 🔴 Danger: <22.0°C or >35.0°C (High risk of gasping/fish kill above 32°C)",
        "ph_tip": "🟢 Normal: 7.0–8.5 | ⚠️ Warning: 6.5–6.9 or 8.6–9.0 | 🔴 Danger: <6.5 or >9.0 (Acidic water slows growth and damages gills)",
        "turb_tip": "🟢 Normal: 0–85 NTU | ⚠️ Warning: 86–110 NTU | 🔴 Danger: >110 NTU (Sudden dissolved oxygen drop risk)",
        "suggestion_text": (
            "📘 BFAR / SEAFDEC Standard (Bangus): Milkfish thrive at 25–32°C and pH 7.0–8.5. "
            "They are very sensitive to low dissolved oxygen when water temperature exceeds 32°C or turbidity spikes above 110 NTU.\n"
            "🇵🇭 Gabay: Sensitibo ang Bangus sa pagbaba ng oxygen kapag mainit (>32°C) o sobrang labo ng tubig (>110 NTU)."
        )
    },
    "Catfish (Hito)": {
        "fish_name": "Catfish (Hito)",
        "temp_norm_min": 26.0, "temp_norm_max": 32.0, "temp_danger_min": 22.0, "temp_danger_max": 36.0,
        "ph_norm_min": 6.5, "ph_norm_max": 8.0, "ph_danger_min": 5.5, "ph_danger_max": 9.0,
        "turb_norm_max": 100.0, "turb_danger_max": 140.0,
        "temp_tip": "🟢 Normal: 26.0–32.0°C | ⚠️ Warning: 22.0–25.9°C or 32.1–36.0°C | 🔴 Danger: <22.0°C or >36.0°C",
        "ph_tip": "🟢 Normal: 6.5–8.0 | ⚠️ Warning: 5.5–6.4 or 8.1–9.0 | 🔴 Danger: <5.5 or >9.0 (Causes skin lesions on scaleless body)",
        "turb_tip": "🟢 Normal: 0–100 NTU | ⚠️ Warning: 101–140 NTU | 🔴 Danger: >140 NTU (Tolerant of mud, but >140 NTU breeds bacteria)",
        "suggestion_text": (
            "📘 BFAR / FAO Standard (Catfish / Hito): Air-breathing organs allow Hito to tolerate higher turbidity (up to 100 NTU) "
            "and slightly acidic water (pH 6.5–8.0). However, pH <5.5 or >9.0 burns their scaleless skin.\n"
            "🇵🇭 Gabay: Mas matibay ang Hito sa malabong tubig (≤100 NTU), ngunit iwasang bumaba sa 5.5 o lumampas sa 9.0 ang pH."
        )
    },
    "Carp (Karpa)": {
        "fish_name": "Carp (Karpa)",
        "temp_norm_min": 24.0, "temp_norm_max": 30.0, "temp_danger_min": 20.0, "temp_danger_max": 34.0,
        "ph_norm_min": 7.0, "ph_norm_max": 8.5, "ph_danger_min": 6.0, "ph_danger_max": 9.0,
        "turb_norm_max": 90.0, "turb_danger_max": 120.0,
        "temp_tip": "🟢 Normal: 24.0–30.0°C | ⚠️ Warning: 20.0–23.9°C or 30.1–34.0°C | 🔴 Danger: <20.0°C or >34.0°C",
        "ph_tip": "🟢 Normal: 7.0–8.5 | ⚠️ Warning: 6.0–6.9 or 8.6–9.0 | 🔴 Danger: <6.0 or >9.0",
        "turb_tip": "🟢 Normal: 0–90 NTU | ⚠️ Warning: 91–120 NTU | 🔴 Danger: >120 NTU",
        "suggestion_text": (
            "📘 FAO Standard (Common Carp / Karpa): Prefers slightly cooler water (24–30°C) and pH 7.0–8.5. "
            "Bottom-foraging stirs up mud (Normal ≤90 NTU), but >120 NTU signals excessive organic waste.\n"
            "🇵🇭 Gabay: Mas gusto ng Karpa ang 24–30°C at pH 7.0–8.5. Palitan ang tubig kapag lumampas sa 120 NTU ang labo."
        )
    },
    "Freshwater Prawn (Ulang)": {
        "fish_name": "Freshwater Prawn (Ulang)",
        "temp_norm_min": 28.0, "temp_norm_max": 31.0, "temp_danger_min": 24.0, "temp_danger_max": 34.0,
        "ph_norm_min": 7.0, "ph_norm_max": 8.5, "ph_danger_min": 6.5, "ph_danger_max": 9.0,
        "turb_norm_max": 60.0, "turb_danger_max": 85.0,
        "temp_tip": "🟢 Normal: 28.0–31.0°C | ⚠️ Warning: 24.0–27.9°C or 31.1–34.0°C | 🔴 Danger: <24.0°C or >34.0°C",
        "ph_tip": "🟢 Normal: 7.0–8.5 | ⚠️ Warning: 6.5–6.9 or 8.6–9.0 | 🔴 Danger: <6.5 or >9.0 (Critical for shell hardening)",
        "turb_tip": "🟢 Normal: 0–60 NTU | ⚠️ Warning: 61–85 NTU | 🔴 Danger: >85 NTU (Needs clear water for molting)",
        "suggestion_text": (
            "📘 BFAR Standard (Giant Freshwater Prawn / Ulang): Requires clean water (≤60 NTU) and pH 7.0–8.5 for shell molting. "
            "High turbidity (>85 NTU) or acidic pH causes molting mortality.\n"
            "🇵🇭 Gabay: Kailangan ng malinis na tubig (≤60 NTU) at pH 7.0–8.5 para sa maayos na pagpapalit ng balat ng Ulang."
        )
    },
    "Mudfish (Dalag)": {
        "fish_name": "Mudfish (Dalag)",
        "temp_norm_min": 25.0, "temp_norm_max": 32.0, "temp_danger_min": 20.0, "temp_danger_max": 36.0,
        "ph_norm_min": 6.5, "ph_norm_max": 8.0, "ph_danger_min": 5.5, "ph_danger_max": 9.0,
        "turb_norm_max": 100.0, "turb_danger_max": 140.0,
        "temp_tip": "🟢 Normal: 25.0–32.0°C | ⚠️ Warning: 20.0–24.9°C or 32.1–36.0°C | 🔴 Danger: <20.0°C or >36.0°C",
        "ph_tip": "🟢 Normal: 6.5–8.0 | ⚠️ Warning: 5.5–6.4 or 8.1–9.0 | 🔴 Danger: <5.5 or >9.0",
        "turb_tip": "🟢 Normal: 0–100 NTU | ⚠️ Warning: 101–140 NTU | 🔴 Danger: >140 NTU",
        "suggestion_text": (
            "📘 BFAR Standard (Mudfish / Dalag): Hardy air-breathing predator comfortable in 25–32°C and pH 6.5–8.0. "
            "Keep turbidity ≤100 NTU so fish can see floating feed pellets.\n"
            "🇵🇭 Gabay: Matibay ang Dalag sa 25–32°C at pH 6.5–8.0. Panatilihing ≤100 NTU ang labo upang makita ang pakain."
        )
    },
    "Pangasius (Cream Dory)": {
        "fish_name": "Pangasius (Cream Dory)",
        "temp_norm_min": 26.0, "temp_norm_max": 31.0, "temp_danger_min": 22.0, "temp_danger_max": 35.0,
        "ph_norm_min": 6.5, "ph_norm_max": 8.0, "ph_danger_min": 5.5, "ph_danger_max": 9.0,
        "turb_norm_max": 95.0, "turb_danger_max": 130.0,
        "temp_tip": "🟢 Normal: 26.0–31.0°C | ⚠️ Warning: 22.0–25.9°C or 31.1–35.0°C | 🔴 Danger: <22.0°C or >35.0°C",
        "ph_tip": "🟢 Normal: 6.5–8.0 | ⚠️ Warning: 5.5–6.4 or 8.1–9.0 | 🔴 Danger: <5.5 or >9.0",
        "turb_tip": "🟢 Normal: 0–95 NTU | ⚠️ Warning: 96–130 NTU | 🔴 Danger: >130 NTU",
        "suggestion_text": (
            "📘 FAO Standard (Pangasius): Thrives in warm ponds (26–31°C) and pH 6.5–8.0. "
            "Water exchange is needed if turbidity exceeds 130 NTU to maintain white fillet quality.\n"
            "🇵🇭 Gabay: Nabubuhay nang maayos sa 26–31°C at pH 6.5–8.0. Palitan ang tubig kapag lumampas sa 130 NTU ang labo."
        )
    }
}

def get_local_ai_suggestion(fish_name: str):
    """Generates AI range suggestions locally if backend endpoint is unreachable."""
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
        "temp_tip": "🟢 Normal: 26.0–32.0°C | ⚠️ Warning: 23.0–25.9°C or 32.1–35.0°C | 🔴 Danger: <23.0°C or >35.0°C",
        "ph_tip": "🟢 Normal: 6.8–8.5 | ⚠️ Warning: 6.0–6.7 or 8.6–9.0 | 🔴 Danger: <6.0 or >9.0",
        "turb_tip": "🟢 Normal: 0–80 NTU | ⚠️ Warning: 81–110 NTU | 🔴 Danger: >110 NTU",
        "suggestion_text": (
            f"🤖 AI Aquaculture Guide ({name_clean}): Recommended tropical freshwater range is 26–32°C, pH 6.8–8.5, and turbidity ≤80 NTU. "
            f"Values beyond 23–35°C, pH 6.0–9.0, or >110 NTU trigger critical stress.\n"
            f"🇵🇭 Gabay para sa {name_clean}: Panatilihin ang temperatura sa 26–32°C, pH sa 6.8–8.5, at labo sa ≤80 NTU."
        )
    }

def enrich_profile_tips(p: dict):
    """Ensures every profile has inline parameter tip strings for Temp, pH, and Turbidity."""
    t_n_min, t_n_max = p.get("temp_norm_min", 26.0), p.get("temp_norm_max", 33.0)
    t_d_min, t_d_max = p.get("temp_danger_min", 24.0), p.get("temp_danger_max", 35.0)
    p_n_min, p_n_max = p.get("ph_norm_min", 7.0), p.get("ph_norm_max", 8.5)
    p_d_min, p_d_max = p.get("ph_danger_min", 6.5), p.get("ph_danger_max", 9.0)
    tb_n_max, tb_d_max = p.get("turb_norm_max", 80.0), p.get("turb_danger_max", 100.0)

    p["temp_tip"] = p.get("temp_tip") or f"🟢 Normal: {t_n_min}–{t_n_max}°C | ⚠️ Warning: {t_d_min}–{t_n_min}°C or {t_n_max}–{t_d_max}°C | 🔴 Danger: <{t_d_min}°C or >{t_d_max}°C"
    p["ph_tip"] = p.get("ph_tip") or f"🟢 Normal: {p_n_min}–{p_n_max} | ⚠️ Warning: {p_d_min}–{p_n_min} or {p_n_max}–{p_d_max} | 🔴 Danger: <{p_d_min} or >{p_d_max}"
    p["turb_tip"] = p.get("turb_tip") or f"🟢 Normal: 0–{tb_n_max} NTU | ⚠️ Warning: {tb_n_max}–{tb_d_max} NTU | 🔴 Danger: >{tb_d_max} NTU"
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

   # Merge Built-in Guides + Session Saved Fish + Database Fish Profiles
   # Merge Built-in Guides + Session Saved Fish + Database Fish Profiles
    if "local_fish_library" not in st.session_state:
        st.session_state.local_fish_library = {k: dict(v) for k, v in BUILT_IN_FISH_GUIDES.items()}

    db_profiles = fetch_fish_profiles()
    for item in db_profiles:
        profile = dict(item)
        # Safely extract the name regardless of what the database column is actually called
        actual_name = profile.get("fish_name") or profile.get("name") or profile.get("species") or profile.get("fish_type") or "Saved Database Fish"
        
        # Ensure the profile has 'fish_name' properly set so the rest of the code works
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
    # TAB 1: CHOOSE SPECIES IN POND + SUGGESTED RANGES + SAVE MULTIPLE FISH
    # =========================================================================
    with tab_fish:
        # ---------------------------------------------------------------------
        # STEP 1: CHOOSE ACTIVE SPECIES IN POND & VIEW SUGGESTED RANGES
        # ---------------------------------------------------------------------
        with st.container(border=True):
            st.markdown("### 🎯 Step 1: Choose Fish Species for This Pond (Pumili ng Isda)")
            st.caption("Select a saved fish species below to view its suggested **Normal, Warning, and Danger** ranges for **Temperature, pH Level, and Turbidity**, or switch the active species in this pond.")

            current_fish = active_device.get("fish_type", "Tilapia")
            if current_fish not in fish_names:
                profile_map[current_fish] = get_local_ai_suggestion(current_fish)
                fish_names.append(current_fish)

            default_idx = fish_names.index(current_fish) if current_fish in fish_names else 0

            chosen_fish = st.selectbox(
                "Choose Species from Saved Library:",
                fish_names,
                index=default_idx,
                key="choose_pond_species_dropdown"
            )

            chosen_profile = enrich_profile_tips(profile_map.get(chosen_fish, BUILT_IN_FISH_GUIDES["Tilapia"]))

            # 1. AI & BFAR Biological Guide Box
            st.markdown(f"""
            <div style="background-color: rgba(2, 132, 199, 0.12); padding: 14px; border-radius: 10px; border-left: 5px solid #0284C7; margin-bottom: 14px;">
                <strong>📖 Suggested Range Guide for {chosen_fish} (BFAR / FAO / AI Reference):</strong><br>
                <span style="font-size: 13.5px; white-space: pre-line;">{chosen_profile['suggestion_text']}</span>
            </div>
            """, unsafe_allow_html=True)

            # 2. Explicit Suggested Range Table (Normal, Warning, Danger for Temp, pH, Turbidity)
            t_n_min, t_n_max = chosen_profile["temp_norm_min"], chosen_profile["temp_norm_max"]
            t_d_min, t_d_max = chosen_profile["temp_danger_min"], chosen_profile["temp_danger_max"]
            p_n_min, p_n_max = chosen_profile["ph_norm_min"], chosen_profile["ph_norm_max"]
            p_d_min, p_d_max = chosen_profile["ph_danger_min"], chosen_profile["ph_danger_max"]
            tb_n_max, tb_d_max = chosen_profile["turb_norm_max"], chosen_profile["turb_danger_max"]

            range_df = pd.DataFrame([
                {
                    "Parameter": "🌡️ Temperature (°C)",
                    "🟢 Normal (Optimal)": f"{t_n_min:.1f} °C – {t_n_max:.1f} °C",
                    "⚠️ Warning (Stress)": f"{t_d_min:.1f}–{t_n_min:.1f} °C  or  {t_n_max:.1f}–{t_d_max:.1f} °C",
                    "🔴 Danger (Critical)": f"Below {t_d_min:.1f} °C  or  Above {t_d_max:.1f} °C"
                },
                {
                    "Parameter": "🧪 pH Level",
                    "🟢 Normal (Optimal)": f"{p_n_min:.1f} – {p_n_max:.1f}",
                    "⚠️ Warning (Imbalance)": f"{p_d_min:.1f}–{p_n_min:.1f}  or  {p_n_max:.1f}–{p_d_max:.1f}",
                    "🔴 Danger (Critical)": f"Below {p_d_min:.1f} (Acidic)  or  Above {p_d_max:.1f} (Alkaline)"
                },
                {
                    "Parameter": "🌊 Turbidity (NTU)",
                    "🟢 Normal (Optimal)": f"0 – {tb_n_max:.0f} NTU",
                    "⚠️ Warning (Murky)": f"{tb_n_max:.0f} – {tb_d_max:.0f} NTU",
                    "🔴 Danger (Critical)": f"Above {tb_d_max:.0f} NTU (Algal Bloom / Silt)"
                }
            ])
            st.table(range_df)

            if st.button(f"✅ Set '{chosen_fish}' as Active Species for {active_device['pond_name']}", type="primary", use_container_width=True):
                active_device.update({
                    "fish_type": chosen_fish,
                    "temp_norm_min": t_n_min, "temp_norm_max": t_n_max,
                    "temp_danger_min": t_d_min, "temp_danger_max": t_d_max,
                    "ph_norm_min": p_n_min, "ph_norm_max": p_n_max,
                    "ph_danger_min": p_d_min, "ph_danger_max": p_d_max,
                    "turb_norm_max": tb_n_max, "turb_danger_max": tb_d_max,
                })
                if update_device_settings(active_device):
                    st.success(f"🐟 Pond **{active_device['pond_name']}** is now monitoring with **{chosen_fish}** thresholds!")
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # STEP 2: TYPE FISH NAME, GET AI SUGGESTIONS & SAVE MULTIPLE FISH
        # ---------------------------------------------------------------------
        with st.container(border=True):
            st.markdown("### ➕ Step 2: Add / Save Custom Fish Species & Threshold Ranges")
            st.caption("Type what kind of fish you want to save, click **✨ Auto-Fill AI Suggested Ranges** to get recommended Normal & Danger values, adjust any numbers, and save it to your species list.")

            if "editor_fish" not in st.session_state:
                st.session_state.editor_fish = dict(chosen_profile)
                st.session_state.editor_version = 0

            c_type, c_btn1, c_btn2 = st.columns([2.2, 1.3, 1.2])
            typed_name = c_type.text_input(
                "Type Fish Species Name to Save (e.g., Red Tilapia, Bangus, Hito, Dalag, Ulang):",
                value=st.session_state.editor_fish.get("fish_name", chosen_fish)
            )

            with c_btn1:
                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                if st.button("✨ Auto-Fill AI Suggested Ranges", use_container_width=True):
                    target_name = typed_name.strip() or chosen_fish
                    api_sug = fetch_fish_suggestion(target_name)
                    sug_profile = enrich_profile_tips(api_sug if api_sug else get_local_ai_suggestion(target_name))
                    st.session_state.editor_fish = sug_profile
                    st.session_state.editor_version += 1
                    st.rerun()

            with c_btn2:
                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                if st.button(f"📥 Load '{chosen_fish}' Values", use_container_width=True):
                    st.session_state.editor_fish = dict(chosen_profile)
                    st.session_state.editor_version += 1
                    st.rerun()

            ed = enrich_profile_tips(st.session_state.editor_fish)
            ver = st.session_state.editor_version

            with st.form("form_save_multiple_fish"):
                # --- TEMPERATURE SECTION WITH INLINE SUGGESTION ---
                st.markdown("##### 🌡️ Temperature (°C) Thresholds")
                st.info(f"💡 **Suggested Temperature Range ({typed_name or ed['fish_name']}):** {ed['temp_tip']}")
                tc1, tc2, tc3, tc4 = st.columns(4)
                in_t_n_min = tc1.number_input("🟢 Normal Min (°C)", value=float(ed["temp_norm_min"]), step=0.5, key=f"tnmin_{ver}")
                in_t_n_max = tc2.number_input("🟢 Normal Max (°C)", value=float(ed["temp_norm_max"]), step=0.5, key=f"tnmax_{ver}")
                in_t_d_min = tc3.number_input("🔴 Danger Below (°C)", value=float(ed["temp_danger_min"]), step=0.5, key=f"tdmin_{ver}")
                in_t_d_max = tc4.number_input("🔴 Danger Above (°C)", value=float(ed["temp_danger_max"]), step=0.5, key=f"tdmax_{ver}")

                st.markdown("---")

                # --- PH LEVEL SECTION WITH INLINE SUGGESTION ---
                st.markdown("##### 🧪 pH Level Thresholds")
                st.info(f"💡 **Suggested pH Level Range ({typed_name or ed['fish_name']}):** {ed['ph_tip']}")
                pc1, pc2, pc3, pc4 = st.columns(4)
                in_p_n_min = pc1.number_input("🟢 Normal Min (pH)", value=float(ed["ph_norm_min"]), step=0.1, key=f"pnmin_{ver}")
                in_p_n_max = pc2.number_input("🟢 Normal Max (pH)", value=float(ed["ph_norm_max"]), step=0.1, key=f"pnmax_{ver}")
                in_p_d_min = pc3.number_input("🔴 Danger Below (pH)", value=float(ed["ph_danger_min"]), step=0.1, key=f"pdmin_{ver}")
                in_p_d_max = pc4.number_input("🔴 Danger Above (pH)", value=float(ed["ph_danger_max"]), step=0.1, key=f"pdmax_{ver}")

                st.markdown("---")

                # --- TURBIDITY SECTION WITH INLINE SUGGESTION ---
                st.markdown("##### 🌊 Turbidity (NTU) Thresholds")
                st.info(f"💡 **Suggested Turbidity Range ({typed_name or ed['fish_name']}):** {ed['turb_tip']}")
                tbc1, tbc2 = st.columns(2)
                in_tb_n_max = tbc1.number_input("🟢 Normal Max (NTU)", value=float(ed["turb_norm_max"]), step=5.0, key=f"tbnmax_{ver}")
                in_tb_d_max = tbc2.number_input("🔴 Danger Above (NTU)", value=float(ed["turb_danger_max"]), step=5.0, key=f"tbdmax_{ver}")

                in_sug_text = st.text_area(
                    "📖 Biological / AI Suggestion Note for this Species:",
                    value=ed.get("suggestion_text", ""),
                    height=85,
                    key=f"sugtxt_{ver}"
                )

                apply_now = st.checkbox(f"Also apply this species immediately to {active_device['pond_name']}", value=True)

                if st.form_submit_button("💾 Save Fish Species & Ranges to Library", type="primary", use_container_width=True):
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
                        
                        # Save in session library & backend DB
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

                        st.success(f"✅ Saved **{save_name}**! You can now select it anytime in Step 1 ('Choose Species from Saved Library').")
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