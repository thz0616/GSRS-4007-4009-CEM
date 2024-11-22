import tkinter as tk
from tkinter import Canvas, ttk
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from datetime import datetime
import customtkinter as ctk

# Add these color constants at the top
LIGHT_PURPLE = "#F0E6FF"  # Changed to match the page background
DARKER_PURPLE = "#9370DB"  # Medium Purple
BORDER_PURPLE = "#8B72BE"  # Slightly darker purple for borders
TEXT_PURPLE = "#483D8B"    # Dark slate blue for text

def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=70, outline_color="black", outline_width=1, **kwargs):
    points = [x1 + radius, y1,
              x1 + radius, y1,
              x2 - radius, y1,
              x2 - radius, y1,
              x2, y1,
              x2, y1 + radius,
              x2, y1 + radius,
              x2, y2 - radius,
              x2, y2 - radius,
              x2, y2,
              x2 - radius, y2,
              x2 - radius, y2,
              x1 + radius, y2,
              x1 + radius, y2,
              x1, y2,
              x1, y2 - radius,
              x1, y2 - radius,
              x1, y1 + radius,
              x1, y1 + radius,
              x1, y1]
    return canvas.create_polygon(points, **kwargs, outline=outline_color, width=outline_width, smooth=True)

def get_total_paid_amount():
    db_path = "properties.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = """
    SELECT SUM(r.rentalAmount)
    FROM rental r
    INNER JOIN payment_records p ON p.rentalID = r.rentalID
    WHERE r.isApprove = 1;
    """

    cursor.execute(query)
    total_amount = cursor.fetchone()[0]

    conn.close()

    if total_amount is not None:
        total_amount = round(total_amount, 2)
    else:
        total_amount = 0.00

    return total_amount

def get_total_unpaid_amount():
    db_path = "properties.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = """
    WITH RECURSIVE
    months AS (
        SELECT 
            r.rentalID,
            r.stallName,
            t.fullName as tenant_name,
            r.rentalAmount,
            strftime('%Y-%m', r.startDate) as month_year,
            CASE 
                WHEN date(r.endDate) > date('now') THEN date('now', 'start of month')
                ELSE date(r.endDate, '-1 month', 'start of month')
            END as end_check_date
        FROM rental r
        JOIN tenants t ON r.tenantID = t.tenantID
        WHERE r.isApprove = 1
        
        UNION ALL
        
        SELECT 
            m.rentalID,
            m.stallName,
            m.tenant_name,
            m.rentalAmount,
            strftime('%Y-%m', date(substr(m.month_year, 1, 4) || '-' || 
                    substr(m.month_year, 6, 2) || '-01', '+1 month')),
            m.end_check_date
        FROM months m
        WHERE date(substr(m.month_year, 1, 4) || '-' || 
              substr(m.month_year, 6, 2) || '-01') < m.end_check_date
    )
    SELECT 
        m.rentalID,
        COUNT(*) * m.rentalAmount as total_due
    FROM months m
    LEFT JOIN payment_records pr ON 
        pr.rentalID = m.rentalID AND 
        pr.payment_period = m.month_year
    WHERE pr.id IS NULL
    GROUP BY m.rentalID;
    """

    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()

    # Sum up all the total_due amounts
    total_unpaid = sum(row[1] for row in results) if results else 0.00
    return round(total_unpaid, 2)

def get_total_payment_records():
    db_path = "properties.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = """
    SELECT COUNT(*)
    FROM payment_records;
    """

    cursor.execute(query)
    total_records = cursor.fetchone()[0]

    conn.close()
    return total_records

def get_monthly_data():
    db_path = "properties.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Dictionary to convert month numbers to names
    month_names = {
        '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr',
        '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Aug',
        '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'
    }

    # Modified query to use payment_period instead of startDate
    query = """
    SELECT substr(p.payment_period, 6, 2) as Month, 
           substr(p.payment_period, 1, 4) as Year,
           SUM(r.rentalAmount) as Total
    FROM payment_records p
    INNER JOIN rental r ON p.rentalID = r.rentalID
    GROUP BY payment_period
    ORDER BY Year, Month;
    """

    cursor.execute(query)
    monthly_data = cursor.fetchall()

    # Format the data with month names
    formatted_data = []
    for month, year, amount in monthly_data:
        month_name = month_names.get(month, month)
        formatted_data.append((f"{month_name}\n{year}", amount))

    conn.close()
    return formatted_data

def get_records(selected_period=None):
    db_path = "properties.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Dictionary to convert month names to numbers
    month_to_num = {
        'January': '01', 'February': '02', 'March': '03', 'April': '04',
        'May': '05', 'June': '06', 'July': '07', 'August': '08',
        'September': '09', 'October': '10', 'November': '11', 'December': '12'
    }

    # Dictionary to convert numbers to month names
    num_to_month = {v: k for k, v in month_to_num.items()}

    if selected_period:
        # Split the selected period into month and year
        month_name, year = selected_period.split()
        month_num = month_to_num[month_name]
        
        query = """
        SELECT p.id, p.rentalID, t.fullName, p.payment_method, r.rentalAmount,
               p.payment_period, p.payment_date, p.payment_time
        FROM payment_records p
        INNER JOIN rental r ON p.rentalID = r.rentalID
        INNER JOIN tenants t ON r.tenantID = t.tenantID
        WHERE p.payment_period = ?;
        """
        cursor.execute(query, (f"{year}-{month_num}",))
    else:
        query = """
        SELECT p.id, p.rentalID, t.fullName, p.payment_method, r.rentalAmount,
               p.payment_period, p.payment_date, p.payment_time
        FROM payment_records p
        INNER JOIN rental r ON p.rentalID = r.rentalID
        INNER JOIN tenants t ON r.tenantID = t.tenantID;
        """
        cursor.execute(query)

    records = cursor.fetchall()
    
    # Format the records to display month in words
    formatted_records = []
    for record in records:
        payment_period = record[5]  # Get payment_period
        try:
            year_month = payment_period.split('-')
            month_word = num_to_month[year_month[1]]
            formatted_record = list(record)
            formatted_record[5] = f"{month_word} {year_month[0]}"  # Replace with formatted month year
            formatted_records.append(tuple(formatted_record))
        except (IndexError, KeyError):
            formatted_records.append(record)

    conn.close()
    return formatted_records

def filter_by_month(tree, month_combobox):
    selected_period = month_combobox.get()
    if selected_period == 'Select Month':
        return
        
    for row in tree.get_children():
        tree.delete(row)
    filtered_records = get_records(selected_period)
    for record in filtered_records:
        # Format amount to show RM
        formatted_record = list(record)
        formatted_record[4] = f"RM {formatted_record[4]:.2f}"
        tree.insert('', tk.END, values=formatted_record)

def get_filter_periods():
    current_year = datetime.now().year
    periods = []
    
    # Add periods from two years before to one year after
    for year in range(current_year - 2, current_year + 2):
        for month in ['January', 'February', 'March', 'April', 'May', 'June',
                     'July', 'August', 'September', 'October', 'November', 'December']:
            periods.append(f"{month} {year}")
    
    return periods

def get_top_5_states_sales():
    # Connect to the states_sales database and retrieve the top 5 states by sales
    db_path = "C:/Users/Chicken Chop/PycharmProjects/ALL2/Payment Overview/states_sales.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query to retrieve the top 5 states by sales
    query = """
    SELECT state, sales
    FROM states_sales
    ORDER BY sales DESC
    LIMIT 5;
    """

    cursor.execute(query)
    top_5_states_sales = cursor.fetchall()

    # Close connection
    conn.close()

    return top_5_states_sales

def get_unpaid_records():
    db_path = "properties.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = """
    WITH RECURSIVE
    months AS (
        -- For each rental, generate sequence of months from start date
        SELECT 
            r.rentalID,
            r.stallName,
            t.fullName as tenant_name,
            r.rentalAmount,
            cp.addressLine1,
            cp.city,
            cp.state,
            strftime('%Y-%m', r.startDate) as month_year,
            CASE 
                WHEN date(r.endDate) > date('now') THEN date('now', 'start of month')
                ELSE date(r.endDate, '-1 month', 'start of month')
            END as end_check_date,
            COUNT(*) OVER (PARTITION BY r.rentalID) as total_months_due
        FROM rental r
        JOIN tenants t ON r.tenantID = t.tenantID
        JOIN combined_properties cp ON r.combined_properties_id = cp.id
        WHERE r.isApprove = 1
        
        UNION ALL
        
        SELECT 
            m.rentalID,
            m.stallName,
            m.tenant_name,
            m.rentalAmount,
            m.addressLine1,
            m.city,
            m.state,
            strftime('%Y-%m', date(substr(m.month_year, 1, 4) || '-' || 
                    substr(m.month_year, 6, 2) || '-01', '+1 month')),
            m.end_check_date,
            m.total_months_due
        FROM months m
        WHERE date(substr(m.month_year, 1, 4) || '-' || 
              substr(m.month_year, 6, 2) || '-01') < m.end_check_date
    )
    SELECT 
        m.rentalID,
        m.tenant_name,
        m.stallName,
        m.month_year,
        m.rentalAmount,
        m.addressLine1,
        m.city,
        m.state,
        (m.rentalAmount * m.total_months_due) as total_due
    FROM months m
    LEFT JOIN payment_records pr ON 
        pr.rentalID = m.rentalID AND 
        pr.payment_period = m.month_year
    WHERE pr.id IS NULL
    GROUP BY m.rentalID, m.month_year
    ORDER BY m.month_year, m.rentalID;
    """

    cursor.execute(query)
    unpaid_records = cursor.fetchall()
    conn.close()

    # Format the month names
    month_names = {
        '01': 'January', '02': 'February', '03': 'March', '04': 'April',
        '05': 'May', '06': 'June', '07': 'July', '08': 'August',
        '09': 'September', '10': 'October', '11': 'November', '12': 'December'
    }

    formatted_records = []
    for record in unpaid_records:
        year_month = record[3].split('-')
        month_word = month_names[year_month[1]]
        formatted_record = list(record)
        formatted_record[3] = f"{month_word} {year_month[0]}"
        formatted_records.append(tuple(formatted_record))

    return formatted_records

def show_unpaid_records(tree):
    # Clear existing records
    for row in tree.get_children():
        tree.delete(row)

    # Configure columns for unpaid records view
    tree['columns'] = ('Rental ID', 'Tenant Name', 'Stall Name', 'Unpaid Month', 
                      'Amount Due', 'Total Due', 'Address', 'City', 'State')
    
    # Reset column headings and widths
    column_widths = {
        'Rental ID': 100,
        'Tenant Name': 200,
        'Stall Name': 150,
        'Unpaid Month': 150,
        'Amount Due': 150,
        'Total Due': 150,
        'Address': 250,
        'City': 150,
        'State': 150
    }

    for col in tree['columns']:
        tree.heading(col, text=col, anchor="center")
        tree.column(col, width=column_widths[col], anchor="center")

    # Get and display unpaid records
    unpaid_records = get_unpaid_records()
    
    # Create a dictionary to track total dues per rental
    rental_totals = {}
    
    for record in unpaid_records:
        rental_id = record[0]
        monthly_amount = float(record[4])  # Amount is already a float, no need to replace
        if rental_id not in rental_totals:
            rental_totals[rental_id] = monthly_amount
        else:
            rental_totals[rental_id] += monthly_amount

    # Insert records with total dues
    for record in unpaid_records:
        formatted_record = list(record)
        rental_id = formatted_record[0]
        # Format monthly amount
        formatted_record[4] = f"RM {float(formatted_record[4]):.2f}"  # Format amount with RM
        # Insert total due between Amount Due and Address
        total_due = rental_totals[rental_id]
        formatted_record.insert(5, f"RM {total_due:.2f}")
        tree.insert('', tk.END, values=formatted_record)

def get_unpaid_rental_summaries():
    db_path = "properties.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = """
    WITH RECURSIVE
    months AS (
        -- For each rental, generate sequence of months from start date
        SELECT 
            r.rentalID,
            r.stallName,
            t.fullName as tenant_name,
            r.rentalAmount,
            cp.addressLine1,
            cp.city,
            cp.state,
            strftime('%Y-%m', r.startDate) as month_year,
            CASE 
                WHEN date(r.endDate) > date('now') THEN date('now', 'start of month')
                ELSE date(r.endDate, '-1 month', 'start of month')
            END as end_check_date
        FROM rental r
        JOIN tenants t ON r.tenantID = t.tenantID
        JOIN combined_properties cp ON r.combined_properties_id = cp.id
        WHERE r.isApprove = 1
        
        UNION ALL
        
        SELECT 
            m.rentalID,
            m.stallName,
            m.tenant_name,
            m.rentalAmount,
            m.addressLine1,
            m.city,
            m.state,
            strftime('%Y-%m', date(substr(m.month_year, 1, 4) || '-' || 
                    substr(m.month_year, 6, 2) || '-01', '+1 month')),
            m.end_check_date
        FROM months m
        WHERE date(substr(m.month_year, 1, 4) || '-' || 
              substr(m.month_year, 6, 2) || '-01') < m.end_check_date
    )
    SELECT 
        m.rentalID,
        m.tenant_name,
        m.stallName,
        m.addressLine1,
        m.city,
        m.state,
        COUNT(*) as months_unpaid,
        m.rentalAmount,
        (COUNT(*) * m.rentalAmount) as total_due
    FROM months m
    LEFT JOIN payment_records pr ON 
        pr.rentalID = m.rentalID AND 
        pr.payment_period = m.month_year
    WHERE pr.id IS NULL
    GROUP BY m.rentalID
    ORDER BY total_due DESC;
    """

    cursor.execute(query)
    unpaid_rentals = cursor.fetchall()
    conn.close()
    return unpaid_rentals

def show_unpaid_rental_details(rental_id):
    # Create a new window for details
    details_window = tk.Toplevel()
    details_window.title(f"Unpaid Months Details - Rental ID: {rental_id}")
    details_window.geometry("600x400")
    details_window.configure(bg=LIGHT_PURPLE)

    # Create a frame for the details
    details_frame = ttk.Frame(details_window)
    details_frame.pack(padx=20, pady=20, fill="both", expand=True)

    # Create treeview for unpaid months
    columns = ('Month', 'Amount')
    details_tree = ttk.Treeview(details_frame, columns=columns, show='headings', height=10)

    # Configure columns
    for col in columns:
        details_tree.heading(col, text=col, anchor="center")
        details_tree.column(col, width=250, anchor="center")

    # Style the treeview
    style = ttk.Style()
    style.configure("Treeview",
                   font=("Arial", 12),
                   rowheight=30)
    style.configure("Treeview.Heading",
                   font=("Arial", 14, "bold"))

    # Get unpaid months for this rental
    db_path = "properties.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = """
    WITH RECURSIVE
    months AS (
        SELECT 
            r.rentalID,
            r.rentalAmount,
            strftime('%Y-%m', r.startDate) as month_year,
            CASE 
                WHEN date(r.endDate) > date('now') THEN date('now', 'start of month')
                ELSE date(r.endDate, '-1 month', 'start of month')
            END as end_check_date
        FROM rental r
        WHERE r.rentalID = ? AND r.isApprove = 1
        
        UNION ALL
        
        SELECT 
            m.rentalID,
            m.rentalAmount,
            strftime('%Y-%m', date(substr(m.month_year, 1, 4) || '-' || 
                    substr(m.month_year, 6, 2) || '-01', '+1 month')),
            m.end_check_date
        FROM months m
        WHERE date(substr(m.month_year, 1, 4) || '-' || 
              substr(m.month_year, 6, 2) || '-01') < m.end_check_date
    )
    SELECT 
        month_year,
        rentalAmount
    FROM months m
    LEFT JOIN payment_records pr ON 
        pr.rentalID = m.rentalID AND 
        pr.payment_period = m.month_year
    WHERE pr.id IS NULL
    ORDER BY month_year;
    """

    cursor.execute(query, (rental_id,))
    unpaid_months = cursor.fetchall()
    conn.close()

    # Format and display the unpaid months
    month_names = {
        '01': 'January', '02': 'February', '03': 'March', '04': 'April',
        '05': 'May', '06': 'June', '07': 'July', '08': 'August',
        '09': 'September', '10': 'October', '11': 'November', '12': 'December'
    }

    for month_year, amount in unpaid_months:
        year, month = month_year.split('-')
        month_name = month_names[month]
        formatted_month = f"{month_name} {year}"
        formatted_amount = f"RM {amount:.2f}"
        details_tree.insert('', tk.END, values=(formatted_month, formatted_amount))

    details_tree.pack(padx=10, pady=10, fill="both", expand=True)

def show_unpaid_rentals(tree):
    # Clear existing records
    for row in tree.get_children():
        tree.delete(row)

    # Configure columns for unpaid rentals view
    tree['columns'] = ('Rental ID', 'Tenant Name', 'Stall Name', 
                      'Months Unpaid', 'Monthly Amount', 'Total Due', 'Details')
    
    # Reset column headings and widths
    column_widths = {
        'Rental ID': 150,
        'Tenant Name': 250,
        'Stall Name': 200,
        'Months Unpaid': 150,
        'Monthly Amount': 200,
        'Total Due': 200,
        'Details': 150
    }

    for col in tree['columns']:
        tree.heading(col, text=col, anchor="center")
        tree.column(col, width=column_widths[col], anchor="center")

    # Get and display unpaid rental summaries
    unpaid_rentals = get_unpaid_rental_summaries()
    
    # Style configuration for clickable text
    style = ttk.Style()
    style.configure("Clickable.Treeview", 
                   font=("Arial", 10),
                   foreground="blue")

    for record in unpaid_rentals:
        rental_id = record[0]
        formatted_record = list(record[:3])  # Get rental_id, tenant_name, stall_name
        formatted_record.append(record[6])   # Add months_unpaid
        formatted_record.append(f"RM {float(record[7]):.2f}")  # Monthly Amount
        formatted_record.append(f"RM {float(record[8]):.2f}")  # Total Due
        formatted_record.append("👉 View Details")  # Add text with an icon for Details column
        
        # Insert the record
        item = tree.insert('', tk.END, values=formatted_record)
        
    # Bind click event to the tree
    tree.bind('<ButtonRelease-1>', lambda event: handle_tree_click(event, tree))

def handle_tree_click(event, tree):
    # Get the clicked item and column
    region = tree.identify("region", event.x, event.y)
    if region == "cell":
        column = tree.identify_column(event.x)
        item = tree.identify_row(event.y)
        
        # If clicked on the Details column (last column)
        if column == f'#{len(tree["columns"])}':  # Last column
            rental_id = tree.item(item)['values'][0]  # Get rental ID from first column
            show_unpaid_rental_details(rental_id)

def create_dashboard(root):
    # Main container frame
    main_container = ctk.CTkFrame(root, fg_color="#F0E6FF")
    main_container.pack(fill="both", expand=True, padx=20, pady=20)

    # Top row frame
    top_row = ctk.CTkFrame(main_container, fg_color="#F0E6FF")
    top_row.pack(fill="x", pady=(0, 20))

    # First box - Total Paid Amount (increased size)
    paid_box = ctk.CTkFrame(top_row, fg_color="white", corner_radius=70, width=400, height=350)  # Increased size
    paid_box.pack(side="left", expand=True, padx=10)
    paid_box.pack_propagate(False)  # Prevent box from shrinking
    
    ctk.CTkLabel(paid_box, text="Total Paid Amount", font=("Arial", 18), text_color=TEXT_PURPLE).pack(pady=(40, 0))
    ctk.CTkLabel(paid_box, text="RM", font=("Arial", 30), text_color=TEXT_PURPLE).pack(pady=(40, 0))
    ctk.CTkLabel(paid_box, text=f"{get_total_paid_amount():,.2f}", font=("Arial", 50), text_color=TEXT_PURPLE).pack(pady=40)

    # Second box - Total Unpaid Amount (increased size)
    unpaid_box = ctk.CTkFrame(top_row, fg_color="white", corner_radius=70, width=400, height=350)  # Increased size
    unpaid_box.pack(side="left", expand=True, padx=10)
    unpaid_box.pack_propagate(False)  # Prevent box from shrinking
    
    ctk.CTkLabel(unpaid_box, text="Total Unpaid Amount", font=("Arial", 18), text_color=TEXT_PURPLE).pack(pady=(40, 0))
    ctk.CTkLabel(unpaid_box, text="RM", font=("Arial", 30), text_color=TEXT_PURPLE).pack(pady=(40, 0))
    ctk.CTkLabel(unpaid_box, text=f"{get_total_unpaid_amount():,.2f}", font=("Arial", 50), text_color=TEXT_PURPLE).pack(pady=40)

    # Third box - Graph (increased size)
    graph_box = ctk.CTkFrame(top_row, fg_color="white", corner_radius=70, width=800, height=350)  # Increased size
    graph_box.pack(side="left", expand=True, padx=10)
    graph_box.pack_propagate(False)  # Prevent box from shrinking

    # Create and pack the graph
    sales_data = get_monthly_data()
    if sales_data:
        months = [row[0] for row in sales_data]
        total_sales = [row[1] for row in sales_data]

        fig, ax = plt.subplots(figsize=(8, 3))
        ax.plot(months, total_sales, marker='o', linestyle='-', color=DARKER_PURPLE, linewidth=2, markersize=8)
        
        for i, value in enumerate(total_sales):
            ax.text(i, value, f'RM{value:,.2f}', ha='center', va='bottom', fontsize=8)

        ax.set_ylabel("Total Amount (RM)", fontsize=10, color=TEXT_PURPLE)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_facecolor('white')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        ax.set_ylim(bottom=0)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(TEXT_PURPLE)
        ax.spines['bottom'].set_color(TEXT_PURPLE)
        ax.tick_params(axis='both', colors=TEXT_PURPLE)
        fig.patch.set_facecolor('white')

        canvas_figure = FigureCanvasTkAgg(fig, master=graph_box)
        canvas_figure.draw()
        canvas_figure.get_tk_widget().pack(pady=20, padx=20)

    # Bottom section frame (adjusted padding)
    bottom_section = ctk.CTkFrame(main_container, fg_color="white", corner_radius=70)
    bottom_section.pack(fill="both", expand=True, pady=(0, 20))

    # Controls frame (added padding)
    controls_frame = ctk.CTkFrame(bottom_section, fg_color="transparent")
    controls_frame.pack(fill="x", padx=20, pady=20)  # Increased padding

    # Left side - Title (remains white)
    ctk.CTkLabel(controls_frame, text="Payment Records", font=("Arial", 18), text_color=TEXT_PURPLE).pack(side="left", padx=10)

    # Right side - Filter and buttons (remains white)
    filter_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
    filter_frame.pack(side="right")

    # Filter controls (remains white)
    filter_periods = get_filter_periods()
    month_combobox = ttk.Combobox(filter_frame, values=filter_periods, state='readonly', width=25)
    month_combobox.grid(row=0, column=0, padx=5)
    month_combobox.set('Select Month')

    ttk.Button(filter_frame, text="Filter", width=10,
               command=lambda: filter_by_month(tree, month_combobox)).grid(row=0, column=1, padx=5)
    
    ttk.Button(filter_frame, text="Show All Payments", width=20,
               command=lambda: show_all_payments(tree)).grid(row=0, column=2, padx=5)
    
    ttk.Button(filter_frame, text="Show Unpaid Rentals", width=20,
               command=lambda: show_unpaid_rentals(tree)).grid(row=0, column=3, padx=5)

    # Create frame for treeview and scrollbar
    tree_frame = ctk.CTkFrame(bottom_section, fg_color="transparent")
    tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    # Style configuration for treeview
    style = ttk.Style()
    style.configure("Treeview",
                   font=("Arial", 14),
                   rowheight=30)
    style.configure("Treeview.Heading",
                   font=("Arial", 16, "bold"),
                   background=LIGHT_PURPLE,
                   foreground=TEXT_PURPLE)

    # Create treeview
    columns = ('Payment ID', 'Rental ID', 'Customer Name', 'Payment Method', 
              'Amount', 'Payment Period', 'Payment Date', 'Payment Time')
    tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=10)

    # Configure columns (remains white)
    column_widths = {
        'Payment ID': 100,
        'Rental ID': 100,
        'Customer Name': 200,
        'Payment Method': 150,
        'Amount': 150,
        'Payment Period': 150,
        'Payment Date': 150,
        'Payment Time': 150
    }

    for col in columns:
        tree.heading(col, text=col, anchor="center")
        tree.column(col, width=column_widths[col], anchor="center")

    # Add scrollbar (remains white)
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    # Pack tree and scrollbar (remains white)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Load initial data (remains white)
    payment_records = get_records()
    for record in payment_records:
        formatted_record = list(record)
        formatted_record[4] = f"RM {formatted_record[4]:.2f}"
        tree.insert('', tk.END, values=formatted_record)

def show_all_payments(tree):
    # Clear existing records
    for row in tree.get_children():
        tree.delete(row)

    # Configure columns for payment records view
    tree['columns'] = ('Payment ID', 'Rental ID', 'Customer Name', 'Payment Method', 
                      'Amount', 'Payment Period', 'Payment Date', 'Payment Time')
    
    # Reset column headings and widths
    column_widths = {
        'Payment ID': 100,
        'Rental ID': 100,
        'Customer Name': 200,
        'Payment Method': 150,
        'Amount': 150,
        'Payment Period': 150,
        'Payment Date': 150,
        'Payment Time': 150
    }

    for col in tree['columns']:
        tree.heading(col, text=col, anchor="center")
        tree.column(col, width=column_widths[col], anchor="center")

    # Get and display payment records
    payment_records = get_records()
    for record in payment_records:
        # Format amount to show RM
        formatted_record = list(record)
        formatted_record[4] = f"RM {formatted_record[4]:.2f}"
        tree.insert('', tk.END, values=formatted_record)

def show_payment_overview(root, home_frame, show_dashboard_callback):
    # Hide home frame
    home_frame.pack_forget()
    
    # Create main frame for payment overview
    payment_frame = ctk.CTkFrame(root, fg_color="#F0E6FF")  # Light purple background
    payment_frame.pack(fill="both", expand=True)
    
    def back_to_home():
        # Hide payment frame and call the dashboard callback
        payment_frame.pack_forget()
        show_dashboard_callback()
    
    # Add back button at the top
    back_btn = ctk.CTkButton(
        master=payment_frame,
        text="← Back",
        command=back_to_home,
        width=100,
        height=30,
        fg_color="#9370DB",
        hover_color="#7B68EE"
    )
    back_btn.pack(anchor="nw", padx=20, pady=10)
    
    # Create the dashboard in the payment frame
    create_dashboard(payment_frame)

def main():
    root = tk.Tk()
    root.title("Payment Overview")
    root.geometry("1920x1080")
    
    # Create home frame (white page)
    home_frame = ctk.CTkFrame(master=root, fg_color="white")
    home_frame.pack(fill="both", expand=True)
    
    # Add switch button to home frame
    switch_btn = ctk.CTkButton(
        master=home_frame,
        text="Open Payment Overview",
        command=lambda: show_payment_overview(root, home_frame, lambda: show_dashboard(root, home_frame)),
        width=200,
        height=50,
        fg_color="#9370DB",
        hover_color="#7B68EE"
    )
    switch_btn.pack(expand=True)
    
    root.mainloop()

if __name__ == "__main__":
    main()
