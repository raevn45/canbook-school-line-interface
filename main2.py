from database import get_connection
from datetime import datetime


# =========================================================
# DATABASE SETUP
# =========================================================

def setup_database():
    """Add required columns without deleting existing data."""
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SHOW COLUMNS FROM users LIKE 'favourite_word'")
        if cursor.fetchone() is None:
            cursor.execute(
                "ALTER TABLE users ADD COLUMN favourite_word VARCHAR(255) NULL"
            )
            print("Added favourite_word column.")

        cursor.execute("SHOW COLUMNS FROM orders LIKE 'status'")
        if cursor.fetchone() is None:
            cursor.execute(
                "ALTER TABLE orders ADD COLUMN status "
                "VARCHAR(30) NOT NULL DEFAULT 'Pending'"
            )
            print("Added order status column.")

        cursor.execute("SHOW COLUMNS FROM menu LIKE 'stock_quantity'")
        if cursor.fetchone() is None:
            cursor.execute(
                "ALTER TABLE menu ADD COLUMN stock_quantity "
                "INT NOT NULL DEFAULT 50"
            )
            print("Added stock_quantity column.")
            print("New stock values start at 50.")
            print("Update them to match your actual inventory.")

        conn.commit()
        return True

    except Exception as e:
        print("Database setup error:", e)
        if conn:
            conn.rollback()
        return False

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def read_positive_int(message):
    while True:
        try:
            value = int(input(message))
            if value > 0:
                return value
            print("Please enter a number greater than zero.")
        except ValueError:
            print("Invalid input. Enter a whole number.")


def read_menu_choice(message, minimum, maximum):
    while True:
        try:
            choice = int(input(message))
            if minimum <= choice <= maximum:
                return choice
            print("Choose an option from", minimum, "to", maximum)
        except ValueError:
            print("Invalid input. Enter a number.")


def log_order(username, item_name, quantity, total):
    try:
        with open("orders.txt", "a", encoding="utf-8") as file:
            file.write(
                f"{datetime.now():%Y-%m-%d %H:%M:%S} | "
                f"Student: {username} | Item: {item_name} | "
                f"Quantity: {quantity} | Total: {total:.2f}\n"
            )
    except OSError as e:
        print("Could not write to orders.txt:", e)


# =========================================================
# REGISTRATION
# =========================================================

def register():
    print("\n========== STUDENT REGISTRATION ==========")

    username = input("Choose a username: ").strip()
    password = input("Choose a password: ").strip()
    favourite_word = input(
        "Choose a favourite word for recovery: "
    ).strip()

    if not username or not password or not favourite_word:
        print("All fields are required.")
        return

    if len(username) > 100 or len(password) > 255:
        print("Username or password is too long.")
        return

    if len(favourite_word) > 255:
        print("Favourite word is too long.")
        return

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT username FROM users WHERE username = %s",
            (username,)
        )

        if cursor.fetchone():
            print("That username already exists.")
            return

        cursor.execute(
            """
            INSERT INTO users
                (username, password, role, favourite_word)
            VALUES (%s, %s, 'student', %s)
            """,
            (username, password, favourite_word)
        )

        conn.commit()
        print("Registration successful!")
        print("You can now log in.")

    except Exception as e:
        if conn:
            conn.rollback()
        print("Registration failed:", e)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# =========================================================
# FORGOT PASSWORD
# =========================================================

