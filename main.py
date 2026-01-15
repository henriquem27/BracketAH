import streamlit as st
import database as db
import styles
import auth
import view_bracket
import view_manager # We still keep this for "Player Setup"

# 1. Setup
st.set_page_config(page_title="Air Hockey Bracket", layout="wide")
styles.load_css()
db.init_db()

# 2. Sidebar Auth
auth.login_form()
is_logged_in = auth.check_password()

# 3. Main Routing
if is_logged_in:
    # --- MANAGER MODE ---
    # Tabs: 1. Setup (Add Players), 2. Live Bracket (Interactive)
    tab1, tab2 = st.tabs(["🔧 Player Setup", "🏆 Live Bracket"])
    
    with tab1:
        # We reuse the setup code from view_manager
        view_manager.render_setup_tab() 
        
    with tab2:
        # Render the bracket in "Manager Mode" (Clickable)
        view_bracket.render_bracket(is_manager=True)

else:
    # --- SPECTATOR MODE ---
    # No tabs, just the bracket
    view_bracket.render_bracket(is_manager=False)