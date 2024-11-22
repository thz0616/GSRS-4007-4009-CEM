import sqlite3
from datetime import date, timedelta

conn = sqlite3.connect('properties.db')
cursor = conn.cursor()

# Create the tenants table (as you already have)
cursor.execute('''
CREATE TABLE IF NOT EXISTS tenants (
    tenantID INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    fullName TEXT NOT NULL,
    ICNumber TEXT NOT NULL,
    emailAddress TEXT NOT NULL,
    phoneNumber TEXT NOT NULL,
    password TEXT NOT NULL,
    ICImagePath TEXT NOT NULL,
    FaceImagePath TEXT NOT NULL
)
''')

# Create the rental table
cursor.execute('''
CREATE TABLE IF NOT EXISTS rental (
    rentalID INTEGER PRIMARY KEY AUTOINCREMENT,
    combined_properties_id INTEGER NOT NULL,
    tenantID INTEGER NOT NULL,
    startDate TEXT NOT NULL,
    endDate TEXT NOT NULL,
    rentalAmount REAL NOT NULL,
    FOREIGN KEY (combined_properties_id) REFERENCES combined_properties(id),
    FOREIGN KEY (tenantID) REFERENCES tenants(tenantID)
)
''')

# Insert a rental record
today = date.today()
one_year_later = today + timedelta(days=365)

cursor.execute('''
INSERT INTO rental (combined_properties_id, tenantID, startDate, endDate, rentalAmount)
VALUES (?, ?, ?, ?, ?)
''', (
    1,  # combined_properties_id
    1,  # tenantID
    today.isoformat(),  # startDate (today's date)
    one_year_later.isoformat(),  # endDate (one year from today)
    1000.00  # rentalAmount (example value)
))

conn.commit()
conn.close()

print("Tables created and rental record inserted successfully.")
