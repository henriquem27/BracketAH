import streamlit as st
import database as db
import game_logic as gl
import textwrap

# --- POPUP MODAL ---
@st.dialog("✏️ Edit Player Name")
def rename_modal():
    st.write("Fix a typo or update a name instantly.")
    
    # We load the bracket just to check valid names
    bracket = db.load_bracket_state()
    if not bracket:
        st.error("No active tournament found.")
        return

    # Helper: Get list of current names for a dropdown (easier than typing old name)
    current_names = _extract_names_from_bracket(bracket)
    
    with st.form("rename_form"):
        old_name = st.selectbox("Select Player to Rename:", current_names)
        new_name = st.text_input("New Name:")
        
        if st.form_submit_button("Update Name"):
            if old_name and new_name:
                updated_bracket = db.rename_player_in_active_tournament(old_name, new_name, bracket)
                db.save_bracket_state(updated_bracket)
                st.success(f"Renamed {old_name} to {new_name}")
                st.rerun()
            else:
                st.error("Please provide a new name.")

def _extract_names_from_bracket(bracket):
    """Helper to find all unique names currently in the bracket"""
    names = set()
    all_rounds = bracket.get('winners', []) + bracket.get('losers', []) + bracket.get('finals', [])
    for rounds in all_rounds:
        for m in rounds:
            if m['p1']: names.add(m['p1'])
            if m['p2']: names.add(m['p2'])
            if m['winner']: names.add(m['winner'])
            if m['loser']: names.add(m['loser'])
    
    # Filter out "BYE" and return sorted list
    if "BYE" in names: names.remove("BYE")
    return sorted(list(names))


# --- MAIN RENDERER ---
def render_bracket(is_manager=False):
    st.markdown("## 🏆 Tournament Bracket")
    
    # MANAGER TOOLBAR
    if is_manager:
        c1, c2, c3 = st.columns([1, 1, 6])
        if c1.button("🔄 Refresh"):
            st.rerun()
        if c2.button("✏️ Edit Names"):
            rename_modal() # Opens the popup
    else:
        if st.button("🔄 Refresh Bracket"):
            st.rerun()
    
    bracket_data = db.load_bracket_state()
    if not bracket_data:
        st.info("Waiting for tournament to start...")
        return

    # --- HORIZONTAL SCROLL HACK ---
    num_w_rounds = len(bracket_data['winners'])
    num_l_rounds = len(bracket_data.get('losers', []))
    total_rounds = max(num_w_rounds, num_l_rounds) + (1 if bracket_data.get('finals') else 0)
    
    col_width = 340 
    total_width = total_rounds * col_width
    
    st.markdown(f"""
        <style>
        .block-container {{
            max-width: {total_width}px !important;
            padding-left: 2rem;
            padding-right: 2rem;
        }}
        </style>
    """, unsafe_allow_html=True)

    # --- RENDER SECTIONS ---
    st.markdown("### 🔥 Winners Bracket")
    _render_tree(bracket_data, bracket_data['winners'], is_manager, "W")

    if bracket_data.get('losers'):
        st.markdown("---")
        st.markdown("### 🛡️ Losers Bracket")
        _render_tree(bracket_data, bracket_data['losers'], is_manager, "L")

    if bracket_data.get('finals'):
        st.markdown("---")
        st.markdown("### 👑 Grand Finals")
        _render_tree(bracket_data, bracket_data['finals'], is_manager, "F")

