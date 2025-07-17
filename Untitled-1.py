import mysql.connector
from mysql.connector import Error
from tkinter import Tk, Label, Entry, Button, StringVar, OptionMenu
from tkinter.messagebox import showinfo, showerror
import hashlib
import re

def validate_and_hash_email(email):
    # Check if the email contains "@"
    if re.match(r"[^@]+@[^@]+\.[^@]+", email):
        # Valid email, return MD5 hash
        return hashlib.md5(email.encode()).hexdigest()
    else:
        raise ValueError("Invalid email address")

def create_connection():
    """Create and return a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(
            host="localhost",  # Update if phpMyAdmin runs on a different host
            user="root",       # Replace with your MySQL username
            password="",       # Replace with your MySQL password
            database="CarRentalSystem"
        )
        print("Database connected successfully!")  # Debugging log
        return conn
    except Error as e:
        showerror("Database Error", f"Failed to connect to database: {e}")
        print(f"Database connection error: {e}")  # Debugging log
        return None


def register_car(name, model_year, color, duration, pick_up, return_time, payment, customer_id):
    """Register a new car in the database and create a reservation."""
    conn = create_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()

        # Debugging: Log the data
        print(f"Registering car: {name}, {model_year}, {color}")

        # Insert car into the cars table
        cursor.execute(
            'INSERT INTO cars (name, model_year, color) VALUES (%s, %s, %s)', 
            (name, model_year, color)
        )
        car_id = cursor.lastrowid  # Get the ID of the newly inserted car
        print(f"Inserted car ID: {car_id}")  # Debugging log

        # Insert reservation into the reservations table
        cursor.execute(
            '''INSERT INTO reservations 
               (car_id, customer_id, duration, pick_up, return_time, payment) 
               VALUES (%s, %s, %s, %s, %s, %s)''', 
            (car_id, customer_id, duration, pick_up, return_time, payment)
        )
        conn.commit()
        showinfo("Success", "Car and Reservation registered successfully!")
        print("Car and reservation data committed to the database.")  # Debugging log
    except Error as e:
        showerror("Database Error", f"An error occurred: {e}")
        print(f"Error during car registration: {e}")  # Debugging log
    finally:
        conn.close()


def register_customer(root, name, phone, email, country):
    """Register a new customer in the database and proceed to car registration."""
    try:
        email_hash = validate_and_hash_email(email)
    except ValueError as e:
        showerror("Validation Error", str(e))
        return

    conn = create_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()

        # Check if the email already exists in the database
        cursor.execute('SELECT id FROM customers WHERE email = %s', (email_hash,))
        existing_customer = cursor.fetchone()
        if existing_customer:
            showerror("Error", "Email already exists. Please use a different email.")
            return

        # Insert new customer
        cursor.execute(
            'INSERT INTO customers (name, phone, email, country) VALUES (%s, %s, %s, %s)',
            (name, phone, email_hash, country)
        )
        conn.commit()
        customer_id = cursor.lastrowid
        showinfo("Success", "Customer registered successfully!")
        root.destroy()
        show_car_registration(customer_id)
    except Error as e:
        showerror("Database Error", f"An error occurred: {e}")
    finally:
        conn.close()


def update_car_reservation_status(car_id, customer_id, new_status, return_date=None):
    """Update or insert a car reservation status in the database."""
    conn = create_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()

        # Check if the reservation exists
        cursor.execute('''SELECT id FROM car_reservation_status 
                          WHERE car_id = %s AND customer_id = %s AND status != 'returned' 
                          ORDER BY reservation_date DESC LIMIT 1''', 
                       (car_id, customer_id))
        reservation = cursor.fetchone()

        if reservation:
            # Update existing reservation
            cursor.execute('''UPDATE car_reservation_status
                              SET status = %s, return_date = %s 
                              WHERE id = %s''', 
                           (new_status, return_date, reservation[0]))
            showinfo("Success", f"Reservation status updated to {new_status}.")
        else:
            # Insert a new reservation status
            cursor.execute('''INSERT INTO car_reservation_status 
                              (car_id, customer_id, status, reservation_date, return_date) 
                              VALUES (%s, %s, %s, CURRENT_DATE, %s)''', 
                           (car_id, customer_id, new_status, return_date))
            showinfo("Success", f"New reservation status: {new_status}.")
        
        conn.commit()

    except Error as e:
        showerror("Database Error", f"An error occurred while updating the reservation status: {e}")
    finally:
        conn.close()

def get_car_status(car_id):
    """Fetch and return the current status of a car from the database."""
    conn = create_connection()
    if conn is None:
        return "Error fetching status"

    try:
        cursor = conn.cursor()
        cursor.execute('''SELECT status FROM cars WHERE id = %s''', (car_id,))
        car_status = cursor.fetchone()
        if car_status:
            return car_status[0]
        else:
            return "Car not found"
    except Error as e:
        showerror("Database Error", f"An error occurred while fetching car status: {e}")
        print(f"Error fetching car status: {e}")
        return "Error fetching status"
    finally:
        conn.close()
 
def show_car_registration(customer_id):
    """Show the car registration screen."""
    root = Tk()
    root.title("Car Registration")
    root.configure(bg="#282828")  # Dark theme
    root.geometry("600x550")

    Label(root, text="Car Registration", font=("Arial", 16, "bold"), fg="white", bg="#282828").grid(row=0, column=0, columnspan=2, pady=10)

    Label(root, text="Car Name:", font=("Arial", 12), fg="white", bg="#282828").grid(row=1, column=0, sticky="e", padx=20)
    name_var = StringVar()
    Entry(root, textvariable=name_var, font=("Arial", 12), width=30).grid(row=1, column=1, pady=5)

    Label(root, text="Model Year:", font=("Arial", 12), fg="white", bg="#282828").grid(row=2, column=0, sticky="e", padx=20)
    year_var = StringVar()
    year_options = [str(year) for year in range(2000, 2025)]
    OptionMenu(root, year_var, *year_options).grid(row=2, column=1, pady=5)

    Label(root, text="Color:", font=("Arial", 12), fg="white", bg="#282828").grid(row=3, column=0, sticky="e", padx=20)
    color_var = StringVar()
    color_options = ['Red', 'Blue', 'Black', 'White', 'Silver', 'Green']
    OptionMenu(root, color_var, *color_options).grid(row=3, column=1, pady=5)

    Label(root, text="Duration (days):", font=("Arial", 12), fg="white", bg="#282828").grid(row=4, column=0, sticky="e", padx=20)
    duration_var = StringVar()
    Entry(root, textvariable=duration_var, font=("Arial", 12), width=30).grid(row=4, column=1, pady=5)

    Label(root, text="Pick-Up Date (YYYY-MM-DD):", font=("Arial", 12), fg="white", bg="#282828").grid(row=5, column=0, sticky="e", padx=20)
    pick_up_var = StringVar()
    Entry(root, textvariable=pick_up_var, font=("Arial", 12), width=30).grid(row=5, column=1, pady=5)

    Label(root, text="Return Time (YYYY-MM-DD):", font=("Arial", 12), fg="white", bg="#282828").grid(row=6, column=0, sticky="e", padx=20)
    return_time_var = StringVar()
    Entry(root, textvariable=return_time_var, font=("Arial", 12), width=30).grid(row=6, column=1, pady=5)

    Label(root, text="Payment:", font=("Arial", 12), fg="white", bg="#282828").grid(row=7, column=0, sticky="e", padx=20)
    payment_var = StringVar()
    Entry(root, textvariable=payment_var, font=("Arial", 12), width=30).grid(row=7, column=1, pady=5)

    # Label to display car status
    status_label = Label(root, text="Car Status: N/A", font=("Arial", 12), fg="white", bg="#282828")
    status_label.grid(row=8, column=0, columnspan=2, pady=10)

    Button(root, text="Register Car", font=("Arial", 14), bg="#4CAF50", fg="white", command=lambda: register_car(
        name_var.get(), year_var.get(), color_var.get(), duration_var.get(),
        pick_up_var.get(), return_time_var.get(), payment_var.get(), customer_id
    )).grid(row=9, column=0, columnspan=2, pady=20)

    def check_and_update_status():
        """Check the car status and update the status label."""
        car_name = name_var.get()
        car_model_year = year_var.get()
        car_color = color_var.get()

        # Search for the car by its details
        conn = create_connection()
        if conn is None:
            return

        try:
            cursor = conn.cursor()
            cursor.execute('''SELECT id FROM cars WHERE name = %s AND model_year = %s AND color = %s''', 
                           (car_name, car_model_year, car_color))
            car = cursor.fetchone()

            if car:
                car_id = car[0]
                car_status = get_car_status(car_id)  # Get car status
                status_label.config(text=f"Car Status: {car_status}")  # Update the status label
                return car_id
            else:
                showerror("Car Not Found", "No car found with the provided details.")
                status_label.config(text="Car Status: Not found")  # Update the label if no car is found
                return None
        except Error as e:
            showerror("Database Error", f"An error occurred while searching for the car: {e}")
            print(f"Error during car search: {e}")
            return None
        finally:
            conn.close()

    # Button to check car status when clicked
    Button(root, text="Check Car Status", font=("Arial", 14), bg="#4CAF50", fg="white", command=check_and_update_status).grid(row=20, column=0, columnspan=2, pady=10)

    root.mainloop()


from tkinter import Tk, Label, Button
from PIL import Image, ImageTk

from tkinter import Tk, Label, Button
from PIL import Image, ImageTk

def show_welcome_page():
    """Show the welcome page before starting the registration process."""
    root = Tk()
    root.title("Welcome to Car Rental System")
    root.configure(bg="#282828")
    root.geometry("600x400")

    # Load the background image using Pillow (for .jpg or other formats)
    background_image_path = r"C:\Users\Noure\Downloads\database project\Car-symbols.jpg"  # Replace with your image name and path
    background_image = Image.open(background_image_path)  # Open the image
    background_image = background_image.resize((2000, 1000))  # Resize image to fit the window
    background_image = ImageTk.PhotoImage(background_image)

    # Set the background image
    background_label = Label(root, image=background_image)
    background_label.place(relwidth=1, relheight=1)  # Makes the image fill the entire window

    # Label for the welcome message
    welcome_label = Label(root, text="Welcome to Our Car Rental System", font=("Arial", 40, "bold"), fg="white", bg="#282828")
    welcome_label.pack(pady=20)

    # Button to continue to the registration page
    continue_button = Button(root, text="Continue to Rent a Car", font=("Arial", 40), bg="#4CAF50", fg="white", command=lambda: [root.destroy(), main()])
    continue_button.pack(pady=40)

    root.mainloop()



def main():
    # Your main function to handle next steps
    pass

show_welcome_page()



def main():
    root = Tk()
    root.title("Car Rental System")
    root.configure(bg="#282828")
    root.geometry("600x500")

    Label(root, text="Customer Registration", font=("Arial", 16, "bold"), fg="white", bg="#282828").grid(row=0, column=0, columnspan=2, pady=10)

    Label(root, text="Name:", font=("Arial", 12), fg="white", bg="#282828").grid(row=1, column=0, sticky="e", padx=20)
    name_var = StringVar()
    Entry(root, textvariable=name_var, font=("Arial", 12), width=30).grid(row=1, column=1, pady=5)

    Label(root, text="Phone:", font=("Arial", 12), fg="white", bg="#282828").grid(row=2, column=0, sticky="e", padx=20)
    phone_var = StringVar()
    Entry(root, textvariable=phone_var, font=("Arial", 12), width=30).grid(row=2, column=1, pady=5)

    Label(root, text="Email:", font=("Arial", 12), fg="white", bg="#282828").grid(row=3, column=0, sticky="e", padx=20)
    email_var = StringVar()
    Entry(root, textvariable=email_var, font=("Arial", 12), width=30).grid(row=3, column=1, pady=5)

    Label(root, text="Country:", font=("Arial", 12), fg="white", bg="#282828").grid(row=4, column=0, sticky="e", padx=20)
    country_var = StringVar()
    Entry(root, textvariable=country_var, font=("Arial", 12), width=30).grid(row=4, column=1, pady=5)

    Button(root, text="Register Customer", font=("Arial", 14), bg="#4CAF50", fg="white", command=lambda: register_customer(
        root, name_var.get(), phone_var.get(), email_var.get(), country_var.get()
    )).grid(row=5, column=0, columnspan=2, pady=20)

    root.mainloop()


if __name__ == "__main__":
    show_welcome_page()
