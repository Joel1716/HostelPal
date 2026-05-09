import sqlite3

def insert_students():
    conn = sqlite3.connect('hostel.db')
    cursor = conn.cursor()
    
    # Sample student data (replace with your questionnaire data later)
    students = [
        ('BUI/001', 'John Doe', 'Mark Hostel', '101', 0),
        ('BUI/002', 'Jane Smith', 'Mark Hostel', '102', 0),
        ('BUI/003', 'Peter Okafor', 'Luke Hostel', '201', 0),
        ('BUI/004', 'Amina Bello', 'Mark Hostel', '103', 0),
        ('BUI/005', 'Chidi Nwosu', 'Matthew Hostel', '301', 0),
    ]
    
    cursor.executemany('''
    INSERT OR REPLACE INTO students (matric_number, name, hostel, room_number, enrolled)
    VALUES (?, ?, ?, ?, ?)
    ''', students)
    
    conn.commit()
    conn.close()
    print(f"{len(students)} students inserted successfully!")

if __name__ == "__main__":
    insert_students()