def forgot_password():
    print("\n========== PASSWORD RECOVERY ==========")

    username = input("Enter your username: ").strip()
    favourite_word = input("Enter your favourite word: ").strip()

    if not username or not favourite_word:
        print("Both fields are required.")
        return

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT username
            FROM users
            WHERE username = %s AND favourite_word = %s
            """,
            (username, favourite_word)
        )

        if not cursor.fetchone():
            print("The details do not match.")
            return

        new_password = input("Enter your new password: ").strip()
        confirm_password = input("Confirm your new password: ").strip()

        if not new_password:
            print("Password cannot be blank.")
            return

        if len(new_password) > 255:
            print("Password is too long.")
            return

        if new_password != confirm_password:
            print("Passwords do not match.")
            return

        cursor.execute(
            "UPDATE users SET password = %s WHERE username = %s",
            (new_password, username)
        )

        conn.commit()
        print("Password updated successfully!")

    except Exception as e:
        if conn:
            conn.rollback()
        print("Password recovery failed:", e)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# =========================================================
# SET OR CHANGE RECOVERY WORD
# =========================================================

def set_recovery_word():
    print("\n========== SET RECOVERY WORD ==========")

    username = input("Enter your username: ").strip()
    password = input("Enter your current password: ").strip()
    favourite_word = input(
        "Enter your new favourite/recovery word: "
    ).strip()

    if not username or not password or not favourite_word:
        print("All fields are required.")
        return

    if len(favourite_word) > 255:
        print("Recovery word is too long.")
        return

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT username
            FROM users
            WHERE username = %s AND password = %s
            """,
            (username, password)
        )

        if not cursor.fetchone():
            print("Username or password is incorrect.")
            return

        cursor.execute(
            """
            UPDATE users
            SET favourite_word = %s
            WHERE username = %s
            """,
            (favourite_word, username)
        )

        conn.commit()
        print("Recovery word saved successfully!")
        print("You can use it if you forget your password.")

    except Exception as e:
        if conn:
            conn.rollback()
        print("Could not save the recovery word:", e)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# =========================================================
# LOGIN AND ACCOUNT MENU
# =========================================================

def login():
    while True:
        print("\n========== ACCOUNT MENU ==========")
        print("1. Log in")
        print("2. Forgot password")
        print("3. Set/change recovery word")
        print("4. Back to main menu")

        choice = read_menu_choice("Enter your choice: ", 1, 4)

        if choice == 2:
            forgot_password()
            continue

        elif choice == 3:
            set_recovery_word()
            continue

        elif choice == 4:
            return

        username = input("Username: ").strip()
        password = input("Password: ").strip()

        if not username or not password:
            print("Enter both username and password.")
            continue

        conn = None
        cursor = None
        role = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT role
                FROM users
                WHERE username = %s AND password = %s
                """,
                (username, password)
            )

            result = cursor.fetchone()

            if result:
                role = result[0]

        except Exception as e:
            print("Login failed:", e)

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        if role == "student":
            print("\nLogin successful!")
            student_dashboard(username)
            return

        elif role == "canteen":
            print("\nCanteen login successful!")
            canteen_dashboard()
            return

        else:
            print("Invalid username or password.")


# =========================================================
# VIEW MENU
# =========================================================

def show_menu():
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT item_id, item_name, price, stock_quantity
            FROM menu
            ORDER BY item_id
            """
        )

        items = cursor.fetchall()

        print("\n================ CANTEEN MENU ================")
        print(f"{'ID':<6}{'ITEM':<25}{'PRICE':>10}{'STOCK':>10}")
        print("-" * 51)

        if not items:
            print("No menu items are available.")
            return

        for item_id, item_name, price, stock in items:
            print(
                f"{item_id:<6}{item_name:<25}"
                f"{float(price):>10.2f}{stock:>10}"
            )

    except Exception as e:
        print("Could not display the menu:", e)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# =========================================================
# PLACE ORDER
# =========================================================

