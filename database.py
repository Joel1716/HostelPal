import sqlite3

def create_database():
    conn = sqlite3.connect('hostel.db')
    cursor = conn.cursor()
    
    # Create students table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        matric_number TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        hostel TEXT NOT NULL,
        room_number TEXT NOT NULL,
        enrolled INTEGER DEFAULT 0
    )
    ''')
    
    # Create face_vectors table (references encrypted vector files)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS face_vectors (
        matric_number TEXT PRIMARY KEY,
        vector_path TEXT NOT NULL,
        enrolled_at TEXT NOT NULL,
        FOREIGN KEY (matric_number) REFERENCES students (matric_number)
    )
    ''')
    
    # Create attendance_log table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendance_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        matric_number TEXT NOT NULL,
        name TEXT NOT NULL,
        hostel TEXT NOT NULL,
        room_number TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (matric_number) REFERENCES students (matric_number)
    )
    ''')
    
    conn.commit()
    conn.close()
    print("Database created successfully!")

if __name__ == "__main__":
    create_database()