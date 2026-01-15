import streamlit as st
import database as db
import game_logic as gl
import textwrap

def render_bracket(is_manager=False):
    st.markdown("## 🏆 Tournament Bracket")
    
    # Manager Tools (Reset/Refresh)
    c1, c2 = st.columns([1, 8])
    if c1.button("🔄 Refresh"):
        st.rerun()
    
    bracket_data = db.load_bracket_state()
    if not bracket_data:
        st.info("Waiting for tournament to start...")
        return

    # 1. Render Winners Bracket
    st.markdown("### 🔥 Winners Bracket")
    _render_tree(bracket_data, bracket_data['winners'], is_manager, "W")

    st.markdown("---")

    # 2. Render Losers Bracket (if active)
    if bracket_data.get('losers'):
        st.markdown("### 🛡️ Losers Bracket")
        _render_tree(bracket_data, bracket_data['losers'], is_manager, "L")

def _render_tree(full_bracket_data, rounds, is_manager, prefix):
    # CSS Constants for Spacer Logic
    CARD_HEIGHT = 85 # Slightly taller to fit buttons
    BASE_GAP = 20
    
    cols = st.columns(len(rounds))
    
    for r_idx, round_matches in enumerate(rounds):
        with cols[r_idx]:
            st.caption(f"Round {r_idx + 1}")
            
            # --- SPACER CALCULATION ---
            # Centers the match vertically relative to previous round
            top_pad_units = (2 ** r_idx) - 1
            between_pad_units = (2 ** (r_idx + 1)) - 1
            
            # Draw Top Spacer
            if top_pad_units > 0:
                h = top_pad_units * (CARD_HEIGHT/2 + BASE_GAP/2)
                st.write(f"<div style='height: {h}px'></div>", unsafe_allow_html=True)

            for m_idx, match in enumerate(round_matches):
                # RENDER INDIVIDUAL MATCH
                if is_manager:
                    _render_interactive_match(full_bracket_data, match)
                else:
                    _render_static_match(match)
                
                # Draw Spacer Between Matches
                if m_idx < len(round_matches) - 1:
                    h = between_pad_units * (CARD_HEIGHT/2 + BASE_GAP/2) + BASE_GAP
                    st.write(f"<div style='height: {h}px'></div>", unsafe_allow_html=True)

def _render_interactive_match(bracket_data, match):
    """MANAGER VIEW: Renders clickable buttons"""
    # Container with distinct background
    with st.container():
        st.markdown(f"""<div style="padding: 5px; background: #2b2b2b; border-left: 3px solid #f47920; border-radius: 4px; margin-bottom: 5px;">""", unsafe_allow_html=True)
        
        # Player 1 Button
        p1 = match.get('p1') or "Waiting..."
        if st.button(f"{'✅ ' if match['winner']==p1 else ''}{p1}", 
                     key=f"btn_{match['id']}_p1", 
                     use_container_width=True,
                     disabled=(match['winner'] is not None) or (match['p1'] is None)):
            _handle_win(bracket_data, match, match['p1'], match['p2'])

        # Player 2 Button
        p2 = match.get('p2') or "Waiting..."
        if st.button(f"{'✅ ' if match['winner']==p2 else ''}{p2}", 
                     key=f"btn_{match['id']}_p2", 
                     use_container_width=True,
                     disabled=(match['winner'] is not None) or (match['p2'] is None)):
            _handle_win(bracket_data, match, match['p2'], match['p1'])
        
        st.markdown("</div>", unsafe_allow_html=True)

def _render_static_match(match):
    """SPECTATOR VIEW: Renders pretty HTML"""
    p1 = match.get('p1') or "Waiting..."
    p2 = match.get('p2') or "Waiting..."
    
    # Styling logic
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
        </div>
    """)
    st.markdown(html, unsafe_allow_html=True)

def _handle_win(bracket_data, match, winner, loser):
    match['winner'] = winner
    match['loser'] = loser
    gl.advance_bracket(bracket_data)
    db.save_bracket_state(bracket_data)
    st.rerun()