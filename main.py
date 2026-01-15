import streamlit as st
import database as db
import styles
import auth
import view_bracket
import view_manager

# 1. Setup
st.set_page_config(page_title="Air Hockey Bracket", layout="wide")
styles.load_css()
db.init_db()

# 2. Sidebar Navigation
st.sidebar.title("🏒 Navigation")

# Top-level choice: Are you watching or managing?
# We use a key='nav_mode' so Streamlit remembers this selection perfectly
view_mode = st.sidebar.radio(
    "Select Mode:", 
    ["👀 Spectator View", "🔧 Manager Portal"],
    key="nav_mode"
)

# 3. Routing
if view_mode == "👀 Spectator View":
    # --- SPECTATOR MODE ---
    view_bracket.render_bracket(is_manager=False)

elif view_mode == "🔧 Manager Portal":
    # --- MANAGER MODE ---
    
    # 1. Check Login
    auth.login_form()
    
    if auth.check_password():
        st.sidebar.divider()
        st.sidebar.markdown("### Manager Tools")
        
        # FIX: Use Radio instead of Tabs to prevent "jumping"
        # This keeps you on the same page after clicking "Win"
        manager_task = st.sidebar.radio(
            "Go to:", 
            ["🏆 Live Bracket", "🔧 Player Setup"],
            key="manager_nav"
        )
        
        if manager_task == "🏆 Live Bracket":
            view_bracket.render_bracket(is_manager=True)
            
        elif manager_task == "🔧 Player Setup":
            view_manager.render_setup_tab()
    else:
        st.info("Please log in via the sidebar to access Manager Tools.")