import sqlite3

def ensure_column(cursor, table, column, coltype):
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [col[1] for col in cursor.fetchall()]
    if column not in columns:
        cursor.execute(f'ALTER TABLE {table} ADD COLUMN {column} {coltype}')

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # Таблица metrics
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slots_checked INTEGER DEFAULT 0,
        active_users INTEGER DEFAULT 0,
        successful_records INTEGER DEFAULT 0,
        errors INTEGER DEFAULT 0,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    # Таблица system_status
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS system_status (
        component TEXT PRIMARY KEY,
        status TEXT,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    # Таблица bookings
    cursor.execute('''
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
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully!")