def place_order(username):
    cart = {}

    while True:
        show_menu()
        print("\nEnter 0 when you have finished selecting items.")

        try:
            item_id = int(input("Enter item ID: "))
        except ValueError:
            print("Enter a valid item ID.")
            continue

        if item_id == 0:
            break

        if item_id < 0:
            print("Item ID cannot be negative.")
            continue

        quantity = read_positive_int("Enter quantity: ")

        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT item_name, price, stock_quantity
                FROM menu
                WHERE item_id = %s
                """,
                (item_id,)
            )

            item = cursor.fetchone()

            if not item:
                print("That item does not exist.")
                continue

            item_name, price, stock = item
            already_selected = cart.get(
                item_id, {}
            ).get("quantity", 0)

            if already_selected + quantity > stock:
                print("Not enough stock available.")
                continue

            if item_id in cart:
                cart[item_id]["quantity"] += quantity
            else:
                cart[item_id] = {
                    "name": item_name,
                    "price": float(price),
                    "quantity": quantity
                }

            print("Added to cart.")

        except Exception as e:
            print("Could not add item:", e)

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    if not cart:
        print("Your cart is empty. No order placed.")
        return

    total = sum(
        item["price"] * item["quantity"]
        for item in cart.values()
    )

    print("\n============== ORDER SUMMARY ==============")

    for item in cart.values():
        subtotal = item["price"] * item["quantity"]
        print(
            f"{item['name']} x {item['quantity']} "
            f"= {subtotal:.2f}"
        )

    print(f"Total: {total:.2f}")

    confirm = input("Confirm order? (yes/no): ").strip().lower()

    if confirm != "yes":
        print("Order cancelled. Nothing was saved.")
        return

    conn = None
    cursor = None
    order_rows = []

    try:
        conn = get_connection()
        conn.start_transaction()
        cursor = conn.cursor()

        for item_id, details in cart.items():
            cursor.execute(
                """
                SELECT item_name, price, stock_quantity
                FROM menu
                WHERE item_id = %s
                FOR UPDATE
                """,
                (item_id,)
            )

            current_item = cursor.fetchone()

            if not current_item:
                raise ValueError(
                    f"Menu item {item_id} no longer exists."
                )

            item_name, price, stock = current_item
            quantity = details["quantity"]

            if quantity > stock:
                raise ValueError(
                    f"Not enough stock for {item_name}. "
                    f"Available: {stock}"
                )

            subtotal = float(price) * quantity

            cursor.execute(
                """
                INSERT INTO orders
                    (username, item_id, quantity, total, status)
                VALUES (%s, %s, %s, %s, 'Pending')
                """,
                (username, item_id, quantity, subtotal)
            )

            cursor.execute(
                """
                UPDATE menu
                SET stock_quantity = stock_quantity - %s
                WHERE item_id = %s
                """,
                (quantity, item_id)
            )

            order_rows.append((item_name, quantity, subtotal))

        conn.commit()
        print("Order placed successfully!")

        for item_name, quantity, subtotal in order_rows:
            log_order(username, item_name, quantity, subtotal)

        print("Your order has been saved.")

    except Exception as e:
        if conn:
            conn.rollback()
        print("Could not place the order:", e)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# =========================================================
# VIEW STUDENT'S ORDERS
# =========================================================

def view_orders(username):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT o.order_id, m.item_name, o.quantity,
                   o.total, o.status
            FROM orders o
            JOIN menu m ON o.item_id = m.item_id
            WHERE o.username = %s
            ORDER BY o.order_id DESC
            """,
            (username,)
        )

        orders = cursor.fetchall()

        print("\n================ MY ORDERS ================")

        if not orders:
            print("You have not placed any orders.")
            return

        print(
            f"{'ORDER ID':<12}{'ITEM':<22}{'QTY':<7}"
            f"{'TOTAL':<12}{'STATUS'}"
        )
        print("-" * 65)

        for order_id, item_name, quantity, total, status in orders:
            print(
                f"{order_id:<12}{item_name:<22}{quantity:<7}"
                f"{float(total):<12.2f}{status}"
            )

    except Exception as e:
        print("Could not retrieve your orders:", e)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# =========================================================
# STUDENT ORDER CANCELLATION
# =========================================================

