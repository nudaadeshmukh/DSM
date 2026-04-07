import sqlite3
from flask import g, current_app


def get_db():
    """Get database connection, creating one if it doesn't exist for this request."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    """Close database connection at end of request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Create all tables if they don't exist."""
    db = sqlite3.connect(current_app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            username  TEXT    NOT NULL UNIQUE,
            email     TEXT    NOT NULL UNIQUE,
            password  TEXT    NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Suppliers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS suppliers (
            supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            lead_time   REAL    NOT NULL
        )
    ''')

    # Warehouses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS warehouses (
            warehouse_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name         TEXT NOT NULL,
            location     TEXT NOT NULL
        )
    ''')

    # Retailers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS retailers (
            retailer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            location    TEXT NOT NULL
        )
    ''')

    # Products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT NOT NULL,
            holding_cost  REAL NOT NULL,
            ordering_cost REAL NOT NULL
        )
    ''')

    # Inventory table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            inventory_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            location_id   INTEGER NOT NULL,
            product_id    INTEGER NOT NULL,
            demand        REAL    NOT NULL,
            ordering_cost REAL    NOT NULL,
            holding_cost  REAL    NOT NULL,
            lead_time     REAL    NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    ''')

    # Transportation routes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transportation_routes (
            route_id       INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id      INTEGER NOT NULL,
            destination_id INTEGER NOT NULL,
            cost           REAL    NOT NULL
        )
    ''')

    # Results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            result_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id        INTEGER NOT NULL,
            eoq            REAL,
            rop            REAL,
            best_path      TEXT,
            transport_cost REAL,
            total_cost     REAL,
            created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')

    db.commit()
    db.close()
    print("Database initialized successfully.")
