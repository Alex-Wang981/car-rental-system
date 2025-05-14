import sqlite3
from abc import ABC, abstractmethod

# === Base class: manage database connections ===
class DatabaseManager:
    def __init__(self, database):
        try:
            self.connection = sqlite3.connect(database)
            # print("Database connected successfully.")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            raise

    def close_connection(self):
        if self.connection:
            self.connection.close()
            # print("Database connection closed.")


# === Abstract base class: defines basic user operations ===
class AbstractUser(ABC):
    @abstractmethod
    def menu(self):
        pass


# === User registration and login class ===
class UserManager(DatabaseManager):
    """Handles user-related operations."""
    def __init__(self, database):
        super().__init__(database)

    def register(self):
        print("\n=== Register a New Account ===")
        username = input("Enter your username: ")
        password = input("Enter your password: ")

        if len(password) < 6 or not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password):
            print("Password must be at least 6 characters long and include both letters and numbers.")
            return

        try:
            cursor = self.connection.cursor()
            sql = "INSERT INTO users (username, password, is_admin) VALUES (?, ?, 0)"
            cursor.execute(sql, (username, password))
            self.connection.commit()
            print("Registration successful! You can now log in.")
        except sqlite3.Error as e:
            print(f"Error during registration: {e}")
        finally:
            cursor.close()

    def login(self):
        print("\n=== Login ===")
        username = input("Enter your username: ")
        password = input("Enter your password: ")

        try:
            cursor = self.connection.cursor()
            sql = "SELECT is_admin FROM users WHERE username = ? AND password = ?"
            cursor.execute(sql, (username, password))
            user = cursor.fetchone()
            if user:
                is_admin = user[0]
                if is_admin:
                    print("Welcome, Admin!")
                    return "admin"
                else:
                    print(f"Welcome, {username}!")
                    return "customer"
            else:
                print("Invalid username or password.")
                return None
        except sqlite3.Error as e:
            print(f"Error during login: {e}")
            return None
        finally:
            cursor.close()


