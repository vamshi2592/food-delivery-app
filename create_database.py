"""
create_database.py
-------------------
Generates a realistic synthetic food-delivery SQLite database.

Uses ONLY the Python standard library (sqlite3, random, datetime) so it runs
anywhere with no extra installs. The random seed is FIXED so the database is
byte-for-byte reproducible on every run -- this directly supports the
"ensure reproducibility" rubric item.

Schema (5 related tables):
    customers(customer_id, name, email, phone, city, signup_date)
    restaurants(restaurant_id, name, cuisine, city, rating)
    delivery_agents(agent_id, name, phone, vehicle_type, rating)
    orders(order_id, customer_id, restaurant_id, agent_id, order_date,
           status, payment_method, total_amount, delivery_time_min)
    order_items(item_id, order_id, item_name, quantity, unit_price)

Run:
    python3 create_database.py
"""

import os
import random
import sqlite3
from datetime import datetime, timedelta

# ----------------------------------------------------------------------------
# Reproducibility: fix the seed so the generated data is identical every run.
# ----------------------------------------------------------------------------
SEED = 42
random.seed(SEED)

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "food_delivery.db")

# ----------------------------------------------------------------------------
# Reference data pools
# ----------------------------------------------------------------------------
FIRST_NAMES = ["Aarav", "Vivaan", "Aditya", "Diya", "Ananya", "Ishaan", "Kabir",
               "Saanvi", "Riya", "Arjun", "Meera", "Rohan", "Priya", "Karan",
               "Neha", "Sai", "Anjali", "Dev", "Tara", "Nikhil"]
LAST_NAMES = ["Sharma", "Verma", "Patel", "Reddy", "Nair", "Iyer", "Gupta",
              "Singh", "Khan", "Das", "Rao", "Mehta", "Joshi", "Kapoor"]
CITIES = ["Mumbai", "Bengaluru", "Hyderabad", "Delhi", "Pune", "Chennai"]
CUISINES = ["North Indian", "South Indian", "Chinese", "Italian", "Mexican",
            "Fast Food", "Desserts", "Biryani"]
RESTAURANT_WORDS = ["Spice", "Tandoor", "Curry", "Urban", "Royal", "Green",
                    "Golden", "Coastal", "Street", "Garden", "Express", "House"]
RESTAURANT_TAILS = ["Kitchen", "Diner", "Bistro", "Hub", "Corner", "Junction",
                    "Treat", "Cafe", "Express"]
VEHICLES = ["Bike", "Scooter", "Bicycle", "EV Scooter"]
STATUSES = ["Delivered", "Delivered", "Delivered", "Delivered",
            "Cancelled", "In Transit"]  # weighted toward Delivered
PAYMENTS = ["UPI", "Credit Card", "Debit Card", "Cash on Delivery", "Wallet"]
MENU = {
    "North Indian": [("Butter Chicken", 320), ("Paneer Tikka", 260),
                     ("Dal Makhani", 220), ("Naan", 40), ("Jeera Rice", 150)],
    "South Indian": [("Masala Dosa", 120), ("Idli Sambar", 90),
                     ("Filter Coffee", 50), ("Vada", 60), ("Uttapam", 130)],
    "Chinese": [("Hakka Noodles", 180), ("Manchurian", 200),
                ("Fried Rice", 170), ("Spring Rolls", 140)],
    "Italian": [("Margherita Pizza", 350), ("Pasta Alfredo", 320),
                ("Garlic Bread", 150), ("Lasagna", 380)],
    "Mexican": [("Tacos", 240), ("Burrito", 280), ("Nachos", 220),
                ("Quesadilla", 260)],
    "Fast Food": [("Veg Burger", 120), ("Chicken Burger", 160),
                  ("French Fries", 100), ("Cold Drink", 60)],
    "Desserts": [("Gulab Jamun", 90), ("Chocolate Brownie", 140),
                 ("Ice Cream", 110), ("Rasmalai", 120)],
    "Biryani": [("Chicken Biryani", 280), ("Mutton Biryani", 360),
                ("Veg Biryani", 220), ("Raita", 50)],
}

# ----------------------------------------------------------------------------
# Volume knobs
# ----------------------------------------------------------------------------
N_CUSTOMERS = 60
N_RESTAURANTS = 25
N_AGENTS = 20
N_ORDERS = 300
START_ORDER_ID = 1001  # human-friendly order numbers, easy to test in the agent


def build_schema(cur):
    """Drop and recreate all tables (idempotent re-runs)."""
    cur.executescript(
        """
        DROP TABLE IF EXISTS order_items;
        DROP TABLE IF EXISTS orders;
        DROP TABLE IF EXISTS delivery_agents;
        DROP TABLE IF EXISTS restaurants;
        DROP TABLE IF EXISTS customers;

        CREATE TABLE customers (
            customer_id  INTEGER PRIMARY KEY,
            name         TEXT    NOT NULL,
            email        TEXT    NOT NULL,
            phone        TEXT    NOT NULL,
            city         TEXT    NOT NULL,
            signup_date  TEXT    NOT NULL
        );

        CREATE TABLE restaurants (
            restaurant_id INTEGER PRIMARY KEY,
            name          TEXT    NOT NULL,
            cuisine       TEXT    NOT NULL,
            city          TEXT    NOT NULL,
            rating        REAL    NOT NULL
        );

        CREATE TABLE delivery_agents (
            agent_id     INTEGER PRIMARY KEY,
            name         TEXT    NOT NULL,
            phone        TEXT    NOT NULL,
            vehicle_type TEXT    NOT NULL,
            rating       REAL    NOT NULL
        );

        CREATE TABLE orders (
            order_id          INTEGER PRIMARY KEY,
            customer_id       INTEGER NOT NULL,
            restaurant_id     INTEGER NOT NULL,
            agent_id          INTEGER NOT NULL,
            order_date        TEXT    NOT NULL,
            status            TEXT    NOT NULL,
            payment_method    TEXT    NOT NULL,
            total_amount      REAL    NOT NULL,
            delivery_time_min INTEGER NOT NULL,
            FOREIGN KEY (customer_id)   REFERENCES customers(customer_id),
            FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id),
            FOREIGN KEY (agent_id)      REFERENCES delivery_agents(agent_id)
        );

        CREATE TABLE order_items (
            item_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id   INTEGER NOT NULL,
            item_name  TEXT    NOT NULL,
            quantity   INTEGER NOT NULL,
            unit_price REAL    NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id)
        );
        """
    )


