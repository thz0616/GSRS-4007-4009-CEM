import sqlite3

def check_table_structure(table_name):
    conn = sqlite3.connect('properties.db')
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    conn.close()
    return columns

def check_table_content(table_name):
    conn = sqlite3.connect('properties.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
    rows = cursor.fetchall()
    conn.close()
    return rows

def main():
    tables = ['tenants', 'combined_properties', 'locations']
    for table in tables:
        print(f"\nStructure of {table} table:")
        columns = check_table_structure(table)
        for col in columns:
            print(col)

    print("\nSample content of tenants table:")
    print(check_table_content('tenants'))
    
    print("\nSample content of combined_properties table:")
    print(check_table_content('combined_properties'))

if __name__ == "__main__":
    main()
