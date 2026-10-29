import streamlit as st
import os

# Try to import node_selector (handles if it's in the same folder or root web folder)
try:
    from components import node_selector
except ImportError:
    import node_selector

def render(set_page_callback, logout_callback):
    """Renders the secure sidebar navigation for the PEARL System."""
    
    # Get the current active page to highlight the chosen button
    current_page = st.session_state.get("current_page", "Live Telemetry")
    
    # Helper function to dynamically change button style based on the active page
    def get_btn_type(page_name):
        return "primary" if current_page == page_name else "secondary"

    # --- CUSTOM CSS FOR ACTIVE BUTTON COLOR ---
    st.sidebar.markdown(
        """
        <style>
        /* Change the background color of the active (primary) button in the sidebar */
        [data-testid="stSidebar"] button[kind="primary"] {
            background-color: #d1d1d1 !important;
            color: #0F172A !important; /* Dark text so it's readable on light cyan */
            border: 1px solid #0EA5E9 !important;
            font-weight: 700 !important;
        }
        /* Make it slightly darker when hovered */
        [data-testid="stSidebar"] button[kind="primary"]:hover {
            background-color: #5be3e3 !important; 
            border: 1px solid #0284C7 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 1. Add the Logo (Centered and larger using columns)
    logo_col1, logo_col2, logo_col3 = st.sidebar.columns([1, 2, 1])
    with logo_col2:
        logo_path_1 = os.path.join("assets", "pearl_logo(1).png")
        logo_path_2 = os.path.join("assets", "pearl_logo.png")
        
        if os.path.exists(logo_path_1):
            st.image(logo_path_1, use_container_width=True)
        elif os.path.exists(logo_path_2):
            st.image(logo_path_2, use_container_width=True)
        else:
            st.markdown("<h1 style='text-align: center; margin: 0;'>🐟</h1>", unsafe_allow_html=True)

    # 2. Add the Title and User info
    st.sidebar.markdown(
        f"""
        <div style='text-align: center;'>
            <h3 style='margin-bottom: -15px; margin-top: 5px; padding-top: 0px;'>PEARL System</h3>
            <p style='font-size: 14px; color: #0284C7; margin-top: 0px; padding-top: 0px;'>
                <b>User:</b> {st.session_state.username} ({st.session_state.role.capitalize()})
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    st.sidebar.markdown("---")

    # 3. Main Navigation
    st.sidebar.button("📊 Live Telemetry", on_click=set_page_callback, args=("Live Telemetry",), use_container_width=True, type=get_btn_type("Live Telemetry"))
    st.sidebar.button("🤖 Breeding Forecast", on_click=set_page_callback, args=("Breeding Forecast",), use_container_width=True, type=get_btn_type("Breeding Forecast"))

    if st.session_state.role == "admin":
        st.sidebar.button("🌐 Network Overview", on_click=set_page_callback, args=("Network Overview",), use_container_width=True, type=get_btn_type("Network Overview"))
        st.sidebar.button("📂 Telemetry Records", on_click=set_page_callback, args=("Telemetry Records",), use_container_width=True, type=get_btn_type("Telemetry Records"))

    # 4. Node Selector
    if st.session_state.role == "admin":
        st.sidebar.markdown("---")
        node_selector.render()

    # 5. System Actions
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    st.sidebar.markdown("#### ⚙️ SYSTEM")
    
    st.sidebar.button("👥 Account Management", on_click=set_page_callback, args=("Account Management",), use_container_width=True, type=get_btn_type("Account Management"))
    st.sidebar.button("⚙️ System Settings", on_click=set_page_callback, args=("System Settings",), use_container_width=True, type=get_btn_type("System Settings"))
    
    # Logout set to secondary so it doesn't get the #99FFFF cyan style
    st.sidebar.button("🚪 Logout", on_click=logout_callback, use_container_width=True, type="secondary")