import sqlite3
import json
import uuid
from datetime import datetime

DB_FILE = 'air_hockey.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS players (name TEXT PRIMARY KEY, participation INTEGER DEFAULT 0)')
    c.execute('CREATE TABLE IF NOT EXISTS tournament_state (id INTEGER PRIMARY KEY, data TEXT)')
    # NEW: Table for archival data
    c.execute('''CREATE TABLE IF NOT EXISTS match_history (
                    id TEXT PRIMARY KEY, 
                    tournament_id TEXT,
                    match_label TEXT, 
                    p1 TEXT, 
                    p2 TEXT, 
                    winner TEXT, 
                    timestamp DATETIME)''')
    conn.commit()
    conn.close()

# ... (Keep get_all_players, add_player_to_db, update_participation, save_bracket_state, load_bracket_state exactly as they were) ...
def get_all_players():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.execute('SELECT name FROM players ORDER BY participation DESC, name ASC')
    players = [r[0] for r in cursor.fetchall()]
    conn.close()
    return players

def add_player_to_db(name):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute('INSERT INTO players (name, participation) VALUES (?, 0)', (name,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

def update_participation(player_names):
    conn = sqlite3.connect(DB_FILE)
    data = [(name,) for name in player_names]
    conn.executemany('UPDATE players SET participation = participation + 1 WHERE name = ?', data)
    conn.commit()
    conn.close()

def save_bracket_state(bracket_data):
    conn = sqlite3.connect(DB_FILE)
    data_str = json.dumps(bracket_data) if bracket_data else None
    if data_str is None:
        conn.execute('DELETE FROM tournament_state WHERE id=1')
    else:
        conn.execute('INSERT OR REPLACE INTO tournament_state (id, data) VALUES (1, ?)', (data_str,))
    conn.commit()
    conn.close()

def load_bracket_state():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.execute('SELECT data FROM tournament_state WHERE id=1')
    row = cursor.fetchone()
    conn.close()
    if row and row[0]:
        return json.loads(row[0])
    return None

# --- NEW FEATURES ---

def rename_player_in_active_tournament(old_name, new_name, bracket_data):
    """Recursively finds and replaces a player name in the bracket JSON"""
    if not bracket_data: return None
    
    # Helper to clean a list of matches
    def clean_rounds(rounds_list):
        for round_matches in rounds_list:
            for m in round_matches:
                if m['p1'] == old_name: m['p1'] = new_name
                if m['p2'] == old_name: m['p2'] = new_name
                if m['winner'] == old_name: m['winner'] = new_name
                if m['loser'] == old_name: m['loser'] = new_name
    
    clean_rounds(bracket_data.get('winners', []))
    clean_rounds(bracket_data.get('losers', []))
    clean_rounds(bracket_data.get('finals', []))
    
    # Also update the Players Database
    conn = sqlite3.connect(DB_FILE)
    try:
        # Create new record
        conn.execute('INSERT INTO players (name) VALUES (?)', (new_name,))
        # Copy participation stats if you want (optional, skipping for simplicity)
        # Delete old record
        conn.execute('DELETE FROM players WHERE name = ?', (old_name,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass # New name might already exist
    conn.close()
    
    return bracket_data

def archive_tournament(bracket_data):
    """Writes all finished matches to history and clears active state"""
    if not bracket_data: return

    conn = sqlite3.connect(DB_FILE)
    tournament_id = str(uuid.uuid4())[:8] # Unique ID for this tourney
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    history_rows = []
    
    # Gather all matches
    all_rounds = bracket_data.get('winners', []) + bracket_data.get('losers', []) + bracket_data.get('finals', [])
    
    for round_matches in all_rounds:
        for m in round_matches:
            # Only save matches that actually happened
            if m['winner'] and m['p1'] and m['p2']:
                history_rows.append((
                    str(uuid.uuid4()),
                    tournament_id,
                    m['id'],
                    m['p1'],
                    m['p2'],
                    m['winner'],
                    timestamp
                ))
    
    if history_rows:
        conn.executemany('''INSERT INTO match_history (id, tournament_id, match_label, p1, p2, winner, timestamp) 
                            VALUES (?, ?, ?, ?, ?, ?, ?)''', history_rows)
        conn.commit()
    
    conn.close()