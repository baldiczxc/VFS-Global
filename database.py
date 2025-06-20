import sqlite3

def init_db():
    with sqlite3.connect('vfs_metrics.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slots_checked INTEGER DEFAULT 0,
                active_users INTEGER DEFAULT 0,
                successful_records INTEGER DEFAULT 0,
                errors INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                attempts INTEGER,
                successful INTEGER,
                booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                hour INTEGER,
                date TEXT
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS system_status (
                component TEXT PRIMARY KEY,
                status TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
