import sqlite3
import json

DB_FILE = 'air_hockey.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Updated Schema: Added 'participation' column with default 0
    c.execute('CREATE TABLE IF NOT EXISTS players (name TEXT PRIMARY KEY, participation INTEGER DEFAULT 0)')
    c.execute('CREATE TABLE IF NOT EXISTS tournament_state (id INTEGER PRIMARY KEY, data TEXT,status TEXT)')
    conn.commit()
    conn.close()

def get_all_players():
    conn = sqlite3.connect(DB_FILE)
    # Updated Query: Order by participation (Descending), then alphabetical
    cursor = conn.execute('SELECT name FROM players ORDER BY participation DESC, name ASC')
    players = [r[0] for r in cursor.fetchall()]
    conn.close()
    return players

def add_player_to_db(name):
    conn = sqlite3.connect(DB_FILE)
    try:
        # Default participation is 0
        conn.execute('INSERT INTO players (name, participation) VALUES (?, 0)', (name,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

def update_participation(player_names):
    """Increments the participation count for a list of players"""
    conn = sqlite3.connect(DB_FILE)
    # We use executemany for efficiency
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