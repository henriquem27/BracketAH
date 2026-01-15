import streamlit as st
import database as db
import game_logic as gl

def render_setup_tab():
    st.markdown("### 🛠️ Tournament Admin")
    
    # --- ARCHIVE TOOL ---
    with st.expander("Conclude Tournament", expanded=True):
        st.warning("This will save results to history and clear the current bracket.")
        if st.button("💾 Archive & Reset"):
            bracket = db.load_bracket_state()
            if bracket:
                db.archive_tournament(bracket)
                db.save_bracket_state(None) # Clear active state
                st.success("Tournament saved to history!")
                st.rerun()
            else:
                st.error("No active tournament to archive.")

    st.divider()
    
    # --- STANDARD SETUP ---
    st.subheader("Add Players")
    with st.form("add_player_form", clear_on_submit=True):
        new_player = st.text_input("Player Name (Type & Hit Enter):")
        if st.form_submit_button("Add Player") and new_player:
            db.add_player_to_db(new_player)
            st.success(f"Added {new_player}")
            st.rerun()

    st.subheader("Start New Tournament")
    available_players = db.get_all_players()
    selected = st.multiselect("Select Players:", available_players)
    
    if st.button("🚨 Generate Bracket", type="primary"):
        if len(selected) < 2:
            st.error("Need 2+ players")
        else:
            bracket = gl.generate_bracket(selected)
            db.update_participation(selected)
            db.save_bracket_state(bracket)
            st.success("Bracket Created! Go to 'Live Bracket' tab.")