# update_subnets.py
import sqlite3

def add_subnet_column():
    conn = sqlite3.connect('hostel.db')
    cursor = conn.cursor()
    
    # Add subnet column to students table (if not exists)
    try:
        cursor.execute('ALTER TABLE students ADD COLUMN subnet TEXT')
        print("Added subnet column to students table")
    except sqlite3.OperationalError:
        print("Subnet column already exists")
    
    # Update each student with their hostel's subnet
    subnets = {
        'Mark Hostel': '192.168.110.',
        'Luke Hostel': '196.43.235.34',
        'Matthew Hostel': '192.168.3.',
        'John Hostel': '192.168.4.',
    }
    
    for hostel, subnet in subnets.items():
        cursor.execute('UPDATE students SET subnet = ? WHERE hostel = ?', (subnet, hostel))
        print(f"Updated {hostel} -> subnet: {subnet}x")
    
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    add_subnet_column()