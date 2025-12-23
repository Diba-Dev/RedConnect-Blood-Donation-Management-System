import sqlite3

DB_NAME = "redconnect.db"

# --------------------------
# Helper to get DB connection
# --------------------------
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  
    return conn

# --------------------------
# Initialize the database and tables
# --------------------------
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    # USERS TABLE
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                blood_group TEXT,
                location TEXT,
                phone TEXT,
                is_admin INTEGER DEFAULT 0,
                is_donor INTEGER DEFAULT 0
            )
        """)
    # BLOOD STOCK TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blood_stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            blood_group TEXT NOT NULL,
            units INTEGER NOT NULL,
            location TEXT NOT NULL,
            last_updated DATE DEFAULT CURRENT_DATE
        )
    """)

    # BLOOD REQUESTS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blood_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            blood_group TEXT NOT NULL,
            location TEXT NOT NULL,
            units INTEGER NOT NULL,
            message TEXT,
            status TEXT DEFAULT 'Pending',
            request_date DATE DEFAULT CURRENT_DATE,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # DONATIONS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            blood_group TEXT NOT NULL,
            donation_type TEXT NOT NULL,
            donation_date DATE NOT NULL,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # NOTIFICATIONS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            type TEXT DEFAULT 'info',
            admin_name TEXT,
            admin_phone TEXT,
            created_at DATE DEFAULT CURRENT_DATE,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    cursor.execute("INSERT OR IGNORE INTO users (name, email, password, is_admin) VALUES (?, ?, ?, ?)",
                   ("Admin User", "admin@gmail.com", "admin", 1))

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

