import streamlit as st

# 👇 CHANGED: Pulling from new API modules
from api.auth_api import fetch_all_accounts, admin_create_account, admin_delete_account
from api.device_api import update_device_settings

# Placeholder import just in case you add a password update endpoint to your FastAPI later
try:
    from api.auth_api import admin_update_password
except ImportError:
    admin_update_password = None

def render():
    st.title("👥 Account & Pond Management")
    st.markdown("<p style='color: #64748B; font-style: italic; margin-top: -10px;'>Pamahalaan ang mga detalye ng account at palaisdaan</p>", unsafe_allow_html=True)
    
    user_role = st.session_state.get('role', 'farmer')
    current_user_id = st.session_state.get('user_id')

    # ==========================================
    # ADMIN VIEW: Full Access (Create, Edit, Delete)
    # ==========================================
    if user_role == 'admin':
        tab1, tab2 = st.tabs(["➕ Create New Account", "📋 Manage All Accounts"])
        
        # --- TAB 1: CREATE ACCOUNT & POND PROFILE ---
        with tab1:
            st.markdown("#### 📝 New User & Pond Registration")
            with st.form("form_create_account_detailed"):
                c1, c2, c3, c4 = st.columns(4)
                username = c1.text_input("Username")
                password = c2.text_input("Password", type="password")
                confirm_password = c3.text_input("Confirm Password", type="password")
                role = c4.selectbox("Account Role", ["farmer", "admin"])
                
                st.markdown("---")
                st.markdown("##### 🏡 Pond Specifications")
                
                p1, p2 = st.columns(2)
                pond_name = p1.text_input("Pond Name (Pangalan ng Palaisdaan)", value="My Fish Pond")
                location = p2.text_input("Pond Location (Lokasyon)", value="Angono, Rizal")
                
                d1, d2, d3, d4, d5 = st.columns(5)
                length = d1.number_input("Length (m)", value=25.0, step=1.0)
                width = d2.number_input("Width (m)", value=20.0, step=1.0)
                depth = d3.number_input("Depth (m)", value=1.0, step=0.1)
                fish_count = d4.number_input("Fish Count", value=500, step=50)
                alert_phone = d5.text_input("Alert Phone (+639...)", value="")
                
                if st.form_submit_button("Register Account & Pond Profile", type="primary", use_container_width=True):
                    if username and password and confirm_password:
                        if password != confirm_password:
                            st.error("❌ Passwords do not match. Please type them carefully.")
                        else:
                            payload = {
                                "username": username, "password": password, "role": role,
                                "pond_name": pond_name, "location": location,
                                "length": length, "width": width, "depth": depth,
                                "fish_count": fish_count, "alert_phone": alert_phone
                            }
                            if admin_create_account(payload):
                                st.success(f"✅ Successfully created account for **{username}** with pond location **{location}**!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to create account. Username might already exist.")
                    else:
                        st.warning("⚠️ Please provide a username, password, and confirm password.")

        # --- TAB 2: MANAGE ALL ACCOUNTS ---
        with tab2:
            st.markdown("#### 🗂️ System Users & Connected Ponds")
            accounts = fetch_all_accounts()
            if accounts:
                render_account_editor(accounts, is_admin=True)
            else:
                st.info("No accounts found.")

    # ==========================================
    # FARMER VIEW: Edit Own Profile Only
    # ==========================================
    else:
        st.markdown("#### 📝 Edit My Profile & Pond Details")
        accounts = fetch_all_accounts()
        
        # Filter the list so the farmer only sees their own account block
        my_account = [acc for acc in accounts if acc['id'] == current_user_id]
        
        if my_account:
            render_account_editor(my_account, is_admin=False)
        else:
            st.error("Account details not found.")


def render_account_editor(accounts, is_admin):
    """Reusable UI component that dynamically adjusts buttons based on role."""
    for acc in accounts:
        # Auto-expand the view if a farmer is looking at their solitary profile
        with st.expander(f"👤 {acc['username']} ({acc['role'].upper()}) - Pond: {acc['pond_name'] or 'N/A'}", expanded=not is_admin):
            with st.form(f"edit_acc_{acc['id']}"):
                st.text(f"User ID: {acc['id']} | Device SN: {acc['device_sn'] or 'None (Admin)'}")
                
                st.markdown("##### 🔐 Update Account Password")
                pw1, pw2 = st.columns(2)
                new_password = pw1.text_input("New Password (Leave blank to keep current)", type="password", key=f"npw_{acc['id']}")
                confirm_new_password = pw2.text_input("Confirm New Password", type="password", key=f"cpw_{acc['id']}")
                
                st.markdown("##### 🏡 Update Pond Details")
                e1, e2 = st.columns(2)
                p_name = e1.text_input("Pond Name", value=acc['pond_name'] or "", key=f"pn_{acc['id']}")
                p_loc = e2.text_input("Location", value=acc['location'] or "", key=f"loc_{acc['id']}")
                
                v1, v2, v3, v4, v5 = st.columns(5)
                p_len = v1.number_input("Length", value=float(acc['length'] or 25.0), key=f"len_{acc['id']}")
                p_wid = v2.number_input("Width", value=float(acc['width'] or 20.0), key=f"wid_{acc['id']}")
                p_dep = v3.number_input("Depth", value=float(acc['depth'] or 1.0), key=f"dep_{acc['id']}")
                p_fish = v4.number_input("Fish Count", value=int(acc['fish_count'] or 500), key=f"fc_{acc['id']}")
                p_phone = v5.text_input("Phone", value=acc['alert_phone'] or "", key=f"ph_{acc['id']}")
                
                # If Admin, show both Save and Delete buttons. If Farmer, only show Save.
                if is_admin:
                    col_save, col_del = st.columns([3, 1])
                else:
                    col_save = st.columns(1)[0]
                    col_del = None
                
                if col_save.form_submit_button("Save Changes", type="primary", use_container_width=True):
                    
                    # 1. Validate and Handle Password Update
                    if new_password or confirm_new_password:
                        if new_password != confirm_new_password:
                            st.error("❌ New passwords do not match! Details were not saved.")
                            st.stop() 
                        else:
                            if admin_update_password:
                                admin_update_password(acc['id'], new_password)
                            st.success("✅ Password validated and updated!")

                    # 2. Validate and Handle Pond Node Update
                    if acc['device_sn']:
                        updated_device = {
                            "device_sn": acc['device_sn'], "pond_name": p_name, "location": p_loc,
                            "length": p_len, "width": p_wid, "depth": p_dep, "fish_count": p_fish,
                            "alert_phone": p_phone, "alert_level": "Critical", "sleep_interval": 30, "ph_offset": 0.0, "turb_offset": 0.0
                        }
                        if update_device_settings(updated_device):
                            st.success("✅ Account & Pond details updated successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to update database.")
                    else:
                        if not (new_password and new_password == confirm_new_password):
                            st.warning("⚠️ Admin accounts do not have associated pond nodes. Only password can be updated.")
                        else:
                            st.rerun()
                            
                # Protect the master admin (ID 1) from deletion and restrict delete to Admins only
                if is_admin and col_del and acc['id'] != 1:  
                    if col_del.form_submit_button("Delete Account", type="secondary", use_container_width=True):
                        if admin_delete_account(acc['id']):
                            st.success(f"✅ Deleted user {acc['username']}.")
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete account.")