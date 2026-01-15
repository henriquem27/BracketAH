import streamlit as st
import database as db
import game_logic as gl

def render_setup_tab():
    st.subheader("Add Players")
    with st.form("add_player_form", clear_on_submit=True):
        new_player = st.text_input("Player Name (Type & Hit Enter):")
        if st.form_submit_button("Add Player") and new_player:
            db.add_player_to_db(new_player)
            st.success(f"Added {new_player}")
            st.rerun()

    st.divider()
    st.subheader("Create Tournament")
    
    # Sort players by participation
    available_players = db.get_all_players()
    selected = st.multiselect("Select Players:", available_players)
    
    c1, c2 = st.columns(2)
    if c1.button("🚨 Generate Bracket", type="primary"):
        if len(selected) < 2:
            st.error("Need 2+ players")
        else:
            bracket = gl.generate_bracket(selected)
            db.update_participation(selected)
            db.save_bracket_state(bracket)
            st.success("Bracket Created! Go to 'Live Bracket' tab.")
            
    if c2.button("⚠️ Reset Data"):
        db.save_bracket_state(None)
        st.rerun()