# === Administrator class ===
class Admin(DatabaseManager, AbstractUser):
    def menu(self):
        while True:
            print("\n=== Administrator Menu ===")
            print("1. Add a Car")
            print("2. Remove a Car")
            print("3. Update Car Details")
            print("4. View order history")
            print("5. Manage bookings")
            print("6. View booking history")
            print("7. Back to Main Menu")

            choice = input("Enter your choice (1-7): ")
            if choice == "1":
                self.add_car()
            elif choice == "2":
                self.remove_car()
            elif choice == "3":
                self.update_car()
            elif choice == "4":
                self.view_order_history()
            elif choice == "5":
                self.manage_bookings()
            elif choice == "6":
                self.view_booking_history()
            elif choice == "7":
                break
            else:
                print("Invalid choice, please try again.")

    def add_car(self):
        make = input("Enter car make: ")
        model = input("Enter car model: ")
        year = int(input("Enter car year: "))
        mileage = int(input("Enter car mileage: "))
        price_per_day = float(input("Enter price per day: "))

        try:
            cursor = self.connection.cursor()
            sql = "INSERT INTO cars_info (make, model, year, mileage, price_per_day, is_available) VALUES (?, ?, ?, ?, ?, 1)"
            values = (make, model, year, mileage, price_per_day)
            cursor.execute(sql, values)
            self.connection.commit()
            print(f"Car added successfully. Last inserted ID: {cursor.lastrowid}")
        except sqlite3.Error as e:
            print(f"Error adding car: {e}")
            self.connection.rollback()
        finally:
            cursor.close()

    def remove_car(self):
        car_id = int(input("Enter the car ID to remove: "))
        try:
            cursor = self.connection.cursor()
            sql = "DELETE FROM cars_info WHERE id = ?"
            cursor.execute(sql, (car_id,))
            self.connection.commit()
            if cursor.rowcount > 0:
                print(f"Car with ID {car_id} removed successfully.")
            else:
                print(f"No car found with ID {car_id}.")
        except sqlite3.Error as e:
            print(f"Error removing car: {e}")
            self.connection.rollback()
        finally:
            cursor.close()

    def update_car(self):
        car_id = int(input("Enter the car ID to update: "))
        make = input("Enter new car make: ")
        model = input("Enter new car model: ")
        year = int(input("Enter new car year: "))
        mileage = int(input("Enter new car mileage: "))
        price_per_day = float(input("Enter new price per day: "))

        try:
            cursor = self.connection.cursor()
            sql = """
            UPDATE cars_info 
            SET make = ?, model = ?, year = ?, mileage = ?, price_per_day = ? 
            WHERE id = ?
            """
            values = (make, model, year, mileage, price_per_day, car_id)
            cursor.execute(sql, values)
            self.connection.commit()
            if cursor.rowcount > 0:
                print(f"Car with ID {car_id} updated successfully.")
            else:
                print(f"No car found with ID {car_id}.")
        except sqlite3.Error as e:
            print(f"Error updating car: {e}")
            self.connection.rollback()
        finally:
            cursor.close()

    def manage_bookings(self):
        print("\n=== Manage Bookings ===")
        try:
            cursor = self.connection.cursor()
            sql = "SELECT * FROM bookings WHERE status = 'Pending'"
            cursor.execute(sql)
            bookings = cursor.fetchall()

            for booking in bookings:
                print(booking)

            booking_id = int(input("Enter the booking ID to approve/reject: "))
            decision = input("Enter 'approve' to approve or 'reject' to reject: ").strip().lower()
            new_status = 'Approved' if decision == 'approve' else 'Rejected'

            sql_update = "UPDATE bookings SET status = ? WHERE id = ?"
            cursor.execute(sql_update, (new_status, booking_id))
            self.connection.commit()
            print(f"Booking {new_status.lower()} successfully!")
        except sqlite3.Error as e:
            print(f"Error: {e}")
            self.connection.rollback()
        finally:
            cursor.close()

    def view_booking_history(self):
        print("\n=== Booking History ===")
        try:
            cursor = self.connection.cursor()
            sql = "SELECT * FROM bookings"
            cursor.execute(sql)
            bookings = cursor.fetchall()

            print("\nBooking History:")
            print("ID | Car ID | Username | Start Date | Rental Days | Total Cost | Status")
            for booking in bookings:
                print(f"{booking[0]} | {booking[1]} | {booking[2]} | {booking[3]} | {booking[4]} | {booking[5]:.2f} | {booking[6]}")
        except sqlite3.Error as e:
            print(f"Error: {e}")
            self.connection.rollback()
        finally:
            cursor.close()

    def view_order_history(self):
        print("\n=== Order History ===")
        try:
            cursor = self.connection.cursor()
            sql = "SELECT * FROM car_rental"
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                print(row)
        except sqlite3.Error as e:
            print(f"Error retrieving order history: {e}")
            self.connection.rollback()
        finally:
            cursor.close()


