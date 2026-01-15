import random
import math

def generate_bracket(players):
    players = players.copy()
    random.shuffle(players)
    
    # 1. Pad to power of 2 (4, 8, 16, 32)
    next_pow_2 = 2 ** math.ceil(math.log2(len(players)))
    while len(players) < next_pow_2:
        players.append("BYE")
        
    num_matches = len(players) // 2
    
    # --- STRUCTURE ---
    bracket = {
        "winners": [],  # List of Lists (Rounds)
        "losers": [],   # List of Lists
        "finals": [],   # The Grand Final
        "meta": {"total_players": len(players)}
    }

    # --- WINNERS BRACKET ROUND 1 ---
    w_round_1 = []
    for i in range(num_matches):
        p1 = players[i*2]
        p2 = players[i*2+1]
        match = {
            "id": f"W1-{i+1}", 
            "p1": p1, "p2": p2, 
            "winner": None, "loser": None,
            "next_w": f"W2-{i//2+1}",          # Winner goes here
            "next_l": f"L1-{i//2+1}"           # Loser drops here
        }
        # Auto-advance BYEs immediately
        if p2 == "BYE":
            match['winner'] = p1
            match['loser'] = "BYE"
        w_round_1.append(match)
    bracket['winners'].append(w_round_1)

    # --- BUILD EMPTY BRACKET SKELETON ---
    # We simulate the rounds to create empty slots
    # Logic: Winners Bracket just halves every round
    current_count = num_matches
    r = 2
    while current_count > 1:
        current_count //= 2
        round_matches = []
        for i in range(current_count):
            match = {
                "id": f"W{r}-{i+1}", 
                "p1": None, "p2": None, 
                "winner": None, "loser": None,
                "next_w": f"W{r+1}-{i//2+1}" if current_count > 1 else "F1-1",
                "next_l": _calculate_loser_drop(r, i+1) # Complex logic for where losers go
            }
            round_matches.append(match)
        bracket['winners'].append(round_matches)
        r += 1

    # --- LOSERS BRACKET SKELETON ---
    # Complex: LB has more rounds than WB.
    # Pattern: R1(Drop from W1), R2(Winners of L1 vs Drop from W2), R3(Winners of L2), etc.
    # For a simple portfolio project, we will build a simplified generic container.
    # The 'advance' function will generate LB matches dynamically to avoid complex pre-calculation.
    
    return bracket

def _calculate_loser_drop(round_num, match_num):
    # Mapping logic: W Round 2 losers -> L Round 2 (or specific slot)
    # For this snippet, we'll handle drops dynamically in advance_bracket
    return f"L_DROP_R{round_num}"

def advance_bracket(bracket):
    # This function now checks EVERY match to see if data needs to move
    # 1. Propagate Winners Bracket
    for r_idx, round_matches in enumerate(bracket['winners']):
        for m in round_matches:
            if m['winner']:
                # Move Winner
                _update_match_slot(bracket, m['next_w'], m['winner'])
                # Move Loser (if not BYE)
                if m['loser'] and m['loser'] != "BYE":
                    _place_loser_into_lb(bracket, r_idx + 1, m['loser'])

    # 2. Propagate Losers Bracket
    # (Simple logic: If a match has 2 players, it's ready. If winner, move next.)
    for r_idx, round_matches in enumerate(bracket['losers']):
        for m in round_matches:
            if m['winner']:
                _update_match_slot(bracket, m['next_w'], m['winner'])

    return bracket

def _update_match_slot(bracket, target_id, player_name):
    # Find the match with target_id in Winners or Losers or Finals
    # And fill the first empty slot (p1 or p2)
    
    # Helper to search all lists
    all_rounds = bracket['winners'] + bracket['losers'] + [bracket.get('finals', [])]
    
    for round_matches in all_rounds:
        for m in round_matches:
            if m['id'] == target_id:
                if m['p1'] == player_name or m['p2'] == player_name:
                    return # Already added
                if m['p1'] is None:
                    m['p1'] = player_name
                elif m['p2'] is None:
                    m['p2'] = player_name
                return

def _place_loser_into_lb(bracket, source_wb_round, player_name):
    # This is the tricky "Double Elim" logic.
    # WB Round 1 Losers -> LB Round 1
    # WB Round 2 Losers -> LB Round 2 (playing against Winners of LB R1)
    
    # Ensure LB Round exists
    lb_round_idx = (source_wb_round - 1) * 2 
    # Example: WB R1 (idx 0) -> LB R0. WB R2 (idx 1) -> LB R2 (Wait for LB R1 winners)
    
    if source_wb_round > 1:
        lb_round_idx -= 1 # Adjustment for the structure
        
    # Check if round exists, if not create it
    while len(bracket['losers']) <= lb_round_idx:
        bracket['losers'].append([])
        
    target_round = bracket['losers'][lb_round_idx]
    
    # Find a match with an open slot or create new
    for m in target_round:
        if m['p1'] is None or m['p2'] is None:
             if m['p1'] != player_name and m['p2'] != player_name:
                _update_match_slot(bracket, m['id'], player_name)
                return

    # If no spot, create new match in this LB round
    new_id = f"L{lb_round_idx+1}-{len(target_round)+1}"
    next_w_id = f"L{lb_round_idx+2}-{(len(target_round)//2)+1}" # Next match logic
    
    new_match = {
        "id": new_id, "p1": player_name, "p2": None, 
        "winner": None, "loser": None, # Loser here is out for good
        "next_w": next_w_id
    }
    target_round.append(new_match)