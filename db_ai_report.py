import sqlite3
from datetime import datetime

def create_ai_report_table():
    """Create the aiReport table if it doesn't exist"""
    try:
        conn = sqlite3.connect('properties.db')
        cursor = conn.cursor()
        
        # Create aiReport table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS aiReport (
            reportID INTEGER PRIMARY KEY AUTOINCREMENT,
            reportFilePath TEXT NOT NULL,
            time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        print("AI Report table created successfully")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    
    finally:
        if conn:
            conn.close()

def insert_report(file_path):
    """Insert a new report record"""
    try:
        conn = sqlite3.connect('properties.db')
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO aiReport (reportFilePath, time)
        VALUES (?, ?)
        ''', (file_path, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        conn.commit()
        report_id = cursor.lastrowid
        print(f"Report inserted successfully with ID: {report_id}")
        return report_id
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
        
    finally:
        if conn:
            conn.close()

def get_latest_report():
    """Get the most recent report"""
    try:
        conn = sqlite3.connect('properties.db')
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT reportID, reportFilePath, time 
        FROM aiReport 
        ORDER BY time DESC 
        LIMIT 1
        ''')
        
        report = cursor.fetchone()
        return report  # Returns (reportID, reportFilePath, time) or None
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
        
    finally:
        if conn:
            conn.close()

def get_all_reports():
    """Get all reports ordered by time"""
    try:
        conn = sqlite3.connect('properties.db')
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT reportID, reportFilePath, time 
        FROM aiReport 
        ORDER BY time DESC
        ''')
        
        reports = cursor.fetchall()
        return reports  # Returns list of (reportID, reportFilePath, time)
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
        
    finally:
        if conn:
            conn.close()

def delete_report(report_id):
    """Delete a specific report by ID"""
    try:
        conn = sqlite3.connect('properties.db')
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM aiReport WHERE reportID = ?', (report_id,))
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"Report {report_id} deleted successfully")
            return True
        else:
            print(f"No report found with ID {report_id}")
            return False
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
        
    finally:
        if conn:
            conn.close()

# Create the table when the module is imported
if __name__ == "__main__":
    create_ai_report_table() 