def rand_phone():
    return "9" + "".join(str(random.randint(0, 9)) for _ in range(9))


def seed_customers(cur):
    rows = []
    base = datetime(2023, 1, 1)
    for cid in range(1, N_CUSTOMERS + 1):
        fn, ln = random.choice(FIRST_NAMES), random.choice(LAST_NAMES)
        name = f"{fn} {ln}"
        email = f"{fn.lower()}.{ln.lower()}{cid}@example.com"
        signup = base + timedelta(days=random.randint(0, 700))
        rows.append((cid, name, email, rand_phone(), random.choice(CITIES),
                     signup.strftime("%Y-%m-%d")))
    cur.executemany("INSERT INTO customers VALUES (?,?,?,?,?,?)", rows)


def seed_restaurants(cur):
    rows = []
    for rid in range(1, N_RESTAURANTS + 1):
        name = f"{random.choice(RESTAURANT_WORDS)} {random.choice(RESTAURANT_TAILS)}"
        rows.append((rid, name, random.choice(CUISINES), random.choice(CITIES),
                     round(random.uniform(3.2, 4.9), 1)))
    cur.executemany("INSERT INTO restaurants VALUES (?,?,?,?,?)", rows)
    return {rid: cuisine for rid, _, cuisine, _, _ in rows}


def seed_agents(cur):
    rows = []
    for aid in range(1, N_AGENTS + 1):
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        rows.append((aid, name, rand_phone(), random.choice(VEHICLES),
                     round(random.uniform(3.5, 5.0), 1)))
    cur.executemany("INSERT INTO delivery_agents VALUES (?,?,?,?,?)", rows)


def seed_orders(cur, restaurant_cuisine):
    order_rows = []
    item_rows = []
    base = datetime(2024, 1, 1)
    for i in range(N_ORDERS):
        oid = START_ORDER_ID + i
        cust = random.randint(1, N_CUSTOMERS)
        rest = random.randint(1, N_RESTAURANTS)
        agent = random.randint(1, N_AGENTS)
        odate = base + timedelta(days=random.randint(0, 540),
                                 hours=random.randint(8, 23),
                                 minutes=random.randint(0, 59))
        status = random.choice(STATUSES)

        # 1-4 distinct menu items from the restaurant's cuisine
        cuisine = restaurant_cuisine[rest]
        menu = MENU[cuisine]
        picks = random.sample(menu, k=random.randint(1, min(4, len(menu))))
        total = 0.0
        for item_name, price in picks:
            qty = random.randint(1, 3)
            total += qty * price
            item_rows.append((oid, item_name, qty, float(price)))

        # Cancelled orders carry no realized amount / delivery time
        if status == "Cancelled":
            total_amount = 0.0
            delivery_time = 0
        else:
            total_amount = round(total, 2)
            delivery_time = random.randint(18, 65)

        order_rows.append((oid, cust, rest, agent,
                           odate.strftime("%Y-%m-%d %H:%M:%S"),
                           status, random.choice(PAYMENTS),
                           total_amount, delivery_time))

    cur.executemany(
        "INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?)", order_rows)
    cur.executemany(
        "INSERT INTO order_items (order_id, item_name, quantity, unit_price) "
        "VALUES (?,?,?,?)", item_rows)


def main():
    os.makedirs(DB_DIR, exist_ok=True)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    build_schema(cur)
    seed_customers(cur)
    restaurant_cuisine = seed_restaurants(cur)
    seed_agents(cur)
    seed_orders(cur, restaurant_cuisine)
    conn.commit()

    # Quick summary so the run is self-verifying
    print(f"Database created at: {DB_PATH}\n")
    for tbl in ["customers", "restaurants", "delivery_agents",
                "orders", "order_items"]:
        n = cur.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
        print(f"  {tbl:<16} {n:>5} rows")

    print("\nSample -- everything tied to Order ID 1001:")
    sample = cur.execute(
        """
        SELECT o.order_id, c.name AS customer, r.name AS restaurant,
               r.cuisine, a.name AS agent, o.status, o.total_amount
        FROM orders o
        JOIN customers c        ON c.customer_id   = o.customer_id
        JOIN restaurants r      ON r.restaurant_id = o.restaurant_id
        JOIN delivery_agents a  ON a.agent_id      = o.agent_id
        WHERE o.order_id = 1001
        """
    ).fetchone()
    print("  ", sample)
    conn.close()


if __name__ == "__main__":
    main()
