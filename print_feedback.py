import sqlite3
from datetime import datetime
import textwrap

def print_all_feedback():
    try:
        # Connect to the database
        conn = sqlite3.connect('properties.db')
        cursor = conn.cursor()
        
        # Get all feedback entries ordered by timestamp
        cursor.execute("""
            SELECT id, category, comment, timestamp 
            FROM feedback 
            ORDER BY timestamp DESC
        """)
        
        feedback_entries = cursor.fetchall()
        
        if not feedback_entries:
            print("\n=== No feedback entries found ===\n")
            return
        
        print("\n" + "="*80)
        print("FEEDBACK REPORT")
        print("="*80 + "\n")
        
        for entry in feedback_entries:
            id, category, comment, timestamp = entry
            
            # Convert timestamp to readable format
            try:
                dt = datetime.fromisoformat(timestamp)
                formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                formatted_time = timestamp  # Use as-is if parsing fails
            
            # Format the feedback entry with word wrapping
            print(f"ID: {id}")
            print(f"Category: {category}")
            print("Comment:")
            # Wrap comment text at 70 characters
            wrapped_comment = textwrap.fill(comment, width=70, initial_indent="  ", 
                                          subsequent_indent="  ")
            print(wrapped_comment)
            print(f"Timestamp: {formatted_time}")
            print("-"*80 + "\n")
        
        # Print summary
        print(f"Total Feedback Entries: {len(feedback_entries)}")
        
        # Print category summary
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM feedback 
            GROUP BY category
        """)
        categories = cursor.fetchall()
        
        print("\nFeedback by Category:")
        for category, count in categories:
            print(f"  {category}: {count}")
            
        print("\n" + "="*80 + "\n")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print_all_feedback()