def _render_tree(full_bracket_data, rounds, is_manager, prefix):
    # CSS Constants
    CARD_HEIGHT = 85 
    BASE_GAP = 20
    
    cols = st.columns(len(rounds))
    
    for r_idx, round_matches in enumerate(rounds):
        with cols[r_idx]:
            st.caption(f"Round {r_idx + 1}")
            
            top_pad_units = (2 ** r_idx) - 1
            between_pad_units = (2 ** (r_idx + 1)) - 1
            
            if top_pad_units > 0:
                h = top_pad_units * (CARD_HEIGHT/2 + BASE_GAP/2)
                st.write(f"<div style='height: {h}px'></div>", unsafe_allow_html=True)

            for m_idx, match in enumerate(round_matches):
                if is_manager:
                    _render_interactive_match(full_bracket_data, match)
                else:
                    _render_static_match(match)
                
                if m_idx < len(round_matches) - 1:
                    h = between_pad_units * (CARD_HEIGHT/2 + BASE_GAP/2) + BASE_GAP
                    st.write(f"<div style='height: {h}px'></div>", unsafe_allow_html=True)

def _render_interactive_match(bracket_data, match):
    """MANAGER VIEW"""
    with st.container():
        # Dynamic Border Color: Orange if active, Green if done
        border_color = "#4CAF50" if match['winner'] else "#f47920"
        
        st.markdown(f"""<div style="padding: 5px; background: #2b2b2b; border-left: 3px solid {border_color}; border-radius: 4px; margin-bottom: 5px;">""", unsafe_allow_html=True)
        
        # --- IF MATCH HAS A WINNER: SHOW UNDO BUTTON ---
        if match['winner']:
            st.markdown(f"<div style='text-align:center; color: #4CAF50; font-weight:bold; font-size: 14px; margin-bottom: 5px;'>🎉 {match['winner']} Won</div>", unsafe_allow_html=True)
            
            # Undo Button
            if st.button("↩️ Undo Result", key=f"undo_{match['id']}", use_container_width=True):
                gl.undo_match(bracket_data, match['id'])
                db.save_bracket_state(bracket_data)
                st.rerun()

        # --- IF MATCH IS OPEN: SHOW WIN BUTTONS ---
        else:
            p1 = match.get('p1') or "Waiting..."
            # Disable button if player isn't there yet
            p1_disabled = (match['p1'] is None)
            
            if st.button(f"{p1}", key=f"btn_{match['id']}_p1", use_container_width=True, disabled=p1_disabled):
                _handle_win(bracket_data, match, match['p1'], match['p2'])

            p2 = match.get('p2') or "Waiting..."
            p2_disabled = (match['p2'] is None)
            
            if st.button(f"{p2}", key=f"btn_{match['id']}_p2", use_container_width=True, disabled=p2_disabled):
                _handle_win(bracket_data, match, match['p2'], match['p1'])
        
        st.markdown("</div>", unsafe_allow_html=True)

def _render_static_match(match):
    """SPECTATOR VIEW"""
    p1 = match.get('p1') or "Waiting..."
    p2 = match.get('p2') or "Waiting..."
    
    p1_cls = "winner-text" if match['winner'] == p1 and match['winner'] else ""
    p2_cls = "winner-text" if match['winner'] == p2 and match['winner'] else ""
    p1_mark = "✓" if match['winner'] == p1 and match['winner'] else ""
    p2_mark = "✓" if match['winner'] == p2 and match['winner'] else ""
    p1_box = "winner-box" if match['winner'] == p1 and match['winner'] else ""
    p2_box = "winner-box" if match['winner'] == p2 and match['winner'] else ""

    html = textwrap.dedent(f"""
        <div class="match-card">
            <div class="player-row">
                <span class="player-name {p1_cls}">{p1}</span>
                <span class="score-box {p1_box}">{p1_mark}</span>
            </div>
            <div class="divider"></div>
            <div class="player-row">
                <span class="player-name {p2_cls}">{p2}</span>
                <span class="score-box {p2_box}">{p2_mark}</span>
            </div>
            <div class="connector-r"></div>
        </div>
    """)
    st.markdown(html, unsafe_allow_html=True)

def _handle_win(bracket_data, match, winner, loser):
    match['winner'] = winner
    match['loser'] = loser
    gl.advance_bracket(bracket_data)
    db.save_bracket_state(bracket_data)
    st.rerun()