def cancel_student_order(username):
    view_orders(username)

    order_id = read_positive_int(
        "\nEnter the order ID to cancel: "
    )

    conn = None
    cursor = None

    try:
        conn = get_connection()
        conn.start_transaction()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT o.item_id, o.quantity, o.status
            FROM orders o
            WHERE o.order_id = %s AND o.username = %s
            FOR UPDATE
            """,
            (order_id, username)
        )

        order = cursor.fetchone()

        if not order:
            conn.rollback()
            print("Order not found.")
            return

        item_id, quantity, status = order

        if status != "Pending":
            conn.rollback()
            print("Only pending orders can be cancelled.")
            return

        cursor.execute(
            """
            UPDATE orders
            SET status = 'Cancelled'
            WHERE order_id = %s AND username = %s
            """,
            (order_id, username)
        )

        cursor.execute(
            """
            UPDATE menu
            SET stock_quantity = stock_quantity + %s
            WHERE item_id = %s
            """,
            (quantity, item_id)
        )

        conn.commit()
        print("Order cancelled successfully.")

    except Exception as e:
        if conn:
            conn.rollback()
        print("Could not cancel the order:", e)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# =========================================================
# VIEW ALL ORDERS (CANTEEN)
# =========================================================

def view_all_orders():
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT o.order_id, o.username, m.item_name,
                   o.quantity, o.total, o.status
            FROM orders o
            JOIN menu m ON o.item_id = m.item_id
            ORDER BY o.order_id DESC
            """
        )

        orders = cursor.fetchall()

        print("\n================ ALL ORDERS ================")

        if not orders:
            print("No orders found.")
            return

        print(
            f"{'ID':<8}{'STUDENT':<18}{'ITEM':<20}"
            f"{'QTY':<6}{'TOTAL':<10}{'STATUS'}"
        )
        print("-" * 75)

        for order in orders:
            order_id, username, item, quantity, total, status = order

            print(
                f"{order_id:<8}{username:<18}{item:<20}"
                f"{quantity:<6}{float(total):<10.2f}{status}"
            )

    except Exception as e:
        print("Could not retrieve all orders:", e)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# =========================================================
# UPDATE ORDER STATUS (CANTEEN)
# =========================================================

def update_order_status():
    view_all_orders()

    order_id = read_positive_int(
        "\nEnter the order ID to update: "
    )

    print("\n1. Preparing")
    print("2. Ready")
    print("3. Collected")
    print("4. Cancelled")
    print("5. Back")

    choice = read_menu_choice("Choose status: ", 1, 5)

    if choice == 5:
        return

    statuses = {
        1: "Preparing",
        2: "Ready",
        3: "Collected",
        4: "Cancelled"
    }

    new_status = statuses[choice]

    conn = None
    cursor = None

    try:
        conn = get_connection()
        conn.start_transaction()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT item_id, quantity, status
            FROM orders
            WHERE order_id = %s
            FOR UPDATE
            """,
            (order_id,)
        )

        order = cursor.fetchone()

        if not order:
            conn.rollback()
            print("Order not found.")
            return

        item_id, quantity, old_status = order

        if old_status == "Cancelled":
            conn.rollback()
            print("A cancelled order cannot be changed.")
            return

        if old_status == "Collected":
            conn.rollback()
            print("A collected order cannot be changed.")
            return

        if new_status == "Cancelled":
            cursor.execute(
                """
                UPDATE menu
                SET stock_quantity = stock_quantity + %s
                WHERE item_id = %s
                """,
                (quantity, item_id)
            )

        cursor.execute(
            """
            UPDATE orders
            SET status = %s
            WHERE order_id = %s
            """,
            (new_status, order_id)
        )

        conn.commit()
        print("Order status updated to", new_status)

    except Exception as e:
        if conn:
            conn.rollback()
        print("Could not update order status:", e)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# =========================================================
# VIEW DEMAND REPORT
# =========================================================

def show_demand():
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT m.item_id, m.item_name,
                   COALESCE(SUM(o.quantity), 0) AS total_demand
            FROM menu m
            LEFT JOIN orders o
                ON m.item_id = o.item_id
                AND o.status != 'Cancelled'
            GROUP BY m.item_id, m.item_name
            ORDER BY total_demand DESC, m.item_name
            """
        )

        demand = cursor.fetchall()

        print("\n================ ITEM DEMAND ================")

        if not demand:
            print("No menu items found.")
            return

        print(f"{'ID':<8}{'ITEM':<25}{'QUANTITY ORDERED'}")
        print("-" * 50)

        for item_id, item_name, quantity in demand:
            print(f"{item_id:<8}{item_name:<25}{quantity}")

    except Exception as e:
        print("Could not generate demand report:", e)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# =========================================================
