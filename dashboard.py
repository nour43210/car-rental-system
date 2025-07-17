import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo, showerror
import mysql.connector
from mysql.connector import Error


def create_connection():
    """Create and return a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="CarRentalSystem"
        )
        return conn
    except Error as e:
        showerror("Database Error", f"Failed to connect to database: {e}")
        return None


def fetch_data(query, params=()):
    """Fetch data from the database using the given query."""
    conn = create_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    except Error as e:
        showerror("Database Error", f"An error occurred: {e}")
        return []
    finally:
        conn.close()


def load_overview(frame):
    """Load overview data into the overview frame."""
    total_cars = fetch_data("SELECT COUNT(*) FROM cars")[0][0]
    total_customers = fetch_data("SELECT COUNT(*) FROM customers")[0][0]
    total_reservations = fetch_data("SELECT COUNT(*) FROM reservations")[0][0]

    for widget in frame.winfo_children():
        widget.destroy()

    tk.Label(frame, text="Overview", font=("Arial", 16, "bold"), bg="#282828", fg="white").pack(pady=10)
    tk.Label(frame, text=f"Total Cars: {total_cars}", font=("Arial", 12), bg="#282828", fg="white").pack(pady=5)
    tk.Label(frame, text=f"Total Customers: {total_customers}", font=("Arial", 12), bg="#282828", fg="white").pack(pady=5)
    tk.Label(frame, text=f"Total Reservations: {total_reservations}", font=("Arial", 12), bg="#282828", fg="white").pack(pady=5)


def load_table_data(table, query):
    """Load data into the table widget."""
    rows = fetch_data(query)
    for row in table.get_children():
        table.delete(row)
    for row in rows:
        table.insert("", "end", values=row)


def show_dashboard():
    """Show the dashboard window."""
    root = tk.Tk()
    root.title("Car Rental System Dashboard")
    root.geometry("800x600")
    root.configure(bg="#282828")

    # Overview Frame
    overview_frame = tk.Frame(root, bg="#282828")
    overview_frame.pack(side="top", fill="x")
    load_overview(overview_frame)

    # Table Frame
    table_frame = tk.Frame(root)
    table_frame.pack(side="top", fill="both", expand=True)

    table = ttk.Treeview(table_frame, columns=("ID", "Name", "Details"), show="headings")
    table.heading("ID", text="ID")
    table.heading("Name", text="Name")
    table.heading("Details", text="Details")
    table.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
    scrollbar.pack(side="right", fill="y")
    table.configure(yscrollcommand=scrollbar.set)

    # Button Frame
    button_frame = tk.Frame(root, bg="#282828")
    button_frame.pack(side="bottom", fill="x")

    def load_cars():
        load_table_data(table, "SELECT id, name, model_year FROM cars")

    def load_customers():
        load_table_data(table, "SELECT id, name, country FROM customers")

    def load_reservations():
        load_table_data(table, """
            SELECT r.id, c.name AS customer, car.name AS car 
            FROM reservations r
            JOIN customers c ON r.customer_id = c.id
            JOIN cars car ON r.car_id = car.id
        """)

    tk.Button(button_frame, text="View Cars", font=("Arial", 12), bg="#4CAF50", fg="white", command=load_cars).pack(side="left", padx=10, pady=10)
    tk.Button(button_frame, text="View Customers", font=("Arial", 12), bg="#4CAF50", fg="white", command=load_customers).pack(side="left", padx=10, pady=10)
    tk.Button(button_frame, text="View Reservations", font=("Arial", 12), bg="#4CAF50", fg="white", command=load_reservations).pack(side="left", padx=10, pady=10)

    root.mainloop()


if __name__ == "__main__":
    show_dashboard()