# === Customer class ===
class Customer(DatabaseManager, AbstractUser):
    def menu(self):
        while True:
            print("\n=== Customer Menu ===")
            print("1. View Available Cars")
            print("2. Rent a Car")
            print("3. Book a Car")
            print("4. Return a Car")
            print("5. Back to Main Menu")

            choice = input("Enter your choice (1-5): ")
            if choice == "1":
                self.view_available_cars()
            elif choice == "2":
                self.rent_car()
            elif choice == "3":
                self.book_car()
            elif choice == "4":
                self.return_car()
            elif choice == "5":
                break
            else:
                print("Invalid choice, please try again.")

    def view_available_cars(self):
        try:
            cursor = self.connection.cursor()
            sql = "SELECT * FROM cars_info WHERE is_available = 1"
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                print(row)
        except sqlite3.Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()

    def book_car(self):
        car_id = int(input("Enter the car ID to book: "))
        user_name = input("Enter your username: ")
        booking_start_date = input("Enter the booking start date (YYYY-MM-DD): ")
        rental_days = int(input("Enter the number of rental days: "))
        try:
            cursor = self.connection.cursor()
            sql_check = "SELECT price_per_day FROM cars_info WHERE id = ? AND is_available = 1"
            cursor.execute(sql_check, (car_id,))
            car = cursor.fetchone()
            if car:
                price_per_day = car[0]
                total_cost = price_per_day * rental_days * 1.15

                sql_insert = "INSERT INTO bookings (car_id, user_name, booking_start_date, rental_days, total_cost,status ) VALUES (?, ?, ?, ?, ?, 'Pending')"
                cursor.execute(sql_insert, (car_id, user_name, booking_start_date, rental_days, total_cost))
                self.connection.commit()
                print("Booking is successful! Waiting for admin approval.")
            else:
                print("Car is not available or does not exist.")
        except sqlite3.Error as e:
            print(f"Error: {e}")
            self.connection.rollback()
        finally:
            cursor.close()

    def rent_car(self):
        car_id = int(input("Enter the car ID to rent: "))
        user_name = input("Enter your user name to rent: ")
        rental_days = int(input("Enter the number of rental days: "))
        try:
            cursor = self.connection.cursor()
            sql_check = """
            SELECT price_per_day FROM cars_info WHERE id = ? AND is_available = 1
            """
            cursor.execute(sql_check, (car_id,))
            car = cursor.fetchone()
            if car:
                price_per_day = car[0]
                total_cost = price_per_day * rental_days * 1.15
                sql_rent = """UPDATE cars_info SET is_available = 0 WHERE id = ?"""
                cursor.execute(sql_rent, (car_id,))
                sql_insert = """
                INSERT INTO car_rental (car_id, user_name, rental_days, total_cost, rent_date) 
                VALUES (?, ?, ?, ?, date('now'))
                """
                cursor.execute(sql_insert, (car_id, user_name, rental_days, total_cost))
                self.connection.commit()
                print(f"Car booked successfully! Total cost (GST included): ${total_cost:.2f}")
            else:
                print("Car is not available or does not exist.")
        except sqlite3.Error as e:
            print(f"Error: {e}")
            self.connection.rollback()
        finally:
            cursor.close()

    def return_car(self):
        car_id = int(input("Enter the car ID to return: "))
        try:
            cursor = self.connection.cursor()
            sql_check = """SELECT id FROM car_rental WHERE car_id = ?"""
            cursor.execute(sql_check, (car_id,))
            rental = cursor.fetchone()
            if rental:
                sql_return = """UPDATE cars_info SET is_available = 1 WHERE id = ?"""
                cursor.execute(sql_return, (car_id,))
                sql_delete = """DELETE FROM car_rental WHERE car_id = ?"""
                cursor.execute(sql_delete, (car_id,))
                self.connection.commit()
                print("Car returned successfully!")
            else:
                print("No rental record found for this car.")
        except sqlite3.Error as e:
            print(f"Error: {e}")
            self.connection.rollback()
        finally:
            cursor.close()

# Database file name
DATABASE_FILE = "car_rental.db"

# Function to create tables
def create_tables(connection):
    """Create necessary tables if they don't exist."""
    try:
        cursor = connection.cursor()

        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT  UNIQUE NOT NULL,
                password TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0
            )
        """)

        # Create cars_info table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cars_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                make TEXT NOT NULL,
                model TEXT NOT NULL,
                year INTEGER NOT NULL,
                mileage INTEGER NOT NULL,
                price_per_day REAL NOT NULL,
                is_available INTEGER DEFAULT 1
            )
        """)

        # Create bookings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                car_id INTEGER NOT NULL,
                user_name TEXT NOT NULL,
                booking_start_date TEXT NOT NULL,
                rental_days INTEGER NOT NULL,
                total_cost DECIMAL NOT NULL,
                status TEXT DEFAULT 'Pending',
                FOREIGN KEY (car_id) REFERENCES cars_info (id)
            )
        """)

        # Create car_rental table for rental history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS car_rental (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                car_id INTEGER NOT NULL,
                user_name TEXT  NOT NULL,
                rental_days INTEGER NOT NULL,
                total_cost REAL NOT NULL,
                rent_date TEXT NOT NULL DEFAULT (date('now')),
                FOREIGN KEY (car_id) REFERENCES cars_info (id)
            )
        """)

        connection.commit()
        # print("All necessary tables have been created successfully.")

    except sqlite3.Error as e:
        print(f"Error creating tables: {e}")
        connection.rollback()

