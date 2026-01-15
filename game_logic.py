import random
import math

def generate_bracket(players):
    players = players.copy()
    random.shuffle(players)
    
    # 1. Pad to next power of 2
    next_pow_2 = 2 ** math.ceil(math.log2(len(players)))
    while len(players) < next_pow_2:
        players.append("BYE")
    
    bracket = {
        "winners": [],
        "losers": [],
        "finals": [],
        "meta": {"total_players": len(players)}
    }

    # --- WINNERS BRACKET SKELETON ---
    current_count = len(players) // 2
    w_round_count = 0
    while current_count >= 1:
        w_round_count += 1
        round_matches = []
        for i in range(current_count):
            match = {
                "id": f"W{w_round_count}-{i+1}",
                "p1": None, "p2": None,
                "winner": None, "loser": None,
                "next_w": None, "next_l": None 
            }
            if w_round_count == 1:
                match['p1'] = players[i*2]
                match['p2'] = players[i*2+1]
                # No auto-win here logic anymore, manual control only
            
            round_matches.append(match)
        bracket['winners'].append(round_matches)
        current_count //= 2

    # --- LOSERS BRACKET SKELETON ---
    # Standard Double Elim Pattern for N players
    l_match_counts = []
    count = len(players) // 4
    for _ in range(len(bracket['winners']) - 1):
        l_match_counts.append(count) # Drop Round
        l_match_counts.append(count) # Advancement Round
        count //= 2
        
    for r_idx, count in enumerate(l_match_counts):
        round_matches = []
        for i in range(count):
            match = {
                "id": f"L{r_idx+1}-{i+1}",
                "p1": None, "p2": None,
                "winner": None, "loser": None,
                "next_w": None
            }
            round_matches.append(match)
        bracket['losers'].append(round_matches)

    # --- FINALS SKELETON ---
    bracket['finals'].append([{
        "id": "F1-1",
        "p1": None, "p2": None,
        "winner": None, "loser": None,
        "next_w": None 
    }])

    # --- LINKING LOGIC (The Fix is Here) ---
    _link_brackets(bracket)
    
    return bracket

def _link_brackets(bracket):
    w_rounds = bracket['winners']
    l_rounds = bracket['losers']
    
    # 1. LINK WINNERS BRACKET
    for r_idx, rounds in enumerate(w_rounds):
        for m_idx, match in enumerate(rounds):
            # Advance Winner
            if r_idx < len(w_rounds) - 1:
                match['next_w'] = f"W{r_idx+2}-{m_idx//2+1}"
            else:
                match['next_w'] = "F1-1"
            
            # --- LOSER DROP LOGIC ---
            # Determine which round in Losers Bracket to target
            if r_idx == 0:
                l_target_round = 0 # W1 losers -> L1
            else:
                l_target_round = (r_idx * 2) - 1 # W2->L2, W3->L4
            
            if l_target_round < len(l_rounds):
                # FIXED MAPPING LOGIC:
                # In W Round 1, TWO W-matches feed ONE L-match.
                # W-Match 0 & 1 -> L-Match 0
                # W-Match 2 & 3 -> L-Match 1
                if r_idx == 0:
                    target_match_idx = m_idx // 2
                else:
                    # In later rounds, it's often 1-to-1 mapping
                    target_match_idx = m_idx
                
                # Safety check
                if target_match_idx < len(l_rounds[l_target_round]):
                    match['next_l'] = f"L{l_target_round+1}-{target_match_idx+1}"

    # 2. LINK LOSERS BRACKET
    for r_idx, rounds in enumerate(l_rounds):
        for m_idx, match in enumerate(rounds):
            if r_idx < len(l_rounds) - 1:
                is_even_round = ((r_idx + 1) % 2 == 0)
                if is_even_round:
                    # L2->L3 (Compression Round: 2 matches -> 1 match)
                    match['next_w'] = f"L{r_idx+2}-{m_idx//2+1}"
                else:
                    # L1->L2 (Direct Round: 2 matches -> 2 matches)
                    match['next_w'] = f"L{r_idx+2}-{m_idx+1}"
            else:
                match['next_w'] = "F1-1"

def advance_bracket(bracket):
    all_rounds = bracket['winners'] + bracket['losers'] + bracket['finals']
    
    for round_matches in all_rounds:
        for m in round_matches:
            if m['winner']:
                # Smart Preference Logic
                prefer_p1 = True 
                if m['id'].startswith('L'): prefer_p1 = False
                if m['id'].startswith('W'): prefer_p1 = True

                _fill_slot(bracket, m['next_w'], m['winner'], prefer_p1)
                
                # Move Loser
                if m.get('next_l') and m['loser'] and m['loser'] != "BYE":
                    _fill_slot(bracket, m['next_l'], m['loser'], prefer_p1=True)

    # Secondary Pass for internal L-bracket movement
    for round_matches in bracket['losers']:
        for m in round_matches:
            if m['winner']:
                 _fill_slot(bracket, m['next_w'], m['winner'], prefer_p1=False)

    return bracket

def _fill_slot(bracket, target_id, player_name, prefer_p1=None):
    if not target_id: return 

    target_match = None
    all_rounds = bracket['winners'] + bracket['losers'] + bracket['finals']
    
    for rounds in all_rounds:
        for m in rounds:
            if m['id'] == target_id:
                target_match = m
                break
        if target_match: break
    
    if not target_match: return

    # Avoid adding duplicates if the player is already there
    if target_match['p1'] == player_name or target_match['p2'] == player_name:
        return

    # Slotting Logic
    if prefer_p1 is True:
        if target_match['p1'] is None: target_match['p1'] = player_name
        elif target_match['p2'] is None: target_match['p2'] = player_name
    elif prefer_p1 is False:
        if target_match['p2'] is None: target_match['p2'] = player_name
        elif target_match['p1'] is None: target_match['p1'] = player_name
    else:
        if target_match['p1'] is None: target_match['p1'] = player_name
        elif target_match['p2'] is None: target_match['p2'] = player_name
def undo_match(bracket, match_id):
    """
    Reverts a match result. 
    Recursively clears the player from future matches to prevent broken states.
    """
    match = _find_match_by_id(bracket, match_id)
    if not match or not match['winner']: 
        return bracket

    winner = match['winner']
    loser = match['loser']

    # 1. Recursively clean the Winner's path
    if match.get('next_w'):
        _remove_player_from_match(bracket, match['next_w'], winner)
    
    # 2. Recursively clean the Loser's path (if they dropped)
    if match.get('next_l') and loser != "BYE":
        _remove_player_from_match(bracket, match['next_l'], loser)

    # 3. Reset the current match
    match['winner'] = None
    match['loser'] = None
    
    return bracket

def _remove_player_from_match(bracket, match_id, player_name):
    """Removes a player from a target match. If they already won that match, undo it first."""
    target = _find_match_by_id(bracket, match_id)
    if not target: return

    # RECURSION SAFETY: 
    # If the player we are removing has ALREADY won this future match,
    # we must undo this match first to prevent a "ghost winner".
    if target['winner'] == player_name:
        undo_match(bracket, target['id'])

    # Remove the player from the slot
    if target['p1'] == player_name: target['p1'] = None
    if target['p2'] == player_name: target['p2'] = None

def _find_match_by_id(bracket, match_id):
    """Helper to find a match dict anywhere in the bracket"""
    all_rounds = bracket['winners'] + bracket['losers'] + bracket['finals']
    for rounds in all_rounds:
        for m in rounds:
            if m['id'] == match_id:
                return m
    return None