# LOW-STOCK REPORT
# =========================================================

def show_low_stock():
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT item_id, item_name, stock_quantity
            FROM menu
            WHERE stock_quantity <= 10
            ORDER BY stock_quantity ASC
            """
        )

        items = cursor.fetchall()

        print("\n================ LOW STOCK ================")

        if not items:
            print("No items are currently low on stock.")
            return

        print(f"{'ID':<8}{'ITEM':<25}{'STOCK LEFT'}")
        print("-" * 45)

        for item_id, item_name, stock in items:
            print(f"{item_id:<8}{item_name:<25}{stock}")

    except Exception as e:
        print("Could not display low-stock report:", e)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# =========================================================
# UPDATE MENU STOCK (CANTEEN)
# =========================================================

def update_stock():
    show_menu()

    item_id = read_positive_int(
        "\nEnter the item ID to update: "
    )

    new_stock = None

    while new_stock is None:
        try:
            new_stock = int(input("Enter the new stock quantity: "))
            if new_stock < 0:
                print("Stock cannot be negative.")
                new_stock = None
        except ValueError:
            print("Enter a valid whole number.")

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE menu
            SET stock_quantity = %s
            WHERE item_id = %s
            """,
            (new_stock, item_id)
        )

        if cursor.rowcount == 0:
            conn.rollback()
            print("Item not found, or its stock was unchanged.")
            return

        conn.commit()
        print("Stock updated successfully.")

    except Exception as e:
        if conn:
            conn.rollback()
        print("Could not update stock:", e)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# =========================================================
# STUDENT DASHBOARD
# =========================================================

def student_dashboard(username):
    while True:
        print("\n========== STUDENT DASHBOARD ==========")
        print("Welcome,", username)
        print("1. View Menu")
        print("2. Place Order")
        print("3. View My Orders")
        print("4. Cancel a Pending Order")
        print("5. Logout")

        choice = read_menu_choice("Enter your choice: ", 1, 5)

        if choice == 1:
            show_menu()

        elif choice == 2:
            place_order(username)

        elif choice == 3:
            view_orders(username)

        elif choice == 4:
            cancel_student_order(username)

        elif choice == 5:
            print("Logged out successfully.")
            break


# =========================================================
# CANTEEN DASHBOARD
# =========================================================

def canteen_dashboard():
    while True:
        print("\n========== CANTEEN DASHBOARD ==========")
        print("1. View All Orders")
        print("2. Update Order Status")
        print("3. View Demand Report")
        print("4. View Low Stock")
        print("5. Update Menu Stock")
        print("6. View Menu")
        print("7. Logout")

        choice = read_menu_choice("Enter your choice: ", 1, 7)

        if choice == 1:
            view_all_orders()

        elif choice == 2:
            update_order_status()

        elif choice == 3:
            show_demand()

        elif choice == 4:
            show_low_stock()

        elif choice == 5:
            update_stock()

        elif choice == 6:
            show_menu()

        elif choice == 7:
            print("Logged out successfully.")
            break


# =========================================================
# MAIN MENU
# =========================================================

def main():
    print("======================================")
    print("      CANTEEN PRE-ORDER SYSTEM")
    print("======================================")

    if not setup_database():
        print("\nDatabase setup failed.")
        print("Check your database.py connection and table names.")
        return

    while True:
        print("\n========== MAIN MENU ==========")
        print("1. Login")
        print("2. Register")
        print("3. Exit")

        choice = read_menu_choice("Enter your choice: ", 1, 3)

        if choice == 1:
            login()

        elif choice == 2:
            register()

        elif choice == 3:
            print("Thank you for using the Canteen Pre-Order System!")
            break


# =========================================================
# RUN PROGRAM
# =========================================================

if __name__ == "__main__":
    main()