# Function to populate tables
def populate_database(connection):
    """Populate tables with sample data."""
    try:
        cursor = connection.cursor()

        # Insert data into the cars_info table
        car_info_data = [
            ('Honda', 'Civic', 2019, 60000, 200),
            ('Honda', 'Accord', 2015, 121258, 154.2),
            ('Honda', 'CR-V', 2022, 8000, 249.2),
            ('Ford', 'Focus', 2021, 40001, 300),
            ('Ford', 'Fusion', 2019, 25000, 246.5),
            ('Ford', 'Escape', 2018, 40000, 214.3),
            ('Tesla', 'Model 3', 2010, 101245, 189),
            ('Tesla', 'Model S', 2020, 35480, 463.2),
            ('Tesla', 'Model X', 2019, 41350, 294.3),
            ('Chevrolet', 'Malibu', 2013, 89246, 219),
            ('Chevrolet', 'Impala', 2020, 65000, 158.5),
            ('Chevrolet', 'Equinox', 2021, 54000, 196.4),
            ('Toyota', 'Corolla', 2020, 15000, 245.0),
            ('Toyota', 'Camry', 2018, 30000, 350.0),
            ('Toyota', 'RAV4', 2021, 12000, 255.0),
            ('Nissan', 'Altima', 2018, 30000, 246.00),
            ('Nissan', 'Sentra', 2021, 12000, 240.00),
            ('Nissan', 'Rogue', 2020, 22000, 250.00),
            ('BMW', '3 Series', 2019, 20000, 295.00),
            ('BMW', '5 Series', 2018, 35000, 320.00),
            ('BMW', 'X5', 2021, 15000, 330.00),
            ('Mercedes-Benz', 'C-Class', 2020, 18000, 300.00),
            ('Mercedes-Benz', 'E-Class', 2019, 25000, 425.00),
            ('Mercedes-Benz', 'GLC', 2022, 12000, 500.00),
            ('Audi', 'A4', 2019, 24000, 190.00),
            ('Audi', 'Q5', 2020, 20000, 210.00),
            ('Audi', 'A6', 2018, 40000, 321.00),
            ('Volkswagen', 'Jetta', 2019, 22000, 250.00),
            ('Volkswagen', 'Passat', 2020, 18000, 255.00),
            ('Volkswagen', 'Tiguan', 2021, 12000, 260.00)
        ]

        cursor.executemany("""
            INSERT INTO cars_info (make, model, year, mileage, price_per_day, is_available)
            VALUES (?, ?, ?, ?, ?, 1)
        """, car_info_data)

        # Insert admin user into the users table
        admin_user_data = ('admin', 'admin123', 1)
        cursor.execute("""
            INSERT INTO users (username, password, is_admin)
            VALUES (?, ?, ?)
        """, admin_user_data)

        connection.commit()
        # print("Sample data has been successfully inserted into the database.")

    except sqlite3.Error as e:
        print(f"Error inserting data into database: {e}")
        connection.rollback()


# === Main Program ===
def main():
    # Connect to the database (it will be created if it doesn't exist)
    connection = sqlite3.connect(DATABASE_FILE)

    # try:
    #     # Create tables
    #     create_tables(connection)
    #
    #     # Populate tables with sample data
    #     populate_database(connection)
    #
    # finally:
    #     # Close the connection
    #     connection.close()
    #     # print("Database connection closed.")


    # Initialize database connection
    user_manager = UserManager(DATABASE_FILE)

    while True:
        print("\n=== Car Rental System ===")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            user_manager.register()
        elif choice == "2":
            user_type = user_manager.login()
            if user_type == "admin":
                admin = Admin(DATABASE_FILE)
                admin.menu()
                admin.close_connection()
            elif user_type == "customer":
                customer = Customer(DATABASE_FILE)
                customer.menu()
                customer.close_connection()
        elif choice == "3":
            print("Thank you for using the Car Rental System!")
            user_manager.close_connection()
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()