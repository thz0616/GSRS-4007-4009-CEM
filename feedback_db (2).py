
import sqlite3

def insert_feedback(table, tenant_id, column, comment):
    conn = sqlite3.connect('all.db')
    cursor = conn.cursor()

    # Check if a row for this tenant already exists
    cursor.execute(f"SELECT tenantID FROM {table} WHERE tenantID = ?", (tenant_id,))
    result = cursor.fetchone()

    if result:
        # Update the existing record
        cursor.execute(f"UPDATE {table} SET {column} = ? WHERE tenantID = ?", (comment, tenant_id))
    else:
        # Insert a new record
        cursor.execute(
            f"INSERT INTO {table} (tenantID, {column}) VALUES (?, ?)", (tenant_id, comment)
        )

    conn.commit()
    conn.close()

def fetch_feedback(table):
    conn = sqlite3.connect('all.db')
    cursor = conn.cursor()

    # Query to fetch all feedback data
    cursor.execute(f"SELECT tenantID, Complaints, SystemIssues, PaymentIssues, FeatureRequests FROM {table}")
    rows = cursor.fetchall()
    conn.close()
    return rows
