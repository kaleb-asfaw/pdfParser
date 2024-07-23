import sqlite3

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def find_user_by_email(email):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    return user

def create_user(email, password):
    conn = get_db_connection()
    conn.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, password))
    conn.commit()
    conn.close()

def create_users_table():
    conn = sqlite3.connect('database.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )''')
    conn.close()

def create_files_table():
    conn = sqlite3.connect('database.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS user_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        pdf_path TEXT,
        mp3_path TEXT,
        summary_text TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    conn.close()

def print_table_contents():
    # Connect to the SQLite database
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Execute a query to select all data from the user_files table
    cursor.execute("SELECT * FROM user_files")

    # Fetch all rows from the query result
    rows = cursor.fetchall()

    # Print the rows
    for row in rows:
        print(row)

    # Close the connection
    conn.close()

print_table_contents()

create_users_table()
create_files_table()

